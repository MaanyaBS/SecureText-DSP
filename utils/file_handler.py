"""Small file helpers used by the GUI. Text files are always UTF-8."""

import os


def read_text_file(path):
    """Read a UTF-8 text file and return its content."""
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def read_bytes_file(path):
    """Read a file as raw bytes."""
    with open(path, "rb") as handle:
        return handle.read()


def write_text_file(path, content):
    """Write text to ``path`` (UTF-8), creating parent folders if needed."""
    _ensure_parent(path)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def write_private_file(path, data):
    """Write bytes to ``path`` and restrict permissions where the OS allows.

    On POSIX the file mode is set to 0o600. Windows ignores most POSIX mode
    bits, so the call is best effort there.
    """
    _ensure_parent(path)
    with open(path, "wb") as handle:
        handle.write(data)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def _ensure_parent(path):
    folder = os.path.dirname(os.path.abspath(path))
    if folder:
        os.makedirs(folder, exist_ok=True)
