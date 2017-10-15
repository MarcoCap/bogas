"""Tornado implementation of the bogas server"""

from tornado.ioloop import IOLoop
from tornado.iostream import IOStream
from tornado.tcpserver import TCPServer

from bogascore.log import get_logger
from bogasserver import ILobby

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"

log = get_logger(__name__)


class ClientData(object):

    def __init__(self):
        self.ip_address = None
        self.tcp_port = None


class TornadoTCPServer(TCPServer):

    def __init__(self, lobby: ILobby, port=30645, io_loop=IOLoop.current()):
        super(TornadoTCPServer, self).__init__(io_loop=io_loop)
        self.listen(port)
        self.lobby = lobby

    def start_listening(self):
        super(TornadoTCPServer, self).start()
        log.info('Starting TCP server, waiting for incoming connections.')
        self.io_loop.start()

    async def handle_stream(self, stream: IOStream, address):
        log.info('Received new TCP connection from {}.', address)
        await self.lobby.accept_new_client(stream, address)
