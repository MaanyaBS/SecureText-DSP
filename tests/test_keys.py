import os
import tempfile
import unittest

from tests._helpers import get_key  # noqa: F401  (sets sys.path)

from crypto import rsa_keys
from utils.file_handler import write_private_file, read_bytes_file
from utils.validation import ValidationError


class KeyTests(unittest.TestCase):
    def test_T01_generate_2048(self):
        key = get_key("a")
        self.assertEqual(key.key_size, 2048)
        n, e = rsa_keys.public_numbers(key)
        self.assertEqual(e, 65537)
        self.assertEqual(n.bit_length(), 2048)

    def test_T02_reject_small_key_size(self):
        with self.assertRaises(ValidationError):
            rsa_keys.generate_key_pair(1024)
        with self.assertRaises(ValidationError):
            rsa_keys.generate_key_pair("abc")

    def test_T03_math_relationships(self):
        key = get_key("a")
        p, q, d = rsa_keys.private_numbers(key)
        n, e = rsa_keys.public_numbers(key)
        self.assertEqual(p * q, n)
        phi = (p - 1) * (q - 1)
        # d is the modular inverse of e modulo the Carmichael value, hence also
        # a valid inverse modulo phi up to the gcd factor.
        self.assertEqual((e * d) % ((p - 1) * (q - 1) // _gcd(p - 1, q - 1)), 1)
        self.assertEqual(pow(pow(42, e, n), d, n), 42)
        self.assertGreater(phi, 0)

    def test_T04_public_pem_roundtrip(self):
        key = get_key("a")
        pem = rsa_keys.export_public_key_pem(key.public_key())
        self.assertTrue(pem.startswith(b"-----BEGIN PUBLIC KEY-----"))
        loaded = rsa_keys.load_public_key_pem(pem)
        self.assertEqual(loaded.public_numbers(), key.public_key().public_numbers())
        loaded2 = rsa_keys.load_public_key_pem(pem.decode())
        self.assertEqual(loaded2.public_numbers(), key.public_key().public_numbers())

    def test_T05_private_pem_is_encrypted_and_roundtrips(self):
        key = get_key("a")
        pem = rsa_keys.export_private_key_pem(key, "correct horse battery")
        self.assertIn(b"ENCRYPTED PRIVATE KEY", pem)
        loaded = rsa_keys.load_private_key_pem(pem, "correct horse battery")
        self.assertEqual(loaded.private_numbers(), key.private_numbers())

    def test_T06_wrong_password_rejected(self):
        key = get_key("a")
        pem = rsa_keys.export_private_key_pem(key, "correct horse battery")
        with self.assertRaises(rsa_keys.KeyError_):
            rsa_keys.load_private_key_pem(pem, "wrong password 1")

    def test_T07_short_or_empty_password_rejected_on_export(self):
        key = get_key("a")
        with self.assertRaises(ValidationError):
            rsa_keys.export_private_key_pem(key, "short")
        with self.assertRaises(ValidationError):
            rsa_keys.export_private_key_pem(key, "")

    def test_T08_invalid_key_files(self):
        with self.assertRaises(rsa_keys.KeyError_):
            rsa_keys.load_public_key_pem(b"this is not a key")
        with self.assertRaises(rsa_keys.KeyError_):
            rsa_keys.load_private_key_pem(b"this is not a key", "password123")
        with self.assertRaises(rsa_keys.KeyError_):
            rsa_keys.load_private_key_pem(b"", "")

    def test_T09_public_key_not_accepted_as_private(self):
        key = get_key("a")
        pub_pem = rsa_keys.export_public_key_pem(key.public_key())
        with self.assertRaises(rsa_keys.KeyError_):
            rsa_keys.load_private_key_pem(pub_pem, "password123")

    def test_T10_private_key_file_save_and_load(self):
        key = get_key("a")
        pem = rsa_keys.export_private_key_pem(key, "file password 1")
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "nested", "private.pem")
            write_private_file(path, pem)
            self.assertTrue(os.path.exists(path))
            loaded = rsa_keys.load_private_key_pem(read_bytes_file(path), "file password 1")
            self.assertEqual(loaded.private_numbers(), key.private_numbers())

    def test_T11_fingerprint_stable_and_distinct(self):
        a, b = get_key("a"), get_key("b")
        self.assertEqual(rsa_keys.fingerprint(a.public_key()), rsa_keys.fingerprint(a.public_key()))
        self.assertNotEqual(rsa_keys.fingerprint(a.public_key()), rsa_keys.fingerprint(b.public_key()))


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


if __name__ == "__main__":
    unittest.main()
