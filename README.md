# **PyLI** - *Not harvesting your data since 2025!*
**This is JOKE software, expect roughness or... about anything!**

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![C](https://img.shields.io/badge/-darkblue?logo=c&logoColor=white)
![ChaCha20-Poly1305](https://img.shields.io/badge/Encryption-ChaCha20--Poly1305-green?logo=lock&logoColor=white)
![AES](https://img.shields.io/badge/Encryption-AES--256--GCM-green?logo=lock&logoColor=white)
![Offline](https://img.shields.io/badge/100%25-Offline-important)
![License](https://img.shields.io/badge/License-MIT-orange)

## "Why does this exist?" - *Good question Jimmy!*
Sometimes, maybe all the times. You have a need to encrypt your files from whoever: could be your parents, your ISP, the government, the feds?

All of the above in general, PyLI allows that in just 4 simple steps!!!

### The steps mentioned above :]

*+-* **Choose your file(s) or entire folders.**

*+-* **Choose your output directory in `settings`.**

*+-* **Set a password, don't lazy out on this or AES-256-GCM or ChaCha20-Poly1305 WILL be rendered useless.**

*+-* **Hit encrypt or decrypt, ez.**

## "Can't I just use WinRAR or 7z for encryption?" - *Well, yes you technically can.*
...but why settle for a swiss army knife when you can have a sledgehammer? While **WinRAR** and **7z** are great for compression and
do offer encryption, they're not built from the ground up to be a dedicated security tool.
**PyLI's** only job is to encrypt your files and do it well.

My take on this?
If it's for a single file or not too many files, use **PyLI** directly to encrypt them.
If you have multiple files you wish to encrypt, use **PyLI's** archive mode to bundle them into a single encrypted file that preserves your folder structure. Or first compress them with WinRAR/7z, THEN use **PyLI** to encrypt your compressed archive for double-layered protection. After all I'm not a compression expert, they are!!

## "But wait what about compression?" - *Uhh scrap the shit I said earlier...*
**PyLI** now includes multiple compression options:
- **None**: Skip compression (**fastest**, non-existant-ratio)
- **Normal**: Zlib compression (**fast**, shit-ish ratio)  
- **Best**: Zstandard level 3 (**balanced** speed/compression)
- **ULTRAKILL**: Zstandard level 22 (**slow**, excellent compression)
- **[L] ULTRAKILL**: Legacy LZMA preset 9 (**extremely slow,** for masochists)

The app automatically skips compression for already compressed formats like `.jpg`, `.mp4`, `.zip`, etc.

## "What about the master password?" - *Well, just cause we use military grade encryption does not mean you should cheap out on this...*
**AES-256-GCM** or **ChaCha20-Poly1305** is complex math all under one master password, even with **Argon2ID** or **PBKDF2**. If your password is weak example `1234` or `password`, then yeah expect AES to be pure useless; use strong passwords for sensitive information.

## "okay... now why should I use this?" - *Well, you don't have to use it but when making this app, I made some… decisions…*
*+-* **PyLI works offline and is portable.**

*+-* **All file(s) processed stay LOCALLY on YOUR PC or machine.**

*+-* **Open source, pretty common for many projects but you can get a good peek under the hood of PyLI.**

*+-* **No data collection since the app works without Internet, 
you have no reasons to worry about any breaches.**

*+-* **PyLI as a whole is pretty straight-fucking-forward, ever tried using GPG or PGP? Yeah you'd be grateful for this app.**

*+-* **If you don't like the app, uninstalling is easy as selecting the `.exe` and hitting delete. And if you wanna clear it off for good, delete the PyLI folder in `%AppData%`.**

*+-* **Archive mode preserves your folder structure when encrypting multiple files, basically knock off `.zip`.**

*+-* **Optional Reedsolo error correction protects against bit rot and minor corruption.**

*+-* **PyLI does not come with half-ass or baked features that nobody wants, pretty neat.**

*+-* **No dependency hell, just run the `.exe`. Or if you downloaded the source code then yeah there'd be a few things you have to do...**

*+-* **Secure memory clearing (when C library is available) to wipe passwords from RAM.**

# `End of README`

# **PyLI docs cuz ppl r dumb** - *read this I beg...*

## "What the hell IS **PyLI**...?" - *Well, you sure know already but...*
**PyLI** is a dedicated encryption software that uses **AES-256-GCM** (or **ChaCha20-Poly1305**) and **Argon2ID** (or **PBKDF2**) as `KDFs`.

You might ask yourself: *"What the fuck does any of that mean?"*; Well if you plan on using **PyLI** I expect you to know the basics of crypto but we can quickly go over it.

### AES-256-GCM and ChaCha20-Poly1305
**PyLI** supports two encryption algorithms, both of which are **Authenticated Encryption with Associated Data (AEAD)**. This means they don't just encrypt your data; they also detect if anyone has tampered with it. In simpler terms: encryption + built-in "fuck you" to anyone trying to modify your files.

**AES (Advanced Encryption Standard)** is a symmetric block cipher and the global standard for encrypting sensitive data. It's trusted enough for government classified information, so yeah, it's legit.

The `256` in **AES-256** refers to the key size; `256` bits. This gives you `2^256` possible combinations, which is such a stupidly large number that brute-forcing it is computationally impossible with current technology (and will stay that way for a long ass time).

`GCM` stands for **Galois/Counter Mode**. This is what gives **AES** both confidentiality (data is encrypted) and integrity (tampering is detected). If someone tries to flip bits or modify your encrypted file, `GCM` will catch it during decryption.

**ChaCha20** is the encryption cipher, `Poly1305` is the authentication tag. Together they form an **AEAD** algorithm designed by Daniel J. Bernstein (the guy who made a lot of modern crypto). Unlike **AES**, **ChaCha20** doesn't rely on hardware acceleration. It's designed to be fast in software, which makes it ideal for devices without `AES-NI` or older hardware.

`Poly1305` handles authentication (detecting tampering), just like `GCM` does for `AES`. So basically the same shit.

Bottom line; do the following...

*+-* **If your CPU supports `AES-NI`, use AES-256-GCM.**

*+-* **If not, use ChaCha20-Poly1305 or use it on much harder / slower hardware.**

Either way, both are actually VERY secure and recommended. So it's EITHER way; hell you just might like it more cause of the name. Valid since **ChaCha20-Poly1305** sounds sick as hell.

### AES-NI
Speaking of `AES-NI` **(Advanced Encryption Standard New Instructions)** is a custom set of instructions that *most* modern day CPUs have. That said helps in this kind of stuff and gives a massive `(¯\_(ツ)_/¯)` speed boost when it comes to general use of **AES**; On hardware without `AES-NI` **PyLI** might feel... slow.

### Argon2ID
**Argon2** is the winner of the **Password Hashing Competition (2015)** and is currently the modern standard for password based key derivation. It comes in three flavors: **Argon2D**, **Argon2I**, and **Argon2ID**... **PyLI** uses the `ID` one. **Argon2ID** is a hybrid version that combines both approaches to resist both **Side Channel Attacks (SCA)** and GPU based attacks. It's designed to be memory hard, meaning it requires a shitload of RAM to compute, which makes it expensive for attackers to parallelize on GPUs or custom hardware.

### PBKDF2
**Password Based Key Derivation Function 2 (PBKDF2)** is the fallback `KDF` when **Argon2ID** isn't available. It's older (from 2000) but still considered secure when used with enough iterations. While **PBKDF2** is secure, it's not memory hard like **Argon2ID**, so it's more vulnerable to GPU attacks. That's why I *STRONGLY* recommend you use **Argon2ID** over **PBKDF2**.

In simpler terms; **PBKDF2** only targets mostly CPUs and falls flat to GPU attacks. Still paired up with `HMAC-SHA-256` it can do a fine well job with deriving keys.

## "Geez you talk a lot, how does **PyLI** work?" - *Fine I'll shut up, but going onward...*

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
**Nonce** is usually (and in **PyLI**) a `12 byte` unique set of data that applies per chunk. Re-using / hardcoding **Nonce** (which **PyLI** does NOT do) is a sure way for **AES-256-GCM** to also be totally useless.

With that, do not mix up **Nonce** and **Salt**, **Nonce** gives actual data in the file unique data and encryption while **Salt** is more of a hash for the ACTUAL file.

### Authenticated tag
`GCM` as said earlier gives files a tag that helps detect tampering in other software. This adds another layer of "Fuck me..." when trying to crack a file that uses **AES-256-GCM**.

### Compression (optional)
While I might know a bit about `cryptography` itself when it comes to compression... but hey that's why we use trusted Python libraries like `zlib`, `zstd` and `lzma` (`lzma` is mostly deprecated in **PyLI**). With this you can expect *very good* compression rates, not **WinRAR** or **7-zip** level ones but for built in; can be useful?

### Reedsolo (optional)
If you're ever *VERY* paranoid about bit rot (error misshaps) that can occur in files, **Reedsolo** is exactly what stops that. Now **Reedsolo** does NOT help making files more secure, only there to ease true paranoia and it will HEAVILY increase processing time. I myself don't recommend it for most use cases.

### C memory clearing (optional)
Now, when you type in a password **AES-256-GCM** or in general with the Python based `cryptography` library. Python strings are immutable, which means your password might lurk in your RAM; hence why **PyLI** using `secure_mem.c` zero's out the memory containing your password. Highly overkill; either way I have tested this feature to it's near end so I recommend the use of it.

This feature only works on **Windows** and **Linux**, **macOS** requires a `darwin--toolchain` which I uh... do not have nor know nothing about so it uses a Python (more unsecure but better than nothing) fall back.

## "Right right... now how do we use the app?" - *Oh yeah, the part you probably skipped to...*
Now for this unchanged it's pretty simple...

### Encryption
*+-* **Launch `PyLI.exe` or in whatever way you doin' it.**

*+-* **Select file(s) either by using the `Browse` button or dragging n' dropping them or folders; folders only with drag n' drop.**

*+-* **Select a password worth Gods might, or ya might regret it...**

*+-* **In the `Settings` tab and `General` subtab you can choose your output directory (default is desktop)**.

*+-* **Click the big ass (or maybe not) encrypt button to start work.**

And wallahi, you have your first encrypted **PyLI** file / archive. How simple, right?!?!?

Trying to encrypt an already encrypted **PyLI** file will cause corruption, the app accounts for this by skipping already **PyLI'ifed** files...?

### Decryption
Basically the same process besides that you have select and encrypted file(s) or archive that were encrypted with **PyLI**.

And other than that, you enter the password for the encrypted file or archive and hit the big ol' decrypt button.

## "Okay, now what about ALL of the settings?" - *Oh dear, well stay strapped since this part will be most informal...*

Alright alright... this is probably the bit you ACTUALLY need to read, trust me.

### Settings - `General` tab
*+-* **Custom extension: PyLI allows your encrypted files to be ANY extension you wish to give them. Default is `.dat`.**

*+-* **Output directory: this is where you choose for PyLI to place your encrypted / decrypted files. Default is at the desktop.**

*+-* **New name type: the options will do the following... `keep` is when encrypting a file that the file will keep it's original name. `hash` via SHA-256 will give (based off file data) the file / archive a random name.**

*+-* **Archive mode: a must have honestly. But this is basically a `.zip` file built into PyLI that stores file contents and structure.**

### Settings - `Audio` tab
*+-* **Mute sfx: mutes any and all sound effects that are in the app. This can be useful if ya don't wanna wake anyone up or they just annoy you.**

### Settings - `Advanced` tab
*+-* **AEAD algorithm: can set your AEAD as either AES-256-GCM or ChaCha20-Poly1305, both are VERY secure.**

*+-* **Use Argon2ID: uses `Argon2ID` instead of `PBKDF2` for the apps `KDF`.**

*+-* **PBKDF2 iterations: the amount of `KDFs` this function will do on your original password; the higher the more secure but slower (not applied if `Argon2ID` is used).**

*+-* **Argon2ID time cost: `Argon2IDs` of the iteration count for `PBKDF2`, same principal. The higher the number the more secure but slower the app is (does not apply if `PBKDF2` is being used).**

*+-* **Argon2ID memory cost: the amount of RAM `Argon2ID` will use when deriving a key. The higher the more secure and more RAM it will use, this can be very brutal IF trying to brute force `Argon2ID` files.**

*+-* **Presets: `Argon2ID` memory presets. Yeah nothing more than that.**

*+-* **Argon2ID parallelism: the amount of cores `Argon2ID` will use when working with PyLI to derive keys, recommended amount is 4-6 cores. Anything more is mostly overkill.**

*+-* **Compression level: compression level applied from either `zlib`, `zstd` or `lzma`. Usually if you don't care about this keep it to `None` but if you want a mix of it, go with `Normal (fast)` or `Best (slow-er)`. Either way optional.**

*+-* **Smart compression: while this option cannot be toggled (unless you manually tweak it in the source code). PyLI will automatically skip already compressed files like `.zip`, `.rar`, `.7z`, `.dll`, `.flac` and so on to save usage.**

*+-* **Securely clear password from memory: like said before, uses the C library (`secure_mem.c`) to zero out memory left by the password when encrypting / decrypting. This feature does not work on macOS and it uses the Python fallback**

*+-* **Add partial data recovery info: also like said from earlier; uses Reedsolo to prevent bit rot and data loss, does not help with encryption and heavily slows down the process. Not recommended unless you REALLY need it...**

*+-* **Chunk size: PyLI will process chunks in whatever number is chosen to prevent overly heavy RAM usage or disk usage, default and recommended in 3-5MB. For the lord's sake do not mess with THIS feature.**

### My personal settings; not needed
*+-* **Custom extension: `.dat`.**

*+-* **Output directory: desktop**

*+-* **Mute sfx: true**

*+-* **AEAD algorithm: AES-256-GCM**

*+-* **Use Argon2ID: true**

*+-* **PBKDF2 hash type: SHA-512**

*+-* **PBKDF2 iterations: 1,000,000 (1m)**

*+-* **Argon2 time cost: 4**

*+-* **Argon2 memory cost: 96MB**

*+-* **Argon2 parallelism: 4**

*+-* **Compression level: `None`**

*+-* **Securely clear password from memory: true**

*+-* **Add partial data recovery info: false**

*+-* **Chunk size: 4MB**

## "Okay but I have some questions!!!" - *Aight.*
### "If I lose / forget my password for a file or archive, can I get it back?"
The answer is yes... is what I would say if we we're using **ROT13**, **AES-256-GCM** (same with **ChaCha20-Poly1305**) is very unforgiving, so NO you can't recover your data in the sense of decrypting it.

### "How secure is this AES or Cha shit?"
Well, a direct but indirect answer but **AES-256-GCM** / **ChaCha20-Poly1305** or any `cryptography` element like `PBKDF2` or `Argon2ID` is actually used to encrypt military / government secrets... yet the War Thunder community still keeps getting them somehow?

Now in short: yes. Very secure and powerful as hell.

### "Why does Windows Defender flag the `.exe`?"
Well, here's what **Windows** sees when looking at **PyLI**...

*+-* **Unregistered or unsigned `.exe`.**

*+-* **Can read, write and encrypt files.**

*+-* **MUST BE RANSOMEWARE!!**

So yeah, that's my best reasoning, and if you don't trust if you can run it in **Sandbox** or **VM** or toss into **VirusTotal**, it don't really matter. And yeah; without a 300-damn-euro code signature **Windows** will always do this no matter what.

### "Can I use this for [insert_illegal_thing]?"
Well, in theory yes'nt. But from my view I won't encourage it, but you have free will to do whatever with my software. After all it's open source...

### "Um, is the crypto audited??"
The core... or well `core.py` is not audited by professionals; but if you check yourself or ask anyone about it. Nine times out of ten they will say that the implementation is good.

### "Okay, now erm... 🤓 I use Arch btw... how do I use CLI?" - *Yeah um... about that...!*
Now in all honesty this issue is on **me** since I never really tested CLI mode. It's buggy, doesn't work... and somehow I'm better with GUI work?

That being said, you can try the CLI mode...? It's just really shit.

# `End of documentation`

# PyLI build information
### Warning
This build version is for **PyLI** version `v1.3`

## "Where do I get the source code?" - *Well...!*
From the releases tab you can get the source code for version `v1.3` or any older version. If you want the best support and UX, choose the **LATEST** version and download the `.zip` file.

The password for the `.zip` file(s) is; `PyLI`, use a tool like **WinRAR**, **7-zip** or **WinZip (built in)** to extract it.

## "Right... but what do I need for this?" *Probably should of said this earlier but anyways.*

### Python 3.12
To compile **PyLI**, you'll need at least **Python `3.10+`** (tested on `3.12`). If you are using `MSVC` as your C compiler; you can use **Python** `3.13`, otherwise you must use either `3.12` for `GCC` or `Clang` as your compiler.

#### [Python 3.12 download page](https://www.python.org/downloads/release/python-3120/)

### Python libraries
Simply run this somewhere in your terminal WITH **pip** and **Python** both in your PATH.
```bash
pip install numpy pyside6 cryptography colorama pygame reedsolo zstandard argon2-cffi nuitka
```

There 100% is NOT a `requirements.txt` in there so sorry :)

## "What about the C libraries?" - *Short answer too...*
Both C libraries (in `v1.2`) are ALREADY compiled both for **Windows** and **Linux**. **macOS** is still lacking since I cannot bother getting a darwin--toolchain SDK nor a compiler.

## "Right... now how do I build it?" - *Also very simple...*

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

## "I got [insert_error]!!! 😔" - *Oh boy...*
Now it all depends on your error, but the most common issues are only having `GCC` or `Clang` but a higher version of **Python** `3.12`; use **MSVC** if you have `3.13`.

Another issue could be **macOS** in general... God I hate that OS but yeah, **PyLI** is meant for **Windows** mostly, stuff like **Linux** or **macOS** is a... best effort to say the least!

Or an issue could be missing deps... which in that case read these fucking instructions once more.

# `End of build information`