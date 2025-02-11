import { useRef, useEffect } from "preact/hooks";

export interface Nutcalc {
  request: <T, R>(data: T, key?: string) => Promise<R>;
  eval: (id: string, contents: string) => Promise<string>;
  loadModule: (id: string, name: string, contents: string) => Promise<string>;
  reset: () => Promise<void>;
}

export default function useNutcalc(): Nutcalc {
  const continuations = useRef(new Map());
  const nutcalcReady = useRef(undefined);

  useEffect(() => {
    document.addEventListener("nutcalc_from", handleFromNutcalc);
    document.addEventListener("nutcalc_ready", handleNutcalcReady);

    return () => {
      document.removeEventListener("nutcalc_from", handleFromNutcalc);
      document.removeEventListener("nutcalc_ready", handleNutcalcReady);
    };
  });

  function handleNutcalcReady(e: CustomEvent) {
    const rr = nutcalcReady.current;
    if ("undefined" === typeof rr) return;
    const { resolve, reject: _reject } = rr;
    nutcalcReady.current = undefined;
    resolve();
  }

  function handleFromNutcalc(e: CustomEvent) {
    const msg = e.detail;
    console.log(msg);
    switch (msg.type) {
      case "response":
        if (!continuations.current.has(msg["of"])) {
          console.error("unknown continuation: " + msg["of"]);
          return;
        }
        const payload = msg.data;
        const k = continuations.current.get(msg["of"]);
        continuations.current.set(msg["of"], null);
        return payload.success
          ? k.onSuccess(payload.data)
          : k.onFailure(payload.error);
      default:
        console.warn("unknown Nutcalc message type: " + msg.type);
    }
  }

  const sendToNutcalc = (data: any, key = "nutcalc_to") => {
    console.log(`Send ${key}`, data);
    document.dispatchEvent(new CustomEvent(key, { detail: data }));
  };

  const nutcalc: Nutcalc = {
    request: (data: any, key = "nutcalc_to"): Promise<any> =>
      new Promise((resolve, reject) => {
        if ("undefined" === typeof data?.id) throw Error("damn");
        continuations.current.set(data.id, {
          onSuccess: resolve,
          onFailure: reject,
        });
        sendToNutcalc(data, key);
      }),

    eval: (id: string, contents: string): Promise<string> =>
      nutcalc.request({ type: "eval", id, contents }),

    loadModule: (id: string, name: string, contents: string): Promise<any> =>
      nutcalc.request({ type: "load-module", id, name, contents }),

    reset: (): Promise<void> =>
      new Promise((resolve, reject) => {
        if ("undefined" !== typeof nutcalcReady.current) {
          console.warn("Nutcalc reset already in progress.");
          resolve();
        }
        nutcalcReady.current = { resolve, reject };
        continuations.current.clear();
        sendToNutcalc({}, "nutcalc_reset");
      }),
  };

  return nutcalc;
}
