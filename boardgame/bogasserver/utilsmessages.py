"""Utility (i.e.: non game related) messages"""
from bogascore.communication.message import Message
from bogascore.serialization.codec import Codec, AvailableCodecs

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"


class IntroductionMessage(Message):

    members = Message.members + (
        ('username', str),
        ('codec', str)
    )

    def __init__(self, username: str, codec: str, msg_type: type = None) -> None:
        super(IntroductionMessage, self).__init__(msg_type)
        self.username = username
        self.codec = codec

    def get_codec(self) -> Codec:
        try:
            return AvailableCodecs[self.codec].get_codec()
        except KeyError:
            raise ValueError('Codec "{}" is not available.'.format(self.codec))


class ServerKeysMessage(Message):

    members = Message.members + (
        ('server_key',  bytes),
        ('client_key', bytes)
    )

    def __init__(self, server_key: bytes, client_key: bytes, msg_type: type = None) -> None:
        super(ServerKeysMessage, self).__init__(msg_type)
        self.server_key = server_key
        self.client_key = client_key

    def is_client_key_missing(self):
        return self.client_key == ''


class ClientKeyMessage(Message):

    members = Message.members + (
        ('client_key', bytes),
    )

    def __init__(self, client_key: bytes, msg_type: type = None) -> None:
        super(ClientKeyMessage, self).__init__(msg_type)
        self.client_key = client_key
