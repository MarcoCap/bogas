from unittest import TestCase

from bogascore import JsonCodec
from bogascore.communication.client import Client
from bogascore.communication.connection import DirectConnection
from bogascore.environment import Player
from bogascore.examples.testgames import RandomWinsGame
from bogascore.game import Game


class TestHighestWins(TestCase):

    def test_simple_game(self):
        event = RandomWinsGame()
        players = [
            Player('pippo'),
            Player('pluto')
        ]
        remote_client = None  # TODO: should be type bogasclient.Client
        clients = [
            Client(JsonCodec(), DirectConnection(remote_client))
        ]
        game = Game(event, players)
        game.start_game()
