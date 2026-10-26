# Presentation: SecureText (15 slides)

An editable PowerPoint version is at `docs/SecureText_Presentation.pptx`. Slide 12 needs your own screenshots.

## Slide 1: SecureText

* A Secure Message Communication System Using RSA Public-Key Cryptography, Digital Signatures, and Message Integrity Verification
* [YOUR NAME]  |  USN: [YOUR USN]
* [YOUR COLLEGE], [YOUR DEPARTMENT]  |  Guide: [GUIDE NAME]  |  [YYYY-YY]

**Suggested visual:** Title slide with a padlock and key icon.

**Speaker notes:** Good morning. My project is SecureText, a desktop application that sends messages securely using RSA. It protects secrecy, detects changes, and proves who sent a message.

## Slide 2: Introduction

* Messages travel over networks anyone can watch
* Public-key cryptography lets two people communicate securely without sharing a secret first
* SecureText turns RSA, signatures and AES-GCM into an easy offline desktop tool
* Built with Python, Tkinter and the 'cryptography' library

**Suggested visual:** Simple picture: two people, a network, an eavesdropper.

**Speaker notes:** Normally to use secret-key encryption you must first share the key safely. Public-key cryptography removes that problem. My app makes these ideas usable and visible.

## Slide 3: Problem Statement

* Plain messages can be read and altered in transit
* Receiver cannot be sure who really sent a message
* Symmetric keys are hard to distribute securely
* Textbook RSA is unsafe and plain RSA cannot handle long messages
* Need: confidentiality + integrity + authenticity in one simple tool

**Suggested visual:** Three icons: eye (eavesdropping), pencil (tampering), mask (impersonation).

**Speaker notes:** There are three threats: someone reads the message, someone changes it, or someone pretends to be the sender. Also, RSA has size limits and needs proper padding.

## Slide 4: Objectives

* Implement RSA key generation and secure key storage
* Encrypt and decrypt with RSA-OAEP (SHA-256)
* Sign and verify with RSA-PSS (SHA-256)
* Support long messages through hybrid AES-256-GCM + RSA
* Demonstrate wrong-key and tampering failures
* Teach RSA mathematics and test everything

**Suggested visual:** Checklist graphic.

**Speaker notes:** These are the goals of the project. Each one maps to a tab in the application and to automated tests.

## Slide 5: Public-Key Cryptography Background

* Each user has a public key (share) and a private key (secret)
* Requirements: easy to generate, easy to use, infeasible to derive private from public
* Applications: encryption, digital signatures, key exchange
* Symmetric = fast, one shared key; Asymmetric = slower, solves key distribution

**Suggested visual:** Table: symmetric vs asymmetric.

**Speaker notes:** Think of the public key as an open padlock anyone can close, and the private key as the only key that opens it. Diffie and Hellman introduced the idea in 1976, and RSA made it practical in 1978.

## Slide 6: RSA Algorithm and Mathematics

* Pick primes p, q;  n = p x q;  phi(n) = (p-1)(q-1)
* Public e = 65537;  private d = e^-1 mod phi(n)
* Encrypt c = m^e mod n;  decrypt m = c^d mod n
* Security rests on the difficulty of factoring n
* Example: p=61, q=53, e=17, d=2753; m=65 -> c=2790
* Textbook RSA is deterministic and malleable -> use OAEP / PSS padding

**Suggested visual:** Formula card plus the 61/53 worked example.

**Speaker notes:** These are the exact steps from the syllabus. The small example is only for learning. In the real application the numbers are 2048 bits long and we always use padding.

## Slide 7: System Architecture

* GUI layer: Tkinter tabs, no crypto code
* Crypto layer: keys, OAEP, PSS, hybrid, toy RSA
* Utilities: validation and file handling
* Backend: Python 'cryptography' library (OpenSSL)

**Suggested visual:** Architecture diagram.

**Speaker notes:** The design separates the interface from the cryptography. That makes the crypto code easy to test without opening a window.

## Slide 8: Application Modules

* Dashboard - key status and shortcuts
* Key Management - generate, export, import (encrypted private key)
* Encryption / Decryption - RSA-OAEP, Base64, copy and save
* Digital Signature - sign, verify, tamper demos
* Hybrid Encryption - long messages, JSON envelope
* RSA Math and Help - toy calculator and guide

**Suggested visual:** Screenshot collage of the tabs (add your own).

**Speaker notes:** Every button works. The demo buttons deliberately use wrong keys or modified data to show how failure looks.

## Slide 9: Encryption and Decryption Workflow

* Recipient shares public key
* Sender encrypts with RSA-OAEP (max 190 bytes at 2048 bits)
* Output is Base64
* Recipient decrypts with private key
* Wrong key or modified data -> clear error

**Suggested visual:** Sequence diagram.

**Speaker notes:** OAEP adds randomness, so the same message gives a different ciphertext every time. If anything is wrong, decryption fails instead of giving wrong text.

## Slide 10: Digital Signatures

* Sign with private key (RSA-PSS + SHA-256)
* Verify with public key
* Proves integrity, authenticity, non-repudiation
* Does NOT hide the message
* Changing one character makes verification fail

**Suggested visual:** Signature sequence diagram.

**Speaker notes:** A signature is like a stamp only you can make. Anyone can check it, but nobody can forge it. The message itself stays readable.

## Slide 11: Hybrid Encryption

* RSA is slow and limited to 190 bytes
* Fresh AES-256 key + random 12-byte nonce per message
* AES-GCM encrypts and authenticates the text
* RSA-OAEP wraps the AES key
* Envelope: version, alg, wrapped_key, nonce, ciphertext (Base64 JSON)

**Suggested visual:** Hybrid sequence diagram.

**Speaker notes:** This is how real systems like TLS work in principle: public-key crypto protects a small key, and a fast symmetric cipher protects the data.

## Slide 12: Implementation Screenshots

* [Insert your own screenshots here]
* Dashboard, key generation, encryption, decryption, wrong-key demo, signature valid / tampered, hybrid, tests
* See screenshots/README.md for the list

**Suggested visual:** Four to six real screenshots from your computer.

**Speaker notes:** Show the application windows here. Take the screenshots yourself by running the program, as listed in the screenshots folder.

## Slide 13: Testing and Results

* 46 automated unit tests: keys, OAEP, PSS, hybrid, toy RSA
* Recorded run: 46 run, 46 passed, 0 failed (Python 3.13, Linux, cryptography 50.0.1)
* Covers wrong key, tampering, invalid input, Unicode, oversize message, bad key files
* GUI wiring checked with a fake Tkinter (30 checks); real GUI tried manually - [confirm before presenting]
* Re-run: python -m unittest discover -s tests -v

**Suggested visual:** Test result table or terminal screenshot (your own run).

**Speaker notes:** These are results from an actual run. Please run the tests again on your own laptop and quote the numbers you see on screen.

## Slide 14: Security Analysis and Limitations

* Strong: OAEP/PSS padding, 2048+ bit keys, AES-GCM, encrypted private keys
* No certificates: public keys are not authenticated
* No key rotation, revocation or forward secrecy
* Keys held in memory; no secure wipe
* RSA is vulnerable to future quantum computers
* Educational software, not independently audited

**Suggested visual:** Two-column table: protections vs limitations.

**Speaker notes:** I want to be honest about limits. The algorithms are standard and used correctly, but a complete system would also need certificates and key lifecycle management.

## Slide 15: Conclusion and Future Enhancements

* SecureText delivers confidentiality, integrity and authenticity with standard RSA
* Future: certificates / PKI, ECC and post-quantum options, file encryption, network messaging, key rotation
* Thank you - questions?

**Suggested visual:** Closing slide.

**Speaker notes:** To summarise, the project shows how RSA is used correctly in practice, and demonstrates failures as well as successes. Thank you.
