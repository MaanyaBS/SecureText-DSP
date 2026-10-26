"""RSA key generation, serialization and loading.

Private keys are exported as PKCS#8 PEM encrypted with a user password
(BestAvailableEncryption). Public keys are exported as SubjectPublicKeyInfo PEM.
"""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from utils.validation import ValidationError, require_key_size, require_password

PUBLIC_EXPONENT = 65537
DEFAULT_KEY_SIZE = 2048


class KeyError_(Exception):
    """Raised when a key file cannot be parsed or decrypted."""


def generate_key_pair(key_size=DEFAULT_KEY_SIZE):
    """Generate an RSA private key (the public key is derived from it)."""
    key_size = require_key_size(key_size)
    return rsa.generate_private_key(public_exponent=PUBLIC_EXPONENT, key_size=key_size)


def export_public_key_pem(public_key):
    """Return the public key as PEM bytes."""
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def export_private_key_pem(private_key, password):
    """Return the private key as password-protected PKCS#8 PEM bytes."""
    password = require_password(password)
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(
            password.encode("utf-8")
        ),
    )


def load_public_key_pem(data):
    """Load a PEM public key (str or bytes). Raises KeyError_ on failure."""
    data = _to_bytes(data)
    try:
        key = serialization.load_pem_public_key(data)
    except Exception:
        raise KeyError_("Not a valid PEM public key.")
    if not isinstance(key, rsa.RSAPublicKey):
        raise KeyError_("The key is not an RSA public key.")
    return key


def load_private_key_pem(data, password):
    """Load an encrypted PEM private key. Raises KeyError_ on failure."""
    data = _to_bytes(data)
    if not isinstance(password, str) or not password:
        raise KeyError_("A password is required to open a private key.")
    try:
        key = serialization.load_pem_private_key(data, password=password.encode("utf-8"))
    except TypeError:
        raise KeyError_("This key file is not password protected or is malformed.")
    except ValueError:
        raise KeyError_("Wrong password or corrupted private key file.")
    except Exception:
        raise KeyError_("Not a valid PEM private key.")
    if not isinstance(key, rsa.RSAPrivateKey):
        raise KeyError_("The key is not an RSA private key.")
    return key


def public_key_from_private(private_key):
    return private_key.public_key()


def key_size_bits(key):
    return key.key_size


def public_numbers(key):
    """Return (n, e) for a public or private key."""
    pub = key.public_key() if hasattr(key, "public_key") else key
    nums = pub.public_numbers()
    return nums.n, nums.e


def private_numbers(private_key):
    """Return (p, q, d). Only for the educational display - never log these."""
    nums = private_key.private_numbers()
    return nums.p, nums.q, nums.d


def fingerprint(public_key):
    """SHA-256 fingerprint (hex, colon separated) of the DER public key."""
    der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    digest = hashes.Hash(hashes.SHA256())
    digest.update(der)
    raw = digest.finalize().hex()
    return ":".join(raw[i : i + 2] for i in range(0, len(raw), 2))


def _to_bytes(data):
    if isinstance(data, str):
        return data.encode("utf-8")
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    raise KeyError_("Key data must be text or bytes.")
