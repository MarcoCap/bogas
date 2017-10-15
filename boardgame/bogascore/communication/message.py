"""Messages exchanged between client and server"""

from typing import Dict, TypeVar, Iterable
from typing import Type

from bogascore.serialization.serialization import Serializable, Primitive, resolve_class_name

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"

S = TypeVar('S', bound='Message')


class Message(Serializable):

    @staticmethod
    def parse_message(v: Dict[str, Primitive]) -> S:
        t_name = v['msg_type']
        t = resolve_class_name(t_name)  # type: Type[Message]
        output = t.deserialize(v)
        return output

    members = Serializable.members + (
        ('msg_type', 'type'),
    )

    def __init__(self, msg_type: type = None):
        self.msg_type = msg_type if msg_type is not None else type(self)

    def __str__(self) -> str:
        s = type(self).__name__ + "["
        s += ",".join((member[0] + ":" + str(getattr(self, member[0])) for member in self.members))
        s += "]"
        return s

    def p_print(self) -> str:
        s = type(self).__name__ + "[\n\t"
        s += ",\n\t".join((
            member[0] + ": " + str(getattr(self, member[0]))
            for member in type(self).members
            if member[0] != 'msg_type'
        ))
        s += "\n]"
        return s


class InfoMessage(Message):

    members = Message.members + (
        ('text', str),
    )

    def __init__(self, text: str, msg_type: type = None):
        super().__init__(msg_type)
        self.text = text


class MultiMessage(Message):

    members = Message.members + (
        ('messages', list),
    )

    def __init__(self, messages: list, msg_type: type = None):
        super(MultiMessage, self).__init__(msg_type)
        self.messages = messages


class ChoiceMessage(Message):

    members = Message.members + (
        ('description', str),
        ('choices', list)
    )

    def __init__(self, description: str, choices: Iterable[str], msg_type: type = None):
        super(ChoiceMessage, self).__init__(msg_type)
        self.description = description
        self.choices = list(choices)


class ChoiceResponseMessage(Message):

    members = Message.members + (
        ('choice', str),
    )

    def __init__(self, choice: str, msg_type: type = None):
        super(ChoiceResponseMessage, self).__init__(msg_type)
        self.choice = choice
