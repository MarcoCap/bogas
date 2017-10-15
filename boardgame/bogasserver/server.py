"""Entry point for server."""
from typing import Dict, List, Iterable, Callable

from nacl.public import PublicKey
from tornado.ioloop import IOLoop
from tornado.iostream import IOStream

from bogascore.communication.client import Client, ClientDetails, ClientException, ClientBuilder
from bogascore.communication.connection import SocketConnection
from bogascore.communication.message import InfoMessage, ChoiceMessage, ChoiceResponseMessage
from bogascore.environment import Player
from bogascore.examples.testgames import RandomWinsGame
from bogascore.game import Event, Game
from bogascore.log import get_logger
from bogascore.serialization.serialization import Serializable
from bogasserver import ILobby
from bogasserver.tornadowrapper import TornadoTCPServer

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"

log = get_logger(__name__)


class GamesRepo(object):

    def __init__(self) -> None:
        self.repo = {}

    async def get_available_games(self):
        return self.repo.keys()

    async def add_game(self, game: Callable[[], Event]) -> None:
        self.repo[game.__name__] = game  # TODO: currently assumes 'game' is a class

    def __getitem__(self, item: str) -> Event:
        return self.repo[item]

    async def load_games(self):
        # TODO stubbed
        await self.add_game(RandomWinsGame)


class GameInfo(Serializable):

    members = Serializable.members + (
        ('name', str),
        ('game', str)
    )

    def __init__(self, name: str, game: str):
        self.name = name
        self.game = game


class GameLobby(object):

    def __init__(self, host: Client, game_info: GameInfo, io_loop: IOLoop = None):
        self.io_loop = io_loop if io_loop is not None else IOLoop.current()
        self.host = host
        self.players = [host]
        self.game_info = game_info
        self.io_loop.spawn_callback(self.loop)

    async def loop(self):
        # TODO completely
        for player in self.players:
            await player.send(InfoMessage('You are in the game lobby!'))


class OpenGamesRepo(object):

    def __init__(self, games_repo=GamesRepo):
        self.repo = {}
        self.games_repo = games_repo

    async def get_available_games(self):
        return await self.games_repo.get_available_games()

    async def open_game(self, game_info: GameInfo, lobby: GameLobby):
        self.repo[game_info] = lobby

    async def get_game(self, game_info: GameInfo) -> GameLobby:
        return self.repo[game_info]

    async def get_all_games(self) -> Iterable[GameInfo]:
        return self.repo.keys()

    async def get_public_games(self) -> Iterable[GameInfo]:
        return self.repo.keys()

    async def get_pw_games(self) -> Iterable[GameInfo]:
        return []


class WelcomeHandler(object):

    def __init__(self, client: Client, open_games: OpenGamesRepo, games: GamesRepo, io_loop: IOLoop = None):
        self.io_loop = io_loop if io_loop is not None else IOLoop.current()
        self.client = client
        self.open_games = open_games
        self.games = games
        log.debug("Making handler for client '{}'.", self.client.username)

    async def do_welcome(self):
        log.debug("do_welcome on user '{}'.", self.client.username)
        # TODO completely
        await self.client.send(InfoMessage('Welcome!'))
        await self.client.send(ChoiceMessage(
            'What would you like to do?',
            ('new_game', 'join_game')
        ))
        resp = await self.client.receive(ChoiceResponseMessage)
        if resp.choice == 'join_game':
            await self.client.send(ChoiceMessage(
                'Which game do you want to join?',
                (str(x) for x in await self.open_games.get_public_games())
            ))
            # TODO if no games are open etc.
        if resp.choice == 'new_game':
            await self.client.send(ChoiceMessage(
                'What game do you want to play?',
                (x for x in await self.games.get_available_games())
            ))
            game_resp = await self.client.receive(ChoiceResponseMessage)
            game_info = GameInfo('test_game', game_resp.choice)  # TODO
            game_lobby = GameLobby(self.client, game_info, self.io_loop)
            await self.open_games.open_game(game_info, game_lobby)


class Lobby(ILobby):

    def __init__(self, io_loop: IOLoop = IOLoop.current()):
        # TODO: Recover dbs (known users, loadable games ecc.)
        self.active_clients = {}  # type: Dict[str, Client]
        self.io_loop = io_loop
        self.running = False
        self.games = GamesRepo()
        self.open_games = OpenGamesRepo(self.games)

    def run(self):
        server = TornadoTCPServer(self, io_loop=self.io_loop)
        server.start_listening()

    async def welcome_client(self, client: Client):
        await self.games.load_games()
        log.debug("Welcoming client '{}'.", client.username)
        handler = WelcomeHandler(client, self.open_games, self.games, self.io_loop)
        self.io_loop.spawn_callback(handler.do_welcome)

    async def query_public_key(self, username: str) -> PublicKey:
        """Return either the public key or None if unknown user."""
        pass  # TODO

    async def save_public_key(self, username: str, public_key: PublicKey) -> None:
        pass

    async def accept_new_client(self, stream: IOStream, client_details):
        log.info('New client connected. Client data is {}.', client_details)
        new_connection = SocketConnection(stream)
        try:
            # TODO should check username for duplication
            client_builder = ClientBuilder(
                new_connection,
                ClientDetails(address=client_details[0], port=client_details[1])
            )
            await client_builder.do_handshake()
            client_key = await self.query_public_key(client_builder.username)
            await client_builder.exchange_keys(client_key)
            await self.save_public_key(client_builder.username, client_key)
            client = client_builder.build()
            self.active_clients[client.username] = client
            log.debug("Client {} added to clients.", client.username)
            await self.welcome_client(client)
        except ClientException as e:
            log.warning('Client refused: {}.', e)

    def start_new_game(self, game: Event, players: List[Player], clients: List[Client]):
        # TODO metadata for game setup
        game = Game(game, players, clients)
        game.start_game()  # TODO: should be spawn_callback to have it as a separate context.
