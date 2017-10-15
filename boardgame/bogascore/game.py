"""Core machinery"""

from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from bogascore.communication.client import Client
from bogascore.elements import Element, StrPlayerChoice
from bogascore.environment import Environment, NewElementModification, EnvModification, Player, PlayerWinsModification, \
    NullModification

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"


class SerialHaving(object):

    def __init__(self, serial: int) -> None:
        self._serial = serial
        super(SerialHaving, self).__init__()

    @property
    def serial(self):
        return self.serial

    @serial.setter
    def serial(self, new_serial: int) -> None:
        if self.serial is not None:
            raise ValueError('Serial of SerialHaving {} is already set.'.format(self))
        self.serial = new_serial


class EventEffectArguments(object):
    # TODO
    pass


class Event(SerialHaving, metaclass=ABCMeta):

    def __init__(self, serial: int):
        super(Event, self).__init__(serial)

    def run(self, env: Environment) -> None:
        args = self.compute_arguments(env)
        mod = self.apply_effects(env, **args)
        env.accept(mod)

    @abstractmethod
    def compute_arguments(self, env: Environment) -> Dict[str, Any]:
        pass

    @abstractmethod
    def apply_effects(self, **kwargs) -> EnvModification:
        pass


class ChainEvent(Event):

    def __init__(self, serial: int, events: List['Event']):
        super(ChainEvent, self).__init__(serial)
        self.chain = events

    def run(self, env: Environment) -> None:
        for event in self.chain:
            event.run(env)

    def compute_arguments(self, env: Environment):
        # Not necessary, doesn't work like that
        pass

    def apply_effects(self, **kwargs):
        # Not necessary, doesn't work like that
        pass


class MakeElement(Event):

    def __init__(self, serial: int, element: Element):
        super(MakeElement, self).__init__(serial)
        self.element = element

    def compute_arguments(self, env: Environment):
        return {}

    def apply_effects(self, env: Environment, **kwargs) -> EnvModification:
        element_class = type(self.element)
        return NewElementModification(
            element_class,
            tuple((k, getattr(self.element, k)) for k, _ in element_class.members)
        )


class PlayerWins(Event):

    def __init__(self, player: Optional[List[Player]], serial: int, may_abort: bool = False):
        super(PlayerWins, self).__init__(serial)
        self.player = player
        self.may_abort = may_abort

    def compute_arguments(self, env: Environment):
        return {}

    def apply_effects(self, env, **kwargs) -> EnvModification:
        if self.player is None or not self.player:
            if not self.may_abort:
                raise ValueError('Expected non null player in event {}'.format(self.serial))
            else:
                return NullModification()
        return PlayerWinsModification(self.player)


class PlayerChooses(Event):

    def __init__(self, serial, alternatives: Tuple[Any], player: Player):
        super(PlayerChooses, self).__init__(serial)
        self.alternatives = alternatives
        self.player = player

    def compute_arguments(self, env: Environment) -> Dict[str, Any]:
        client = env.fetch_client_for_player(self.player)
        client.send('Choose between {}.'. format(self.alternatives))
        # TODO hugely
        msg = client.receive()
        assert isinstance(msg, StrPlayerChoice)
        return {'choice': msg.choice}

    def apply_effects(self, **kwargs) -> EnvModification:
        output = StrPlayerChoice('choice', kwargs['choice'])
        return output


class Game(object):

    def __init__(self, event: Event, players: List[Player], clients: List[Client]):
        self.over = False

        def callback(env: Environment):
            players = env.get_players()
            print('\n**************** TESTING!!!!!! *************')
            print("\n".join([p.identifier + " is winner: " + str(p.is_winner) for p in players]))
            self.over = True

        self.env = Environment(callback, clients)
        for player in players:
            self.env.make_player(player)
        self.game = event

    def start_game(self):
        while not self.over:
            self.game.run(self.env)
