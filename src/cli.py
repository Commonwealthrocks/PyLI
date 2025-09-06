## cli.py
## last updated: 05/09/2025 <d/m/y>
## p-y-l-i
from importzz import *
from core import CryptoWorker, MAGIC_NUMBER
from sm import isca

def print_progress(percentage, width=50):
    filled_len = int(round(width * percentage / 100))
    bar = "+" * filled_len + "-" * (width - filled_len)
    sys.stdout.write(f"\rProgress: |{bar}| {percentage:.2f}%")
    sys.stdout.flush()

def main():
    parser = argparse.ArgumentParser(description="PyLI CLI")
    parser.add_argument("operation", choices=["encrypt", "decrypt"], help="The operation to perform.")
    parser.add_argument("path", nargs="+", help="One or more input file(s) or folder(s).")
    parser.add_argument("-o", "--output", help="Output directory. Defaults to the input file's directory.")
    parser.add_argument("-p", "--password", help="Password for the operation. If not provided, will be prompted for securely.")
    parser.add_argument("--ext", default="dat", help="Custom extension for encrypted files. Default: 'dat'.")
    parser.add_argument("--name-type", choices=["keep", "hash", "base64"], default="keep", help="Filename transformation for encrypted files. Default: 'keep'.")
    parser.add_argument("--chunk-size", type=int, default=3, help="Chunk size in MB. Default: 3 MB.")
    parser.add_argument("--kdf-iter", type=int, default=1000000, help="Number of KDF iterations. Default: 1,000,000.")
    parser.add_argument("--secure-clear", action="store_true", help="Attempt to securely clear sensitive data from memory. WARNING: Experimental.")
    parser.add_argument("--recovery-data", action="store_true", help="Add Reed-Solomon recovery data to the file for minor corruption protection.")
    parser.add_argument("--compress", choices=["none", "normal", "good", "best", "ultrakill"], default="none", help="Compression level. 'ultrakill' uses preset 9 and is very slow.")    
    args = parser.parse_args()    
    file_paths = []
    for path in args.path:
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for name in files:
                    file_paths.append(os.path.join(root, name))
        elif os.path.isfile(path):
            file_paths.append(path)
        else:
            print(f"Warning: '{path}' is not a valid file or directory. Skipping.")
    if not file_paths:
        print("No valid files found for processing.")
        return
    password = args.password
    if not password:
        password = getpass.getpass("Enter password: ")
        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            print("Error: Passwords do not match.")
            return
    password = isca(password)  
    errors = []
    for file_path in file_paths:
        try:
            out_path = file_path
            if args.output:
                if not os.path.isdir(args.output):
                    print(f"Error: Output directory '{args.output}' does not exist.")
                    break
                out_path = os.path.join(args.output, os.path.basename(file_path))
            worker = CryptoWorker(
                operation=args.operation,
                in_path=file_path,
                out_path=out_path,
                password=password,
                custom_ext=args.ext,
                new_name_type=args.name_type,
                output_dir=args.output,
                chunk_size=args.chunk_size * 1024 * 1024,
                kdf_iterations=args.kdf_iter,
                secure_clear=args.secure_clear,
                add_recovery_data=args.recovery_data,
                compression_level=args.compress,
                progress_callback=print_progress
            )
            if args.operation == "encrypt":
                worker.encrypt_file()
            elif args.operation == "decrypt":
                worker.decrypt_file()
            print("\nDone.")
        except Exception as e:
            errors.append(f"File '{os.path.basename(file_path)}' failed: {e}")
            print(f"\nError: {e}")
    password = None
    if errors:
        print("\nOperation finished with errors: ")
        for error in errors:
            print(f"- {error}")
    else:
        print("\nAll files processed successfully.")

if __name__ == '__main__':
    main()