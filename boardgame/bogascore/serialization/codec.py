"""Package containing codecs for (de)-serialization"""
import json
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Dict

from bogascore.serialization.serialization import Primitive

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"


class AvailableCodecs(Enum):
    JSON = 1

    def get_codec(self):
        if self == AvailableCodecs.JSON:
            return JsonCodec
        else:
            raise ValueError('Codec {} is not available.'.format(self.name))


class Codec(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def encode(cls, data_dict: Dict[str, Primitive]) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def decode(cls, data: bytes) -> Dict[str, Primitive]:
        pass

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)


class JsonCodec(Codec):

    @classmethod
    def encode(cls, data_dict: Dict[str, Primitive]) -> bytes:
        return json.dumps(data_dict).encode()

    @classmethod
    def decode(cls, data: bytes) -> Dict[str, Primitive]:
        return json.loads(data)

    def __str__(self):
        return str(self.__class__)

    def __repr__(self):
        return str(self)
