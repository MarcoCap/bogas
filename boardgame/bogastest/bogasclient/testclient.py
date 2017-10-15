"""Tests for client class"""
import socket
from threading import Thread
from time import sleep

from tornado.ioloop import IOLoop
from tornado.iostream import IOStream

from bogasclient.client import Client
from bogascore.communication.connection import SelfOpeningSocketConnection
from bogasserver.server import Lobby
from bogasserver.tornadowrapper import TornadoTCPServer

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"


def manual():

    import bogascore.log as log
    log.root_log.setLevel(3)

    server_loop = IOLoop()
    server = TornadoTCPServer(Lobby(), io_loop=server_loop)
    print("Starting server loop.")
    thread = Thread(target=server.start_listening)
    thread.start()
    sleep(2)

    print("Starting client loop.")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stream = IOStream(s)
    connection = SelfOpeningSocketConnection(stream)
    client_loop = IOLoop()
    client = Client(connection)
    client.main(client_loop)


if __name__ == '__main__':
    manual()