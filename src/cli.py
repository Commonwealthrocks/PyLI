## cli.py
## last updated: 16/09/2025 <d/m/y>
## p-y-l-i
from importzz import *
from core import CryptoWorker, MAGIC_NUMBER, create_archive, decompress_archive
from sm import clear_buffer
from cmp import COMPRESSION_MODES

def print_progress(percentage, width=50):
    filled_len = int(round(width * percentage / 100))
    bar = Fore.GREEN + "█" * filled_len + Style.RESET_ALL + Fore.WHITE + "░" * (width - filled_len) + Style.RESET_ALL
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
    parser.add_argument("--chunk-size", type=int, default=3, help="Chunk size in MB. Default: 3MB.")
    parser.add_argument("--kdf-iter", type=int, default=200000, help="KDF iterations. Default: 200000.")
    parser.add_argument("--no-secure-clear", action="store_true", help="Disables secure clearing of sensitive data.")
    parser.add_argument("--no-recovery-data", action="store_true", help="Excludes recovery data from the header.")
    parser.add_argument("-c", "--compress", choices=list(COMPRESSION_MODES.keys()), default="none", help="Compression level to use. Default: 'none'.")
    parser.add_argument("-a", "--archive", choices=["create", "extract"], help="Create or extract a single archive file from multiple files. When used, only a single output file is generated or multiple files are extracted.")
    args = parser.parse_args()
    password = None
    if args.password:
        password = args.password.encode("utf-8")
    else:
        password = getpass.getpass("Enter password: ").encode("utf-8")
        if not password:
            print(Fore.YELLOW + "Warning: Empty password provided. This is insecure." + Style.RESET_ALL)
    errors = []
    if args.archive:
        if args.archive == "create":
            print(f"Creating archive from {len(args.path)} file(s)...")
            try:
                archive_name = "archive.dat"
                if args.output:
                    archive_name = os.path.join(args.output, archive_name)
                if os.path.exists(archive_name):
                    print(Fore.YELLOW + f"Warning: Archive '{archive_name}' already exists and will be overwritten." + Style.RESET_ALL)
                create_archive(args.path, archive_path=archive_name, progress_callback=print_progress)
                print(f"\nSuccessfully created archive: {archive_name}")
            except Exception as e:
                print(Fore.RED + f"\nError creating archive: {e}" + Style.RESET_ALL)
                errors.append(f"Archive creation failed: {e}")
        elif args.archive == "extract":
            if len(args.path) != 1:
                print(Fore.RED + "Error: 'extract' operation requires exactly one archive file path." + Style.RESET_ALL)
                sys.exit(1)  
            archive_path = args.path[0]
            print(f"Extracting archive: {archive_path}")
            try:
                extract_path = args.output if args.output else os.path.dirname(archive_path)
                decompress_archive(archive_path, output_dir=extract_path, password=password, progress_callback=print_progress)
                print(f"\nSuccessfully extracted files to: {extract_path}")
            except Exception as e:
                print(Fore.RED + f"\nError extracting archive: {e}" + Style.RESET_ALL)
                errors.append(f"Archive extraction failed: {e}")
    else:
        for file_path in args.path:
            try:
                if not os.path.isfile(file_path):
                    print(Fore.YELLOW + f"Warning: Skipping '{file_path}' as it is not a file." + Style.RESET_ALL)
                    continue
                out_path = file_path
                if args.output:
                    if not os.path.isdir(args.output):
                        print(Fore.RED + f"Error: Output directory '{args.output}' does not exist." + Style.RESET_ALL)
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
                    secure_clear=not args.no_secure_clear,
                    add_recovery_data=not args.no_recovery_data,
                    compression_level=args.compress,
                    progress_callback=print_progress
                )               
                print(f"Processing file: {os.path.basename(file_path)}")
                if args.operation == "encrypt":
                    worker.encrypt_file()
                elif args.operation == "decrypt":
                    worker.decrypt_file()
                print("\nDone.")
            except Exception as e:
                errors.append(f"File '{os.path.basename(file_path)}' failed: {e}")
                print(Fore.RED + f"\nError: {e}" + Style.RESET_ALL)
    clear_buffer(password)
    password = None
    if errors:
        print(Fore.RED + "\nOperation finished with errors:" + Style.RESET_ALL)
        for error in errors:
            print(Fore.RED + f"- {error}" + Style.RESET_ALL)
    
if __name__ == "__main__":
    init()
    main()