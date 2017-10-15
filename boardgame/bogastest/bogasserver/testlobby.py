"""Tests for Lobby"""
from typing import List
from unittest.case import TestCase

from nacl.public import PrivateKey, Box
from tornado.gen import sleep
from tornado.ioloop import IOLoop

from bogascore.communication.client import Client
from bogascore.communication.message import Message
from bogascore.serialization.codec import JsonCodec
from bogasserver.server import Lobby
from bogasserver.utilsmessages import IntroductionMessage, ClientKeyMessage
from bogascore.log import get_logger

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"

log = get_logger(__name__)


class FakeStream(object):

    def __init__(self, responses: List[Message], codec=JsonCodec):
        self.read_count = 0
        self.responses = responses
        self.codec = codec

    async def read_until(self, *a, **ka):
        response = self.responses[self.read_count]
        log.debug('Read count: {}. Sending: {}.', self.read_count, response)
        bytes_response = self.codec.encode(response.serialize())
        self.read_count += 1
        return bytes_response

    async def write(self, msg: bytes):
        log.info('Fake stream got message {}.', msg)


class TestLobby(TestCase):

    def test_new_client(self):
        lobby = Lobby()
        loop = IOLoop.current()
        client_key = PrivateKey.generate()
        public_client = client_key.public_key
        stream = FakeStream([
            IntroductionMessage('test_user', 'JSON'),
            ClientKeyMessage(public_client.encode())
        ])
        async def cb():
            data = ('127.0.0.1', 8888)
            try:
                await lobby.accept_new_client(stream, data)
                await sleep(0.5)
            finally:
                loop.stop()
        loop.run_sync(cb)
        user_in_lobby = lobby.active_clients['test_user']  # type: Client
        assert user_in_lobby.crypto.client_key == public_client
