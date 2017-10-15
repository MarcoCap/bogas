"""Tests for tornado wrappers"""

import socket
from unittest.case import TestCase

from tornado.gen import sleep
from tornado.ioloop import IOLoop
from tornado.iostream import IOStream

from bogascore.log import get_logger
from bogasserver.server import Lobby
from bogasserver.tornadowrapper import TornadoTCPServer

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"


log = get_logger(__name__)


class FakeLobby(Lobby):
    async def start_new_game(self, game, players, clients):
        assert False, 'Should not have been called'

    async def accept_new_client(self, stream: IOStream, client_details):
        log.info('Test result: accept_new_client got: {}; {}.', stream, client_details)
        log.info('Stream is closed: {}.', stream.closed())
        try:
            self.message = await stream.read_until(b'\n')
            log.info('Message is: {}.', self.message)
        except BaseException as e:
            log.error('Could not read.', exc_info=e)
            log.error('Stream error is: {}.', stream.error)
        finally:
            await sleep(0.5)
            IOLoop.current().stop()

    def __init__(self):
        self.message = 'SBAGLIATO!'


class TCPTest(TestCase):

    def test_new_client(self):
        lobby = FakeLobby()
        loop = IOLoop.current()
        server = TornadoTCPServer(lobby, io_loop=loop)
        async def connect_and_send():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            stream = IOStream(s)

            async def send_request():
                try:
                    msg = 'Testing\n'.encode()
                    log.info('Type of msg is: {}.', type(msg))
                    await stream.write(msg)
                except BaseException as e:
                    log.error('Could not write: {}.', exc_info=e)
                    log.error('Stream error after write is: {}.', stream.error)

            await stream.connect(("localhost", 30645))
            await send_request()
        loop.spawn_callback(connect_and_send)
        server.start_listening()
        assert lobby.message == b'Testing\n', 'Expected b\'Testing\n\', got {}.'.format(repr(lobby.message))
