"""Contains the Environment class and related classes"""

from abc import abstractmethod
from collections import deque
from enum import Enum
from typing import Callable, Set, Iterable, List

from bogascore.communication.client import Client
from bogascore.communication.message import Message
from bogascore.elements import Element
from bogascore.log import get_logger

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"


logger = get_logger(__name__)


class Player(Element):

    def __init__(self, name: str):
        super(Player, self).__init__(name)
        self.is_winner = False
        self.is_loser = False


class HookTriggers(Enum):
    PRE_ACCEPT = 1
    POST_ACCEPT = 2


class EnvironmentElements(object):

    def __init__(self) -> None:
        self._dict = {}
        self._class_dict = {}

    def __getitem__(self, item: str) -> Element:
        return self._dict[item]

    def get(self, item: str, default: Element) -> Element:
        return self._dict.get(item, default)

    def add(self, element: Element) -> None:
        self._dict[element.identifier] = element
        class_name = element.__class__.__name__
        self._class_dict.setdefault(class_name, set()).add(element)

    def get_by_class(self, class_name: str) -> Set[Element]:
        return self._class_dict.get(class_name, set())

    def remove(self, element_id: str):
        del self._dict[element_id]


class Environment(object):

    def __init__(self, post_game_hook: Callable[['Environment'], None], clients: List[Client]):
        self.elements = EnvironmentElements()
        self.hooks = {
            HookTriggers.POST_ACCEPT: deque([GameOverHook(self, post_game_hook)]),
            HookTriggers.PRE_ACCEPT: deque()
        }
        self.clients = clients

    def get_players(self):
        return self.elements.get_by_class(Player.__name__)

    def make_player(self, player: Player):
        self.elements.add(player)

    def accept(self, modification: 'EnvModification'):
        logger.debug("Accepting modification %s.", modification)
        for hook in self.hooks.get(HookTriggers.PRE_ACCEPT, []):
            modification = hook(modification)
        modification.apply(self)
        for client in self.clients:
            client.send(modification)
        for hook in self.hooks.get(HookTriggers.POST_ACCEPT, []):
            hook(modification)

    def add_pre_hook(self, hook: Callable[['EnvModification'], 'EnvModification']):
        self._add_hook(HookTriggers.PRE_ACCEPT, hook)

    def add_post_hook(self, hook: Callable[['EnvModification'], None]):
        self._add_hook(HookTriggers.POST_ACCEPT, hook)

    def _add_hook(self, trigger: HookTriggers, hook: Callable):
        self.hooks[trigger].append(hook)

    def remove_hook(self, trigger: HookTriggers, hook: Callable, strict: bool = False):
        try:
            self.hooks[trigger].remove(hook)
        except ValueError as e:
            if strict:
                raise e

    def fetch_client_for_player(self, player: Player) -> Client:
        # TODO
        pass


class EnvModification(Message):

    members = Message.members

    @abstractmethod
    def apply(self, env: Environment) -> None:
        pass


class MultipleModification(EnvModification):

    members = EnvModification.members + (
        ('modifications', list),
    )

    def __init__(self, modifications: List[EnvModification], msg_type: type = None):
        super(MultipleModification, self).__init__(msg_type)
        self.modifications = modifications

    def apply(self, env: Environment) -> None:
        for mod in self.modifications:
            mod.apply()


class NullModification(EnvModification):

    members = EnvModification.members

    def apply(self, env: Environment) -> None:
        # Do nothing.
        pass


class NewElementModification(EnvModification):
    """
    The args field should be a list of couples (field_name, new value) such that
    new_element = element_class(**dict(args))

    Overwrites if the element already exists.
    Must be subclassed for specific elements.
    """

    members = EnvModification.members + (
        ('element_class', 'type'),
        ('args', list)
    )

    private_members = (
        'element'
    )

    def __init__(self, element_class: type, args: Iterable, msg_type: type = None):
        super(NewElementModification, self).__init__(msg_type)
        self.element_class = element_class
        self.args = args
        self.element = element_class(**dict(args))

    def apply(self, env: Environment) -> None:
        env.elements.add(self.element)


class ChangeElementModification(EnvModification):
    """
    The args field should be a list of couples (field_name, new value)
    containing a field if and only if this envMod changes it.
    """

    members = EnvModification.members + (
        ('element_class', 'type'),
        ('element_id', str),
        ('args', list)
    )

    def __init__(self, element_class: type, element_id: str, args: Iterable, msg_type: type = None):
        super(ChangeElementModification, self).__init__(msg_type)
        self.element_class = element_class
        self.element_id = element_id
        self.args = args

    def apply(self, env: Environment) -> None:
        old_element = env.elements[self.element_id]
        d = {}
        for k, _ in type(old_element).members:
            d[k] = getattr(old_element, k)
        d.update(self.args)
        new_element = self.element_class(**d)
        env.elements.add(new_element)


class RemoveElementModification(EnvModification):

    members = EnvModification.members + (
        ('element', Element),
    )

    def __init__(self, element: Element, msg_type: type = None):
        super(RemoveElementModification, self).__init__(msg_type)
        self.element = element

    def apply(self, env: Environment) -> None:
        env.elements.remove(self.element.identifier)


class GameOverModification(EnvModification):

    members = ()

    def apply(self, env: Environment) -> None:
        return


class PlayerWinsModification(GameOverModification):

    members = GameOverModification.members + (
        ('player', Player),
    )

    def __init__(self, player: List[Player], msg_type: type = None):
        super(PlayerWinsModification, self).__init__(msg_type)
        self.player = player

    def apply(self, env: Environment) -> None:
        for p in self.player:
            p.is_winner = True
        env.winning_player = self.player


class PlayerLosesModification(EnvModification):

    members = EnvModification.members + (
        ('player', Player),
    )

    def __init__(self, player: List[Player], msg_type: type = None):
        super(PlayerLosesModification, self).__init__(msg_type)
        self.player = player

    def apply(self, env: Environment) -> None:
        for p in self.player:
            p.is_loser = True
        if getattr(env, 'losing_players', None) is None:
            env.losing_players = set()
        env.losing_players += self.player


# noinspection PyUnusedLocal
def cancel_hook(modification: EnvModification):
    return NullModification()


class GameOverHook(object):

    __slots__ = [
        'callback',
        'env'
    ]

    def __init__(self, env: Environment, post_game_hook: Callable[[Environment], None]):
        self.callback = post_game_hook
        self.env = env

    def __call__(self, modification: EnvModification):
        if isinstance(modification, GameOverModification):
            self.callback(self.env)


class LastManStandingWins(object):

    __slots__ = [
        'players',
        'losers'
    ]

    def __init__(self, env: Environment):
        self.players = env.get_players()
        if getattr(env, 'losing_players', None) is None:
            env.losing_players = set()
        self.losers = env.losing_players

    def __call__(self, modification: EnvModification):
        if isinstance(modification, PlayerLosesModification):
            losing_players = set()
            for p in self.players:
                if getattr(p, 'is_loser', False):
                    losing_players.add(p)
            losing_players = losing_players.union(self.losers)
            losing_players = losing_players.union(modification.player)
            non_losers = self.players.difference(losing_players)
            if len(non_losers) == 1:
                logger.debug('Last Man Standing triggered on modification {}. Winner is: {}.'
                             .format(str(modification), non_losers))
                # It is a Set of players
                # noinspection PyTypeChecker
                return MultipleModification([modification, PlayerWinsModification(list(non_losers))])
            else:
                return modification

