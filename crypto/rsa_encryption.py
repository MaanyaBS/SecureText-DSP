"""Direct RSA-OAEP (SHA-256) encryption of short messages."""

import base64
import binascii

from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from utils.validation import ValidationError, require_text

HASH_LEN = 32  # SHA-256 digest size in bytes


class DecryptionError(Exception):
    """Raised when RSA decryption fails (wrong key, corrupted data, etc.)."""


def oaep_padding():
    return padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    )


def max_message_bytes(public_key):
    """Largest plaintext (bytes) RSA-OAEP-SHA256 can encrypt: k - 2*hLen - 2."""
    k = (public_key.key_size + 7) // 8
    return k - 2 * HASH_LEN - 2


def encrypt_message(message, public_key):
    """Encrypt ``message`` (str) with RSA-OAEP and return Base64 text."""
    require_text(message, "Message")
    data = message.encode("utf-8")
    limit = max_message_bytes(public_key)
    if len(data) > limit:
        raise ValidationError(
            f"Message is {len(data)} bytes but direct RSA-OAEP with a "
            f"{public_key.key_size}-bit key allows at most {limit} bytes. "
            "Use the Hybrid Encryption tab for longer messages."
        )
    ciphertext = public_key.encrypt(data, oaep_padding())
    return base64.b64encode(ciphertext).decode("ascii")


def tamper_ciphertext(ciphertext_b64):
    """Demo helper: flip one bit of the ciphertext and return new Base64 text."""
    try:
        raw = bytearray(base64.b64decode("".join(ciphertext_b64.split()), validate=True))
    except (binascii.Error, ValueError, AttributeError):
        raise DecryptionError("Ciphertext is not valid Base64.")
    if not raw:
        raise ValidationError("Ciphertext must not be empty.")
    raw[len(raw) // 2] ^= 0x01
    return base64.b64encode(bytes(raw)).decode("ascii")


def decrypt_message(ciphertext_b64, private_key):
    """Decrypt Base64 RSA-OAEP ciphertext and return the plaintext string."""
    if not isinstance(ciphertext_b64, str) or not ciphertext_b64.strip():
        raise ValidationError("Ciphertext must not be empty.")
    try:
        raw = base64.b64decode("".join(ciphertext_b64.split()), validate=True)
    except (binascii.Error, ValueError):
        raise DecryptionError("Ciphertext is not valid Base64.")
    expected = (private_key.key_size + 7) // 8
    if len(raw) != expected:
        raise DecryptionError(
            f"Ciphertext length is {len(raw)} bytes; this key expects {expected} bytes."
        )
    try:
        plain = private_key.decrypt(raw, oaep_padding())
    except (ValueError, InvalidKey):
        raise DecryptionError(
            "Decryption failed: wrong private key or corrupted ciphertext."
        )
    try:
        return plain.decode("utf-8")
    except UnicodeDecodeError:
        raise DecryptionError("Decrypted bytes are not valid UTF-8 text.")
