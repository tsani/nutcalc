import { useEffect, useRef, useState } from 'preact/hooks';
import { Terminal } from '@xterm/xterm';
import '@xterm/xterm/css/xterm.css';

export default function Repl({ onLineEnter: handleLineEnter }) {
    const terminalRef = useRef(null);
    const xterm = useRef(null);

    useEffect(() => {
        if (!terminalRef.current) return;
        

        xterm.current = new Terminal();
        xterm.current.open(terminalRef.current);
        xterm.current.write("Welcome to Nutcalc!\r\n\r\n> ");
        xterm.current.onData(handleInput);

        return () => {
            xterm.current.dispose();
        };

    }, [terminalRef]);
    
    const cursorPosition = useRef(0);
    const inputBuffer = useRef("");
    
    const handleInput = (input) => {
        if (input === "\r") {
            xterm.current.write("\r\n");
            handleLineEnter(inputBuffer.current);
            inputBuffer.current = "";
            cursorPosition.current = 0;
            xterm.current.write("> ");
            return;
        }
        else if (input === BACKSPACE)
        xterm.current.write(input);
        inputBuffer.current += input;
    };
    
    return <div ref={terminalRef} />;
}
//         return () => {
//             xterm.current.dispose();
//         };
// 
//     }, [terminalRef]);
//     
//     const cursorPosition = useRef(0);
//     const inputBuffer = useRef("");
//     const history = useRef([]);
//     
//     const handleInput = (input) => {
//         if (input === "\r") {
//             xterm.current.write("\r\n");
//             handleLineEnter(inputBuffer.current);
//             inputBuffer.current = "";
//             cursorPosition.current = 0;
//             xterm.current.write("> ");
//             return;
//         }
//         else if (input === BACKSPACE)
//         xterm.current.write(input);
//         inputBuffer.current += input;
//     };
//     
//     return <div ref={terminalRef} />;
// }