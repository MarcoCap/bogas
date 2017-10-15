"""Minimal client for testing"""
import socket

from tornado.ioloop import IOLoop
from tornado.iostream import IOStream

from bogasclient.client import Client
from bogascore.communication.connection import SelfOpeningSocketConnection

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"


def main():

    print("Starting client.")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stream = IOStream(s)
    connection = SelfOpeningSocketConnection(stream)
    client_loop = IOLoop.current()
    client = Client(connection)
    client.main(client_loop)


if __name__ == '__main__':
    main()
