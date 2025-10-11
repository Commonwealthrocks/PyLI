## PyLI 

Build env-s0 for **PyLI**
Latest version: `v1.1`

## "What the fuck do I need?" *Well to build manually yourself you'd need...*
- Python `3.10+` (tested on `3.12`)
- pip package manager

Python `3.12` download: https://www.python.org/downloads/release/python-3120/

## "What about the libs?" *Glad you asked!*
```bash
pip install PySide6 cryptography pygame reedsolo zstandard argon2-cffi
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
- Secure memory clearing has been killed off for macOS entirely

### **TempleOS** - *shoutout Terry Davis*
- No lol

## "Okay, how the flip do I build it now?" *Pretty straight-forward to!!*

### For **Python**
```bash
python -m gui
```

### C compiling with **nuitka** (recommended)
```bash
pip install nuitka
python -m nuitka --standalone --windows-icon-from-ico=pyli_icon.ico --windows-console-mode=disable --onefile --mingw64 --enable-plugin=pyside6 --include-data-dir=txts=txts --include-data-dir=sfx=sfx --include-data-dir=img=img --include-data-files=c/spyware/secure_mem.dll=c/spyware/secure_mem.dll --include-data-files=c/penguin/secure_mem.so=c/penguin/secure_mem.so gui.py
```
TLDR; If you use MSVC, remove the `--mingw64` argument  from the command

### Glorified zipfile (**PyInstaller**)
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "sfx;sfx" --add-data "txts;txts" --add-data "c;c" --icon="pyli_icon.ico" gui.py
```

## "What about the PS?" - *Well, here it is. And no I won't be explaining it.*
```
src
│   cli.py
│   cmp.py
│   core.py
│   gui.py
│   outs.py
│   sfx.py
│   sm.py
│   stylez.py
│
├───c
│   │   secure_mem.c
│   │
│   ├───penguin
│   │       secure_mem.so
│   │
│   └───spyware
│           secure_mem.dll
│
├───sfx
│       error.wav
│       info.wav
│       success.wav
│
└───txts
        changelog.txt
        disclaimer.txt
        info.txt
```

## "What do these **nuitka** options do?" - *Bet my ass you didn't ask for this but...!*
- `--onefile`: create single executable
- `--enable-plugin=pyside6`: include QtFramework
- `--include-data-dir`: include asset directories
- `--windows-disable-console`: hide console on Windows (optional)

## "What about the glorified zip builder?? (**PyInstaller**)" - *Also you probably don't care but here!!*
- `--onefile`: single executable file
- `--windowed`: no console window
- `--add-data`: include data files (format: "source;destination")

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

## "How big will the final files be?" - *Well, in all honesty I only know for **nuitka** but I can say for the others...*
- **Nuitka** build `.exe`: ~30-40MB
- **PyInstaller** build `".exe"`: ~50-70MB (**est.**) 
- **Source + libs**: ~200MB (**est.** ngl)

## Platform support - *Might or might not work on other OS's, find out ig...*
- **Windows**: full support including secure memory clearing
- **Linux**: core functionality works, secure memory may be disabled
- **macOS**: core functionality works, secure memory may be disabled  

## "I'm having issues while building it!!" - *Shame, but these are the most common issues I assume...*
1. **Missing PySide6**: install with `pip install PySide6`
2. **zstandard import error**: install with `pip install zstandard`
3. **cryptography not found**: install with `pip install cryptography`
4. **Argon2ID missing**: install with `pip install argon2-cffi`
5. **C library not loading**: check file permissions on `c/` directory
6. **Sound system initialization failed**: pygame audio not available (non-critical)

## "During runtime I have more issues :(" - *Well in that case, it's probably one of these fucky-ups*
1. **Drag & drop not working**: run without Administrator privileges
2. **Config not saving**: check write permissions to `AppData` folder
3. **Compression errors**: verify zstandard installation
4. **Memory errors with large archives**: reduce chunk size in settings

## "What IDE should I use?" - *Well, you probably expect this but!!*
Use **Visual Studio Code (VSCode)** for everyones sake, or if you really despise life and all that is... use **IDLE** :D

## "Where the hell do I build this??" - *A machine duh...? but on a serious note...*
- Build on clean, trusted systems
- Verify cryptography library integrity
- Keep build tools updated
- Use official Python packages only