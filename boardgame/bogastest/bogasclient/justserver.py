"""DOCSTRING"""
from tornado.ioloop import IOLoop

import bogascore.log as log
from bogasserver.server import Lobby
from bogasserver.tornadowrapper import TornadoTCPServer

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"

log.root_log.setLevel(3)


def main():
    server_loop = IOLoop()
    lobby = Lobby(io_loop=server_loop)
    print("Starting server loop.")
    lobby.run()


if __name__ == '__main__':
    main()
