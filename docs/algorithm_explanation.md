# Algorithm Explanation

## 1. Public-key cryptography in one paragraph

Symmetric ciphers (AES) use one shared secret key, which raises the key-distribution problem. Public-key cryptography (Diffie and Hellman, 1976) gives each user a key pair: a **public key** that anyone may know and a **private key** that stays secret. Requirements of a public-key cryptosystem: generating a key pair is easy; encrypting with the public key and decrypting with the private key is easy; deriving the private key from the public key is computationally infeasible; and the two operations invert each other. Applications: encryption/decryption, digital signatures, and key exchange.

## 2. RSA

### Key generation

1. Choose two large distinct primes **p** and **q**.
2. **n = p × q** (the modulus, public).
3. **φ(n) = (p − 1)(q − 1)** (Euler's totient, secret).
4. Choose public exponent **e**, 1 < e < φ(n), gcd(e, φ(n)) = 1. SecureText uses e = 65537.
5. Compute private exponent **d** with **d·e ≡ 1 (mod φ(n))**.
6. Public key (n, e); private key (n, d), stored with p and q.

### Worked toy example (insecure, for understanding only)

p = 61, q = 53 → n = 3233; φ(n) = 60 × 52 = 3120; e = 17; d = 2753 (since 17 × 2753 = 46801 = 15 × 3120 + 1).
Encrypt m = 65: c = 65¹⁷ mod 3233 = 2790. Decrypt: 2790²⁷⁵³ mod 3233 = 65.
The "RSA Math" tab reproduces this, and test T44 checks it.

### Modular exponentiation

Computing m^e mod n by multiplying e times is impossible for large e. Square-and-multiply processes the bits of the exponent: square at each bit, multiply when the bit is 1, reducing mod n each step. A 2048-bit exponent needs about 2048 squarings plus about 1024 multiplications.

### Why security holds, and its limits

Anyone knows n and e; finding d requires φ(n), which requires factoring n. No known classical algorithm factors a 2048-bit modulus in practical time. This is a belief, not a proof. A large quantum computer running Shor's algorithm would break RSA.

### Why textbook RSA is unsafe

* **Deterministic:** same message → same ciphertext, so guesses can be confirmed.
* **Malleable:** E(m1)·E(m2) mod n = E(m1·m2 mod n).
* **Small-message weakness:** if m^e < n, an ordinary e-th root recovers m.

Secure systems add randomised padding. SecureText uses **RSA-OAEP** (encryption) and **RSA-PSS** (signatures) from RFC 8017, never custom padding.

## 3. RSA-OAEP with SHA-256

OAEP masks the message with a random seed through a mask generation function (MGF1-SHA-256) before the RSA operation, so encrypting the same text twice gives different ciphertexts and chosen-ciphertext attacks are mitigated. Capacity: **k − 2·hLen − 2** bytes, with k = key bytes and hLen = 32. For 2048-bit keys: 256 − 64 − 2 = **190 bytes**. Longer data needs hybrid encryption.

## 4. RSA-PSS signatures with SHA-256

Signing: hash the message with SHA-256, apply PSS encoding with a random salt (32 bytes here), then apply the RSA private-key operation. Verification: apply the public-key operation and check the PSS encoding against the hash of the received message. Because of the random salt, signing the same message twice gives different valid signatures. A signature gives **authenticity, integrity and non-repudiation** but **no confidentiality**.

## 5. Encryption vs hashing vs signature

| | Encryption | Hash (SHA-256) | Digital signature |
|---|---|---|---|
| Key | public / private or shared | none | private to sign, public to verify |
| Reversible | yes | no | verify only |
| Output size | about message size | fixed 256 bits | key size |
| Provides | confidentiality | integrity check (no origin) | authenticity + integrity + non-repudiation |

## 6. Hybrid encryption (AES-256-GCM + RSA-OAEP)

1. Generate a fresh random 256-bit AES key and a random 96-bit nonce for every message.
2. AES-GCM encrypts the message and produces a 128-bit authentication tag. The header `1|RSA-OAEP-SHA256+AES-256-GCM` is passed as associated data so it is authenticated.
3. RSA-OAEP wraps the AES key with the recipient's public key.
4. Output is Base64 of this JSON:

```json
{"version":1,"alg":"RSA-OAEP-SHA256+AES-256-GCM",
 "wrapped_key":"<base64>","nonce":"<base64, 12 bytes>","ciphertext":"<base64, ciphertext + 16-byte tag>"}
```

5. Decryption unwraps the AES key with the private key, then AES-GCM decrypts and verifies the tag; any change to ciphertext, tag, nonce or header raises an authentication error.

Why hybrid: RSA is slow and size-limited; AES is fast and handles any length. A fresh key per message means a random 96-bit nonce is safe (never reused with the same key).

## 7. Key management in SecureText

* **Generation:** the `cryptography` library, OS randomness, minimum 2048 bits.
* **Storage:** private key exported as PKCS#8 PEM encrypted with a user password (`BestAvailableEncryption`); file mode set to 0600 where supported. The password is never stored, logged or hardcoded.
* **Distribution:** public key PEM; fingerprint (SHA-256 of DER) shown for out-of-band comparison.
* **Usage:** private key used only to decrypt and sign; keys held in memory only.
* **Not provided:** certificates/PKI, key rotation, revocation, secure memory wiping. See the report's limitations.
