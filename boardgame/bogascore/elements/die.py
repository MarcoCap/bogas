"""Dice-related events, elements and classes"""

from random import randint

from bogascore.elements import Element
from bogascore.environment import NewElementModification
from bogascore.game import MakeElement

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"


class Die(Element):

    __slots__ = [
        'faces',
        'number'
    ]

    def __init__(self, identifier: str, faces: int, number: int = -1):
        super(Die, self).__init__(identifier)
        self.faces = faces
        self.number = number
        if self.number == -1:
            self.roll()

    def roll(self):
        self.number = randint(1, self.faces)


class MakeDie(MakeElement):

    def __init__(self, serial: int, identifier: str, faces: int, number: int = -1):
        super(MakeDie, self).__init__(serial, Die(identifier, faces, number))


class NewDie(NewElementModification):

    def __init__(self, identifier: str, faces: int, number: int = -1):
        super(NewDie, self).__init__(Die(identifier, faces, number))
