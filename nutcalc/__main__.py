from . import parser
from . import repl
from . import syntax
from .interpret import Interpreter, InterpretationError

import os.path as ospath
import sys

### REAL MAIN ###

interpreter = Interpreter()

def parse_and_execute(interpreter, path):
    with open(path) as f:
        module = parser.file_module(f)
        for imp in module.imports:
            parse_and_execute(
                interpreter,
                ospath.join(ospath.dirname(path), imp.path + '.nut'),
            )
        interpreter.load_module(path, module)

INTERACTIVE = False

try:
    i = 1
    while i < len(sys.argv) - 1:
        arg = sys.argv[i]
        if arg == '-i':
            INTERACTIVE = True
        if arg == '-c':
            stmt = parser.stmt.parse(sys.argv[i+1])
            interpreter.execute(stmt)
            i += 1
        else:
            parse_and_execute(interpreter, arg)
        i += 1

except InterpretationError as e:
    print('error:', e)
    sys.exit(1)
else:
    if INTERACTIVE:
        repl.start(interpreter)
