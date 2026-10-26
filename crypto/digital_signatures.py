"""RSA-PSS (SHA-256) digital signatures."""

import base64
import binascii

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from utils.validation import ValidationError, require_text


def pss_padding():
    return padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.DIGEST_LENGTH,
    )


def sign_message(message, private_key):
    """Sign ``message`` (str) and return the signature as Base64 text."""
    require_text(message, "Message")
    signature = private_key.sign(message.encode("utf-8"), pss_padding(), hashes.SHA256())
    return base64.b64encode(signature).decode("ascii")


def verify_signature(message, signature_b64, public_key):
    """Return True if the signature is valid, False otherwise.

    Malformed Base64 or a wrong-length signature also returns False; only
    empty inputs raise ValidationError.
    """
    require_text(message, "Message")
    if not isinstance(signature_b64, str) or not signature_b64.strip():
        raise ValidationError("Signature must not be empty.")
    try:
        raw = base64.b64decode("".join(signature_b64.split()), validate=True)
    except (binascii.Error, ValueError):
        return False
    try:
        public_key.verify(raw, message.encode("utf-8"), pss_padding(), hashes.SHA256())
        return True
    except InvalidSignature:
        return False
    except ValueError:
        return False
