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

try:
    for arg in sys.argv[1:]:
        parse_and_execute(interpreter, arg)
except InterpretationError as e:
    print('error:', e)
    sys.exit(1)
else:
    repl.start(interpreter)
