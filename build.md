## PyLI 

Build env-s0 for **PyLI**
Latest version: `0.7a`

## "What the fuck do I need?" *Well to build manually yourself you'd need...*
- Python `3.10+` (tested on `3.12`)
- pip package manager

Python `3.12` download: https://www.python.org/downloads/release/python-3120/

## "What about the libs?" *Glad you asked!*
```bash
pip install PySide6 cryptography pygame reedsolo zstandard
```

Or install from requirements if available (prolly not lol):
```bash
pip install -r requirements.txt
```

## "What about platform specific requirements?" *Oddly specific but...*

The key thing to have would be a working OS... yeah I know it's crazy. Anywho under is more OS info!!

### **Windows** - *spyware+*
- No additional requirements
- Secure memory clearing C library (`secure_mem.dll`) included

### **Linux/macOS** - *nerds or geeks use this*
- Secure memory clearing libraries may not work (`secure_mem.so/.dylib`)
- All other functionality should work normally

### **TempleOS** - *shoutout Terry Davis*
- No lol

## "Okay, how the flip do I build it now?" *Pretty straight-forward to!!*

### For **Python**
```bash
python gui.py
```

### C compiling with **nuitka** (recommended)
```bash
pip install nuitka
python -m nuitka --standalone --windows-console-mode=disable --onefile --enable-plugin=pyside6 --include-data-dir=txts=txts --include-data-dir=sfx=sfx --include-data-files=c/*.dll=c/ --include-data-files=c/*.so=c/ --include-data-files=c/*.dylib=c/ gui.py
```

### Glorified zipfile (**PyInstaller**)
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "sfx;sfx" --add-data "txts;txts" --add-data "c;c" gui.py
```

## "What about the PS?" - *Well, here it is. And no I won't be explaining it, making this with ASCII was already hellish enough.*
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

## "What do these **nuitka** options do?" - *Bet my ass you didn't ask for this but...!*
- `--onefile`: create single executable
- `--enable-plugin=pyside6`: include QtFramework
- `--include-data-dir`: include asset directories
- `--windows-disable-console`: hide console on Windows (optional)

## "What about the glorified zip builder?? (**PyInstaller**)" - *Also you probably don't care but here!!*
- `--onefile`: Single executable file
- `--windowed`: No console window
- `--add-data`: Include data files (format: "source;destination")

## "How do I know if PyLI is working right?" - *Oh I wonder, but do the following:*
1. GUI loads without errors
2. File encryption/decryption works
3. Archive mode preserves folder structure  
4. Compression options function correctly
5. Sound effects play (if not muted)
6. Settings save/load properly
7. Debug console works (Administrator mode)

## "What about the performance??" - *Really depends on your rig, but to test it yourself you can stress the following...*
- Large file handling (1GB+)
- Multiple file batches (100+ files)
- Archive creation with deep folder structures
- Memory usage during intensive operations

## "How big will the final files be?" - *Well, in all honesty I only know for **nuikta** but I can say for the others...*
- **Nuitka** build `.exe`: ~30-40MB
- **PyInstaller** build `".exe"`: ~50-70MB (**est.**) 
- **Source + libs**: ~200MB (**est.** ngl)

## Platform support - *Might or might not work on other OS's, find out ig...*
- **Windows**: Full support including secure memory clearing
- **Linux**: Core functionality works, secure memory may be disabled
- **macOS**: Core functionality works, secure memory may be disabled  

## "I'm having issues while buidling it!!" - *Shame, but these are the most common issues I assume...*
1. **Missing PySide6**: Install with `pip install PySide6`
2. **zstandard import error**: Install with `pip install zstandard`  
3. **C library not loading**: Check file permissions on `c/` directory
4. **Sound system initialization failed**: pygame audio not available (non-critical)

## "During runtime I have more issues :(" - *Well in that case, it's probably one of these fucky-ups*
1. **Drag & drop not working**: Run without Administrator privileges
2. **Config not saving**: Check write permissions to AppData folder
3. **Compression errors**: Verify zstandard installation
4. **Memory errors with large archives**: Reduce chunk size in settings

## "What IDE should I use?" - *Well, you probably expect this but!!*
Use **Visual Studio Code (VSCode)** for everyones sake, or if you really despise life and all that is... use **IDLE** :D

## "Where the hell do I build this??" - *A machine duh...? but on a serious note...*
- Build on clean, trusted systems
- Verify cryptography library integrity
- Keep build tools updated
- Use official Python packages only