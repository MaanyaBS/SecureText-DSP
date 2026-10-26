import base64
import unittest

from tests._helpers import get_key

from crypto import rsa_encryption as enc
from utils.validation import ValidationError


class EncryptionTests(unittest.TestCase):
    def test_T12_roundtrip(self):
        key = get_key("a")
        ct = enc.encrypt_message("Hello SecureText", key.public_key())
        self.assertNotIn("Hello", ct)
        self.assertEqual(enc.decrypt_message(ct, key), "Hello SecureText")

    def test_T13_ciphertext_is_base64_256_bytes(self):
        key = get_key("a")
        ct = enc.encrypt_message("abc", key.public_key())
        self.assertEqual(len(base64.b64decode(ct, validate=True)), 256)

    def test_T14_oaep_is_randomised(self):
        key = get_key("a")
        c1 = enc.encrypt_message("same message", key.public_key())
        c2 = enc.encrypt_message("same message", key.public_key())
        self.assertNotEqual(c1, c2)
        self.assertEqual(enc.decrypt_message(c1, key), enc.decrypt_message(c2, key))

    def test_T15_wrong_private_key_fails(self):
        a, b = get_key("a"), get_key("b")
        ct = enc.encrypt_message("secret", a.public_key())
        with self.assertRaises(enc.DecryptionError):
            enc.decrypt_message(ct, b)

    def test_T16_invalid_ciphertext(self):
        key = get_key("a")
        with self.assertRaises(enc.DecryptionError):
            enc.decrypt_message("!!!not base64!!!", key)
        with self.assertRaises(enc.DecryptionError):
            enc.decrypt_message(base64.b64encode(b"short").decode(), key)
        with self.assertRaises(enc.DecryptionError):
            enc.decrypt_message(base64.b64encode(b"\x00" * 256).decode(), key)

    def test_T17_tampered_ciphertext_fails(self):
        key = get_key("a")
        raw = bytearray(base64.b64decode(enc.encrypt_message("secret", key.public_key())))
        raw[10] ^= 0x01
        with self.assertRaises(enc.DecryptionError):
            enc.decrypt_message(base64.b64encode(bytes(raw)).decode(), key)

    def test_T18_oversized_message_rejected(self):
        key = get_key("a")
        limit = enc.max_message_bytes(key.public_key())
        self.assertEqual(limit, 190)  # 256 - 2*32 - 2
        ok = "a" * limit
        self.assertEqual(enc.decrypt_message(enc.encrypt_message(ok, key.public_key()), key), ok)
        with self.assertRaises(ValidationError) as ctx:
            enc.encrypt_message("a" * (limit + 1), key.public_key())
        self.assertIn("Hybrid", str(ctx.exception))

    def test_T19_unicode(self):
        key = get_key("a")
        text = "नमस्ते 🌍 café 你好"
        self.assertEqual(enc.decrypt_message(enc.encrypt_message(text, key.public_key()), key), text)

    def test_T20_unicode_limit_counts_bytes(self):
        key = get_key("a")
        text = "é" * 96  # 192 bytes in UTF-8 > 190
        with self.assertRaises(ValidationError):
            enc.encrypt_message(text, key.public_key())

    def test_T21_empty_input(self):
        key = get_key("a")
        for bad in ("", "   ", None, 123):
            with self.assertRaises(ValidationError):
                enc.encrypt_message(bad, key.public_key())
        for bad in ("", "  ", None):
            with self.assertRaises(ValidationError):
                enc.decrypt_message(bad, key)

    def test_T22_whitespace_in_ciphertext_tolerated(self):
        key = get_key("a")
        ct = enc.encrypt_message("wrap me", key.public_key())
        wrapped = "\n".join(ct[i : i + 64] for i in range(0, len(ct), 64))
        self.assertEqual(enc.decrypt_message(wrapped, key), "wrap me")


class TamperDemoTests(unittest.TestCase):
    def test_T42_tamper_helper_breaks_decryption(self):
        key = get_key("a")
        ct = enc.encrypt_message("demo", key.public_key())
        bad = enc.tamper_ciphertext(ct)
        self.assertNotEqual(ct, bad)
        with self.assertRaises(enc.DecryptionError):
            enc.decrypt_message(bad, key)
        with self.assertRaises(enc.DecryptionError):
            enc.tamper_ciphertext("###")


if __name__ == "__main__":
    unittest.main()
