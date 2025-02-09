import { render } from "preact";
import { useRef, useState, useEffect } from "preact/hooks";

import Editor, { useMonaco, loader } from "@monaco-editor/react";
import * as monaco from 'monaco-editor';

import Repl, { ReplManager } from './Repl';

import "./style.css";

export function App() {
  const editorRef = useRef(null);
  const monacoRef = useRef(null);
  const repl = useRef(null);
  const continuations = useRef(new Map());
  const nutcalcReady = useRef(undefined);
  // ^ otherwise holds a resolve/reject pair for a promise waiting for nutcalc to ready

  function handleEditorMount(editor, monacoInstance) {
    editorRef.current = editor;
    monacoRef.current = monacoInstance;

    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, async () => {
      await loadRootModule();
      repl.current?.focus();
    });
  }

  useEffect(() => {
    document.addEventListener("nutcalc_from", handleFromNutcalc);
    document.addEventListener("nutcalc_ready", handleNutcalcReady);

    return () => {
      document.removeEventListener("nutcalc_from", handleFromNutcalc);
      document.removeEventListener("nutcalc_ready", handleNutcalcReady);
    }
  });

  function handleNutcalcReady(e : CustomEvent) {
    const rr = nutcalcReady.current;
    if ('undefined' === typeof(rr)) return;
    const { resolve, reject: _reject } = rr;
    nutcalcReady.current = undefined;
    resolve();
  }

  function handleFromNutcalc(e: CustomEvent) {
    const msg = e.detail;
    console.log(msg);
    switch (msg.type) {
      case "response":
        if (!continuations.current.has(msg['of'])) {
          console.error('unknown continuation: ' + msg['of']);
          return;
        }
        const payload = msg.data;
        const k = continuations.current.get(msg['of']);
        continuations.current.set(msg['of'], null);
        return payload.success ?
          k.onSuccess(payload.data) :
          k.onFailure(payload.error)
      default:
        console.warn('unknown Nutcalc message type: ' + msg.type);
    }
  }

  const sendToNutcalc = (data: any, key = "nutcalc_to") => {
    console.log(`Send ${key}`, data);
    document.dispatchEvent(new CustomEvent(key, { detail: data }));
  }

  const nutcalc = {
    request: (data: any, key = "nutcalc_to"): Promise<any> =>
      new Promise((resolve, reject) => {
        if ('undefined' === typeof(data?.id)) throw Error('damn');
        continuations.current.set(data.id, { onSuccess: resolve, onFailure: reject });
        sendToNutcalc(data, key);
      }),

    eval: (id: string, contents: string): Promise<any> =>
      nutcalc.request({ type: 'eval', id, contents }),

    loadModule: (id: string, name: string, contents: string): Promise<any> =>
      nutcalc.request({ type: 'load-module', id, name, contents }),

    reset: (): Promise<void> =>
      new Promise((resolve, reject) => {
        if ('undefined' !== typeof(nutcalcReady.current)) {
          console.warn('Nutcalc reset already in progress.')
          resolve();
        }
        nutcalcReady.current = { resolve, reject };
        continuations.current.clear();
        sendToNutcalc({}, 'nutcalc_reset');
      }),
  };

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

  const handleLineEnter = (line: string) => {
    console.log('got line enter', line);
    return nutcalc.eval('lineEnter', line);
  }

  const handleReplLoaded = (manager: ReplManager) => {
    repl.current = manager;
  };

  return (
    <>
      <h1> Nutcalc </h1>
      <div id="main">
        <div className="nutcalc-editor">
          <Editor
            options={EDITOR_OPTIONS}
            onMount={handleEditorMount}
          />
          <button onClick={loadRootModule}>Load</button>
        </div>
        <Repl onLineEnter={handleLineEnter} onLoaded={handleReplLoaded} />
      </div>
    </>
  );
}

const EDITOR_OPTIONS = {
  minimap: { enabled: false },
};

render(<App />, document.getElementById("app"));
