## core.py
## last updated: 28/8/2025 <d/m/y>
## p-y-l-i
from importzz import *
from sm import clear_buffer

CHUNK_SIZE = 3 * 1024 * 1024
FORMAT_VERSION = 3
ALGORITHM_ID = 1
KDF_ID = 1
SALT_SIZE = 16
NONCE_SIZE = 12
MAGIC_NUMBER = b"PYLI\x00"
MAX_EXT_LEN = 256
TAG_SIZE = 16
ECC_BYTES = 32
FLAG_RECOVERY_DATA = 0x01

class CryptoWorker:
    def __init__(self, operation, in_path, out_path, password, custom_ext=None, new_name_type=None, output_dir=None, chunk_size=CHUNK_SIZE, kdf_iterations=1000000, secure_clear=False, add_recovery_data=False, progress_callback=None, parent=None):
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
        self.progress_callback = progress_callback
        self.is_canceled = False

    def _derive_key(self, salt):
        pwd_bytes = self.password.encode('utf-8')
        pwd_buffer = ctypes.create_string_buffer(len(pwd_bytes))
        pwd_buffer.raw = pwd_bytes
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.kdf_iterations,
            backend=default_backend()
        )
        key = kdf.derive(pwd_bytes)
        if self.secure_clear:
            clear_buffer(pwd_buffer) 
        return key

    def encrypt_file(self):
        with open(self.in_path, 'rb') as f:
            if f.read(len(MAGIC_NUMBER)) == MAGIC_NUMBER:
                raise ValueError("This file appears to be already encrypted with PyLI. Aborting to prevent corruption.")
        salt = os.urandom(SALT_SIZE)
        key = self._derive_key(salt)
        aesgcm = AESGCM(key)     
        original_ext = os.path.splitext(self.in_path)[1].lstrip('.').encode('utf-8')
        if len(original_ext) > MAX_EXT_LEN:
            raise ValueError(f"File extension exceeds maximum length of {MAX_EXT_LEN} bytes.")
        ext_nonce = os.urandom(NONCE_SIZE)
        encrypted_ext = aesgcm.encrypt(ext_nonce, original_ext, None)      
        if self.new_name_type == "hash":
            hasher = hashlib.sha256()
            with open(self.in_path, 'rb') as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk: break
                    hasher.update(chunk)
            out_filename = f"{hasher.hexdigest()}.{self.custom_ext}"
            self.out_path = os.path.join(os.path.dirname(self.out_path), out_filename)
        elif self.new_name_type == "base64":
            original_name = os.path.basename(self.in_path)
            base64_name = base64.b64encode(original_name.encode('utf-8')).decode('utf-8')
            out_filename = f"{base64_name}.{self.custom_ext}"
            self.out_path = os.path.join(os.path.dirname(self.out_path), out_filename)
        else:
            self.out_path = f"{os.path.splitext(self.out_path)[0]}.{self.custom_ext}"         
        if os.path.exists(self.out_path) and not os.path.samefile(self.in_path, self.out_path):
            raise IOError(f"Output file '{os.path.basename(self.out_path)}' already exists.")      
        total_size = os.path.getsize(self.in_path)
        processed_size = 0
        rs_codec = reedsolo.RSCodec(ECC_BYTES) if self.add_recovery_data else None
        with open(self.in_path, 'rb') as infile, open(self.out_path, 'wb') as outfile:
            outfile.write(MAGIC_NUMBER)
            outfile.write(struct.pack('!B', FORMAT_VERSION))
            flags = FLAG_RECOVERY_DATA if self.add_recovery_data else 0
            outfile.write(struct.pack('!B', flags))
            if self.add_recovery_data:
                outfile.write(struct.pack('!B', ECC_BYTES))
            outfile.write(struct.pack('!I', self.kdf_iterations))
            outfile.write(salt)
            outfile.write(ext_nonce)
            outfile.write(struct.pack('!I', len(encrypted_ext)))
            outfile.write(encrypted_ext)
            while True:
                if self.is_canceled: raise Exception("Operation canceled by user.")
                chunk = infile.read(self.chunk_size)
                if not chunk: break
                chunk_nonce = os.urandom(NONCE_SIZE)
                encrypted_chunk = aesgcm.encrypt(chunk_nonce, chunk, None)
                outfile.write(chunk_nonce)
                outfile.write(encrypted_chunk)
                if rs_codec:
                    parity = rs_codec.encode(encrypted_chunk)[-ECC_BYTES:]
                    outfile.write(parity) 
                processed_size += len(chunk)
                if self.progress_callback: self.progress_callback(processed_size / total_size * 100)
        if self.progress_callback: self.progress_callback(100.0)

    def decrypt_file(self):
        with open(self.in_path, 'rb') as infile:
            if infile.read(len(MAGIC_NUMBER)) != MAGIC_NUMBER: raise ValueError("Not a valid PyLI encrypted file.")
            version = struct.unpack('!B', infile.read(1))[0]
            if version < 3: raise ValueError(f"Unsupported format version: {version}. This version requires format 3 or higher.")
            flags = struct.unpack('!B', infile.read(1))[0]
            recovery_enabled = (flags & FLAG_RECOVERY_DATA) != 0
            ecc_bytes = 0
            if recovery_enabled:
                ecc_bytes = struct.unpack('!B', infile.read(1))[0]
            kdf_iterations = struct.unpack('!I', infile.read(4))[0]
            salt = infile.read(SALT_SIZE)
            key = self._derive_key(salt)
            aesgcm = AESGCM(key)
            ext_nonce = infile.read(NONCE_SIZE)
            ext_len = struct.unpack('!I', infile.read(4))[0]
            encrypted_ext = infile.read(ext_len)
            try:
                original_ext = aesgcm.decrypt(ext_nonce, encrypted_ext, None).decode('utf-8')
            except InvalidTag:
                raise ValueError("Incorrect password or corrupt file extension data.")
            out_dir = self.output_dir or os.path.dirname(self.in_path)
            base_filename = os.path.splitext(os.path.basename(self.in_path))[0]
            out_path = os.path.join(out_dir, f"{base_filename}.{original_ext}")
            if os.path.exists(out_path) and not os.path.samefile(self.in_path, out_path):
                raise IOError(f"Output file '{os.path.basename(out_path)}' already exists.")
            total_size = os.path.getsize(self.in_path)
            header_size = infile.tell()
            rs_codec = reedsolo.RSCodec(ecc_bytes) if recovery_enabled else None
            with open(out_path, 'wb') as outfile:
                while True:
                    if self.is_canceled: raise Exception("Operation canceled by user.")     
                    chunk_nonce = infile.read(NONCE_SIZE)
                    if not chunk_nonce: break    
                    read_size = self.chunk_size + TAG_SIZE
                    encrypted_chunk = infile.read(read_size)
                    parity_data = b''
                    if recovery_enabled:
                        parity_data = infile.read(ecc_bytes)
                    if not encrypted_chunk: break 
                    try:
                        if rs_codec:
                            try:
                                combined_data = bytearray(encrypted_chunk + parity_data)
                                decrypted_chunk_with_parity, _, _ = rs_codec.decode(combined_data)
                                encrypted_chunk = bytes(decrypted_chunk_with_parity)
                            except reedsolo.ReedSolomonError:
                                raise ValueError("File chunk is corrupt and could not be recovered.")                        
                        decrypted_chunk = aesgcm.decrypt(chunk_nonce, encrypted_chunk, None)
                        outfile.write(decrypted_chunk)
                    except InvalidTag:
                        raise ValueError("File appears to be corrupted or password is incorrect (chunk authentication failed).")                        
                    processed_size = infile.tell()
                    if total_size > header_size:
                        progress = min(100.0, (processed_size - header_size) / (total_size - header_size) * 100)
                        if self.progress_callback: self.progress_callback(progress)        
        if self.progress_callback: self.progress_callback(100.0)

    def cancel(self):
        self.is_canceled = True

class BatchProcessorThread(QThread):
    batch_progress_updated = pyqtSignal(int, int)
    status_message = pyqtSignal(str)
    progress_updated = pyqtSignal(float)
    finished = pyqtSignal(list)
    
    def __init__(self, operation, file_paths, password, custom_ext=None, output_dir=None, new_name_type=None, chunk_size=CHUNK_SIZE, kdf_iterations=1000000, secure_clear=False, add_recovery_data=False, parent=None):
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
        self.is_canceled = False
        self.errors = []
        self.worker = None

    def run(self):
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
                    progress_callback=lambda p: self.progress_updated.emit(p)
                )                
                if self.operation == 'encrypt': self.worker.encrypt_file()
                elif self.operation == 'decrypt': self.worker.decrypt_file()
            except Exception as e:
                self.errors.append(f"File '{os.path.basename(file_path)}' failed: {str(e)}")
        self.password = None
        self.finished.emit(self.errors)

    def cancel(self):
        self.is_canceled = True
        if self.worker:
            self.worker.cancel()

## end
