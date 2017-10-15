"""
Serialization machinery for BoGaS

Every message class and every class that could be passed as a field in a message must implement
the serializable interface, and register itself through the SerializableMeta class.
SerializableMeta is a utility metaclass, that automates the building of slotted classes and
serializable classes registry management.
"""
from base64 import encodebytes, decodebytes
from datetime import datetime
from typing import TypeVar, Dict

from bogascore.log import get_logger

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"

Primitive = TypeVar('Primitive', None, str, int, bool, float, set, list, tuple, dict)

log = get_logger(__name__)

S = TypeVar('S', bound='Serializable')

class_name_table = {
    'None': None,
    'str': str,
    'int': int,
    'bool': bool,
    'float': float,
    'datetime': datetime,
    'set': set,
    'list': list,
    'tuple': tuple,
    'bytes': bytes
}


def resolve_class_name(name: str) -> type:
    return class_name_table[name]

serialization_dispatch_table = {
    type(None): lambda n: n,
    str: lambda s: s,
    int: lambda i: i,
    bool: lambda b: b,
    float: lambda f: f,
    datetime: lambda d: d.timestamp,
    set: lambda s: tuple(s),
    list: lambda l: tuple(l),
    tuple: lambda t: t,
    bytes: lambda b: encodebytes(b).decode().replace('\n', ''),
    'type': lambda t: t.__name__
}

deserialization_dispatch_table = {
    str: lambda s: s,
    int: lambda i: i,
    bool: lambda b: b,
    float: lambda f: f,
    datetime: lambda d: datetime.fromtimestamp(d),
    set: lambda s: set(s),
    list: lambda l: list(l),
    tuple: lambda t: tuple(t),
    bytes: lambda b: decodebytes(b.encode()),
    'type': resolve_class_name
}


class SerializableMeta(type):

    def __init__(cls, name: str, bases: tuple, cls_dict: dict) -> None:
        try:
            members = [x for x, _ in cls.members]
            if hasattr(cls, 'private_members'):
                members = members + list(cls.private_members)
        except (KeyError, TypeError, ValueError) as e:
            raise TypeError('Class "{}" attribute "members" illegally defined. '
                            .format(name)) from e
        if not hasattr(cls, 'serialize') or not callable(cls.serialize):
            raise TypeError('Class "{}" attribute "serialize" undefined or not callable.'
                            .format(name))
        if not hasattr(cls, 'deserialize') or not callable(cls.deserialize):
            raise TypeError('Class "{}" attribute "deserialize" undefined or not callable.'
                            .format(name))
        cls.__slots__ = members
        super().__init__(name, bases, cls_dict)
        cls.register()

    def register(cls, serialize_function=None, deserialize_function=None):
        if serialize_function is None:
            def serialize_function(o: 'Serializable'):
                return o.serialize()
        if deserialize_function is None:
            def deserialize_function(d: Dict[str, Primitive]):
                cls.deserialize(d)
        serialization_dispatch_table[cls] = serialize_function
        deserialization_dispatch_table[cls] = deserialize_function
        class_name_table[cls.__name__] = cls


class Serializable(metaclass=SerializableMeta):

    members = ()

    def serialize(self) -> Dict[str, Primitive]:
        try:
            output = {}
            for attr, attr_type in self.members:
                value = getattr(self, attr, None)
                output[attr] = serialization_dispatch_table[attr_type](value)
            return output
        except Exception as e:
            raise SerializationException("Error during serialization.") from e

    @classmethod
    def deserialize(cls, v: Dict[str, Primitive]) -> S:
        try:
            args = {
                k: deserialization_dispatch_table[k_type](v[k])
                for k, k_type in cls.members
            }
            # Calls the class (i.e. the constructor) with the unpacked dictionary
            # noinspection PyTypeChecker
            return cls(**args)
        except Exception as e:
            log.debug('v: {}, members: {}.', v, cls.members)
            raise SerializationException("Error during deserialization.") from e

    def __eq__(self, other):
        if not isinstance(other, Serializable):
            return False
        return self.serialize() == other.serialize()

    def __hash__(self):
        # TODO: won't work right now as Dict is un-hashable. Migrate to unmodifiable dict?
        return hash(self.serialize())


class SerializationException(Exception):
    pass
