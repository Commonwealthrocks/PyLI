## core.py
## last updated: 26/8/2025 <d/m/y>
## p-y-l-i
from importzz import *

CHUNK_SIZE = 3 * 1024 * 1024
FORMAT_VERSION = 2
ALGORITHM_ID = 1
KDF_ID = 1
KDF_ITERATIONS = 1000000
SALT_SIZE = 16
NONCE_SIZE = 12
MAGIC_NUMBER = b"PYLI\x00"
MAX_EXT_LEN = 256
TAG_SIZE = 16

class CryptoWorker(QObject):
    progress_updated = pyqtSignal(float)
    finished = pyqtSignal(bool, str)

    def __init__(self, operation, in_path, out_path, password, custom_ext=None, new_name_type=None, output_dir=None, chunk_size=CHUNK_SIZE, kdf_iterations=KDF_ITERATIONS, parent=None):
        super().__init__(parent)
        self.operation = operation
        self.in_path = in_path
        self.out_path = out_path
        self.password = password
        self.custom_ext = custom_ext
        self.new_name_type = new_name_type
        self.output_dir = output_dir
        self.chunk_size = chunk_size
        self.kdf_iterations = kdf_iterations
        self.is_canceled = False

    @Slot()
    def run(self):
        try:
            if self.operation == 'encrypt':
                self.encrypt_file()
            elif self.operation == 'decrypt':
                self.decrypt_file()
            self.finished.emit(True, "Donezo :>")
        except Exception as e:
            self.finished.emit(False, str(e))
        finally:
            self.password = None

    def encrypt_file(self):
        salt = os.urandom(SALT_SIZE)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.kdf_iterations,
            backend=default_backend()
        )
        key = kdf.derive(self.password.encode())
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
                    if not chunk:
                        break
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
            raise IOError(f"Output file '{os.path.basename(self.out_path)}' already exists. Aborting to prevent overwrite.")      
        total_size = os.path.getsize(self.in_path)
        processed_size = 0     
        with open(self.in_path, 'rb') as infile, open(self.out_path, 'wb') as outfile:
            outfile.write(MAGIC_NUMBER)
            outfile.write(struct.pack('!B', FORMAT_VERSION))
            outfile.write(struct.pack('!B', ALGORITHM_ID))
            outfile.write(struct.pack('!B', KDF_ID))
            outfile.write(struct.pack('!I', self.kdf_iterations))
            outfile.write(salt)
            outfile.write(ext_nonce)
            outfile.write(struct.pack('!I', len(encrypted_ext)))
            outfile.write(encrypted_ext)
            while True:
                if self.is_canceled:
                    try:
                        os.remove(self.out_path)
                    except:
                        pass
                    raise Exception("Operation cancelled by user.")                  
                chunk = infile.read(self.chunk_size)
                if not chunk:
                    break
                chunk_nonce = os.urandom(NONCE_SIZE)
                encrypted_chunk = aesgcm.encrypt(chunk_nonce, chunk, None)
                outfile.write(chunk_nonce)
                outfile.write(encrypted_chunk)                
                processed_size += len(chunk)
                self.progress_updated.emit(processed_size / total_size * 100)                
        self.progress_updated.emit(100.0)

    def decrypt_file(self):
        in_path = self.in_path        
        with open(in_path, 'rb') as infile:
            if infile.read(len(MAGIC_NUMBER)) != MAGIC_NUMBER:
                raise ValueError("Not a valid PyLI encrypted file.")                
            version = struct.unpack('!B', infile.read(1))[0]
            if version != FORMAT_VERSION:
                raise ValueError(f"Unsupported format version: {version}. Expected {FORMAT_VERSION}.")                
            alg_id = struct.unpack('!B', infile.read(1))[0]
            kdf_id = struct.unpack('!B', infile.read(1))[0]
            kdf_iterations = struct.unpack('!I', infile.read(4))[0]
            salt = infile.read(SALT_SIZE)
            ext_nonce = infile.read(NONCE_SIZE)            
            ext_len_bytes = infile.read(4)
            if len(ext_len_bytes) < 4:
                raise ValueError("Corrupt file: not my issue.")
            ext_len = struct.unpack('!I', ext_len_bytes)[0]
            encrypted_ext = infile.read(ext_len)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=kdf_iterations,
                backend=default_backend()
            )
            key = kdf.derive(self.password.encode())
            aesgcm = AESGCM(key)          
            try:
                original_ext = aesgcm.decrypt(ext_nonce, encrypted_ext, None).decode('utf-8')
            except InvalidTag:
                raise ValueError("Incorrect password. Cannot decrypt file dummy.")
            if self.output_dir:
                out_dir = self.output_dir
            else:
                out_dir = os.path.dirname(in_path)                
            base_filename = os.path.splitext(os.path.basename(in_path))[0]
            out_path = os.path.join(out_dir, f"{base_filename}.{original_ext}")            
            if os.path.exists(out_path) and not os.path.samefile(in_path, out_path):
                raise IOError(f"Output file '{os.path.basename(out_path)}' already exists. Aborting to prevent overwrite.")            
            total_size = os.path.getsize(in_path)
            header_size = infile.tell()
            processed_size = header_size            
            with open(out_path, 'wb') as outfile:
                while True:
                    if self.is_canceled:
                        try:
                            os.remove(out_path)
                        except:
                            pass
                        raise Exception("Operation cancelled by user.")
                    chunk_nonce = infile.read(NONCE_SIZE)
                    if not chunk_nonce or len(chunk_nonce) < NONCE_SIZE:
                        break
                    encrypted_chunk = b""
                    chunk_size_guess = self.chunk_size + TAG_SIZE
                    temp_chunk = infile.read(chunk_size_guess)                  
                    if not temp_chunk:
                        break
                    remaining_file = total_size - infile.tell()
                    if remaining_file <= 0:
                        encrypted_chunk = temp_chunk
                    else:
                        actual_chunk_size = len(temp_chunk)
                        encrypted_chunk = temp_chunk                       
                    if not encrypted_chunk:
                        break                        
                    try:
                        decrypted_chunk = aesgcm.decrypt(chunk_nonce, encrypted_chunk, None)
                        outfile.write(decrypted_chunk)
                    except InvalidTag:
                        try:
                            if len(encrypted_chunk) > TAG_SIZE:
                                smaller_chunk = encrypted_chunk[:len(encrypted_chunk)//2]
                                infile.seek(infile.tell() - len(encrypted_chunk) + len(smaller_chunk))
                                decrypted_chunk = aesgcm.decrypt(chunk_nonce, smaller_chunk, None)
                                outfile.write(decrypted_chunk)
                        except:
                            raise ValueError("File appears to be corrupted or password is incorrect.")                    
                    processed_size = infile.tell()
                    if total_size > header_size:
                        progress = min(100.0, (processed_size - header_size) / (total_size - header_size) * 100)
                        self.progress_updated.emit(progress)
        self.progress_updated.emit(100.0)

    @Slot()
    def cancel(self):
        self.is_canceled = True

class BatchProcessorThread(QThread):
    batch_progress_updated = pyqtSignal(int, int)
    status_message = pyqtSignal(str)
    progress_updated = pyqtSignal(float)
    finished = pyqtSignal(list)
    
    def __init__(self, operation, file_paths, password, custom_ext=None, output_dir=None, new_name_type=None, chunk_size=CHUNK_SIZE, kdf_iterations=KDF_ITERATIONS, parent=None):
        super().__init__(parent)
        self.operation = operation
        self.file_paths = file_paths
        self.password = password
        self.custom_ext = custom_ext
        self.output_dir = output_dir
        self.new_name_type = new_name_type
        self.chunk_size = chunk_size
        self.kdf_iterations = kdf_iterations
        self.is_canceled = False
        self.errors = []
        self.completed_count = 0
        
    def run(self):
        total_files = len(self.file_paths)
        for i, file_path in enumerate(self.file_paths):
            if self.is_canceled:
                break
            self.batch_progress_updated.emit(i + 1, total_files)
            self.status_message.emit(f"Processing: {os.path.basename(file_path)}")
            try:
                out_path = file_path
                if self.output_dir:
                    out_path = os.path.join(self.output_dir, os.path.basename(file_path))
                worker = CryptoWorker(
                    operation=self.operation,
                    in_path=file_path,
                    out_path=out_path,
                    password=self.password,
                    custom_ext=self.custom_ext,
                    new_name_type=self.new_name_type,
                    output_dir=self.output_dir,
                    chunk_size=self.chunk_size,
                    kdf_iterations=self.kdf_iterations
                )
                worker.progress_updated.connect(self.progress_updated)
                success = False
                error_msg = ""
                try:
                    if self.operation == 'encrypt':
                        worker.encrypt_file()
                    elif self.operation == 'decrypt':
                        worker.decrypt_file()
                    success = True
                    error_msg = "Donezo :>"
                except Exception as e:
                    success = False
                    error_msg = str(e)
                if not success:
                    self.errors.append(f"File '{os.path.basename(file_path)}' failed: {error_msg}")
                self.completed_count += 1
            except Exception as e:
                self.errors.append(f"File '{os.path.basename(file_path)}' failed: {str(e)}")
                self.completed_count += 1
        self.finished.emit(self.errors)

    @Slot()
    def cancel(self):
        self.is_canceled = True

## end
