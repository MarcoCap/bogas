"""Security tools for bogas server"""
from nacl.public import PrivateKey, Box, PublicKey

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"


def load_private_key() -> PrivateKey:
    return PrivateKey.generate()  # TODO


class Crypto(object):
    _private_key = load_private_key()
    _public_key = _private_key.public_key

    def __init__(self, other_public_key: PublicKey):
        self.box = Box(self._private_key, other_public_key)
        self.other_key = other_public_key

    @classmethod
    def get_private_key(cls):
        return cls._private_key

    @classmethod
    def get_public_key(cls):
        return cls._public_key

    def encrypt(self, msg: bytes) -> bytes:
        return self.box.encrypt(msg)

    def decrypt(self, msg: bytes) -> bytes:
        return self.box.decrypt(msg)
