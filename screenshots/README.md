# Screenshots

**No screenshots are included.** The development environment had no display or Tkinter, so the real window could not be opened, and fabricated screenshots would be dishonest.

Take these on your own computer after running `python main.py` (Windows: `Win + Shift + S`) and save them here with these names:

| File name | What to capture |
|---|---|
| 01_dashboard.png | Dashboard after generating keys |
| 02_key_management.png | Key Management tab with public key PEM shown |
| 03_encryption.png | Encryption tab with Base64 ciphertext |
| 04_decryption_success.png | Decryption tab showing recovered text |
| 05_wrong_key_demo.png | Decryption tab after "Try Wrong Key" |
| 06_signature_valid.png | Digital Signature tab with VALID result |
| 07_signature_tampered.png | Result after "Tamper Message & Verify" |
| 08_hybrid.png | Hybrid tab with envelope and decrypted text |
| 09_rsa_math.png | RSA Math tab with the toy example |
| 10_tests.png | Terminal showing `python -m unittest discover -s tests -v` ending in OK |

Then insert them into `docs/project_report.md` (section 33) and the presentation (slide 12) and re-export the PDF.
