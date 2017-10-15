"""Connections established between server and client"""

from abc import ABCMeta, abstractmethod
from typing import List

from tornado.iostream import IOStream

from bogascore.log import get_logger

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"


logger = get_logger(__name__)


class Connection(metaclass=ABCMeta):

    @abstractmethod
    async def send(self, message: bytes) -> None:
        pass

    @abstractmethod
    async def receive(self) -> bytes:
        pass


# class DirectConnection(Connection):
#
#     def __init__(self, client: Client):
#         self.client = client
#         self.buffer = None
#
#     async def receive(self) -> str:
#         res = await self.client.get_input()
#         return res
#
#     async def send(self, message: str) -> None:
#         self.client.accept_message(message)


class FakeConnection(Connection):

    def __init__(self, responses: List[str]):
        responses.reverse()
        self.responses = responses

    async def receive(self) -> str:
        msg = self.responses.pop()
        print('FakeConnection receiving "{}".'.format(msg))
        return msg

    async def send(self, message: str) -> None:
        print('FakeConnection sending "{}".'.format(message))


class SocketConnection(Connection):

    def __init__(self, stream: IOStream) -> None:
        self.stream = stream

    async def receive(self) -> bytes:
        await super(SocketConnection, self).receive()
        l_bytes = await self.stream.read_bytes(2)
        l = int.from_bytes(l_bytes, 'big')
        return await self.stream.read_bytes(l)

    async def send(self, message: bytes) -> None:
        await super(SocketConnection, self).send(message)
        l = len(message)
        l_bytes = bytes([l // 256, l % 256])
        return await self.stream.write(l_bytes + message)


class SelfOpeningSocketConnection(SocketConnection):

    def __init__(self, stream: IOStream, address: str = "127.0.0.1", port: int = 30645) -> None:
        super().__init__(stream)
        self.address = address
        self.port = port

        async def connect():
            await self.stream.connect((self.address, self.port))

            async def null_connect():
                pass
            self.connect = null_connect
        self.connect = connect

    async def send(self, message: bytes) -> None:
        await self.connect()
        await super().send(message)

    async def receive(self) -> bytes:
        await self.connect()
        return await super().receive()
