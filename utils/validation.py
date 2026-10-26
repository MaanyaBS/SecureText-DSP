"""Input validation helpers shared by the GUI and the crypto layer."""

MIN_PASSWORD_LENGTH = 8


class ValidationError(ValueError):
    """Raised when user supplied input is missing or invalid."""


def require_text(value, field_name="Message"):
    """Return ``value`` if it is a non-empty (non-whitespace) string."""
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be text.")
    if not value.strip():
        raise ValidationError(f"{field_name} must not be empty.")
    return value


def require_password(password, confirm=None):
    """Validate a key-protection password.

    The password is never logged or echoed in error messages.
    """
    if not isinstance(password, str) or not password:
        raise ValidationError("A password is required.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."
        )
    if confirm is not None and password != confirm:
        raise ValidationError("Password and confirmation do not match.")
    return password


def require_key_size(bits):
    """Validate an RSA modulus size (minimum 2048 bits)."""
    try:
        bits = int(bits)
    except (TypeError, ValueError):
        raise ValidationError("Key size must be a whole number.")
    if bits < 2048:
        raise ValidationError("RSA key size must be at least 2048 bits.")
    if bits > 8192:
        raise ValidationError("RSA key size above 8192 bits is not supported.")
    return bits
