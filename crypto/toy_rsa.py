"""Textbook RSA with tiny numbers - FOR LEARNING ONLY, NEVER FOR REAL DATA.

This module shows the arithmetic behind RSA step by step. It uses no padding and
tiny primes, so it is completely insecure. The real application uses the
'cryptography' package with RSA-OAEP / RSA-PSS and 2048-bit or larger keys.
"""

from math import gcd

MAX_PRIME = 10**6


class ToyRSAError(ValueError):
    """Raised for invalid toy-RSA parameters."""


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def toy_rsa_walkthrough(p, q, e, m):
    """Return a list of human-readable steps for a toy RSA computation."""
    for name, value in (("p", p), ("q", q), ("e", e), ("m", m)):
        if not isinstance(value, int):
            raise ToyRSAError(f"{name} must be a whole number.")
    if not (is_prime(p) and is_prime(q)):
        raise ToyRSAError("p and q must both be prime numbers.")
    if p == q:
        raise ToyRSAError("p and q must be different primes.")
    if p > MAX_PRIME or q > MAX_PRIME:
        raise ToyRSAError(f"Keep p and q below {MAX_PRIME:,} for this demo.")
    n = p * q
    phi = (p - 1) * (q - 1)
    if not (1 < e < phi):
        raise ToyRSAError(f"e must satisfy 1 < e < phi(n) = {phi}.")
    if gcd(e, phi) != 1:
        raise ToyRSAError(f"e = {e} is not coprime with phi(n) = {phi}; choose another e.")
    if not (0 <= m < n):
        raise ToyRSAError(f"The message number m must satisfy 0 <= m < n = {n}.")
    d = pow(e, -1, phi)
    c = pow(m, e, n)
    back = pow(c, d, n)
    steps = [
        f"Step 1: p = {p}, q = {q}  (both prime)",
        f"Step 2: n = p x q = {n}",
        f"Step 3: phi(n) = (p-1)(q-1) = {p - 1} x {q - 1} = {phi}",
        f"Step 4: e = {e}, gcd(e, phi(n)) = 1  OK",
        f"Step 5: d = e^-1 mod phi(n) = {d}   (check: e x d mod phi = {(e * d) % phi})",
        f"Public key  = (n={n}, e={e})",
        f"Private key = (n={n}, d={d})",
        f"Step 6: encrypt  c = m^e mod n = {m}^{e} mod {n} = {c}",
        f"Step 7: decrypt  m = c^d mod n = {c}^{d} mod {n} = {back}",
        f"Result: recovered message = {back}  ({'matches' if back == m else 'DOES NOT match'} the original)",
        f"Warning: textbook RSA is deterministic - encrypting {m} again always gives {c}.",
    ]
    return steps
