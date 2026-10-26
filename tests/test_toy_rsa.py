import unittest

from tests._helpers import get_key  # noqa: F401  (sets sys.path)

from crypto.toy_rsa import ToyRSAError, is_prime, toy_rsa_walkthrough


class ToyRSATests(unittest.TestCase):
    def test_T44_classic_example(self):
        steps = "\n".join(toy_rsa_walkthrough(61, 53, 17, 65))
        self.assertIn("n = p x q = 3233", steps)
        self.assertIn("phi(n) = (p-1)(q-1) = 60 x 52 = 3120", steps)
        self.assertIn("d = e^-1 mod phi(n) = 2753", steps)
        self.assertIn("= 2790", steps)
        self.assertIn("recovered message = 65", steps)

    def test_T45_invalid_parameters(self):
        for args in [(60, 53, 17, 65), (61, 61, 17, 65), (61, 53, 15, 65),
                     (61, 53, 17, 5000), (61, 53, 1, 65), (61, 53, 17, -1)]:
            with self.assertRaises(ToyRSAError):
                toy_rsa_walkthrough(*args)
        with self.assertRaises(ToyRSAError):
            toy_rsa_walkthrough("61", 53, 17, 65)

    def test_T46_is_prime(self):
        self.assertEqual([n for n in range(20) if is_prime(n)], [2, 3, 5, 7, 11, 13, 17, 19])


if __name__ == "__main__":
    unittest.main()
