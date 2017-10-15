"""Package containing dice-related events"""

from bogascore.elements import NumberResult
from bogascore.elements.die import Die
from bogascore.game import MakeElement

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"


class MakeDie(MakeElement):

    def __init__(self, serial: int, identifier: str, faces: int, number: int = -1):
        super(MakeDie, self).__init__(serial, Die(identifier, faces, number))


class RollDie(MakeElement):

    def __init__(self, serial: int, faces: int):
        die = Die('temp_die', faces)
        self.element = NumberResult('roll', die.number, ('die_roll', 'number'), (0, 0))
        super(RollDie, self).__init__(serial, self.element)
