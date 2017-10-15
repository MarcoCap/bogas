"""Server machinery for BOGAS"""
from abc import abstractmethod, ABCMeta

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"


class ILobby(object, metaclass=ABCMeta):

    @abstractmethod
    def accept_new_client(self, stream, client_details):
        pass
