from . import parser, interpret

import readline
import sys
import os
import atexit

from parsy import ParseError

HISTORY_FILE_PATH = os.path.join(os.path.expanduser("~"), ".nutcalc_history")

def load_history():
    try:
        readline.read_history_file(HISTORY_FILE_PATH)
    except FileNotFoundError:
        pass

def save_history():
    readline.write_history_file(HISTORY_FILE_PATH)

def start(interpreter: interpret.Interpreter | None = None):
    if interpreter is None:
        interpreter = interpret.Interpreter()

    load_history()
    try:
        while True:
            user_input = input("nutcalc> ")
            if user_input.strip().lower() == "exit":
                break

            if user_input.strip().lower() == "debug":
                import pdb;pdb.set_trace()
                continue

            try:
                stmt = parser.stmt.parse(user_input)
            except ParseError as e:
                print('error:', e)
                continue

            try:
                interpreter.execute(stmt)
            except interpret.InterpretationError as e:
                print('error:', e)

    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        save_history()

