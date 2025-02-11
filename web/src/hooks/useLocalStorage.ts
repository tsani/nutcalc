import { useState, useEffect } from "preact/hooks";

export default function useLocalStorage<R>(
  key: string,
  initialValue: R,
  debounce: number = 0,
): ReturnType<typeof useState<R>> {
  const [state, setState] = useState(() => {
    try {
      const storedValue = localStorage.getItem(key);
      return storedValue === null ? initialValue : JSON.parse(storedValue);
    } catch (error) {
      console.error("reading localstorage key", key, error);
      return initialValue;
    }
  });

  useEffect(() => {
    const doWrite = () => {
      console.log("saving");
      try {
        localStorage.setItem(key, JSON.stringify(state));
      } catch (error) {
        console.error("Error writing key to localstorage", key, error);
      }
    };

    const handler = setTimeout(doWrite, debounce);
    return () => {
      clearTimeout(handler);
    };
  }, [key, state, debounce]);

  return [state, setState];
}
