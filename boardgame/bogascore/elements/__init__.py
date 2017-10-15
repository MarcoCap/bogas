"""Package containing Element base classes"""
from typing import Tuple

from bogascore.serialization.serialization import Serializable

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"


class Element(Serializable):

    members = Serializable.members + (
        ('identifier', str),
    )

    def __init__(self, identifier):
        self.identifier = identifier


class NumberResult(Element):

    members = (
        ('identifier', str),
        ('number', int),
        ('classifiers', tuple),
        ('orders', tuple)
    )

    private_members = (
        'classifiers_dict',
    )

    def __init__(self, identifier: str, number: int, classifiers: Tuple[str, ...], orders: Tuple[int, ...]):
        super(NumberResult, self).__init__(identifier)
        self.number = number
        self.classifiers = classifiers
        self.orders = orders
        self.classifiers_dict = dict(zip(classifiers, orders))


class StrPlayerChoice(Element):

    members = Element.members + (
        ('choice', str),
    )

    def __init__(self, identifier: str, choice: str):
        super(StrPlayerChoice, self).__init__(identifier)
        self.choice = choice
