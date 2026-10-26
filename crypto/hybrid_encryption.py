"""Hybrid encryption: AES-256-GCM for the message, RSA-OAEP for the AES key.

Envelope format (JSON, UTF-8, then Base64 for transport)::

    {
      "version": 1,
      "alg": "RSA-OAEP-SHA256+AES-256-GCM",
      "wrapped_key": "<base64 RSA-OAEP encrypted 32-byte AES key>",
      "nonce": "<base64 12-byte random GCM nonce>",
      "ciphertext": "<base64 AES-GCM ciphertext followed by 16-byte tag>"
    }

The envelope header (version and alg) is passed to AES-GCM as associated data
so it is authenticated as well.
"""

import base64
import binascii
import json
import os

from cryptography.exceptions import InvalidKey, InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from crypto.rsa_encryption import DecryptionError, oaep_padding
from utils.validation import ValidationError, require_text

VERSION = 1
ALGORITHM = "RSA-OAEP-SHA256+AES-256-GCM"
AES_KEY_BYTES = 32
NONCE_BYTES = 12
_AAD = f"{VERSION}|{ALGORITHM}".encode("ascii")


def encrypt_hybrid(message, public_key):
    """Encrypt a message of any length. Returns the Base64 envelope string."""
    require_text(message, "Message")
    aes_key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(NONCE_BYTES)  # fresh random nonce, key is also fresh
    ciphertext = AESGCM(aes_key).encrypt(nonce, message.encode("utf-8"), _AAD)
    wrapped = public_key.encrypt(aes_key, oaep_padding())
    envelope = {
        "version": VERSION,
        "alg": ALGORITHM,
        "wrapped_key": _b64(wrapped),
        "nonce": _b64(nonce),
        "ciphertext": _b64(ciphertext),
    }
    blob = json.dumps(envelope, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(blob).decode("ascii")


def decrypt_hybrid(envelope_b64, private_key):
    """Decrypt an envelope produced by :func:`encrypt_hybrid`."""
    if not isinstance(envelope_b64, str) or not envelope_b64.strip():
        raise ValidationError("Envelope must not be empty.")
    try:
        blob = base64.b64decode("".join(envelope_b64.split()), validate=True)
        envelope = json.loads(blob.decode("utf-8"))
        if not isinstance(envelope, dict):
            raise ValueError
        if envelope.get("version") != VERSION or envelope.get("alg") != ALGORITHM:
            raise DecryptionError("Unsupported envelope version or algorithm.")
        wrapped = _unb64(envelope["wrapped_key"])
        nonce = _unb64(envelope["nonce"])
        ciphertext = _unb64(envelope["ciphertext"])
    except DecryptionError:
        raise
    except (binascii.Error, ValueError, KeyError, TypeError, UnicodeDecodeError):
        raise DecryptionError("Envelope is malformed (not valid Base64/JSON).")

    if len(nonce) != NONCE_BYTES:
        raise DecryptionError("Envelope nonce has the wrong length.")

    try:
        aes_key = private_key.decrypt(wrapped, oaep_padding())
    except (ValueError, InvalidKey):
        raise DecryptionError(
            "Could not unwrap the AES key: wrong private key or altered envelope."
        )
    if len(aes_key) != AES_KEY_BYTES:
        raise DecryptionError("Unwrapped AES key has an unexpected length.")

    try:
        plain = AESGCM(aes_key).decrypt(nonce, ciphertext, _AAD)
    except InvalidTag:
        raise DecryptionError(
            "Authentication failed: the ciphertext was modified or the key is wrong."
        )
    try:
        return plain.decode("utf-8")
    except UnicodeDecodeError:
        raise DecryptionError("Decrypted bytes are not valid UTF-8 text.")


def tamper_envelope(envelope_b64):
    """Demo helper: flip one bit inside the AES-GCM ciphertext of an envelope."""
    try:
        blob = base64.b64decode("".join(envelope_b64.split()), validate=True)
        envelope = json.loads(blob.decode("utf-8"))
        raw = bytearray(_unb64(envelope["ciphertext"]))
        raw[0] ^= 0x01
        envelope["ciphertext"] = _b64(bytes(raw))
    except (binascii.Error, ValueError, KeyError, TypeError, IndexError,
            AttributeError, UnicodeDecodeError):
        raise DecryptionError("Envelope is malformed (not valid Base64/JSON).")
    out = json.dumps(envelope, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(out).decode("ascii")


def _b64(data):
    return base64.b64encode(data).decode("ascii")


def _unb64(text):
    return base64.b64decode(text, validate=True)
