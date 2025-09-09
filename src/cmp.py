# cmp.py
## last updated: 05/09/2025 <d/m/y>
## p-y-l-i
from importzz import *

COMPRESSION_NONE = 0
COMPRESSION_ZLIB = 1
COMPRESSION_ZSTD_NORMAL = 2
COMPRESSION_ZSTD_BEST = 3
COMPRESSION_LZMA_ULTRAKILL = 4
COMPRESSION_MODES = {
    "none": {"id": COMPRESSION_NONE},
    "normal": {"id": COMPRESSION_ZLIB, "func": zlib.compress},
    "best": {"id": COMPRESSION_ZSTD_NORMAL, "func": lambda d: zstd.ZstdCompressor(level=3).compress(d)},
    "ultrakill": {"id": COMPRESSION_ZSTD_BEST, "func": lambda d: zstd.ZstdCompressor(level=22).compress(d)},
    "[L] ultrakill": {"id": COMPRESSION_LZMA_ULTRAKILL, "func": lambda d: lzma.compress(d, preset=9)},
}
DECOMPRESSION_FUNCS = {
    COMPRESSION_NONE: lambda d: d,
    COMPRESSION_ZLIB: zlib.decompress,
    COMPRESSION_ZSTD_NORMAL: lambda d: zstd.ZstdDecompressor().decompress(d),
    COMPRESSION_ZSTD_BEST: lambda d: zstd.ZstdDecompressor().decompress(d),
    COMPRESSION_LZMA_ULTRAKILL: lzma.decompress,
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
    if len(compressed_data) >= len(data):
        return data, COMPRESSION_NONE
    return compressed_data, compression_id

def decompress_chunk(data, compression_id):
    if compression_id not in DECOMPRESSION_FUNCS:
        raise ValueError(f"Unknown compression ID: {compression_id}")
    return DECOMPRESSION_FUNCS[compression_id](data)

## end