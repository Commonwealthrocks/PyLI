# Build Instructions & Requirements

### Python Environment
- Python 3.10+ (tested on **3.12**)
- pip package manager

### Required Python packages
```bash
pip install PySide6 cryptography pygame reedsolo zstandard
```

Or install from requirements if available:
```bash
pip install -r requirements.txt
```

### Platform specific requirements

#### Windows
- No additional requirements
- Secure memory clearing C library (`secure_mem.dll`) included

#### Linux/macOS  
- Secure memory clearing libraries may not work (`secure_mem.so/.dylib`)
- All other functionality should work normally

## Building from source

### Method 1: Direct Python Execution
```bash
python gui.py
```

### Method 2: Nuitka compilation (recommended)
```bash
pip install nuitka
python -m nuitka --onefile --enable-plugin=pyside6 --include-data-dir=sfx=sfx --include-data-dir=txts=txts --include-data-dir=c=c gui.py
```

### Method 3: PyInstaller (alternative)
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "sfx;sfx" --add-data "txts;txts" --add-data "c;c" gui.py
```

## Project structure
```
PyLI/
├── cli.py
├── core.py
├── gui.py
├── cmp.py
├── importzz.py
├── outs.py
├── sfx.py
├── sm.py
├── stylez.py
├── c/
│   ├── secure_mem.dll
│   ├── secure_mem.so
│   └── secure_mem.dylib
├── sfx/
│   ├── success.wav
│   ├── error.wav
│   └── info.wav
└── txts/
    ├── disclaimer.txt
    ├── info.txt
    └── changelog.txt
```

## Build configuration

### Nuitka options explained
- `--onefile`: Create single executable
- `--enable-plugin=pyside6`: Include Qt framework
- `--include-data-dir`: Include asset directories
- `--windows-disable-console`: Hide console on Windows (optional)

### PyInstaller options explained  
- `--onefile`: Single executable file
- `--windowed`: No console window
- `--add-data`: Include data files (format: "source;destination")

## Functionality tests
1. GUI loads without errors
2. File encryption/decryption works
3. Archive mode preserves folder structure  
4. Compression options function correctly
5. Sound effects play (if not muted)
6. Settings save/load properly
7. Debug console works (Administrator mode)

## Performance Tests
- Large file handling (1GB+)
- Multiple file batches (100+ files)
- Archive creation with deep folder structures
- Memory usage during intensive operations

## File Size Expectations
- Nuitka build: ~30MB
- PyInstaller build: ~50-70MB (estimated) 
- Source + dependencies: ~200MB (estimated ngl)

## Runtime requirements
- No Python installation needed for compiled versions
- All dependencies bundled in executable
- Runs completely offline

## Platform support
- **Windows**: Full support including secure memory clearing
- **Linux**: Core functionality works, secure memory may be disabled
- **macOS**: Core functionality works, secure memory may be disabled  

## Common build issues
1. **Missing PySide6**: Install with `pip install PySide6`
2. **zstandard import error**: Install with `pip install zstandard`  
3. **C library not loading**: Check file permissions on `c/` directory
4. **Sound system initialization failed**: pygame audio not available (non-critical)

## Runtime issues
1. **Drag & drop not working**: Run without Administrator privileges
2. **Config not saving**: Check write permissions to AppData folder
3. **Compression errors**: Verify zstandard installation
4. **Memory errors with large archives**: Reduce chunk size in settings

## Recommended IDE
- Visual Studio Code or IDLE if you hate yourself

## Build Environment
- Build on clean, trusted systems
- Verify cryptography library integrity
- Keep build tools updated
- Use official Python packages only