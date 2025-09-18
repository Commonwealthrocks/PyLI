## cli.py
## last updated: 19/09/2025 <d/m/y>
## p-y-l-i
import os
import sys
import argparse
import getpass
from colorama import *

from core import CryptoWorker, create_archive, decompress_archive
from sm import clear_buffer
from cmp import COMPRESSION_MODES

def print_progress(percentage, width=50):
    filled_len = int(round(width * percentage / 100))
    bar = (
        Fore.GREEN
        + "█" * filled_len
        + Style.RESET_ALL
        + Fore.WHITE
        + "░" * (width - filled_len)
        + Style.RESET_ALL
    )
    sys.stdout.write(f"\rProgress: |{bar}| {percentage:.2f}%")
    sys.stdout.flush()

def get_password(args):
    if args.password:
        return args.password.encode("utf-8")
    elif args.password_file:
        with open(args.password_file, "rb") as f:
            return f.read().strip()
    elif args.password_stdin:
        return sys.stdin.buffer.readline().strip()
    else:
        pwd = getpass.getpass("Enter password: ").encode("utf-8")
        if not pwd:
            print(Fore.YELLOW + "Warning: Empty password provided. This is insecure." + Style.RESET_ALL)
        return pwd

def cmd_encrypt(args):
    errors = []
    password = get_password(args)
    for file_path in args.path:
        try:
            if not os.path.isfile(file_path):
                print(Fore.YELLOW + f"Skipping '{file_path}', not a file." + Style.RESET_ALL)
                continue
            out_dir = args.output or os.path.dirname(file_path)
            if not os.path.isdir(out_dir):
                print(Fore.RED + f"Output dir '{out_dir}' does not exist." + Style.RESET_ALL)
                sys.exit(1)
            worker = CryptoWorker(
                operation="encrypt",
                in_path=file_path,
                out_path=os.path.join(out_dir, os.path.basename(file_path)),
                password=password,
                custom_ext=args.ext,
                new_name_type=args.name_type,
                output_dir=out_dir,
                chunk_size=args.chunk_size * 1024 * 1024,
                kdf_iterations=args.kdf_iter,
                secure_clear=not args.no_secure_clear,
                add_recovery_data=not args.no_recovery_data,
                compression_level=args.compress,
                progress_callback=print_progress,
            )
            print(f"Encrypting: {os.path.basename(file_path)}")
            worker.encrypt_file()
            print("\nDone.")
        except Exception as e:
            errors.append(f"'{file_path}' failed: {e}")
            print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
    clear_buffer(password)
    return errors

def cmd_decrypt(args):
    errors = []
    password = get_password(args)
    for file_path in args.path:
        try:
            if not os.path.isfile(file_path):
                print(Fore.YELLOW + f"Skipping '{file_path}', not a file." + Style.RESET_ALL)
                continue
            out_dir = args.output or os.path.dirname(file_path)
            if not os.path.isdir(out_dir):
                print(Fore.RED + f"Output dir '{out_dir}' does not exist." + Style.RESET_ALL)
                sys.exit(1)
            worker = CryptoWorker(
                operation="decrypt",
                in_path=file_path,
                out_path=os.path.join(out_dir, os.path.basename(file_path)),
                password=password,
                custom_ext=args.ext,
                new_name_type=args.name_type,
                output_dir=out_dir,
                chunk_size=args.chunk_size * 1024 * 1024,
                kdf_iterations=args.kdf_iter,
                secure_clear=not args.no_secure_clear,
                add_recovery_data=not args.no_recovery_data,
                compression_level=args.compress,
                progress_callback=print_progress,
            )
            print(f"Decrypting: {os.path.basename(file_path)}")
            worker.decrypt_file()
            print("\nDone.")
        except Exception as e:
            errors.append(f"'{file_path}' failed: {e}")
            print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
    clear_buffer(password)
    return errors

def cmd_archive(args):
    errors = []
    password = get_password(args) if args.operation == "extract" else None
    if args.operation == "create":
        try:
            archive_name = args.output or "archive.dat"
            if os.path.exists(archive_name):
                print(Fore.YELLOW + f"Overwriting existing archive '{archive_name}'." + Style.RESET_ALL)
            print(f"Creating archive from {len(args.path)} file(s)...")
            create_archive(args.path, archive_path=archive_name, progress_callback=print_progress)
            print(f"\nArchive created: {archive_name}")
        except Exception as e:
            errors.append(f"Archive creation failed: {e}")
            print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
    elif args.operation == "extract":
        if len(args.path) != 1:
            print(Fore.RED + "Error: 'extract' needs exactly one archive path." + Style.RESET_ALL)
            sys.exit(1)
        archive_path = args.path[0]
        extract_path = args.output or os.path.dirname(archive_path)
        try:
            print(f"Extracting archive: {archive_path}")
            decompress_archive(archive_path, output_dir=extract_path, password=password, progress_callback=print_progress)
            print(f"\nExtracted to: {extract_path}")
        except Exception as e:
            errors.append(f"Archive extraction failed: {e}")
            print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
    clear_buffer(password)
    return errors

def build_parser():
    parser = argparse.ArgumentParser(description="PyLI CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    def add_common_args(sp):
        sp.add_argument("path", nargs="+", help="File(s) or folder(s) to process.")
        sp.add_argument("-o", "--output", help="Output directory or file.")
        sp.add_argument("--password", help="Password (unsafe: visible in process list).")
        sp.add_argument("--password-file", help="Read password from file.")
        sp.add_argument("--password-stdin", action="store_true", help="Read password from stdin.")
        sp.add_argument("--ext", default="dat", help="Custom extension for encrypted files.")
        sp.add_argument("--name-type", choices=["keep", "hash", "base64"], default="keep")
        sp.add_argument("--chunk-size", type=int, default=3, help="Chunk size in MB.")
        sp.add_argument("--kdf-iter", type=int, default=1000000, help="KDF iterations.")
        sp.add_argument("--no-secure-clear", action="store_true", help="Disable secure buffer clearing.")
        sp.add_argument("--no-recovery-data", action="store_true", help="Exclude recovery data.")
        sp.add_argument("-c", "--compress", choices=list(COMPRESSION_MODES.keys()), default="none")
    sp_encrypt = subparsers.add_parser("encrypt", help="Encrypt files.")
    add_common_args(sp_encrypt)
    sp_encrypt.set_defaults(func=cmd_encrypt)
    sp_decrypt = subparsers.add_parser("decrypt", help="Decrypt files.")
    add_common_args(sp_decrypt)
    sp_decrypt.set_defaults(func=cmd_decrypt)
    sp_archive = subparsers.add_parser("archive", help="Archive operations.")
    sp_archive.add_argument("operation", choices=["create", "extract"])
    sp_archive.add_argument("path", nargs="+", help="Input files or archive path.")
    sp_archive.add_argument("-o", "--output", help="Output archive file or extraction dir.")
    sp_archive.add_argument("--password", help="Password for extraction.")
    sp_archive.add_argument("--password-file", help="Read password from file.")
    sp_archive.add_argument("--password-stdin", action="store_true", help="Read password from stdin.")
    sp_archive.set_defaults(func=cmd_archive)
    return parser

def main():
    init(autoreset=True)
    parser = build_parser()
    args = parser.parse_args()
    errors = args.func(args)

    if errors:
        print(Fore.RED + "\nFinished with errors:" + Style.RESET_ALL)
        for e in errors:
            print(Fore.RED + f"- {e}" + Style.RESET_ALL)
        sys.exit(1)

if __name__ == "__main__":
    main()