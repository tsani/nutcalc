import { render } from "preact";
import { useRef } from "preact/hooks";

import Editor, { OnMount } from "@monaco-editor/react";

import Repl, { ReplManager } from "./Repl";
import useNutcalc from "./hooks/useNutcalc";
import useLocalStorage from "./hooks/useLocalStorage";
import EDITOR_STARTER_CODE from "./starter-code";

import "./style.css";

export function App() {
  const editorRef = useRef(null);
  const monacoRef = useRef(null);
  const repl = useRef(null);
  const nutcalc = useNutcalc();
  const [editorContent, setEditorContent] = useLocalStorage(
    "editor-module-root",
    EDITOR_STARTER_CODE,
    1000,
  );

  const handleEditorMount: OnMount = (editor, monaco) => {
    console.log('editor mounted');
    setupNutcalcLanguage(monaco);

    editorRef.current = editor;
    monacoRef.current = monaco;

    editor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
      async () => {
        await loadRootModule();
        repl.current?.focus();
      },
    );

    editor.onDidChangeModelContent(() => {
      setEditorContent(editor.getValue());
    });
  };

  async function loadModule(name: string, contents: string): Promise<void> {
    await nutcalc.reset();
    let output = "";
    try {
      output = await nutcalc.loadModule(
        "loadModule",
        "root",
        editorRef.current.getValue() ?? "",
      );
    } catch (e) {
      output = e?.toString();
    }
    output = output || "Module loaded";
    repl.current?.paste(output);
  }

  const loadRootModule = () =>
    loadModule("root", editorRef.current.getValue() ?? "");

  return (
    <>
      <h1> Nutcalc </h1>
      <div id="main">
        <div className="nutcalc-editor">
          <Editor
            language="nutcalc"
            theme="solarized-light"
            options={EDITOR_OPTIONS}
            onMount={handleEditorMount}
            value={editorContent}
          />
        </div>
        <Repl
          onLineEnter={(line: string) => nutcalc.eval("lineEnter", line)}
          onEscape={() => editorRef.current?.focus()}
          onLoaded={(x: ReplManager) => (repl.current = x)}
        />
      </div>
    </>
  );
}

const EDITOR_OPTIONS = {
  minimap: { enabled: false },
};

function setupNutcalcLanguage(monaco) {
  monaco.languages.register({ id: 'nutcalc' });
  monaco.languages.setMonarchTokensProvider("nutcalc", {
    tokenizer: {
      root: [
        ["#.*", "comment"],
        ["\\b(import|weighs)\\b", "keyword"],
        ["[:=-]", "delimiter"],
        ["[+*/]", "operator"],
        ["\\d+(\\.\\d+)?", { token: "number", next: "@unit" }],
        // ["'[^']*'", "string"],
        // ["\"[^\"]*\"", "string"],
        ["\\b[a-zA-Z][0-9a-zA-Z]*\\b", "identifier"],
      ],
      unit: [
        ["\\s+", "white"],
        ["'[^']*'", { token: "type", next: "@food" }],
        ['"[^"]*"', { token: "type", next: "@food" }],
        ["\\b[a-zA-Z][0-9a-zA-Z]*\\b", { token: "type", next: "@food" }],
        ["", "", "@pop"],
      ],
      food: [
        ["\\s+", "white"],
        ["'[^']*'", "function"],
        ['"[^"]*"', "function"],
        ["\\b[a-zA-Z][0-9a-zA-Z]*\\b", "function"],
        ["", "", "@pop"],
      ],
    },
  });
  monaco.editor.defineTheme('solarized-light', {
    base: 'vs', // 'vs' is the default light theme
    inherit: true,
    rules: [
      { token: 'keyword', foreground: '859900', fontStyle: 'bold' }, // Green
      { token: 'number', foreground: '2aa198' }, // Cyan
      { token: 'string', foreground: '2aa198' }, // Cyan
      { token: 'comment', foreground: '93a1a1', fontStyle: 'italic' }, // Base1
      { token: 'identifier', foreground: '586e75' }, // Base00
      // { token: 'delimiter', foreground: '657b83' }, // Base0
      { token: 'delimiter', foreground: 'd33682' }, // Magenta
      { token: 'type', foreground: 'b58900' }, // Yellow
      { token: 'function', foreground: '268bd2' }, // Blue
      { token: 'variable', foreground: 'cb4b16' }, // Orange
      { token: 'operator', foreground: '6c71c4' }, // Violet
      { token: 'constant', foreground: 'd33682' }, // Magenta
    ],
    colors: {
      'editor.foreground': '#657b83', // Base0
      'editor.background': '#fdf6e3', // Base3
      'editorCursor.foreground': '#586e75', // Base00
      'editor.selectionBackground': '#eee8d5', // Base2
      'editor.lineHighlightBackground': '#eee8d5', // Base2
      'editor.selectionHighlightBackground': '#93a1a144', // Base1 (transparent)
      'editor.inactiveSelectionBackground': '#93a1a166', // Base1 (transparent)
    },
  });
  monaco.editor.setTheme('solarized-light');
}

render(<App />, document.getElementById("app"));
