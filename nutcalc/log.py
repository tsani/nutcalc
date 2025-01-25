from . import config

import sys

def log(*msg):
    if config.VERBOSE:
        print(*msg, file=sys.stderr)
    else:
        return None
