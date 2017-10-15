"""Extremely simple games meant for testing."""
from typing import Callable, List

from bogascore.elements import Element, NumberResult, StrPlayerChoice
from bogascore.environment import Environment, EnvModification, PlayerWinsModification, Player, PlayerLosesModification, \
    NullModification
from bogascore.events.dice import RollDie
from bogascore.game import PlayerWins, ChainEvent, Event

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"


class RandomPlayerWins(PlayerWins):

    def __init__(self, serial):
        super(RandomPlayerWins, self).__init__(None, serial)

    def compute_arguments(self, env: Environment):
        result = env.elements['roll'].number
        players = list(env.get_players())
        self.player = players[result % len(players)]
        return {}


class RandomWinsGame(ChainEvent):

    def __init__(self):
        chain = [RollDie(1, 20), RandomPlayerWins(2)]
        super(RandomWinsGame, self).__init__(0, chain)


class IfConditionOnElementsWins(Event):

    def __init__(self, serial,
                 player: Player,
                 condition: Callable[[List[Element]], bool],
                 elements: List[str],
                 else_loses=False):
        super(IfConditionOnElementsWins, self).__init__(serial)
        self.player = player
        self.else_loses = else_loses
        self.condition = condition
        self.elements = elements
        self.effect = None

    def apply_effects(self, **kwargs) -> EnvModification:
        if self.effect is None:
            raise ValueError('Trying to apply None effect in Event {}.'.format(self.serial))
        return self.effect

    def compute_arguments(self, env: Environment):
        actual_elements = [env.elements[n] for n in self.elements]
        result = self.condition(actual_elements)
        if result:
            self.effect = PlayerWinsModification([self.player])
        else:
            if self.else_loses:
                self.effect = PlayerLosesModification([self.player])
            else:
                self.effect = NullModification()


class IfOddWinsGame(ChainEvent):

    def __init__(self, player: Player):

        def condition(elements: List[Element]):
            if len(elements) != 2:
                raise ValueError('Expected 2 arguments to condition in event {}.'.format(self.serial))
            number, choice = elements
            if not isinstance(number, NumberResult):
                raise ValueError('Expected NumberResult as first argument in event {}.'.format(self.serial))
            if not isinstance(number, StrPlayerChoice):
                raise ValueError('Expected StrPlayerChoice as first argument in event {}.'.format(self.serial))
            if choice.content == 'odd':
                if number.number % 2 == 1:
                    return True
                else:
                    return False
            elif choice.content == 'even':
                if number.number % 2 == 0:
                    return True
                else:
                    return False

        chain = [
            PlayerChooses(1, ('odd', 'even')),
            RollDie(2, 20),
            IfConditionOnElementsWins(3, player=player,
                                      condition=condition,
                                      elements=['roll', 'choice'],
                                      else_loses=True)
        ]

        super(IfOddWinsGame, self).__init__(0, chain)