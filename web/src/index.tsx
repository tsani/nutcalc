import { render } from "preact";
import { useRef, useState, useEffect } from "preact/hooks";

import Editor, { useMonaco, loader } from "@monaco-editor/react";

import Repl from './Repl';

import "./style.css";

export function App() {
  const editorRef = useRef(null);
  const [output, setOutput] = useState('');

  function handleEditorMount(editor, monaco) {
    editorRef.current = editor;
  }

  function handleButtonClick(e) {
    document.dispatchEvent(
      new CustomEvent("nutcalc_to", {
        detail: {
          type: 'eval',
          id: 'aaaaaaa',
          contents: editorRef.current.getValue(),
        },
      })
    );
  }

  function handleFromNutcalc(e) {
    const msg = e.detail;
    console.log(msg);
    setOutput(msg?.data?.data ?? '');
  }

  useEffect(() => {
    document.addEventListener("nutcalc_from", handleFromNutcalc);
    return () =>
      document.removeEventListener("nutcalc_from", handleFromNutcalc);
  });
  
  function handleLineEnter(line) {
  }

  return (
    <>
      <h1> Nutcalc </h1>
      <div id="main">
        <Editor
          defaultLanguage="javascript"
          options={EDITOR_OPTIONS}
          onMount={handleEditorMount}
        />
        <Repl onLineEnter={handleLineEnter} />
      </div>
    </>
  );
}

const EDITOR_OPTIONS = {
  minimap: { enabled: false },
};

render(<App />, document.getElementById("app"));
