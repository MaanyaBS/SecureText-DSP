# SecureText

**A Secure Message Communication System Using RSA Public-Key Cryptography, Digital Signatures, and Message Integrity Verification**

B.Tech project for Data Security and Privacy / Cryptography and Network Security (Module 2: public-key cryptography and RSA).

Student: `[YOUR NAME]` | USN: `[YOUR USN]` | College: `[YOUR COLLEGE]` | Department: `[YOUR DEPARTMENT]` | Guide: `[GUIDE NAME]` | Year: `[YYYY-YY]`

## Features

* RSA key generation (2048 / 3072 / 4096 bits), public key display, copy, export, import
* Private key export as password-protected PKCS#8 PEM, protected import
* RSA-OAEP (SHA-256) message encryption and decryption, Base64 output, copy / save / load
* RSA-PSS (SHA-256) digital signatures and verification
* Hybrid encryption for long text: fresh AES-256-GCM key per message, key wrapped with RSA-OAEP, documented JSON envelope
* Demonstrations: wrong private key, tampered ciphertext, tampered signed message, wrong verification key, tampered hybrid envelope
* RSA mathematics tab with a tiny-prime toy calculator (clearly labelled insecure)
* Offline, no database, one dependency (`cryptography`)

## Setup on Windows 10/11 (PowerShell or Command Prompt)

Open a terminal **inside the SecureText folder** (the one that contains `main.py`).

```
python --version
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

PowerShell may block activation. If so run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, or use Command Prompt.

macOS / Linux: use `python3`, and `source .venv/bin/activate`.

## Run the automated tests

From the project root:

```
python -m unittest discover -s tests -v
```

Optional headless check of the GUI handlers against a fake Tkinter (does not open windows):

```
python tests/gui_logic_check.py
```

## Project layout

```
main.py                 entry point
crypto/                 rsa_keys, rsa_encryption, digital_signatures, hybrid_encryption, toy_rsa
gui/                    main_window.py (Tkinter/ttk), content.py (help and maths text)
utils/                  validation.py, file_handler.py
tests/                  unittest suites + gui_logic_check.py
docs/                   report, algorithm notes, test cases/results, viva, demo script, presentation, diagrams
screenshots/            put your own screenshots here (see its README)
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` not recognised | Reinstall Python from python.org and tick **Add python.exe to PATH**, or try `py` instead of `python`. |
| `No module named 'cryptography'` | Activate the venv, then `python -m pip install -r requirements.txt`. |
| `No module named 'crypto'` / `gui` / `utils` or `tests` | You are in the wrong folder. `cd` into the folder containing `main.py` and run commands from there. |
| `No module named 'tkinter'` | Windows: rerun the Python installer, choose Modify, tick **tcl/tk and IDLE**. Ubuntu: `sudo apt install python3-tk`. macOS Homebrew: `brew install python-tk`. |
| Permission denied when saving | Choose a folder you own (Documents, Desktop), not `C:\Program Files`. |
| "Wrong password or corrupted private key file" | Retype the password exactly (case-sensitive). A forgotten password cannot be recovered; generate a new key pair. |
| "Message too large" | Direct RSA-OAEP allows 190 bytes with a 2048-bit key. Use the Hybrid Encryption tab. |
| `crypto` import clash | Do not install the unrelated `pycrypto` package in the same environment. |

## Security notes

Educational project. Keys live in memory unless you export them. Public keys are not authenticated (no certificates), so compare fingerprints out of band. See `docs/project_report.md` section 35 for the security analysis.
