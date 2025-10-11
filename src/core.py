## core.py
## last updated: 11/010/2025 <d/m/y>
## p-y-l-i
import os
import io
import struct
import ctypes
import hashlib
import reedsolo
import mmap
import base64
import threading
from PySide6.QtCore import QThread
from PySide6.QtCore import Signal as pyqtSignal
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError, HashingError
    from argon2.low_level import hash_secret_raw, Type
    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False

from sm import clear_buffer
from cmp import compress_chunk, decompress_chunk, should_skip_compression, COMPRESSION_NONE, COMPRESSION_MODES

CHUNK_SIZE = 3 * 1024 * 1024
FORMAT_VERSION = 6
ALGORITHM_ID = 1
KDF_ID_PBKDF2 = 1
KDF_ID_ARGON2 = 2
SALT_SIZE = 16
NONCE_SIZE = 12
MAGIC_NUMBER = b"PYLI\x00"
MAX_EXT_LEN = 256
TAG_SIZE = 16
ECC_BYTES = 32
FLAG_RECOVERY_DATA = 0x01
FLAG_ARCHIVE_MODE = 0x02
ARGON2_TIME_COST = 3
ARGON2_MEMORY_COST = 65536
ARGON2_PARALLELISM = 4

def compress_chunk_threaded(chunk_data, compression_level):
    return compress_chunk(chunk_data, compression_level)

def create_archive(file_paths, progress_callback=None):
    archive_header = bytearray()
    archive_header.extend(struct.pack("!I", len(file_paths)))
    total_size = 0
    file_info = []
    for file_path in file_paths:
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            rel_path = os.path.relpath(file_path, os.path.commonpath(file_paths) if len(file_paths) > 1 else os.path.dirname(file_path))
            file_info.append((file_path, rel_path, size))
            total_size += size
    for file_path, rel_path, file_size in file_info:
        rel_path_bytes = rel_path.encode("utf-8")
        archive_header.extend(struct.pack("!I", len(rel_path_bytes)))
        archive_header.extend(rel_path_bytes)
        archive_header.extend(struct.pack("!Q", file_size))
    return bytes(archive_header), file_info, total_size

def extract_archive(archive_data, output_dir, progress_callback=None):
    offset = 0
    if len(archive_data) < 4:
        raise ValueError("Invalid archive: too short")    
    num_files = struct.unpack("!I", archive_data[offset:offset+4])[0]
    offset += 4   
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    files_info = []
    for i in range(num_files):
        if offset + 4 > len(archive_data):
            raise ValueError(f"Invalid archive: unexpected end while reading path length for file {i}")      
        path_len = struct.unpack("!I", archive_data[offset:offset+4])[0]
        offset += 4      
        if offset + path_len > len(archive_data):
            raise ValueError(f"Invalid archive: unexpected end while reading path for file {i}")        
        rel_path = archive_data[offset:offset+path_len].decode("utf-8")
        offset += path_len        
        if offset + 8 > len(archive_data):
            raise ValueError(f"Invalid archive: unexpected end while reading file size for file {i}")       
        file_size = struct.unpack("!Q", archive_data[offset:offset+8])[0]
        offset += 8        
        files_info.append((rel_path, file_size))
    data_offset = offset
    total_size = len(archive_data)    
    for rel_path, file_size in files_info:
        if progress_callback:
            progress_callback((data_offset / total_size) * 100)        
        if data_offset + file_size > len(archive_data):
            raise ValueError(f"Invalid archive: unexpected end while reading file data for {rel_path}")        
        file_data = archive_data[data_offset:data_offset+file_size]
        data_offset += file_size        
        output_path = os.path.join(output_dir, rel_path)
        if not os.path.abspath(output_path).startswith(os.path.abspath(output_dir)):
            raise ValueError(f"Invalid archive: path traversal attempt in {rel_path}")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)        
        with open(output_path, "wb") as f:
            f.write(file_data)  
    if progress_callback:
        progress_callback(100.0)

class CryptoWorker:
    def __init__(self, operation, in_path, out_path, password, custom_ext=None, new_name_type=None, output_dir=None, chunk_size=CHUNK_SIZE, kdf_iterations=1000000, secure_clear=False, add_recovery_data=False, compression_level="none", archive_mode=False, use_argon2=False, argon2_time_cost=ARGON2_TIME_COST, argon2_memory_cost=ARGON2_MEMORY_COST, argon2_parallelism=ARGON2_PARALLELISM, progress_callback=None, parent=None):
        self.operation = operation
        self.in_path = in_path
        self.out_path = out_path
        self.password = password
        self.custom_ext = custom_ext
        self.new_name_type = new_name_type
        self.output_dir = output_dir
        self.chunk_size = chunk_size
        self.kdf_iterations = kdf_iterations
        self.secure_clear = secure_clear
        self.add_recovery_data = add_recovery_data
        self.compression_level = compression_level
        self.archive_mode = archive_mode
        self.use_argon2 = use_argon2 and ARGON2_AVAILABLE
        self.argon2_time_cost = argon2_time_cost
        self.argon2_memory_cost = argon2_memory_cost
        self.argon2_parallelism = argon2_parallelism
        self.progress_callback = progress_callback
        self.is_canceled = False
        self.max_workers = min(8, os.cpu_count() or 1)

    def _derive_key_pbkdf2(self, salt, iterations=None):
        if iterations is None:
            iterations = self.kdf_iterations
        pwd_bytes = self.password.encode("utf-8")
        pwd_buffer = ctypes.create_string_buffer(len(pwd_bytes))
        pwd_buffer.raw = pwd_bytes
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        key = kdf.derive(pwd_buffer.value)
        if self.secure_clear:
            clear_buffer(pwd_buffer) 
        pwd_bytes = None
        return key

    def _derive_key_argon2(self, salt):
        try:
            password_bytes = self.password.encode("utf-8")
            key = hash_secret_raw(
                secret=password_bytes,
                salt=salt,
                time_cost=self.argon2_time_cost,
                memory_cost=self.argon2_memory_cost,
                parallelism=self.argon2_parallelism,
                hash_len=32,          # <- AES-256 key
                type=Type.ID
            )
            password_bytes = None
            return key
        except HashingError as e:
            raise ValueError(f"Argon2 key derivation failed: {str(e)}")

    def _derive_key(self, salt, iterations=None, kdf_type=None):
        if kdf_type is None:
            kdf_type = KDF_ID_ARGON2 if self.use_argon2 else KDF_ID_PBKDF2
        if kdf_type == KDF_ID_ARGON2 and ARGON2_AVAILABLE:
            return self._derive_key_argon2(salt)
        else:
            return self._derive_key_pbkdf2(salt, iterations)

    def encrypt_file(self):
        if not self.archive_mode or not hasattr(self, "_file_list") or len(self._file_list) <= 1:
            return self._encrypt_single_file()
        else:
            return self._encrypt_archive()

    def _encrypt_single_file(self):
        with open(self.in_path, "rb") as f:
            if f.read(len(MAGIC_NUMBER)) == MAGIC_NUMBER:
                raise ValueError("This file appears to be already encrypted with PyLI. Aborting to prevent corruption.")    
        effective_compression_level = self.compression_level
        if should_skip_compression(self.in_path):
            effective_compression_level = "none"        
        salt = os.urandom(SALT_SIZE)
        kdf_type = KDF_ID_ARGON2 if self.use_argon2 else KDF_ID_PBKDF2
        key = self._derive_key(salt, kdf_type=kdf_type)
        aesgcm = AESGCM(key)     
        original_ext = os.path.splitext(self.in_path)[1].lstrip(".").encode("utf-8")
        if len(original_ext) > MAX_EXT_LEN:
            raise ValueError(f"File extension exceeds maximum length of {MAX_EXT_LEN} bytes.")        
        ext_nonce = os.urandom(NONCE_SIZE)
        encrypted_ext = aesgcm.encrypt(ext_nonce, original_ext, None)            
        if self.new_name_type == "hash":
            hasher = hashlib.sha256()
            with open(self.in_path, "rb") as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk: break
                    hasher.update(chunk)
            out_filename = f"{hasher.hexdigest()}.{self.custom_ext}"
            self.out_path = os.path.join(os.path.dirname(self.out_path), out_filename)
        elif self.new_name_type == "base64":
            original_name = os.path.basename(self.in_path)
            base64_bytes = base64.urlsafe_b64encode(original_name.encode("utf-8"))
            base64_name = base64_bytes.decode("utf-8").rstrip("=")[:96]
            out_filename = f"{base64_name}.{self.custom_ext}"
            self.out_path = os.path.join(os.path.dirname(self.out_path), out_filename)
        else:
            self.out_path = f"{os.path.splitext(self.out_path)[0]}.{self.custom_ext}"                 
        if os.path.exists(self.out_path) and not os.path.samefile(self.in_path, self.out_path):
            raise IOError(f"Output file '{os.path.basename(self.out_path)}' already exists.")              
        total_size = os.path.getsize(self.in_path)
        processed_size = 0
        rs_codec = reedsolo.RSCodec(ECC_BYTES) if self.add_recovery_data else None        
        with open(self.in_path, "rb") as infile, open(self.out_path, "wb") as outfile:
            outfile.write(MAGIC_NUMBER)
            outfile.write(struct.pack("!B", FORMAT_VERSION))
            flags = FLAG_RECOVERY_DATA if self.add_recovery_data else 0
            outfile.write(struct.pack("!B", flags))
            outfile.write(struct.pack("!B", kdf_type))
            compression_id_pos = outfile.tell()
            outfile.write(struct.pack("!B", COMPRESSION_NONE))
            if self.add_recovery_data:
                outfile.write(struct.pack("!B", ECC_BYTES))
            if kdf_type == KDF_ID_ARGON2:
                outfile.write(struct.pack("!I", self.argon2_time_cost))
                outfile.write(struct.pack("!I", self.argon2_memory_cost))
                outfile.write(struct.pack("!I", self.argon2_parallelism))
            else:
                outfile.write(struct.pack("!I", self.kdf_iterations))
            outfile.write(salt)
            outfile.write(ext_nonce)
            outfile.write(struct.pack("!I", len(encrypted_ext)))
            outfile.write(encrypted_ext)            
            first_chunk = True
            final_compression_id = COMPRESSION_NONE
            if total_size > self.chunk_size * 4 and effective_compression_level != "none":
                try:
                    with mmap.mmap(infile.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                        chunk_futures = []
                        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                            offset = 0
                            while offset < total_size:
                                if self.is_canceled: raise Exception("Operation canceled by user.")
                                chunk_size = min(self.chunk_size, total_size - offset)
                                chunk_data = mmapped_file[offset:offset + chunk_size]
                                future = executor.submit(compress_chunk_threaded, bytes(chunk_data), effective_compression_level)
                                chunk_futures.append((future, offset, len(chunk_data)))
                                offset += chunk_size
                            for future, chunk_offset, chunk_len in chunk_futures:
                                if self.is_canceled: raise Exception("Operation canceled by user.")
                                compressed_chunk, compression_id = future.result()
                                if first_chunk:
                                    final_compression_id = compression_id
                                    current_pos = outfile.tell()
                                    outfile.seek(compression_id_pos)
                                    outfile.write(struct.pack("!B", final_compression_id))
                                    outfile.seek(current_pos)
                                    first_chunk = False                
                                if final_compression_id == COMPRESSION_NONE:
                                    mmapped_file.seek(chunk_offset)
                                    compressed_chunk = mmapped_file.read(chunk_len)
                                elif compression_id == COMPRESSION_NONE:
                                    mode = COMPRESSION_MODES[effective_compression_level]
                                    mmapped_file.seek(chunk_offset)
                                    original_chunk = mmapped_file.read(chunk_len)
                                    compressed_chunk = mode["func"](original_chunk)               
                                chunk_nonce = os.urandom(NONCE_SIZE)
                                encrypted_chunk = aesgcm.encrypt(chunk_nonce, compressed_chunk, None)              
                                outfile.write(chunk_nonce)
                                outfile.write(struct.pack("!I", len(encrypted_chunk)))
                                outfile.write(encrypted_chunk)                
                                if rs_codec:
                                    parity = rs_codec.encode(encrypted_chunk)[-ECC_BYTES:]
                                    outfile.write(parity)                
                                processed_size += chunk_len
                                if self.progress_callback: self.progress_callback(processed_size / total_size * 100)
                except (OSError, ValueError):
                    infile.seek(0)
                    while True:
                        if self.is_canceled: raise Exception("Operation canceled by user.")
                        chunk = infile.read(self.chunk_size)
                        if not chunk: break                
                        compressed_chunk, compression_id = compress_chunk(chunk, effective_compression_level)
                        if first_chunk:
                            final_compression_id = compression_id
                            current_pos = outfile.tell()
                            outfile.seek(compression_id_pos)
                            outfile.write(struct.pack("!B", final_compression_id))
                            outfile.seek(current_pos)
                            first_chunk = False                
                        if final_compression_id == COMPRESSION_NONE:
                            compressed_chunk = chunk
                        elif compression_id == COMPRESSION_NONE:
                            mode = COMPRESSION_MODES[effective_compression_level]
                            compressed_chunk = mode["func"](chunk)               
                        chunk_nonce = os.urandom(NONCE_SIZE)
                        encrypted_chunk = aesgcm.encrypt(chunk_nonce, compressed_chunk, None)              
                        outfile.write(chunk_nonce)
                        outfile.write(struct.pack("!I", len(encrypted_chunk)))
                        outfile.write(encrypted_chunk)                
                        if rs_codec:
                            parity = rs_codec.encode(encrypted_chunk)[-ECC_BYTES:]
                            outfile.write(parity)                
                        processed_size += len(chunk)
                        if self.progress_callback: self.progress_callback(processed_size / total_size * 100)
            else:
                while True:
                    if self.is_canceled: raise Exception("Operation canceled by user.")
                    chunk = infile.read(self.chunk_size)
                    if not chunk: break                
                    compressed_chunk, compression_id = compress_chunk(chunk, effective_compression_level)
                    if first_chunk:
                        final_compression_id = compression_id
                        current_pos = outfile.tell()
                        outfile.seek(compression_id_pos)
                        outfile.write(struct.pack("!B", final_compression_id))
                        outfile.seek(current_pos)
                        first_chunk = False                
                    if final_compression_id == COMPRESSION_NONE:
                        compressed_chunk = chunk
                    elif compression_id == COMPRESSION_NONE:
                        mode = COMPRESSION_MODES[effective_compression_level]
                        compressed_chunk = mode["func"](chunk)               
                    chunk_nonce = os.urandom(NONCE_SIZE)
                    encrypted_chunk = aesgcm.encrypt(chunk_nonce, compressed_chunk, None)              
                    outfile.write(chunk_nonce)
                    outfile.write(struct.pack("!I", len(encrypted_chunk)))
                    outfile.write(encrypted_chunk)                
                    if rs_codec:
                        parity = rs_codec.encode(encrypted_chunk)[-ECC_BYTES:]
                        outfile.write(parity)                
                    processed_size += len(chunk)
                    if self.progress_callback: self.progress_callback(processed_size / total_size * 100)        
        if self.progress_callback: self.progress_callback(100.0)

    def _encrypt_archive(self):
        archive_header, file_info, total_source_size = create_archive(self._file_list)
        if self.progress_callback:
            self.progress_callback(5.0)
        effective_compression_level = self.compression_level
        salt = os.urandom(SALT_SIZE)
        kdf_type = KDF_ID_ARGON2 if self.use_argon2 else KDF_ID_PBKDF2
        key = self._derive_key(salt, kdf_type=kdf_type)
        aesgcm = AESGCM(key)
        original_ext = "archive".encode("utf-8")
        ext_nonce = os.urandom(NONCE_SIZE)
        encrypted_ext = aesgcm.encrypt(ext_nonce, original_ext, None)
        if self.new_name_type == "hash":
            hasher = hashlib.sha256()
            hasher.update(archive_header)
            for file_path, _, _ in file_info:
                with open(file_path, "rb") as f:
                    while True:
                        chunk = f.read(self.chunk_size)
                        if not chunk: break
                        hasher.update(chunk)
            out_filename = f"{hasher.hexdigest()}.{self.custom_ext}"
            self.out_path = os.path.join(os.path.dirname(self.out_path), out_filename)
        elif self.new_name_type == "base64":
            original_name = f"archive_{len(self._file_list)}_files"
            base64_bytes = base64.urlsafe_b64encode(original_name.encode("utf-8"))
            base64_name = base64_bytes.decode("utf-8").rstrip("=")[:96]
            out_filename = f"{base64_name}.{self.custom_ext}"
            self.out_path = os.path.join(os.path.dirname(self.out_path), out_filename)
        else:
            base_name = os.path.splitext(os.path.basename(self._file_list[0]))[0]
            out_filename = f"{base_name}_archive.{self.custom_ext}"
            self.out_path = os.path.join(os.path.dirname(self.out_path), out_filename)
        if os.path.exists(self.out_path):
            raise IOError(f"Output file '{os.path.basename(self.out_path)}' already exists.")
        rs_codec = reedsolo.RSCodec(ECC_BYTES) if self.add_recovery_data else None
        with open(self.out_path, "wb") as outfile:
            outfile.write(MAGIC_NUMBER)
            outfile.write(struct.pack("!B", FORMAT_VERSION))
            flags = FLAG_RECOVERY_DATA if self.add_recovery_data else 0
            flags |= FLAG_ARCHIVE_MODE
            outfile.write(struct.pack("!B", flags))
            outfile.write(struct.pack("!B", kdf_type))
            compression_id_pos = outfile.tell()
            outfile.write(struct.pack("!B", COMPRESSION_NONE))
            if self.add_recovery_data:
                outfile.write(struct.pack("!B", ECC_BYTES))
            if kdf_type == KDF_ID_ARGON2:
                outfile.write(struct.pack("!I", self.argon2_time_cost))
                outfile.write(struct.pack("!I", self.argon2_memory_cost))
                outfile.write(struct.pack("!I", self.argon2_parallelism))
            else:
                outfile.write(struct.pack("!I", self.kdf_iterations))
            outfile.write(salt)
            outfile.write(ext_nonce)
            outfile.write(struct.pack("!I", len(encrypted_ext)))
            outfile.write(encrypted_ext)
            first_chunk = True
            final_compression_id = COMPRESSION_NONE
            processed_size = 0
            def data_stream():
                yield archive_header
                for file_path, _, _ in file_info:
                    if self.is_canceled:
                        raise Exception("Operation canceled by user.")
                    with open(file_path, "rb") as f:
                        while True:
                            chunk = f.read(self.chunk_size)
                            if not chunk:
                                break
                            yield chunk
            chunk_batch = []
            batch_size = self.max_workers * 2
            for chunk_data in data_stream():
                if self.is_canceled:
                    raise Exception("Operation canceled by user.")
                chunk_batch.append(chunk_data)
                if len(chunk_batch) >= batch_size or (effective_compression_level == "none"):
                    if effective_compression_level != "none" and len(chunk_batch) > 1:
                        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                            futures = [executor.submit(compress_chunk_threaded, chunk, effective_compression_level) for chunk in chunk_batch]
                            for future in futures:
                                if self.is_canceled:
                                    raise Exception("Operation canceled by user.")
                                compressed_chunk, compression_id = future.result()
                                if first_chunk:
                                    final_compression_id = compression_id
                                    current_pos = outfile.tell()
                                    outfile.seek(compression_id_pos)
                                    outfile.write(struct.pack("!B", final_compression_id))
                                    outfile.seek(current_pos)
                                    first_chunk = False
                                if final_compression_id == COMPRESSION_NONE and compression_id != COMPRESSION_NONE:
                                    compressed_chunk = decompress_chunk(compressed_chunk, compression_id)
                                elif final_compression_id != COMPRESSION_NONE and compression_id == COMPRESSION_NONE:
                                    mode = COMPRESSION_MODES[effective_compression_level]
                                    compressed_chunk = mode["func"](compressed_chunk)
                                chunk_nonce = os.urandom(NONCE_SIZE)
                                encrypted_chunk = aesgcm.encrypt(chunk_nonce, compressed_chunk, None)
                                outfile.write(chunk_nonce)
                                outfile.write(struct.pack("!I", len(encrypted_chunk)))
                                outfile.write(encrypted_chunk)
                                if rs_codec:
                                    parity = rs_codec.encode(encrypted_chunk)[-ECC_BYTES:]
                                    outfile.write(parity)
                                processed_size += len(chunk_data)
                                if self.progress_callback:
                                    progress = 5.0 + (processed_size / (len(archive_header) + total_source_size)) * 95.0
                                    self.progress_callback(min(100.0, progress))
                    else:
                        for chunk in chunk_batch:
                            if self.is_canceled:
                                raise Exception("Operation canceled by user.")
                            compressed_chunk, compression_id = compress_chunk(chunk, effective_compression_level)
                            if first_chunk:
                                final_compression_id = compression_id
                                current_pos = outfile.tell()
                                outfile.seek(compression_id_pos)
                                outfile.write(struct.pack("!B", final_compression_id))
                                outfile.seek(current_pos)
                                first_chunk = False
                            if final_compression_id == COMPRESSION_NONE:
                                compressed_chunk = chunk
                            elif compression_id == COMPRESSION_NONE:
                                mode = COMPRESSION_MODES[effective_compression_level]
                                compressed_chunk = mode["func"](chunk)
                            chunk_nonce = os.urandom(NONCE_SIZE)
                            encrypted_chunk = aesgcm.encrypt(chunk_nonce, compressed_chunk, None)
                            outfile.write(chunk_nonce)
                            outfile.write(struct.pack("!I", len(encrypted_chunk)))
                            outfile.write(encrypted_chunk)
                            if rs_codec:
                                parity = rs_codec.encode(encrypted_chunk)[-ECC_BYTES:]
                                outfile.write(parity)
                            processed_size += len(chunk)
                            if self.progress_callback:
                                progress = 5.0 + (processed_size / (len(archive_header) + total_source_size)) * 95.0
                                self.progress_callback(min(100.0, progress))
                    chunk_batch.clear()
            if chunk_batch:
                for chunk in chunk_batch:
                    if self.is_canceled:
                        raise Exception("Operation canceled by user.")
                    compressed_chunk, compression_id = compress_chunk(chunk, effective_compression_level)
                    if first_chunk:
                        final_compression_id = compression_id
                        current_pos = outfile.tell()
                        outfile.seek(compression_id_pos)
                        outfile.write(struct.pack("!B", final_compression_id))
                        outfile.seek(current_pos)
                        first_chunk = False
                    if final_compression_id == COMPRESSION_NONE:
                        compressed_chunk = chunk
                    elif compression_id == COMPRESSION_NONE:
                        mode = COMPRESSION_MODES[effective_compression_level]
                        compressed_chunk = mode["func"](chunk)
                    chunk_nonce = os.urandom(NONCE_SIZE)
                    encrypted_chunk = aesgcm.encrypt(chunk_nonce, compressed_chunk, None)
                    outfile.write(chunk_nonce)
                    outfile.write(struct.pack("!I", len(encrypted_chunk)))
                    outfile.write(encrypted_chunk)
                    if rs_codec:
                        parity = rs_codec.encode(encrypted_chunk)[-ECC_BYTES:]
                        outfile.write(parity)
                    processed_size += len(chunk)
                    if self.progress_callback:
                        progress = 5.0 + (processed_size / (len(archive_header) + total_source_size)) * 95.0
                        self.progress_callback(min(100.0, progress))
        if self.progress_callback:
            self.progress_callback(100.0)

    def decrypt_file(self):
        with open(self.in_path, "rb") as infile:
            if infile.read(len(MAGIC_NUMBER)) != MAGIC_NUMBER: 
                raise ValueError("Not a valid PyLI encrypted file.")            
            version = struct.unpack("!B", infile.read(1))[0]
            if version < 3: 
                raise ValueError(f"Unsupported format version: {version}. This version requires format 3 or higher.")         
            flags = struct.unpack("!B", infile.read(1))[0]
            recovery_enabled = (flags & FLAG_RECOVERY_DATA) != 0
            is_archive = (flags & FLAG_ARCHIVE_MODE) != 0
            kdf_type = KDF_ID_PBKDF2
            if version >= 6:
                kdf_type = struct.unpack("!B", infile.read(1))[0]
            compression_id = COMPRESSION_NONE
            if version >= 4:
                 compression_id = struct.unpack("!B", infile.read(1))[0]
            ecc_bytes = 0
            if recovery_enabled:
                ecc_bytes = struct.unpack("!B", infile.read(1))[0]
            if kdf_type == KDF_ID_ARGON2:
                argon2_time_cost = struct.unpack("!I", infile.read(4))[0]
                argon2_memory_cost = struct.unpack("!I", infile.read(4))[0]
                argon2_parallelism = struct.unpack("!I", infile.read(4))[0]
                kdf_iterations = None
            else:
                kdf_iterations = struct.unpack("!I", infile.read(4))[0]
                argon2_time_cost = argon2_memory_cost = argon2_parallelism = None   
            salt = infile.read(SALT_SIZE)
            self.argon2_time_cost = argon2_time_cost
            self.argon2_memory_cost = argon2_memory_cost
            self.argon2_parallelism = argon2_parallelism
            key = self._derive_key(salt, iterations=kdf_iterations, kdf_type=kdf_type)
            aesgcm = AESGCM(key)
            ext_nonce = infile.read(NONCE_SIZE)
            ext_len = struct.unpack("!I", infile.read(4))[0]
            encrypted_ext = infile.read(ext_len)
            try:
                original_ext = aesgcm.decrypt(ext_nonce, encrypted_ext, None).decode("utf-8")
            except InvalidTag:
                raise ValueError("Incorrect password or corrupt file extension data.")
            decrypted_data = bytearray()
            total_size = os.path.getsize(self.in_path)
            header_size = infile.tell()
            rs_codec = reedsolo.RSCodec(ecc_bytes) if recovery_enabled else None
            chunk_data = []
            while True:
                if self.is_canceled: raise Exception("Operation canceled by user.")     
                chunk_nonce = infile.read(NONCE_SIZE)
                if not chunk_nonce: break
                len_bytes = infile.read(4)
                if not len_bytes: break
                encrypted_chunk_len = struct.unpack("!I", len_bytes)[0]
                encrypted_chunk = infile.read(encrypted_chunk_len)
                parity_data = b""
                if recovery_enabled:
                    parity_data = infile.read(ecc_bytes)
                if not encrypted_chunk: break
                chunk_data.append((chunk_nonce, encrypted_chunk, parity_data))
            if len(chunk_data) > 4 and compression_id != COMPRESSION_NONE:
                def decrypt_chunk_worker(chunk_info):
                    chunk_nonce, encrypted_chunk, parity_data = chunk_info
                    try:
                        if rs_codec:
                            try:
                                combined_data = bytearray(encrypted_chunk + parity_data)
                                decrypted_chunk_with_parity, _, _ = rs_codec.decode(combined_data)
                                encrypted_chunk = bytes(decrypted_chunk_with_parity)
                            except reedsolo.ReedSolomonError:
                                raise ValueError("File chunk is corrupt and could not be recovered.")                                            
                        decrypted_chunk = aesgcm.decrypt(chunk_nonce, encrypted_chunk, None)
                        decompressed_chunk = decompress_chunk(decrypted_chunk, compression_id)
                        return decompressed_chunk                    
                    except InvalidTag:
                        raise ValueError("File appears to be corrupted or password is incorrect (chunk authentication failed).")
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = {executor.submit(decrypt_chunk_worker, chunk_info): i for i, chunk_info in enumerate(chunk_data)}
                    results = [None] * len(chunk_data)
                    for future in as_completed(futures):
                        chunk_index = futures[future]
                        try:
                            results[chunk_index] = future.result()
                        except Exception as e:
                            raise e
                        processed_chunks = chunk_index + 1
                        if total_size > header_size:
                            progress = min(100.0, (processed_chunks / len(chunk_data)) * 70)
                            if self.progress_callback:
                                self.progress_callback(progress)
                for result in results:
                    decrypted_data.extend(result)
            else:
                for i, (chunk_nonce, encrypted_chunk, parity_data) in enumerate(chunk_data):
                    if self.is_canceled: raise Exception("Operation canceled by user.")
                    try:
                        if rs_codec:
                            try:
                                combined_data = bytearray(encrypted_chunk + parity_data)
                                decrypted_chunk_with_parity, _, _ = rs_codec.decode(combined_data)
                                encrypted_chunk = bytes(decrypted_chunk_with_parity)
                            except reedsolo.ReedSolomonError:
                                raise ValueError("File chunk is corrupt and could not be recovered.")                                            
                        decrypted_chunk = aesgcm.decrypt(chunk_nonce, encrypted_chunk, None)
                        decompressed_chunk = decompress_chunk(decrypted_chunk, compression_id)
                        decrypted_data.extend(decompressed_chunk)                    
                    except InvalidTag:
                        raise ValueError("File appears to be corrupted or password is incorrect (chunk authentication failed).")
                    if total_size > header_size:
                        progress = min(100.0, ((i + 1) / len(chunk_data)) * 70)
                        if self.progress_callback:
                            self.progress_callback(progress)
        if is_archive and original_ext == "archive":
            out_dir = self.output_dir or os.path.dirname(self.in_path)
            base_filename = os.path.splitext(os.path.basename(self.in_path))[0]
            extract_dir = os.path.join(out_dir, f"{base_filename}_extracted")
            if os.path.exists(extract_dir):
                counter = 1
                while os.path.exists(f"{extract_dir}_{counter}"):
                    counter += 1
                extract_dir = f"{extract_dir}_{counter}"            
            extract_archive(bytes(decrypted_data), extract_dir,
                          lambda p: self.progress_callback(70 + p * 0.3) if self.progress_callback else None)
        else:
            out_dir = self.output_dir or os.path.dirname(self.in_path)
            base_filename = os.path.splitext(os.path.basename(self.in_path))[0]
            out_path = os.path.join(out_dir, f"{base_filename}.{original_ext}")          
            if os.path.exists(out_path) and not os.path.samefile(self.in_path, out_path):
                raise IOError(f"Output file '{os.path.basename(out_path)}' already exists.")            
            with open(out_path, "wb") as outfile:
                outfile.write(decrypted_data)        
        if self.progress_callback: self.progress_callback(100.0)

class BatchProcessorThread(QThread):
    batch_progress_updated = pyqtSignal(int, int)
    status_message = pyqtSignal(str)
    progress_updated = pyqtSignal(float)
    finished = pyqtSignal(list)
    
    def __init__(self, operation, file_paths, password, custom_ext=None, output_dir=None, new_name_type=None, chunk_size=CHUNK_SIZE, kdf_iterations=1000000, secure_clear=False, add_recovery_data=False, compression_level="none", archive_mode=False, use_argon2=False, argon2_time_cost=ARGON2_TIME_COST, argon2_memory_cost=ARGON2_MEMORY_COST, argon2_parallelism=ARGON2_PARALLELISM, parent=None):
        super().__init__(parent)
        self.operation = operation
        self.file_paths = file_paths
        self.password = password
        self.custom_ext = custom_ext
        self.output_dir = output_dir
        self.new_name_type = new_name_type
        self.chunk_size = chunk_size
        self.kdf_iterations = kdf_iterations
        self.secure_clear = secure_clear
        self.add_recovery_data = add_recovery_data
        self.compression_level = compression_level
        self.archive_mode = archive_mode
        self.use_argon2 = use_argon2
        self.argon2_time_cost = argon2_time_cost
        self.argon2_memory_cost = argon2_memory_cost
        self.argon2_parallelism = argon2_parallelism
        self.is_canceled = False
        self.errors = []
        self.worker = None

    def run(self):
        if self.operation == "encrypt" and self.archive_mode and len(self.file_paths) > 1:
            self.batch_progress_updated.emit(1, 1)
            self.status_message.emit("Creating archive...")         
            try:
                out_path = self.file_paths[0]
                if self.output_dir:
                    out_path = os.path.join(self.output_dir, os.path.basename(self.file_paths[0]))               
                self.worker = CryptoWorker(
                    operation=self.operation, in_path=self.file_paths[0], out_path=out_path, password=self.password,
                    custom_ext=self.custom_ext, new_name_type=self.new_name_type, output_dir=self.output_dir,
                    chunk_size=self.chunk_size, kdf_iterations=self.kdf_iterations,
                    secure_clear=self.secure_clear, add_recovery_data=self.add_recovery_data,
                    compression_level=self.compression_level, archive_mode=self.archive_mode,
                    use_argon2=self.use_argon2, argon2_time_cost=self.argon2_time_cost,
                    argon2_memory_cost=self.argon2_memory_cost, argon2_parallelism=self.argon2_parallelism,
                    progress_callback=lambda p: self.progress_updated.emit(p)
                )                
                self.worker._file_list = self.file_paths
                self.worker.encrypt_file()              
            except Exception as e:
                self.errors.append(f"Archive creation failed: {str(e)}")
        else:
            total_files = len(self.file_paths)
            for i, file_path in enumerate(self.file_paths):
                if self.is_canceled: break
                self.batch_progress_updated.emit(i + 1, total_files)
                self.status_message.emit(f"Processing: {os.path.basename(file_path)}")                
                try:
                    out_path = file_path
                    if self.output_dir:
                        out_path = os.path.join(self.output_dir, os.path.basename(file_path))                    
                    self.worker = CryptoWorker(
                        operation=self.operation, in_path=file_path, out_path=out_path, password=self.password,
                        custom_ext=self.custom_ext, new_name_type=self.new_name_type, output_dir=self.output_dir,
                        chunk_size=self.chunk_size, kdf_iterations=self.kdf_iterations,
                        secure_clear=self.secure_clear, add_recovery_data=self.add_recovery_data,
                        compression_level=self.compression_level, archive_mode=self.archive_mode,
                        use_argon2=self.use_argon2, argon2_time_cost=self.argon2_time_cost,
                        argon2_memory_cost=self.argon2_memory_cost, argon2_parallelism=self.argon2_parallelism,
                        progress_callback=lambda p: self.progress_updated.emit(p))
                    if self.operation == "encrypt": 
                        self.worker.encrypt_file()
                    elif self.operation == "decrypt": 
                        self.worker.decrypt_file()                     
                except Exception as e:
                    self.errors.append(f"File '{os.path.basename(file_path)}' failed: {str(e)}")        
        self.password = None
        self.finished.emit(self.errors)

    def cancel(self):
        self.is_canceled = True
        if self.password:
            if self.secure_clear:
                pwd_bytes = self.password.encode("utf-8")
                pwd_buffer = ctypes.create_string_buffer(len(pwd_bytes))
                pwd_buffer.raw = pwd_bytes
                clear_buffer(pwd_buffer)
            self.password = None
        if hasattr(self, 'out_path') and self.out_path and os.path.exists(self.out_path):
            try:
                import time
                time.sleep(0.1)
                os.remove(self.out_path)
            except Exception:
                pass

## end