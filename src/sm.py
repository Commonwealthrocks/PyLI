## sm.py
## last updated: 24/09/2025 <d/m/y>
## p-y-l-i
import ctypes
import os
import sys
from colorama import *

_lib = None
lib_name = None
lib_dir = None
if sys.platform == "win32":
    lib_name = "secure_mem.dll"
    lib_dir = "spyware"  # no the code is not ACTUALLY spyware...
elif sys.platform == "darwin":
    lib_name = "secure_mem.dylib"
    lib_dir = "sosumi"
elif sys.platform.startswith("linux"):
    lib_name = "secure_mem.so"
    lib_dir = "penguin"
override_path = os.environ.get("PYLI_SECURE_MEM") 
if sys.platform == "darwin":
    print(Fore.YELLOW + "[DEV PRINT] Secure memory clearing could not be loaded on macOS; it needs to be compiled on a darwin--toolchain.")
    print("[DEV PRINT] Secure password clearing will be disabled." + Style.RESET_ALL)
    _lib = None
else:
    if lib_dir and lib_name:
        try:
            if override_path:
                lib_path = override_path
            else:
                if getattr(sys, "frozen", False):
                    lib_path = os.path.join(sys._MEIPASS, "c", lib_dir, lib_name)
                else:
                    lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c", lib_dir, lib_name)
            lib_path = os.path.normpath(lib_path)
            _lib = ctypes.CDLL(lib_path)
            _lib.zero_memory.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
            _lib.zero_memory.restype = None
            print(Fore.GREEN + f"[DEV PRINT] Loaded secure memory library '{lib_name}'; zero'd" + Style.RESET_ALL)
        except (OSError, AttributeError) as e:
            _lib = None
            print(Fore.RED + f"[DEV PRINT] Could not load secure memory library '{lib_name}'.\n\ne: {e}")
            print("[DEV PRINT] Secure password clearing will be disabled." + Style.RESET_ALL)

def clear_buffer(buffer):
    try:
        is_ctypes_array = isinstance(buffer, ctypes.Array) and getattr(buffer, "_type_", None) is ctypes.c_char
    except Exception:
        is_ctypes_array = False

    if is_ctypes_array:
        if _lib:
            buf_ptr = ctypes.cast(buffer, ctypes.c_void_p)
            _lib.zero_memory(buf_ptr, len(buffer))
        else:
            try:
                cleared = (b"\x00" * len(buffer))
                mv = memoryview(buffer)
                mv[:] = cleared
            except Exception:
                try:
                    for i in range(len(buffer)):
                        buffer[i] = b"\x00"
                except Exception:
                    pass
    else:
        if isinstance(buffer, bytearray):
            for i in range(len(buffer)):
                buffer[i] = 0
        elif isinstance(buffer, memoryview) and buffer.readonly is False:
            buffer[:] = b"\x00" * len(buffer)
        else:
            raise TypeError("clear_buffer expects a writable ctypes.c_char array or bytearray / mutable memoryview; unexpected")

def isca():
    return _lib is not None

## end