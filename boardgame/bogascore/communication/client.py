"""Client class and related"""
from typing import TypeVar, Type

from nacl.public import PublicKey

from bogascore.communication.connection import Connection
from bogascore.communication.message import MultiMessage, Message
from bogascore.serialization.codec import JsonCodec, Codec, AvailableCodecs
from bogascore.serialization.serialization import Serializable, SerializationException
from bogascore.log import get_logger
from bogasserver.security import Crypto
from bogasserver.utilsmessages import IntroductionMessage, ServerKeysMessage, ClientKeyMessage

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"

S = TypeVar('S', bound=Serializable)

log = get_logger(__name__)


class ClientDetails(object):

    def __init__(self, address=None, port=None):
        self.address = address
        self.port = port

    def __str__(self):
        data = []
        if self.address is not None:
            data.append('address: {}'.format(self.address))
        if self.port is not None:
            data.append('port: {}'.format(self.port))
        return '[{}]'.format(', '.join(data))


class ClientBuilder(object):

    DEFAULT_CODEC = JsonCodec

    def __init__(self, connection: Connection, client_details: ClientDetails) -> None:
        self.codec = None
        self.username = None
        self.details = client_details
        self.connection = connection
        self.crypto = None

    async def do_handshake(self) -> None:
        log.debug("Starting handshake with client {}.", self.details)
        tries = 3
        while tries > 0:
            try:
                msg = await self.receive(IntroductionMessage)
                break
            except SerializationException as e:
                log.debug('Handshake failed: {}', e.__cause__)
                tries -= 1
        else:  # Executes only if the loop did not encounter a 'break'
            raise ClientException('Client {} did not complete handshake'.format(self.details))
        self.username = msg.username
        try:
            self.codec = AvailableCodecs[msg.codec].get_codec()
            log.debug(str(self.codec))
            log.debug("Client {} assigned username '{}' and codec {}.", self.details, self.username, str(self.codec))
        except (KeyError, ValueError):
            raise ClientException('Client {} requested unavailable codec {}'.format(self.details, msg.codec))

    async def exchange_keys(self, client_key: PublicKey) -> None:
        log.debug("Exchanging keys with client {}.", self.username)
        server_key = Crypto.get_public_key()
        actual_server = server_key.encode()
        actual_client = client_key.encode() if client_key is not None else b''
        await self.send(ServerKeysMessage(actual_server, actual_client))
        if client_key is None:  # If the user is unknown, wait for his public key
            ckm = await self.receive(ClientKeyMessage)
            client_key = PublicKey(ckm.client_key)
        self.crypto = Crypto(client_key)
        log.debug("Successfully exchanged keys with client '{}'.", self.username)

    def build(self) -> 'Client':
        if self.username is None or self.codec is None:
            raise ValueError('Handshake not yet completed')
        if self.crypto is None:
            raise ValueError('Key exchange not yet completed')
        log.debug("Client '{}' now active.", self.username)
        return Client(self.connection, self.details, self.codec, self.username, self.crypto)

    async def receive(self, message_class: Type(S)) -> S:
        msg = await self.connection.receive()
        codec = self.codec if self.codec is not None else self.DEFAULT_CODEC
        decoded_msg = codec.decode(msg)

        return message_class.deserialize(decoded_msg)

    async def send(self, message: Message):
        codec = self.codec if self.codec is not None else self.DEFAULT_CODEC
        enc_message = codec.encode(message.serialize())
        await self.connection.send(enc_message)


class Client(object):

    def __init__(self,
                 connection: Connection,
                 client_details: ClientDetails,
                 codec: Codec,
                 username: str,
                 crypto: Crypto):
        self.codec = codec
        self.username = username
        self.details = client_details
        self.connection = connection
        self.crypto = crypto
        self.buffer = []

    async def send(self, message: Message):
        # self.buffer.append(message)
        await self._send(message)

    async def flush_buffer(self):
        multi_message = MultiMessage(self.buffer)
        self.buffer.clear()
        await self._send(multi_message)

    async def _send(self, message: Message):
        encoded_message = self.codec.encode(message.serialize())
        log.debug("Sending: {}.", repr(encoded_message.decode()))
        encrypted_message = self.crypto.encrypt(encoded_message)
        await self.connection.send(encrypted_message)

    async def receive(self, message_class: Type[S]) -> S:
        # await self.flush_buffer()
        log.debug("Waiting for a '{}'.", message_class.__name__)
        msg = await self.connection.receive()
        decrypted_message = self.crypto.decrypt(msg)
        decoded_msg = self.codec.decode(decrypted_message)

        # Below is due to type hinting limitation. Receive actually asks
        # for a subclass of Serializable, but it had to be declared as
        # above in order for the return value to be detected as the correct type.

        # noinspection PyUnresolvedReferences
        return message_class.deserialize(decoded_msg)


class ClientException(Exception):
    pass
