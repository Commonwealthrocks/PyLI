# Features at glance if you don't give a shit about this read me :)
- Uses AES-256-GCM with PBKDF2HMAC.
- Unique salt and nonce per file.
- portable + offline with ZERO data collection.
- encrypt file(s) with any given extension example: `.dat`, `.dll` and so on.
- No dependency hell, just pure Python or run the `.exe` if you download it that way.
- Open source, and easy to wipe off your system if you hate it.


# **PyLI** - *Not harvesting your data since 2025!*
**PyLI** is an application coded in Python used for encrypting files with AES-256-GCM and PBKDF2HMAC for key derivation up to
1,000,000 (editable in source). It uses Salt and Nonce to ensure secure and robust cryptographic operations, pretty fancy I know...!


## "Why does this exist?" - *Good question Jimmy!*
Sometimes, maybe all the times. You have a need to encrypt your files from whoever: could be your parents, your ISP, the goverment, the feds?
All of the above in general, PyLI allows that in just 4 simple steps!
1. Choose your file(s).
2. Choose your output directory in `settings`.
3. Set a password, don't lazy out on this or AES WILL be rendered useless.
4. Hit encrypt or decrypt, ez.


## "Can't I just use WinRAR or 7z for encryption?" - *Well, yes you technically can.*
...but as of version `0.5a`, **PyLI** has compression included which in **SOME** tests beats out WinRAR and 7-zip, then again it might be slower than those two.
But considering it's Python and optional, nothing stops you to keep using WinRAR or 7-zip first THEN **PyLI**.

My take on this?
If you wish to use WinRAR or 7-zip first for compression, by all means go ahead. But **PyLI's** compression rates are nothing
to be mad of too!!

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
- Runs SHA-256 on files for integrity checks / hash comparisons. Which can be used to upload certain content to sites like MEGA or PixelDrain, if ykyk.
- **PyLI** does not come with half-ass or baked features that nobody wants, pretty neat.
- No dependency hell, just run the `.exe`. Or if you downloaded the source code then yeah there'd be a few things you have to do...


# **PyLI:**
Because WinRAR asks you for money and I don't, for now!!
