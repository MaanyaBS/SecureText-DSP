import base64
import json
import unittest

from tests._helpers import get_key

from crypto import hybrid_encryption as hyb
from crypto.rsa_encryption import DecryptionError
from utils.validation import ValidationError


def _open(env):
    return json.loads(base64.b64decode(env).decode())


def _pack(obj):
    return base64.b64encode(json.dumps(obj).encode()).decode()


class HybridTests(unittest.TestCase):
    def test_T31_roundtrip_long_message(self):
        key = get_key("a")
        text = "SecureText hybrid test. " * 500
        env = hyb.encrypt_hybrid(text, key.public_key())
        self.assertEqual(hyb.decrypt_hybrid(env, key), text)

    def test_T32_envelope_structure(self):
        key = get_key("a")
        data = _open(hyb.encrypt_hybrid("hi", key.public_key()))
        self.assertEqual(set(data), {"version", "alg", "wrapped_key", "nonce", "ciphertext"})
        self.assertEqual(len(base64.b64decode(data["nonce"])), 12)
        self.assertEqual(len(base64.b64decode(data["wrapped_key"])), 256)
        self.assertEqual(len(base64.b64decode(data["ciphertext"])), 2 + 16)

    def test_T33_fresh_key_and_nonce_each_time(self):
        key = get_key("a")
        d1 = _open(hyb.encrypt_hybrid("same", key.public_key()))
        d2 = _open(hyb.encrypt_hybrid("same", key.public_key()))
        self.assertNotEqual(d1["nonce"], d2["nonce"])
        self.assertNotEqual(d1["wrapped_key"], d2["wrapped_key"])
        self.assertNotEqual(d1["ciphertext"], d2["ciphertext"])

    def test_T34_tampered_ciphertext_detected(self):
        key = get_key("a")
        data = _open(hyb.encrypt_hybrid("important", key.public_key()))
        raw = bytearray(base64.b64decode(data["ciphertext"]))
        raw[0] ^= 0x01
        data["ciphertext"] = base64.b64encode(bytes(raw)).decode()
        with self.assertRaises(DecryptionError) as ctx:
            hyb.decrypt_hybrid(_pack(data), key)
        self.assertIn("Authentication", str(ctx.exception))

    def test_T35_tampered_tag_detected(self):
        key = get_key("a")
        data = _open(hyb.encrypt_hybrid("important", key.public_key()))
        raw = bytearray(base64.b64decode(data["ciphertext"]))
        raw[-1] ^= 0x01
        data["ciphertext"] = base64.b64encode(bytes(raw)).decode()
        with self.assertRaises(DecryptionError):
            hyb.decrypt_hybrid(_pack(data), key)

    def test_T36_tampered_nonce_and_wrapped_key(self):
        key = get_key("a")
        env = hyb.encrypt_hybrid("important", key.public_key())
        data = _open(env)
        n = bytearray(base64.b64decode(data["nonce"]))
        n[0] ^= 1
        bad_nonce = dict(data, nonce=base64.b64encode(bytes(n)).decode())
        with self.assertRaises(DecryptionError):
            hyb.decrypt_hybrid(_pack(bad_nonce), key)
        w = bytearray(base64.b64decode(data["wrapped_key"]))
        w[5] ^= 1
        bad_key = dict(data, wrapped_key=base64.b64encode(bytes(w)).decode())
        with self.assertRaises(DecryptionError):
            hyb.decrypt_hybrid(_pack(bad_key), key)

    def test_T37_header_is_authenticated_version_check(self):
        key = get_key("a")
        data = _open(hyb.encrypt_hybrid("x", key.public_key()))
        data["version"] = 2
        with self.assertRaises(DecryptionError):
            hyb.decrypt_hybrid(_pack(data), key)

    def test_T38_wrong_private_key(self):
        a, b = get_key("a"), get_key("b")
        env = hyb.encrypt_hybrid("secret", a.public_key())
        with self.assertRaises(DecryptionError):
            hyb.decrypt_hybrid(env, b)

    def test_T39_malformed_envelopes(self):
        key = get_key("a")
        for bad in ("@@@", base64.b64encode(b"not json").decode(), _pack([1, 2]), _pack({"version": 1})):
            with self.assertRaises(DecryptionError):
                hyb.decrypt_hybrid(bad, key)
        data = _open(hyb.encrypt_hybrid("x", key.public_key()))
        data["nonce"] = base64.b64encode(b"123").decode()
        with self.assertRaises(DecryptionError):
            hyb.decrypt_hybrid(_pack(data), key)

    def test_T40_unicode_hybrid(self):
        key = get_key("a")
        text = "மொழி 🔐 日本語 " * 40
        self.assertEqual(hyb.decrypt_hybrid(hyb.encrypt_hybrid(text, key.public_key()), key), text)

    def test_T41_empty_input(self):
        key = get_key("a")
        for bad in ("", "   ", None):
            with self.assertRaises(ValidationError):
                hyb.encrypt_hybrid(bad, key.public_key())
        for bad in ("", "  ", None):
            with self.assertRaises(ValidationError):
                hyb.decrypt_hybrid(bad, key)


class HybridTamperDemoTests(unittest.TestCase):
    def test_T43_tamper_envelope_helper(self):
        key = get_key("a")
        env = hyb.encrypt_hybrid("demo message", key.public_key())
        bad = hyb.tamper_envelope(env)
        self.assertNotEqual(env, bad)
        with self.assertRaises(DecryptionError):
            hyb.decrypt_hybrid(bad, key)
        with self.assertRaises(DecryptionError):
            hyb.tamper_envelope("###")


if __name__ == "__main__":
    unittest.main()
