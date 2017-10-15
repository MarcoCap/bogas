"""Implementation of client class"""
from typing import TypeVar, Type

from nacl.public import PublicKey
from tornado.ioloop import IOLoop

from bogascore.log import get_logger
from bogascore.communication.connection import Connection
from bogascore.communication.message import Message, ChoiceMessage, ChoiceResponseMessage
from bogascore.serialization.codec import JsonCodec
from bogasserver.security import Crypto
from bogasserver.utilsmessages import IntroductionMessage, ServerKeysMessage, ClientKeyMessage

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"

S = TypeVar('S', bound=Message)


logger = get_logger(__name__)


class LogIn(object):

    def __init__(self, connection: Connection):
        self.connection = connection
        self.codec = JsonCodec
        self.crypto = None

    async def do_login(self) -> None:
        logger.debug('Sending introduction')
        await self.send(IntroductionMessage('test_user', 'JSON'))
        skm = await self.receive(ServerKeysMessage)
        server_key = PublicKey(skm.server_key)
        self.crypto = Crypto(server_key)
        await self.send(ClientKeyMessage(self.crypto.get_public_key().encode()))

    async def receive(self, message_class: Type[S]) -> S:
        msg = await self.connection.receive()
        decoded_msg = self.codec.decode(msg)
        return message_class.deserialize(decoded_msg)

    async def send(self, message: Message):
        enc_message = self.codec.encode(message.serialize())
        logger.debug("Sending '{}'.", str(message))
        await self.connection.send(enc_message)


class Client(object):

    def __init__(self, connection: Connection):
        self.connection = connection
        self.crypto = None
        self.codec = JsonCodec
        self.running = False
        # TODO: a separate thread for the UI, with some communication method.

    async def login(self) -> None:
        login = LogIn(self.connection)
        await login.do_login()
        self.crypto = login.crypto

    async def stop(self):
        logger.info('Client shutting down.')
        self.running = False

    def main(self, loop: IOLoop) -> None:
        logger.info('Starting client.')
        async def actual_main():
            self.running = True
            await self.login()
            while self.running:
                try:
                    await self.communication_loop()
                except KeyboardInterrupt:
                    await self.stop()
        loop.spawn_callback(actual_main)
        loop.start()

    async def communication_loop(self):
        logger.info('Starting communication loop.')
        while True:
            msg = await self.receive()
            logger.debug("Got {}.", msg.msg_type.__name__)
            if msg.msg_type == ChoiceMessage:
                # By the check above we know msg is a ChoiceMessage
                # noinspection PyTypeChecker
                resp = await self.make_choice(msg)
                await self.send(resp)
            else:
                await self.show_message(msg)

    async def show_message(self, msg: Message) -> None:
        print(msg.p_print())

    async def make_choice(self, msg: ChoiceMessage) -> Message:
        done = False
        choice = None
        while not done:
            try:
                print(msg.p_print())
                choice_index = int(input("> Which choice?\n> "))
                choice = msg.choices[choice_index]
                done = True
            except (TypeError, ValueError, IndexError):
                print("Value must be integer between 0 and {}.". format(len(msg.choices) - 1))
        return ChoiceResponseMessage(choice)

    async def send(self, message: Message):
        encoded_message = self.codec.encode(message.serialize())
        encrypted_message = self.crypto.encrypt(encoded_message)
        await self.connection.send(encrypted_message)

    async def receive(self, message_class: Type[S] = None) -> S:
        logger.debug("Waiting for a {}.", message_class.__name__ if message_class is not None else 'Message')
        msg = await self.connection.receive()
        decrypted_message = self.crypto.decrypt(msg)
        decoded_msg = self.codec.decode(decrypted_message)
        if message_class is not None:
            return message_class.deserialize(decoded_msg)
        else:
            return Message.parse_message(decoded_msg)
