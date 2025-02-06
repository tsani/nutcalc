
import { useEffect, useRef } from "preact/hooks";
import { Terminal } from "@xterm/xterm";
import "@xterm/xterm/css/xterm.css";

const BACKSPACE = "\u007F";
const LEFT_ARROW = "\x1B[D";
const RIGHT_ARROW = "\x1B[C";
const UP_ARROW = "\x1B[A";
const DOWN_ARROW = "\x1B[B";

export default function Repl({ onLineEnter: handleLineEnter }) {
  const terminalRef = useRef(null);
  const xterm = useRef(null);
  const history = useRef([]);
  const inputBuffer = useRef("");
  const cursorPosition = useRef(0);
  const historyIndex = useRef(-1);

  useEffect(() => {
    if (!terminalRef.current) return;

    xterm.current = new Terminal({
      cursorBlink: true,
      rows: 24,
    });

    xterm.current.open(terminalRef.current);
    xterm.current.write("Welcome to Nutcalc!\r\n\r\n> ");

    xterm.current.onData(handleInput);

    return () => {
      xterm.current.dispose();
    };
  }, []);

  /** Changes the current input mode.
   * The given callback runs on the next tick.
   */
  function switchInputMode(newMode, cb=undefined) {
    inputMode.current = newMode;
    if ('undefined' !== typeof(cb)) setTimeout(() => cb(), 0);
  }

  const baseKeyHandler = {
    [BACKSPACE]: () => {
      if (0 === cursorPosition.current) return;

      inputBuffer.current =
        inputBuffer.current.slice(0, cursorPosition.current - 1) +
        inputBuffer.current.slice(cursorPosition.current);
      cursorPosition.current--;
      const remainder = inputBuffer.current.slice(cursorPosition.current);
      xterm.current.write(
        "\b" + remainder + " \b" + times(remainder.length, LEFT_ARROW)
      );
    },

    [LEFT_ARROW]: () => {
      if (0 === cursorPosition.current) return;

      cursorPosition.current--;
      xterm.current.write(LEFT_ARROW);
    },

    [RIGHT_ARROW]: () => {
      if (cursorPosition.current === inputBuffer.current.length) return;

      cursorPosition.current++;
      xterm.current.write(RIGHT_ARROW);
    },

    [UP_ARROW]: () => {
      if (0 === history.current.length) return;

      if (historyIndex.current === -1) {
        historyIndex.current = history.current.length - 1;
      } else if (historyIndex.current > 0) {
        historyIndex.current--;
      }
      replaceCurrentInput(history.current[historyIndex.current]);
    },

    [DOWN_ARROW]: () => {
      if (0 === history.current.length) return;
      if (-1 === historyIndex.current) return;

      if (historyIndex.current + 1 < history.current.length) {
        historyIndex.current++;
        replaceCurrentInput(history.current[historyIndex.current]);
      } else {
        historyIndex.current = -1;
        replaceCurrentInput("");
      }
    },
  };

  const userInputKeyHandler = {
    ...baseKeyHandler,

    // For user input, the enter key is very special
    '\r': () => {
      history.current.push(inputBuffer.current);
      historyIndex.current = -1;
      xterm.current.write("\r\n");

      switchInputMode('blocked', async () => {
        let output;
        try {
          output = await handleLineEnter(inputBuffer.current)
        } catch(e) {
          output = 'undefined' === typeof(e) ?
            'Unknown error :(' :
            `Error: ${e?.toString() ?? 'unknown'}`;
        }
        switchInputMode("pasteInput");
        xterm.current.input(output);
        xterm.current.write("\r\n> ");
        switchInputMode("userInput");
        inputBuffer.current = "";
        cursorPosition.current = 0;
      });
    },
  };

  const inputMode = useRef('userInput'); // one of the keys in the following object
  const inputHandler = {
    userInput: (input) => {
      const handler = userInputKeyHandler[input];
      if ('undefined' !== typeof(handler))
        return handler(input);

      inputBuffer.current =
        inputBuffer.current.slice(0, cursorPosition.current) +
        input +
        inputBuffer.current.slice(cursorPosition.current);
      xterm.current.write(inputBuffer.current.slice(cursorPosition.current));
      cursorPosition.current++;
    },

    // blocked mode ignores all input
    blocked: (_input) => {
      return;
    },

    pasteInput: (input) => {
      xterm.current.write(input.replace(/\n/g, '\r\n'));
    },
  };

  const handleInput = (input) => inputHandler[inputMode.current](input);

  const replaceCurrentInput = (newInput) => {
    while (cursorPosition.current > 0) {
      xterm.current.write("\b \b");
      cursorPosition.current--;
    }
    inputBuffer.current = newInput;
    cursorPosition.current = newInput.length;
    xterm.current.write(newInput);
  };

  return <div class="nutcalc-repl" ref={terminalRef} />;
}

const times = (n, s) => {
  let out = "";
  for (let i = 0; i < n; i++) out += s;
  return out;
};