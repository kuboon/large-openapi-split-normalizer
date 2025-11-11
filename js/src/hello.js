import { readFile } from 'fs/promises';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

export async function loadHelloWasm() {
  // Load the WASM file
  const wasmPath = resolve(__dirname, '../../core/target/wasm/release/hello.wasm');
  const wasmBuffer = await readFile(wasmPath);
  
  // Instantiate the WASM module
  const wasmModule = await WebAssembly.instantiate(wasmBuffer, {
    // Import object if needed
  });
  
  return wasmModule.instance.exports;
}

export class Hello {
  constructor(wasmExports) {
    this.exports = wasmExports;
    this.memory = wasmExports.memory;
  }
  
  greet(name) {
    // Encode the name string to UTF-8 bytes
    const encoder = new TextEncoder();
    const nameBytes = encoder.encode(name);
    
    // Write name to WASM memory at offset 0
    const namePtr = 0;
    const memoryView = new Uint8Array(this.memory.buffer);
    memoryView.set(nameBytes, namePtr);
    
    // Call the WASM greet function
    const resultPtr = this.exports.greet(namePtr, nameBytes.length);
    const resultLen = this.exports.greet_len(nameBytes.length);
    
    // Read the result from WASM memory
    const resultBytes = memoryView.slice(resultPtr, resultPtr + resultLen);
    const decoder = new TextDecoder();
    return decoder.decode(resultBytes);
  }
  
  add(a, b) {
    return this.exports.add(a, b);
  }
}
