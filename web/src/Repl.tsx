import { useCallback, useEffect, useRef } from "preact/hooks";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from '@xterm/addon-fit';
import "@xterm/xterm/css/xterm.css";

const BACKSPACE = "\u007F";
const LEFT_ARROW = "\x1B[D";
const RIGHT_ARROW = "\x1B[C";
const UP_ARROW = "\x1B[A";
const DOWN_ARROW = "\x1B[B";
const CTRL_C = "\x03"; // ASCII ETX (end-of-text)

export interface ReplManager {
  /** Directly write to the underlying xterm instance. */
  write(contents: string): void;

  /** High-level write that turns \n into \r\n, and accounts for the
   * user possibly being in the middle of writing an input.
   */
  paste(contents: string): void;

  /** Register a callback to run whenever wants to run a completed input.
   * The resulting string is pasted into the terminal.
   */
  onLineEnter(callback: (line: string) => string): void;

  /** Registers a callback to run when the user requests to leave the terminal. */
  onEscape(calback: () => void): void;

  /** Destroy the underlying xterm instance. */
  dispose(): void;

  /** Focuses the REPL. */
  focus(): void;
}

const ReplManager = (xterm): ReplManager => {
  const history = [];
  let inputBuffer = "";
  let cursorPosition = 0;
  let historyIndex = -1;
  let inputMode = "userInput";
  let handleLineEnter = null;
  let handleEscape = null;

  const replaceCurrentInput = (newInput) => {
    while (cursorPosition > 0) {
      xterm.current.write("\b \b");
      cursorPosition--;
    }
    inputBuffer = newInput;
    cursorPosition = newInput.length;
    xterm.current.write(newInput);
  };

  function switchInputMode(newMode, cb = undefined) {
    inputMode = newMode;
    if ("undefined" !== typeof cb) setTimeout(() => cb(), 0);
  }

  const baseKeyHandler = {
    [BACKSPACE]: () => {
      if (0 === cursorPosition) return;

      inputBuffer =
        inputBuffer.slice(0, cursorPosition - 1) +
        inputBuffer.slice(cursorPosition);
      cursorPosition--;
      const remainder = inputBuffer.slice(cursorPosition);
      xterm.write(
        "\b" + remainder + " \b" + times(remainder.length, LEFT_ARROW),
      );
    },

    [LEFT_ARROW]: () => {
      if (0 === cursorPosition) return;

      cursorPosition--;
      xterm.write(LEFT_ARROW);
    },

    [RIGHT_ARROW]: () => {
      if (cursorPosition === inputBuffer.length) return;

      cursorPosition++;
      xterm.write(RIGHT_ARROW);
    },

    [UP_ARROW]: () => {
      if (0 === history.length) return;

      if (historyIndex === -1) {
        historyIndex = history.length - 1;
      } else if (historyIndex > 0) {
        historyIndex--;
      }
      replaceCurrentInput(history[historyIndex]);
    },

    [DOWN_ARROW]: () => {
      if (0 === history.length) return;
      if (-1 === historyIndex) return;

      if (historyIndex + 1 < history.length) {
        historyIndex++;
        replaceCurrentInput(history[historyIndex]);
      } else {
        historyIndex = -1;
        replaceCurrentInput("");
      }
    },
  };

  const userInputKeyHandler = {
    ...baseKeyHandler,

    // For user input, the enter key is very special
    "\r": () => {
      history.push(inputBuffer);
      historyIndex = -1;
      xterm.write("\r\n");

      switchInputMode("blocked", async () => {
        let output;
        try {
          console.log("hi");
          output = await handleLineEnter(inputBuffer);
        } catch (e) {
          output =
            "undefined" === typeof e
              ? "Unknown error :("
              : `Error: ${e?.toString() ?? "unknown"}`;
        }
        switchInputMode("pasteInput");
        xterm.input(output);
        xterm.write("\r\n> ");
        switchInputMode("userInput");
        inputBuffer = "";
        cursorPosition = 0;
      });
    },

    [CTRL_C]: () => {
      if (inputBuffer.length) {
        historyIndex = -1;
        xterm.write("\r\n> ");
        inputBuffer = "";
        cursorPosition = 0;
      }
      handleEscape?.();
    },
  };

  const inputHandler = {
    userInput: (input) => {
      const handler = userInputKeyHandler[input];
      if ("undefined" !== typeof handler) return handler(input);

      inputBuffer =
        inputBuffer.slice(0, cursorPosition) +
        input +
        inputBuffer.slice(cursorPosition);
      xterm.write(inputBuffer.slice(cursorPosition));
      cursorPosition++;
    },

    // blocked mode ignores all input
    blocked: (_input) => {
      return;
    },

    pasteInput: (input) => {
      console.log("input", input);
      xterm.write(input.replace(/\n/g, "\r\n"));
    },
  };

  xterm.onData((input) => inputHandler[inputMode](input));

  return {
    write(contents) {
      xterm.write(contents);
    },

    paste(contents) {
      const oldInputMode = inputMode;
      xterm.write("\r\n");
      switchInputMode("pasteInput");
      xterm.input(contents);
      xterm.write("\r\n> ");
      if (inputBuffer.length) {
        xterm.write(inputBuffer);
        xterm.write(times(inputBuffer.length - cursorPosition, "\b"));
      }
      switchInputMode(oldInputMode);
    },

    onLineEnter(callback) {
      handleLineEnter = callback;
    },

    onEscape(callback) {
      handleEscape = callback;
    },

    dispose() {
      xterm.dispose();
    },

    focus() {
      xterm.focus();
    },
  };
};

export default function Repl({
  onLineEnter: handleLineEnter,
  onLoaded: handleLoaded,
  onEscape: handleEscape,
}) {
  const terminalRef = useRef(null);
  const fitAddonRef = useRef(null);

  const resizeCallback = useCallback(() => {
    fitAddonRef.current.fit();
  }, []);

  useEffect(() => {
    if (!terminalRef.current) return;

    const xterm = new Terminal({
      cursorBlink: true,
      rows: 24,
    });
    fitAddonRef.current = new FitAddon();
    xterm.loadAddon(fitAddonRef.current);
    window.addEventListener('resize', resizeCallback);

    xterm.open(terminalRef.current);
    fitAddonRef.current.fit();
    const repl = ReplManager(xterm);
    repl.write("Welcome to Nutcalc!\r\n\r\n> ");
    repl.onLineEnter(handleLineEnter);
    repl.onEscape(handleEscape);
    handleLoaded?.(repl);
    return () => {
      repl.dispose();
      window.removeEventListener('resize', resizeCallback);
    };
  }, [terminalRef]);

  return <div class="nutcalc-repl" ref={terminalRef} />;
}

const times = (n, s) => {
  let out = "";
  for (let i = 0; i < n; i++) out += s;
  return out;
};
