## cmp.py
## last updated: 01/9/2025 <d/m/y>
## p-y-l-i
from importzz import *

COMPRESSION_NONE = 0
COMPRESSION_ZLIB = 1
COMPRESSION_LZMA_NORMAL = 2
COMPRESSION_LZMA_BEST = 3
COMPRESSION_MODES = {
    'none': {"id": COMPRESSION_NONE},
    'normal': {"id": COMPRESSION_ZLIB, "func": zlib.compress},
    'good': {"id": COMPRESSION_LZMA_NORMAL, "func": lambda d: lzma.compress(d, preset=1)},
    'best': {"id": COMPRESSION_LZMA_BEST, "func": lambda d: lzma.compress(d, preset=6)},
}
DECOMPRESSION_FUNCS = {
    COMPRESSION_NONE: lambda d: d,
    COMPRESSION_ZLIB: zlib.decompress,
    COMPRESSION_LZMA_NORMAL: lzma.decompress,
    COMPRESSION_LZMA_BEST: lzma.decompress,
}
SKIP_COMPRESSION_EXTS = {
   ## ".zip", ".rar", ".7z", ".gz", ".bz2", ".xz", ".lzma",
    ".flac", ".ogg", ".mp3", ".aac", ".opus",
    ".mp4", ".mkv", ".avi", ".mov", ".webm",
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".exe", ".dll", ".so", ".dylib",
    ".iso", ".img",
    ".dat"
}

def should_skip_compression(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if not ext:
        return False
    return ext in SKIP_COMPRESSION_EXTS

def compress_chunk(data, level="none"):
    if level not in COMPRESSION_MODES:
        raise ValueError(f"Unknown compression level: {level}")    
    mode = COMPRESSION_MODES[level]
    compression_id = mode["id"]    
    if compression_id == COMPRESSION_NONE:
        return data, compression_id        
    compressed_data = mode["func"](data)
    if len(compressed_data) < len(data):
        return compressed_data, compression_id
    else:
        return data, COMPRESSION_NONE

def decompress_chunk(data, compression_id):
    if compression_id not in DECOMPRESSION_FUNCS:
        raise ValueError(f"Unknown compression ID: {compression_id}\n\n dafuq?")        
    decompress_func = DECOMPRESSION_FUNCS[compression_id]
    return decompress_func(data)

## end