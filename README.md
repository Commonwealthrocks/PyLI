# Features at glance if you don't give a shit about this readme :)
- Uses AES-256-GCM with PBKDF2HMAC.
- Unique salt and nonce per file / chunk.
- Portable + offline with ZERO data collection.
- Archive mode for multiple files with folder structure preservation.
- Multiple compression options: zlib, Zstandard, legacy LZMA.
- Encrypt file(s) with any given extension example: `.dat`, `.dll` and so on.
- Reed-Solomon error correction for bit rot protection (optional).
- No dependency hell, just pure Python or run the `.exe` if you download it that way.
- Open source, and easy to wipe off your system if you hate it.

# **PyLI** - *Not harvesting your data since 2025!*
**PyLI** is an application coded in Python used for encrypting files with AES-256-GCM and PBKDF2HMAC for key derivation up to
1,000,000 (editable in source). It uses Salt and Nonce to ensure secure and robust cryptographic operations, pretty fancy I know...!

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![](https://img.shields.io/badge/C-Library-darkblue?logo=c&logoColor=white)
![AES](https://img.shields.io/badge/Encryption-AES--256--GCM-green?logo=lock&logoColor=white)
![Offline](https://img.shields.io/badge/100%25-Offline-important)
![License](https://img.shields.io/badge/License-MIT-orange)

## "Why does this exist?" - *Good question Jimmy!*
Sometimes, maybe all the times. You have a need to encrypt your files from whoever: could be your parents, your ISP, the government, the feds?
All of the above in general, PyLI allows that in just 4 simple steps!
1. Choose your file(s) or entire folders.
2. Choose your output directory in `settings`.
3. Set a password, don't lazy out on this or AES WILL be rendered useless.
4. Hit encrypt or decrypt, ez.

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
- **Normal**: zlib compression (**fast**, shit-ish ratio)  
- **Best**: Zstandard level 3 (**balanced** speed/compression)
- **ULTRAKILL**: Zstandard level 22 (**slow*, excellent compression)
- **[L] ULTRAKILL**: Legacy LZMA preset 9 (**extremely slow,** for masochists)

The app automatically skips compression for already compressed formats like `.jpg`, `.mp4`, `.zip`, etc.

## "What about the master password?" - *Well, just cause we use military grade encryption does not mean you should cheap out on this...*
AES-256-GCM is complex math all under one master password, even with 1 MILLION key derivations with PBKDF2HMAC. If your password is weak
example `1234` or `password`, then yeah expect AES to be pure useless; use strong passwords for sensitive information.

## "okay... now why should I use this?" - *Well, you don't have to use it but when making this app, I made some… decisions…*
- **PyLI** works offline and is portable.
- All file(s) processed stay LOCALLY on YOUR PC or machine.
- Open source, pretty common for many projects but you can get a good peek under the hood of **PyLI.**
- No data collection since the app works without Internet, you have no reasons to worry about any breaches.
- **PyLI** as a whole is pretty straight-fucking-forward, ever tried using GPG or PGP? Yeah you'd be grateful for this app.
- If you don't like the app, uninstalling is easy as selecting the `.exe` and hitting delete. And if you wanna clear it off for good, delete the **PyLI** folder in `%AppData%`
- Archive mode preserves your folder structure when encrypting multiple files.
- Optional Reed-Solomon error correction protects against bit rot and minor corruption.
- **PyLI** does not come with half-ass or baked features that nobody wants, pretty neat.
- No dependency hell, just run the `.exe`. Or if you downloaded the source code then yeah there'd be a few things you have to do...
- Secure memory clearing (when C library is available) to wipe passwords from RAM.


# **PyLI:**
Because WinRAR asks you for money and I don't, for now...