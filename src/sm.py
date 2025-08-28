## sm.py
## last updated: 28/8/2025 <d/m/y>
## p-y-l-i
from importzz import *

_lib = None
lib_name = None
if sys.platform == "win32":
    lib_name = "secure_mem.dll"
elif sys.platform == "darwin":
    lib_name = "secure_mem.dylib"
else:
    lib_name = "secure_mem.so"
try:
    if getattr(sys, "frozen", False):
        lib_path = os.path.join(sys._MEIPASS, "c", lib_name)
    else:
        lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c", lib_name)
    _lib = ctypes.CDLL(lib_path)
    _lib.zero_memory.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
    _lib.zero_memory.restype = None
except (OSError, AttributeError) as e:
    _lib = None
    print(f"[DEBUG] Could not load secure memory library '{lib_name}': {e}")
    print("[DEBUG] Secure password clearing will be disabled.")

def clear_buffer(buffer):
    if not isinstance(buffer, ctypes.Array) or not buffer._type_ == ctypes.c_char:
        raise TypeError("Can only clear a ctypes character buffer.")
    if _lib:
        buffer_ptr = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char))
        _lib.zero_memory(buffer_ptr, len(buffer))
    else:
        try:
            buffer.raw = b'\x00' * len(buffer.raw)
        except Exception:
            pass

def is_secure_clear_available():
    return _lib is not None

## end