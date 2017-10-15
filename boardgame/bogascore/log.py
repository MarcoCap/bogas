"""Logging setup"""

import logging

import sys
import re

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "1.0"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"


class BracesAdapter(logging.LoggerAdapter):
    """Allows the use of the {} syntax while in logging calls."""
    BRACES_PATTERN = re.compile(r'{([a-zA-Z0-9]+)?(:[ +]?\d*(\.\d+)?[df])?}')

    @staticmethod
    def substitute(m):
        output = '%'
        if m.group(1) is not None:
            output += '(' + m.group(1) + ')'
        if m.group(2) is not None:
            output += m.group(2).lstrip(':')
        else:
            output += 's'
        return output

    def process(self, msg, kwargs):
        new_msg = self.BRACES_PATTERN.sub(self.substitute, msg)
        return new_msg, kwargs


class ShortFormatter(logging.Formatter):
    """Basic pipe-separated format, with fixed column width."""

    def __init__(self):
        super(ShortFormatter, self).__init__(
            fmt='%(asctime)s | %(levelname)8.8s | '
                '%(name)30.30s | %(message)s',
            datefmt='%H:%M:%S')

    def format(self, record):
        record.name = '.'.join(record.name.split('.')[2:])
        return super(ShortFormatter, self).format(record)


handler = logging.StreamHandler(sys.stdout)
handler.setLevel(1)
formatter = ShortFormatter()
handler.setFormatter(formatter)
logging.basicConfig(handlers=[handler], level=logging.DEBUG)
logging.getLogger('').setLevel(logging.ERROR)

_logger = logging.getLogger("Agent")

root_log = BracesAdapter(_logger, extra={})

root_log.setLevel(logging.DEBUG)


def get_logger(name, extra=None):
    # type: (str) -> logging.LoggerAdapter
    if extra is None:
        extra = {}
    return BracesAdapter(_logger.getChild(name), extra=extra)
