# Viva Questions and Answers

Each answer gives a **short answer** first, then **more detail** where the examiner is likely to dig deeper.

## A. Cryptography basics

**1. What is cryptography? What are the security goals?**
Hiding and protecting information. Goals: confidentiality, integrity, authenticity (and non-repudiation, availability).
*More:* In SecureText, encryption gives confidentiality, GCM tag and signatures give integrity, signatures give authenticity and non-repudiation.

**2. Symmetric vs asymmetric cryptography?**
Symmetric uses one shared key (AES); asymmetric uses a public/private key pair (RSA).
*More:* Symmetric is fast but needs a secure way to share the key. Asymmetric solves distribution but is slow and size-limited, so we combine both in hybrid encryption.

**3. What are the requirements of a public-key cryptosystem?**
Easy key-pair generation; easy encrypt/decrypt with the right keys; infeasible to derive the private key from the public key; the operations invert each other.

**4. What are applications of public-key cryptography?**
Encryption, digital signatures, key exchange (also certificates, TLS, secure email, code signing).

**5. Who invented RSA and when?**
Rivest, Shamir and Adleman, published in 1978 (Communications of the ACM).

## B. RSA mathematics

**6. Explain RSA key generation.**
Pick primes p, q; n = pq; φ(n) = (p−1)(q−1); choose e coprime to φ(n); d = e⁻¹ mod φ(n). Public (n, e), private d.
*More:* Library implementations compute d modulo the Carmichael value λ(n) = lcm(p−1, q−1), which is equivalent for decryption. Test T03 verifies e·d ≡ 1 mod lcm(p−1, q−1).

**7. What is Euler's totient function φ(n)?**
The count of integers from 1 to n that are coprime to n. For n = pq with distinct primes, φ(n) = (p−1)(q−1).

**8. Why is e = 65537?**
It is prime, so coprime to φ(n) almost always; it has only two 1-bits (2¹⁶ + 1), so public operations need just 17 squarings and 1 multiplication, and it avoids small-exponent attacks.

**9. How does decryption work mathematically?**
c = mᵉ mod n, so cᵈ = m^(ed) = m^(1 + kφ(n)) ≡ m (mod n) by Euler's theorem.
*More:* Euler's theorem needs gcd(m, n) = 1; RSA still works otherwise via the Chinese Remainder Theorem.

**10. What is modular exponentiation and why is it needed?**
Computing a^b mod n efficiently by square-and-multiply. Without it, 2048-bit exponents would be impossible to compute.

**11. Why is RSA secure?**
Recovering the private key from (n, e) requires factoring n. No known classical algorithm does this for 2048-bit n in practical time.
*More:* It is an assumption, not a proof. Quantum computers (Shor's algorithm) would break it. Bad implementations (weak randomness, no padding) are broken without factoring.

**12. What are the computational aspects of RSA?**
Key generation needs primality testing of large random numbers; encryption is cheap with small e; decryption is the costly step (mitigated using CRT); RSA is roughly orders of magnitude slower than AES.

**13. What is the toy example in your project?**
p=61, q=53, e=17, d=2753, n=3233; m=65 encrypts to 2790. It uses tiny primes purely to show the arithmetic and is insecure.

## C. Padding, OAEP and PSS

**14. Why is textbook RSA unsafe?**
Deterministic, malleable, and small messages can be recovered by taking roots. Hence padding.

**15. What is RSA-OAEP?**
Optimal Asymmetric Encryption Padding (RFC 8017). Adds a random seed and hash-based masking (MGF1) before RSA.
*More:* Security: IND-CCA2 under the RSA assumption in the random-oracle model. Uses SHA-256 here.

**16. Why does the same message give different ciphertexts?**
OAEP uses a fresh random seed each time. Test T14 shows this.

**17. What is the maximum message size, and why?**
k − 2·hLen − 2 = 256 − 64 − 2 = 190 bytes for 2048-bit RSA with SHA-256. The remaining bytes are padding overhead. Test T18.

**18. What is RSA-PSS?**
Probabilistic Signature Scheme: hash the message, add random salt, encode, then sign with the private key. Preferred over PKCS#1 v1.5 signatures because it has a security proof.

**19. Why do two signatures of the same message differ?**
The random salt. Both verify. Test T26.

**20. Why SHA-256?**
A secure 256-bit hash from FIPS 180-4; collision-resistant and widely supported. MD5 and SHA-1 are broken.

## D. Signatures, integrity, authenticity

**21. How does a digital signature work?**
Sign with private key over the message hash; verify with the public key.

**22. Do signatures provide confidentiality?**
No. The message remains readable. Test T30. Combine with encryption if both are needed.

**23. Difference between encryption, hashing and signature?**
Encryption is reversible and keyed; hash is one-way and keyless; signature binds a message to a private-key holder.

**24. What happens if one character of a signed message changes?**
Verification fails because the hash differs. Test T24 and the GUI tamper demo.

**25. Confidentiality vs integrity vs authenticity?**
Confidentiality: only intended readers. Integrity: not modified. Authenticity: it came from the claimed sender.

## E. AES-GCM and hybrid encryption

**26. What is hybrid encryption and why use it?**
AES encrypts the data; RSA encrypts only the AES key. Fast, no length limit.

**27. What is AES-GCM?**
Authenticated encryption: counter-mode confidentiality plus a 128-bit authentication tag (NIST SP 800-38D).
*More:* Reusing a nonce with the same key breaks GCM badly; we use a fresh key and a random 96-bit nonce per message.

**28. How do you detect tampering in hybrid mode?**
GCM verifies the tag during decryption; any modified ciphertext, tag, nonce, or header raises an error (tests T34 to T37).

**29. What is in your envelope?**
JSON with version, alg, wrapped_key, nonce, ciphertext, Base64-encoded.

**30. Why is a nonce safe here?**
New AES key for every message, so a (key, nonce) pair is never reused.

## F. Key management

**31. How are private keys stored?**
Encrypted PKCS#8 PEM, protected by a password (derived key + AES via the library's best available encryption).

**32. What if the user forgets the password?**
The key cannot be recovered; generate a new pair.

**33. How do you share public keys? Can they be trusted?**
Export the PEM and compare the SHA-256 fingerprint through another channel. Without certificates a man-in-the-middle could swap keys: a known limitation.

**34. What is key size policy?**
Minimum 2048 bits enforced in code; 3072 and 4096 optional (test T02).

**35. Key lifecycle?**
Generation, storage, distribution, use, rotation, revocation, destruction (NIST SP 800-57). SecureText implements the first four; the others are future work.

## G. Wrong-key and tamper behaviour

**36. What happens when you decrypt with the wrong key?**
OAEP validation fails and an error is shown; no garbage plaintext is produced. Tests T15, T38.

**37. Why not return random text instead of an error?**
OAEP integrity checks make failure explicit. (Implementations must avoid revealing *why* it failed to remote attackers; this offline app shows a generic reason.)

## H. Implementation and testing

**38. Which library and why not write RSA yourself?**
Python `cryptography` (OpenSSL backend): audited, constant-time operations. Custom crypto is unsafe.

**39. Describe the architecture.**
Three layers: GUI (Tkinter), crypto (five modules), utils (validation, files). The GUI contains no crypto logic.

**40. How did you test?**
46 unittest cases covering keys, OAEP, PSS, hybrid, tamper, unicode, empty input; plus a fake-Tkinter check of GUI handlers.

**41. Did you test the GUI?**
Honest answer: the handlers were exercised against a fake Tkinter module, and I ran the real GUI on my machine following the demo script. *(Only say the second part if you did.)*

**42. How do you handle Unicode?**
Text is encoded as UTF-8 before encryption; the size limit counts bytes, not characters (tests T19, T20).

## I. Security limitations and real-world use

**43. Limitations of the project?**
No certificates, no key revocation, keys in memory, no forward secrecy, no secure memory wipe, not audited, vulnerable to quantum attacks in future.

**44. Is this like HTTPS/TLS?**
TLS also uses public-key crypto for authentication/key exchange and symmetric encryption for data, similar to hybrid encryption, but with certificates, handshakes and forward secrecy.

**45. Real-world uses of RSA?**
TLS certificates, code signing, email (S/MIME, PGP), SSH keys, JWT signing.

**46. What would you improve?**
Certificates, key rotation, ECC/ECDH, post-quantum algorithms, file encryption, a messaging network layer.

---

# Questions the examiner may ask to check whether I actually understand the project

**Q. Show me where in the code the 190-byte limit comes from.**
`max_message_bytes()` in `crypto/rsa_encryption.py` returns `k − 2·32 − 2` with `k = (key_size + 7) // 8`. For 2048 bits that is 190.

**Q. You said RSA is secure. Is it because it is "a hard maths problem"?**
Only partly. The underlying assumption is the difficulty of factoring (or the RSA problem). Real security also depends on correct padding, good randomness and key handling. Textbook RSA with the same maths is insecure.

**Q. Did you implement RSA yourself?**
No. I used the `cryptography` library for real operations. I wrote a tiny textbook RSA (`toy_rsa.py`) only to explain the maths, and it is labelled insecure.

**Q. Why does your wrong-key demo fail instead of giving wrong text?**
OAEP decoding checks structure and a hash; with the wrong key the check fails with overwhelming probability.

**Q. Does a valid signature mean the message is secret or the sender is who they claim?**
No to secrecy. It proves the holder of the matching private key signed it. Whether that key belongs to a particular person depends on how I obtained the public key, which SecureText cannot verify.

**Q. Is the AES key reused?**
No. A new key and nonce are generated for each message.

**Q. What would break if you reused a nonce with the same AES key?**
GCM would leak plaintext relationships and allow forgeries. It does not happen here because keys are never reused.

**Q. Which parts did you not test?**
Real GUI rendering across machines, performance, and security review by third parties. I tested the logic with automated tests and tried the GUI manually *(only if you did)*.

**Q. Why is d computed modulo something other than φ(n) in the library?**
Libraries use the Carmichael function λ(n); the resulting d works identically for decryption.

**Q. Can an attacker who has the ciphertext and the public key decrypt it?**
Not without factoring n or breaking OAEP. They can encrypt guesses but OAEP randomisation prevents confirming them by comparing ciphertexts.
