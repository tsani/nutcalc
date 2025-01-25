from . import repl
from . import syntax
from . import config
from .interpret import Interpreter, InterpretationError
from .parser import (parse_stmt, parse_module, LocatedParseError)

import os.path as ospath
import sys

USAGE = (
    f'usage: {sys.argv[0]} [-i] [-v] [-c STMT | PATH]...\n'
    '\twhere STMT is a nutcalc statement to execute;\n'
    '\twhere PATH is a path to a .nut file to load.\n'
    '\n'
    'Executes all statements and .nut modules in order.\n'
    # 'Reads from stdin if no files or statements are specified.\n'
    '\n'
    '\t-i: start REPL afterwards\n'
    '\t-v: enable verbose output during execution\n'
)

def load_module(interpreter, path):
    """Loads a module specified by a path into the given interpreter.
    Recursively loads imported modules. No effort is made to detect import
    loops."""
    with open(path) as f:
        module = parse_module(f, source=path)
        for imp in module.imports:
            load_module(
                interpreter,
                ospath.join(ospath.dirname(path), imp.path + '.nut'),
            )
        interpreter.load_module(path, module)

def parse_args():
    targets = []

    i = 1
    while i < len(sys.argv) - 1:
        arg = sys.argv[i]

        if arg == '-h':
            print(USAGE)
            sys.exit(0)
        elif arg == '-i':
            config.INTERACTIVE = True
        elif arg == '-v':
            config.VERBOSE = True
        elif arg == '-c':
            targets.append( ('stmt', i+1, sys.argv[i+1]) )
            i += 1
        else:
            targets.append( ('module', i, arg) )
        i += 1

    return targets

def execute_targets(interpreter, targets):
    try:
        for (kind, i, target) in targets:
            if kind == 'stmt':
                stmt = parse_stmt(target, source=f'<argument {i}>')
                interpreter.execute(stmt)
            elif kind == 'module':
                load_module(interpreter, target)
    except (LocatedParseError, InterpretationError) as e:
        print('Error:', e)
        sys.exit(1)
    return interpreter

### REAL MAIN ###

targets = parse_args()
if not config.INTERACTIVE and not len(targets):
    print('Error: nothing to do')
    print(USAGE)
    sys.exit(1)

interpreter = execute_targets(Interpreter(), targets)
if config.INTERACTIVE:
    repl.start(interpreter)
