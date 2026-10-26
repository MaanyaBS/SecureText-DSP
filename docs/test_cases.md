# SecureText Test Cases and Results

**Environment of the recorded run:** Python 3.13.17 on Linux 6.18.44-fc-v153; cryptography 50.0.1

**Command:** `python -m unittest discover -s tests -v` (from the project root)

**Result of the recorded run:** 46 tests run, 46 passed, 0 failed. Raw output: `docs/test_results.txt`.

The Actual column says "Matches expected" only for tests that passed in that run. Re-run the command on your own machine and record your own output before the viva.

| Test ID | Description | Input | Expected output | Actual output | Status |
|---|---|---|---|---|---|
| T01 | RSA key generation (2048-bit) | generate_key_pair(2048) | 2048-bit modulus, e = 65537 | Matches expected (assertions passed) | PASS |
| T02 | Reject weak / invalid key size | 1024 and 'abc' | ValidationError raised | Matches expected (assertions passed) | PASS |
| T03 | RSA math relationships on a real key | p, q, n, e, d of a generated key | p*q = n; e*d = 1 mod lcm(p-1,q-1); (m^e)^d mod n = m | Matches expected (assertions passed) | PASS |
| T04 | Public key PEM export/import | export then load (bytes and str) | Loaded key equals original | Matches expected (assertions passed) | PASS |
| T05 | Private key export is encrypted and re-importable | password 'correct horse battery' | PEM header ENCRYPTED PRIVATE KEY; key restored | Matches expected (assertions passed) | PASS |
| T06 | Wrong password on private key import | wrong password | KeyError_ raised | Matches expected (assertions passed) | PASS |
| T07 | Short / empty export password | 'short' and '' | ValidationError raised | Matches expected (assertions passed) | PASS |
| T08 | Invalid key file content | garbage bytes, empty bytes | KeyError_ raised | Matches expected (assertions passed) | PASS |
| T09 | Public key file given as private key | public PEM + password | KeyError_ raised | Matches expected (assertions passed) | PASS |
| T10 | Private key file save and load via file handler | temp file in new sub-folder | File created; key restored | Matches expected (assertions passed) | PASS |
| T11 | Fingerprint stable and distinct | two different keys | Same key same fingerprint; different keys differ | Matches expected (assertions passed) | PASS |
| T12 | RSA-OAEP encrypt/decrypt round trip | 'Hello SecureText' | Original text recovered; plaintext not in ciphertext | Matches expected (assertions passed) | PASS |
| T13 | Ciphertext is Base64 of key-size bytes | 'abc' | 256 bytes after Base64 decode | Matches expected (assertions passed) | PASS |
| T14 | OAEP is randomised | same message encrypted twice | Different ciphertexts, both decrypt | Matches expected (assertions passed) | PASS |
| T15 | Decrypt with incorrect private key | key A encrypts, key B decrypts | DecryptionError raised | Matches expected (assertions passed) | PASS |
| T16 | Invalid ciphertext handling | non-Base64, short, all-zero blocks | DecryptionError raised | Matches expected (assertions passed) | PASS |
| T17 | Tampered ciphertext | one bit flipped | DecryptionError raised | Matches expected (assertions passed) | PASS |
| T18 | Oversized direct RSA message | 190 bytes OK, 191 bytes | Limit 190; 191 rejected with hint to use Hybrid tab | Matches expected (assertions passed) | PASS |
| T19 | Unicode message | Hindi, emoji, accented, Chinese text | Exact text recovered | Matches expected (assertions passed) | PASS |
| T20 | Limit counts UTF-8 bytes not characters | 96 x 'é' (192 bytes) | ValidationError raised | Matches expected (assertions passed) | PASS |
| T21 | Empty and invalid input | '', '   ', None, 123 | ValidationError raised | Matches expected (assertions passed) | PASS |
| T22 | Whitespace/newlines in pasted ciphertext | ciphertext wrapped at 64 columns | Decrypts correctly | Matches expected (assertions passed) | PASS |
| T23 | Signature creation and valid verification | 'Pay Alice 100' | 256-byte signature; verification True | Matches expected (assertions passed) | PASS |
| T24 | Verification after message modification | 'Pay Alice 900' with original signature | Verification False | Matches expected (assertions passed) | PASS |
| T25 | Verification with wrong public key | key B public key | Verification False | Matches expected (assertions passed) | PASS |
| T26 | PSS signatures are randomised | same message signed twice | Different signatures, both verify | Matches expected (assertions passed) | PASS |
| T27 | Corrupted / malformed signature | flipped byte, '###', short Base64 | Verification False | Matches expected (assertions passed) | PASS |
| T28 | Empty signature inputs | empty message / empty signature | ValidationError raised | Matches expected (assertions passed) | PASS |
| T29 | Unicode signature | Hindi + symbol text; text plus trailing space | Valid, then invalid after change | Matches expected (assertions passed) | PASS |
| T30 | Signature does not hide message | 'visible text' | Signature does not contain text (message stays public) | Matches expected (assertions passed) | PASS |
| T31 | Hybrid round trip, long message | ~12,000 characters | Original text recovered | Matches expected (assertions passed) | PASS |
| T32 | Hybrid envelope structure | 'hi' | 5 documented fields; nonce 12 B; wrapped key 256 B; ciphertext = 2 + 16 B tag | Matches expected (assertions passed) | PASS |
| T33 | Fresh AES key and nonce each time | same message twice | Different nonce, wrapped key and ciphertext | Matches expected (assertions passed) | PASS |
| T34 | Altered hybrid ciphertext detected | one bit flipped in ciphertext | DecryptionError (authentication failed) | Matches expected (assertions passed) | PASS |
| T35 | Altered GCM tag detected | last byte flipped | DecryptionError raised | Matches expected (assertions passed) | PASS |
| T36 | Altered nonce / wrapped key detected | one bit flipped each | DecryptionError raised | Matches expected (assertions passed) | PASS |
| T37 | Unsupported envelope version | version = 2 | DecryptionError raised | Matches expected (assertions passed) | PASS |
| T38 | Hybrid with wrong private key | key A encrypts, key B decrypts | DecryptionError raised | Matches expected (assertions passed) | PASS |
| T39 | Malformed envelopes | bad Base64, non-JSON, list, missing fields, short nonce | DecryptionError raised | Matches expected (assertions passed) | PASS |
| T40 | Unicode hybrid | Tamil, emoji, Japanese text | Exact text recovered | Matches expected (assertions passed) | PASS |
| T41 | Hybrid empty input | '', '   ', None | ValidationError raised | Matches expected (assertions passed) | PASS |
| T42 | Direct-RSA tamper demo helper | tamper_ciphertext then decrypt | DecryptionError raised | Matches expected (assertions passed) | PASS |
| T43 | Hybrid tamper demo helper | tamper_envelope then decrypt | DecryptionError raised | Matches expected (assertions passed) | PASS |
| T44 | Toy RSA textbook example | p=61, q=53, e=17, m=65 | n=3233, phi=3120, d=2753, c=2790, recovered 65 | Matches expected (assertions passed) | PASS |
| T45 | Toy RSA invalid parameters | non-prime p, p=q, bad e, m too big, non-int | ToyRSAError raised | Matches expected (assertions passed) | PASS |
| T46 | Primality helper | numbers 0..19 | 2,3,5,7,11,13,17,19 | Matches expected (assertions passed) | PASS |

## Not covered by automated tests

* **Tkinter GUI rendering and clicks.** The sandbox used for development had no Tkinter or display. `tests/gui_logic_check.py` drives every GUI handler against a *fake* tkinter module to check the wiring to the crypto layer (30 checks), but it does not render real windows. Run `python main.py` and walk through `docs/demo_script.md` yourself before submission.
* Performance, concurrency and cross-platform behaviour (only Linux was used).
