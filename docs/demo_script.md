# Live Demonstration Script (about 6 minutes)

Prepare: terminal open in the SecureText folder with the venv activated. Do a dry run first. Use a second terminal tab for the tests.

## 0:00 - Launch (20 s)
**Do:** `python main.py`
**Say:** "SecureText is an offline desktop app for secure messaging using RSA. It has tabs for keys, encryption, decryption, signatures, hybrid encryption and RSA maths."
**Expect:** Window opens on the Dashboard showing "No own key pair loaded".

## 0:20 - Generate keys (30 s)
**Do:** Key Management tab → size 2048 → **Generate Key Pair**.
**Expect:** Status "Generated a new 2048-bit RSA key pair"; PEM public key and fingerprint appear.
**Say:** "The public key can be shared. The private key stays here and can be exported only with a password."

## 0:50 - Encrypt (40 s)
**Do:** Encryption tab. Type: `Meet me at the library at 5 PM`. Click **Encrypt**.
**Expect:** Base64 text appears; byte counter shows the message size out of 190.
**Say:** "The message was encrypted with the public key using RSA-OAEP with SHA-256. The ciphertext looks random and differs every time because OAEP adds a random seed."
**Do:** Click **Encrypt** again to show a different ciphertext.

## 1:30 - Decrypt (30 s)
**Do:** **Send to Decryption tab** → **Decrypt**.
**Expect:** Original text; green "Decryption successful".
**Say:** "Only the matching private key can undo it."

## 2:00 - Wrong key and tampering (45 s)
**Do:** Click **Demo: Try Wrong Key**, then **Demo: Tamper Ciphertext**.
**Expect:** Green messages explaining that decryption failed as expected.
**Say:** "A different key, or even one flipped bit, makes decryption fail. We get an error, not wrong text."

## 2:45 - Sign and verify (50 s)
**Do:** Digital Signature tab. Message: `Pay Alice 100 rupees`. Click **Sign Message**, then **Verify Signature**.
**Expect:** "VALID".
**Do:** Click **Demo: Tamper Message & Verify**.
**Expect:** Message becomes "... (edited)" and verification FAILS as expected. Then **Demo: Verify With Wrong Key** also fails.
**Say:** "A signature uses the private key and is verified with the public key. It proves integrity and who signed, but does not hide the message."

## 3:35 - Hybrid (50 s)
**Do:** Hybrid Encryption tab → **Insert Sample Long Text** → **Encrypt**. Then **Move Output to Input** → **Decrypt**.
**Expect:** Long JSON envelope (Base64), then the original text.
**Do:** Encrypt again, **Move Output to Input**, click **Demo: Tamper Envelope & Decrypt**.
**Expect:** Authentication failure message.
**Say:** "RSA can only encrypt 190 bytes, so a fresh AES-256-GCM key encrypts the text and RSA wraps that key. GCM detects any change."

## 4:25 - RSA maths (25 s)
**Do:** RSA Math tab → **Run toy RSA** (61, 53, 17, 65).
**Expect:** n = 3233, d = 2753, c = 2790.
**Say:** "This tiny example is only to show the arithmetic. The real app uses 2048-bit keys with padding."

## 4:50 - Automated tests (35 s)
**Do:** In the terminal: `python -m unittest discover -s tests -v`
**Expect:** All tests listed `ok`, ending with `OK`. (Read the real count on your screen.)
**Say:** "These tests cover key generation, encryption, wrong keys, tampering, unicode, empty input and oversized messages."

## 5:25 - Limitations (35 s)
**Say:** "This is an educational project. Public keys are not authenticated with certificates, so fingerprints must be compared by hand. There is no key rotation or revocation, keys sit in memory, and RSA would be broken by large quantum computers. Future work: certificates, elliptic-curve and post-quantum options, file encryption."

## Sample messages
* Short: `Meet me at the library at 5 PM`
* Signed: `Pay Alice 100 rupees`
* Unicode: `नमस्ते 🌍`
* Long: use **Insert Sample Long Text**.

## If something goes wrong
* Window does not open → check Tkinter (README troubleshooting).
* Nothing happens on Encrypt → generate keys first (a warning appears).
* Run out of time → skip RSA Math and the tamper demos, keep the encrypt/decrypt and sign/verify flow.
