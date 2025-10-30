# **PyLI** - *For the power users™️*
**Modern encryption software with AEAD (AES-256-GCM and ChaCha20-Poly1305) and Argon2ID or PBKDF2 for KDF.**

*Free, open source, offline, made with ❤️*

## *"The hell even is **PyLI**?"*
**PyLI** is a dedicated encryption tool that looks to improve the current encryption market with it's use of **Authenticated Encryption with Associated Data (AEAD)** and **Argon2ID** for the apps **KDF**.

## *"Why does this exist?"*
You ever wonder to yourself *"Why the hell does **WinRAR** use **AES-256-CBC** in 2025?"*, yeah me too.

**PyLI** is a dedicated encryption tool built from the ground up for modern security:
- **AEAD encryption** (**AES-256-GCM**, **ChaCha20-Poly1305**)
- **Modern KDF** (**Argon2ID** with GPU resistant hashing / bruteforcing)
- **Offline-first** - your files never leave your machine
- **Open source** - audit the code yourself

If you're encrypting files from a nosy **roommate** / **friend**, **family**, the damn **government**? For all I care, **PyLI** has got your ass covered!

## *"Can't I just use **WinRAR** or **7-zip** tho?"*
Yes. Yes you can, here's the gist of it:

- **WinRAR / 7-zip** - Main priority for them is *compression*, they just have encryption tackled on too.

- **PyLI** - **PyLI** is made exactly for security, it also offers decent compression rates.

Bottom line; if you care more about security than the size of your file(s), **PyLI** is your wingman from now on.

## "Right, but speaking of compression..."
Now for that, **PyLI** uses libraries like `zlib`, `zstd` and `lzma`; these libraries are an *industry* standard.

Is it as good as **WinRAR** or **7-zip**? No; those are dedicated compression tools. But **PyLI's** compression is solid and convenient since it's built right into the encryption workflow.

## "What about passwords?"
Ah yes, this decides the **fate** of your files. **PyLI** uses **AES-256-GCM** or **ChaCha20-Poly1305**, in simpler terms those algorithms are complex ass math under one master password you (yes the user) provides.

If you use a weak password example `1234` or lord forbid `password`, then yeah all of that **AEAD** and **KDF** won't really help you much. Use strong passwords for sensitive data.

## "Right but why should I use **PyLI** when tools like **AxCrypt** exist?"
It comes down to transparency and control. Here's what **PyLI** offers:

- **Fully transparent** - AxCrypt says *"AES-256 `¯\_(ツ)_/¯`"* (or **AES-128** if you don't have premium)... but which mode? What KDF? We show everything: **AES-256-GCM** / **ChaCha20-Poly1305**, **Argon2ID**, the whole stack.
- **Free forever** - no premium tiers, no feature locks ❤️
- **Open source** - audit the code yourself. Don't trust, verify.
- **MIT licensed** - use it however you want
- **100% offline** - never touches the internet, never collects data
- **Actually simple** - ever tried PGP/GPG? Yeah. Thank me later

**AxCrypt** might work fine, but can you see how it works? With **PyLI**, the code is as good as yours.

### End of `README.md`

# **PyLI docs** - The nerd core stuff?

## *"What is **PyLI**?"*
Oh boy...
### **PyLI (again)**
I feel like I've said this a million times BUT... **PyLI** is a dedicated encryption software that uses **AES-256-GCM** (or **ChaCha20-Poly1305**) and **Argon2ID** (or **PBKDF2**) as `KDFs`.

## *"What about the core / crypto of the app?"*
When using **PyLI**; I expect you know this but if you do not I can give a quick rundown!

### **AES-256-GCM and ChaCha20-Poly1305**
**PyLI** supports two encryption algorithms, both of which are **Authenticated Encryption with Associated Data (AEAD)**. This means they don't just encrypt your data; they also detect if anyone has tampered with it.

In simpler terms: encryption + built in "fuck you" mechanism to anyone trying to modify your files.

**AES (Advanced Encryption Standard)** is a symmetric block cipher and the global standard for encrypting sensitive data. It's trusted enough for government classified information, so yeah, it's legit.

The `256` in **AES-256** refers to the key size; `256` bits. This gives you `2^256` possible combinations, which is such a stupidly large number that brute forcing it is computationally impossible with current technology (and will stay that way for a long long time).

`GCM` stands for **Galois / Counter Mode**. This is what gives **AES** both confidentiality (data is encrypted) and integrity (tampering is detected). If someone tries to flip bits or modify your encrypted file, `GCM` will catch it during decryption.

**ChaCha20** is the encryption cipher, `Poly1305` is the authentication tag. Together they form an **AEAD** algorithm designed by **Daniel J. Bernstein** (the guy who made a lot of modern crypto). Unlike **AES**, **ChaCha20** doesn't rely on hardware acceleration. It's designed to be fast in software, which makes it ideal for devices without `AES-NI` or older hardware.

`Poly1305` handles authentication (detecting tampering), just like `GCM` does for `AES`. So basically the same shit.

Now which one should you use? Really, both are very strong and virtually have no difference *except* hardware that does not support `AES-NI` will run **AES-256-GCM** way worse than **ChaCha20-Poly1305**.

### AES-NI
Speaking of `AES-NI` **(Advanced Encryption Standard New Instructions)** is a custom set of instructions that *most* modern day CPUs have. That said helps in this kind of stuff and gives a massive `(¯\_(ツ)_/¯)` speed boost when it comes to general use of **AES**; On hardware without `AES-NI` **PyLI** might feel... slow.

## *"What about the **KDF** for the app?"*

### Argon2ID
**Argon2** is the winner of the **Password Hashing Competition (2015)** and is currently the modern standard for password based key derivation. It comes in three flavors: **Argon2D**, **Argon2I**, and **Argon2ID**... **PyLI** uses the `ID` one. **Argon2ID** is a hybrid version that combines both approaches to resist both **Side Channel Attacks (SCA)** and GPU based attacks. It's designed to be memory hard, meaning it requires a shitload of RAM to compute, which makes it expensive for attackers to parallelize on GPUs or custom hardware.

### PBKDF2
**Password Based Key Derivation Function 2 (PBKDF2)** is the fallback `KDF` when **Argon2ID** isn't available. It's older (from 2000) but still considered secure when used with enough iterations. While **PBKDF2** is secure, it's not memory hard like **Argon2ID**, so it's more vulnerable to GPU attacks. That's why I *STRONGLY* recommend you use **Argon2ID** over **PBKDF2**.

In simpler terms; **PBKDF2** only targets mostly CPUs and falls flat to GPU attacks. Still paired up with `HMAC-SHA-256 / 512` it can do a fine well job with deriving keys.

## *"Okay, now how does **PyLI** work tho...?"*
### Password
Choosing a password like said is what makes **AES-256-GCM** do well enough. Since if you have a weak password it's just fancy base64 at that point. **PyLI** offers built in password scoring via `zxcvbn`; a Python library for said thing.

### Salt
Not the *ingredient* but rather it gives each file a unique `16 byte` **Salt** (in other words unique data). This ensures all files can't be traced to one another file and adds extra obscurity to the encryption.

### Key derivation (KDF)
`KDF` is what takes your password and unique **Salt** that generates a `32 byte` **AES** key to stray away as *MUCH* as possible from the original password / key. This will not save your sorry ass from weak passwords btw.

### Checksum (SHA)
This only applies if you use **PBKDF2** as your `KDF` but in short checksum is a special hash that **SHA** gives to your `KDF` to detect tampering. `GCM` also does this; to it's own extent. Either way both **SHA-256** and **SHA-512** are at the same cryptography.

This setting does not apply if you use **Argon2ID** as your `KDF`, which either way that IS more secure than **SHA** and **PBKDF2**.

### Nonce chunks
**Nonce** is usually (and in **PyLI**) a `12 byte` unique set of data that applies per chunk. Re-using / hardcoding **Nonce** (which **PyLI** does NOT do) is a sure way for **AES-256-GCM** or **ChaCha20-Poly1305** to also be totally useless.

With that, do not mix up **Nonce** and **Salt**, **Nonce** gives actual data in the file unique data and encryption while **Salt** is more of a hash for the ACTUAL file.

### Authenticated tag
`GCM` as said earlier gives files a tag that helps detect tampering in other software. This adds another layer of "Fuck me..." when trying to crack a file that uses **AES-256-GCM**. Same case with `Poly1305`; just for **ChaCha20**.

### Compression (optional)
While I might know a bit about `cryptography` itself when it comes to compression... but hey that's why we use trusted Python libraries like `zlib`, `zstd` and `lzma` (`lzma` is mostly deprecated in **PyLI**). With this you can expect *very good* compression rates, not **WinRAR** or **7-zip** level cause those are dedicated compression tools; either way **PyLI's** rates are still very good.

### Reedsolo (optional)
If you're ever *VERY* paranoid about bit rot (error misshaps) that can occur in files, **Reedsolo** is exactly what stops that. Now **Reedsolo** does NOT help making files more secure, only there to ease true paranoia and it will increase processing time and is slow as **Rust's** compiler. I myself don't recommend it for most use cases.

### C memory clearing (optional)
Now, when you type in a password **AES-256-GCM** or **ChaCha20-Poly1305** or in general with the Python based `cryptography` library. Python strings are immutable, which means your password might lurk in your RAM; hence why **PyLI** using `secure_mem.c` zero's out the memory containing your password. Highly overkill; either way I have tested this feature to it's near end so I recommend the use of it.

This feature only works on **Windows** and **Linux**, **macOS** requires a `darwin--toolchain` which I uh... do not have nor know nothing about so it uses a Python (more unsecure but better than nothing) fall back.

## *"Now how do we use the app?"*
Now also very simple but do the following:
- **Launch the `PyLI.exe` or run it from the source, depends on how you do it.**
- **Go through the settings, yes all of them and see what fits you first.**
- **Select file(s) or a folder; folders only work with drag n' drop so keep that somewhere in that empty mind of yours.**
- **Set a password; pretty straightforward, cheap out here and you'll cheap out on security too...**
- **Hit `Encrypt` / `Decrypt` depending on the use case.**

And *voila*, how to use **PyLI** done simple.

## *"Okay, now what about ALL of the settings?"*

### Settings - `General` tab
- **Custom extension: PyLI allows your encrypted files to be ANY extension you wish to give them. Default is `.dat`.**

- **Output directory: this is where you choose for PyLI to place your encrypted / decrypted files. Default is at the desktop.**

- **New name type: the options will do the following... `keep` is when encrypting a file that the file will keep it's original name. `hash` via SHA-256 will give (based off file data) the file / archive a random name.**

- **Archive mode: a must have honestly. But this is basically a `.zip` file built into PyLI that stores file contents and structure.**

### Settings - `Audio` tab
- **Mute sfx: mutes any and all sound effects that are in the app. This can be useful if ya don't wanna wake anyone up or they just annoy you.**

### Settings - `Advanced` tab
- **AEAD algorithm: can set your AEAD as either AES-256-GCM or ChaCha20-Poly1305, both are highly secure.**

- **Use Argon2ID: uses `Argon2ID` instead of `PBKDF2` for the apps `KDF`.**

- **PBKDF2 hash type: choose your hash type for PBKDF2 between `SHA-256` and `SHA-512`; both are basically the same in the sense of security. `SHA-512` is more future proof though.**

- **PBKDF2 iterations: the amount of `KDFs` this function will do on your original password; the higher the more secure but slower (not applied if `Argon2ID` is used).**

- **Argon2ID time cost: `Argon2IDs` of the iteration count for `PBKDF2`, same principal. The higher the number the more secure but slower the app is (does not apply if `PBKDF2` is being used).**

- **Argon2ID memory cost: the amount of RAM `Argon2ID` will use when deriving a key. The higher the more secure and more RAM it will use, this can be very brutal IF trying to brute force `Argon2ID` files.**

- **Presets: `Argon2ID` memory presets. Yeah nothing more than that.**

- **Argon2ID parallelism: the amount of cores `Argon2ID` will use when working with PyLI to derive keys, recommended amount is 4-6 cores. Anything more is mostly overkill.**

- **Compression level: compression level applied from either `zlib`, `zstd` or `lzma`. Usually if you don't care about this keep it to `None` but if you want a mix of it, go with `Normal (fast)` or `Best (slow-er)`. Either way optional.**

- **Smart compression: while this option cannot be toggled (unless you manually tweak it in the source code). PyLI will automatically skip already compressed files like `.zip`, `.rar`, `.7z`, `.dll`, `.flac` and so on to save usage.**

- **Securely clear password from memory: like said before, uses the C library (`secure_mem.c`) to zero out memory left by the password when encrypting / decrypting. This feature does not work on macOS and it uses the Python fallback**

- **Add partial data recovery info: also like said from earlier; uses Reedsolo to prevent bit rot and data loss, does not help with encryption and heavily slows down the process. Not recommended unless you REALLY need it...**

- **Chunk size: PyLI will process chunks in whatever number is chosen to prevent overly heavy RAM usage or disk usage, default and recommended in 3-5MB. For the lord's sake do not mess with THIS feature.**

## *"What about the FAQ?!?!"*
Yes yes. I hear you...

### *"Can files be recovered if I forget the password?"*
Short answer; no.

I would say yes but I remember that we are using **AEAD** for our algorithms. This kind of stuff is only possibly with *"weak"* crypto like **ROT13** or **Base64**.

**AES-256-GCM** and **ChaCha20-Poly1305** are very unforgiving, forget your password and your file(s) are as good as lost.

### *"How secure is this AES or Cha shit?"*
Well, a direct but indirect answer but **AES-256-GCM** / **ChaCha20-Poly1305** or any `cryptography` element like `PBKDF2` or `Argon2ID` is actually used to encrypt military / government secrets... yet the War Thunder community still keeps getting them somehow?

Bottom line; really really damn secure.

### "Why does Windows Defender flag the `.exe`?"
Well, here's what **Windows** sees when looking at **PyLI**:

- **Unregistered or unsigned `.exe`.**

- **Can read, write and encrypt files.**

- **MUST BE RANSOMEWARE!!**

So yeah, that's my best reasoning, and if you don't trust if you can run it in **Sandbox** or **VM** or toss into **VirusTotal**, it don't really matter. And yeah; without a 300-damn-euro code signature **Windows** will always do this no matter what.

### *"Can I use this for [insert_illegal_thing]?"*
Well, in theory yes'nt. But from my view I won't encourage it, but you have free will to do whatever with my software. After all it's open source `¯\_(ツ)_/¯`

### *"Is this spyware?"*
There is a lingering joke about **PyLI** however if you think that; review every commit and the code too for you to see yourself.

### *"I use Arch btw."*
I'll assume you're asking for the CLI mode... well uh, oh boy!

Yeah the CLI mode for now is very borked and un--tested, that's a fault on MY end and I am planning to fix it in the near future.

### End of `docs.md`

# PyLI build information
### Warning
This build version is for **PyLI** version `v1.3`

## *"Where do I get the source code?"*
From the releases tab you can get the source code for version `v1.3` or any older version. If you want the best support and UX, choose the **LATEST** version and download the `.zip` file.

The password for the `.zip` file(s) is; `PyLI`, use a tool like **WinRAR**, **7-zip** or **WinZip (built in)** to extract it.

## *"Right... but what do I need for this?"*

### Python 3.12
To compile **PyLI**, you'll need at least **Python `3.10+`** (tested on `3.12`). If you are using `MSVC` as your C compiler; you can use **Python** `3.13`, otherwise you must use either `3.12` for `GCC` or `Clang` as your compiler.

#### [Python 3.12 download page](https://www.python.org/downloads/release/python-3120/)

### Python libraries
Simply run this somewhere in your terminal WITH **pip** and **Python** both in your PATH.
```bash
pip install numpy pyside6 cryptography colorama pygame reedsolo zstandard argon2-cffi nuitka
```

There 100% is NOT a `requirements.txt` in there so sorry :)

## *"What about the C libraries?"*
Both C libraries (in `v1.3`) are ALREADY compiled both for **Windows** and **Linux**. **macOS** is still lacking since I cannot bother getting a darwin--toolchain SDK nor a compiler.

## *"Right... now how do I build it?"*

### GCC Nuitka (Linux / Windows)
```bash
nuitka --standalone --windows-icon-from-ico=pyli_icon.ico --mingw64 --windows-console-mode=disable --onefile --enable-plugin=pyside6 --include-data-dir=txts=txts --include-data-dir=sfx=sfx --include-data-dir=img=img --include-data-files=c/win32/secure_mem.dll=c/32/secure_mem.dll --include-data-files=c/penguin/secure_mem.so=c/penguin/secure_mem.so --include-data-files=c/win32/chc_aes_ni.dll=c/win32/chc_aes_ni.dll --include-data-files=c/penguin/chc_aes_ni.so=c/penguin/chc_aes_ni.so gui.py
```
Run this in the root of the project; aka where you'll find `gui.py` in a terminal.

### MSVC Nuitka (Windows)
```bash
nuitka --standalone --windows-icon-from-ico=pyli_icon.ico --windows-console-mode=disable --onefile --enable-plugin=pyside6 --include-data-dir=txts=txts --include-data-dir=sfx=sfx --include-data-dir=img=img --include-data-files=c/win32/secure_mem.dll=c/win32/secure_mem.dll --include-data-files=c/penguin/secure_mem.so=c/penguin/secure_mem.so --include-data-files=c/win32/chc_aes_ni.dll=c/win32/chc_aes_ni.dll --include-data-files=c/penguin/chc_aes_ni.so=c/penguin/chc_aes_ni.so gui.py
```
Same step, run it in the root; this one here is **Windows** only.

### When done
When it's done building, you should get the `gui.exe`, which you can rename to `PyLI.exe`. And voila! You have **PyLI**; use for your needs.

## *"I got [insert_error]!!! 😔"*
Now it all depends on your error, but the most common issues are only having `GCC` or `Clang` but a higher version of **Python** `3.12`; use **MSVC** if you have `3.13`.

Another issue could be **macOS** in general... God I hate that OS but yeah, **PyLI** is meant for **Windows** mostly, stuff like **Linux** or **macOS** is a best effort from my end.

Or an issue could be missing deps... which in that case read these fucking instructions once more.

### End of `build_info.md`