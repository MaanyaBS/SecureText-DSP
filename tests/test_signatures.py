import base64
import unittest

from tests._helpers import get_key

from crypto import digital_signatures as sig
from utils.validation import ValidationError


class SignatureTests(unittest.TestCase):
    def test_T23_sign_and_verify(self):
        key = get_key("a")
        s = sig.sign_message("Pay Alice 100", key)
        self.assertEqual(len(base64.b64decode(s)), 256)
        self.assertTrue(sig.verify_signature("Pay Alice 100", s, key.public_key()))

    def test_T24_modified_message_fails(self):
        key = get_key("a")
        s = sig.sign_message("Pay Alice 100", key)
        self.assertFalse(sig.verify_signature("Pay Alice 900", s, key.public_key()))

    def test_T25_wrong_public_key_fails(self):
        a, b = get_key("a"), get_key("b")
        s = sig.sign_message("hello", a)
        self.assertFalse(sig.verify_signature("hello", s, b.public_key()))

    def test_T26_pss_is_randomised_but_both_verify(self):
        key = get_key("a")
        s1, s2 = sig.sign_message("hello", key), sig.sign_message("hello", key)
        self.assertNotEqual(s1, s2)
        self.assertTrue(sig.verify_signature("hello", s1, key.public_key()))
        self.assertTrue(sig.verify_signature("hello", s2, key.public_key()))

    def test_T27_corrupted_or_malformed_signature(self):
        key = get_key("a")
        s = sig.sign_message("hello", key)
        raw = bytearray(base64.b64decode(s))
        raw[0] ^= 0xFF
        self.assertFalse(sig.verify_signature("hello", base64.b64encode(bytes(raw)).decode(), key.public_key()))
        self.assertFalse(sig.verify_signature("hello", "###", key.public_key()))
        self.assertFalse(sig.verify_signature("hello", base64.b64encode(b"short").decode(), key.public_key()))

    def test_T28_empty_inputs(self):
        key = get_key("a")
        with self.assertRaises(ValidationError):
            sig.sign_message("", key)
        with self.assertRaises(ValidationError):
            sig.verify_signature("", "abcd", key.public_key())
        with self.assertRaises(ValidationError):
            sig.verify_signature("hello", "", key.public_key())

    def test_T29_unicode_signature(self):
        key = get_key("a")
        text = "सत्यमेव जयते ✓"
        s = sig.sign_message(text, key)
        self.assertTrue(sig.verify_signature(text, s, key.public_key()))
        self.assertFalse(sig.verify_signature(text + " ", s, key.public_key()))

    def test_T30_signature_not_confidential(self):
        key = get_key("a")
        msg = "visible text"
        s = sig.sign_message(msg, key)
        self.assertNotIn(msg, s)  # signature does not contain message, message stays public


if __name__ == "__main__":
    unittest.main()
