import logging
import unittest

from command import GeneratePasswordConfig
from keepassxc import get_version, generate_password, estimate_password, generate_diceware
from parameterized import parameterized

logging.basicConfig(level=logging.DEBUG)


class Test(unittest.TestCase):
    def test_get_version(self):
        self.assertRegex(get_version(), "^\\d\\.\\d\\.\\d$")

    @parameterized.expand([[1], [20], [200]])
    def test_generate_password_length(self, length):
        self.assertEqual(
            len(generate_password(GeneratePasswordConfig(length=length))),
            length)

    @parameterized.expand([[1], [20], [200]])
    def test_generate_diceware(self, words: int):
        self.assertEqual(
            len(generate_diceware(words=words).split(' ')),
            words)

    @parameterized.expand([
        ['1234', 4, 2.0, 0.602]
    ])
    def test_estimate_password(self, password, length, entropy, log10):
        estimation = estimate_password(password)
        self.assertEqual(estimation['length'], length)
        self.assertAlmostEqual(estimation['entropy'], entropy)
        self.assertAlmostEqual(estimation['log10'], log10)

    def test_create_database(self):
        pass
