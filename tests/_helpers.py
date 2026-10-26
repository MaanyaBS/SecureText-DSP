"""Shared test setup: make the project root importable and cache RSA keys."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from crypto.rsa_keys import generate_key_pair  # noqa: E402

_cache = {}


def get_key(name="a"):
    """Return a cached 2048-bit test key so the suite stays fast."""
    if name not in _cache:
        _cache[name] = generate_key_pair(2048)
    return _cache[name]
