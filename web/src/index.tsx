import { render } from "preact";
import { useRef } from "preact/hooks";

import Editor, { useMonaco, loader } from "@monaco-editor/react";
import * as monaco from 'monaco-editor';

import Repl, { ReplManager } from './Repl';
import useNutcalc from "./hooks/useNutcalc";

import "./style.css";
import useLocalStorage from "./hooks/useLocalStorage";

export function App() {
  const editorRef = useRef(null);
  const monacoRef = useRef(null);
  const repl = useRef(null);
  const nutcalc = useNutcalc();
  const [editorContent, setEditorContent] = useLocalStorage('editor-module-root', '', 1000);

  function handleEditorMount(editor, monacoInstance) {
    editorRef.current = editor;
    monacoRef.current = monacoInstance;

    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, async () => {
      await loadRootModule();
      repl.current?.focus();
    });

    editor.onDidChangeModelContent(() => {
      setEditorContent(editor.getValue());
    });
  }

  async function loadModule(name: string, contents: string): Promise<void> {
    await nutcalc.reset();
    let output = "";
    try {
      output = await nutcalc.loadModule(
        'loadModule',
        'root',
        editorRef.current.getValue() ?? '',
      );
    } catch(e) {
      output = e?.toString();
    }
    output = output || 'Module loaded'
    repl.current?.paste(output);
  }

  const loadRootModule = () => loadModule('root', editorRef.current.getValue() ?? '');

  return (
    <>
      <h1> Nutcalc </h1>
      <div id="main">
        <div className="nutcalc-editor">
          <Editor
            options={EDITOR_OPTIONS}
            onMount={handleEditorMount}
            value={editorContent}
          />
          <button onClick={loadRootModule}>Load</button>
        </div>
        <Repl
          onLineEnter={(line: string) => nutcalc.eval('lineEnter', line)}
          onEscape={() => editorRef.current?.focus()}
          onLoaded={(x: ReplManager) => repl.current = x} />
      </div>
    </>
  );
}

const EDITOR_OPTIONS = {
  minimap: { enabled: false },
};

render(<App />, document.getElementById("app"));
