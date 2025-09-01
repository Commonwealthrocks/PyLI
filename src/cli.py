## cli.py
## last updated: 01/9/2025 <d/m/y>
## p-y-l-i
from importzz import *
from core import CryptoWorker, MAGIC_NUMBER
from sm import is_secure_clear_available

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
    parser.add_argument("--chunk-size", type=int, default=3, help="Chunk size in MB for processing. Default: 3.")
    parser.add_argument("--kdf-iter", type=int, default=1000000, help="Number of KDF iterations. Higher is more secure but slower. Default: 1,000,000.")
    parser.add_argument("--compress", choices=["none", "normal", "good", "best"], default="none", help="Compression level. Default: 'none'.")
    parser.add_argument("--recovery-data", action="store_true", help="Add Reed-Solomon data recovery information. Increases file size.")
    secure_clear_help = "Securely clear password from memory after use. Requires compiled C library."
    if not is_secure_clear_available():
        secure_clear_help += " (DISABLED: library not found)"
    parser.add_argument("--secure-clear", action="store_true", help=secure_clear_help)
    args = parser.parse_args()
    if args.secure_clear and not is_secure_clear_available():
        print("Warning: Secure password clearing is enabled but the C library is not available. This feature will not work.")
    password = args.password
    if not password:
        try:
            password = getpass.getpass("Enter password: ")
        except (EOFError, KeyboardInterrupt):
            print("\nOperation canceled.")
            return
    if not password:
        print("Error: Password cannot be empty.")
        return
    files_to_process = []
    for p in args.path:
        if os.path.isfile(p):
            files_to_process.append(p)
        elif os.path.isdir(p):
            for root, _, files in os.walk(p):
                for name in files:
                    files_to_process.append(os.path.join(root, name))
        else:
            print(f"Warning: Path '{p}' is not a valid file or directory. Skipping.")
    if not files_to_process:
        print("Error: No valid files to process.")
        return
    print(f"Found {len(files_to_process)} file(s) to process.")
    errors = []
    for i, file_path in enumerate(files_to_process):
        print(f"\nProcessing file {i+1}/{len(files_to_process)}: {os.path.basename(file_path)}")
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
        print("\nOperation finished successfully for all files.")

if __name__ == "__main__":
    main()

## end