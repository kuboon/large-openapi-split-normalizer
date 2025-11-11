# JavaScript Bindings for MoonBit WASM Module

JavaScript/Node.js bindings for the MoonBit hello WASM module.

## Requirements

- Node.js v18 or higher

## Installation

No dependencies required - uses Node.js built-in WebAssembly support.

## Usage

```javascript
import { loadHelloWasm, Hello } from './src/hello.js';

// Load the WASM module
const wasmExports = await loadHelloWasm();
const hello = new Hello(wasmExports);

// Use the functions
console.log(hello.greet('World'));  // Output: "Hello, World!"
console.log(hello.add(5, 3));       // Output: 8
```

## Testing

```bash
npm test
```

## API

### `loadHelloWasm()`

Loads the WASM module and returns the exports.

**Returns:** `Promise<WebAssembly.Exports>`

### `class Hello`

#### `constructor(wasmExports)`

Creates a new Hello instance.

**Parameters:**
- `wasmExports` - The WebAssembly module exports

#### `greet(name: string): string`

Returns a greeting message.

**Parameters:**
- `name` - The name to greet

**Returns:** A string like "Hello, {name}!"

#### `add(a: number, b: number): number`

Adds two numbers.

**Parameters:**
- `a` - First number
- `b` - Second number

**Returns:** The sum of a and b

## Building the WASM Module

The WASM module must be built first:

```bash
cd ../core
moon build --target wasm
```

This creates `../core/target/wasm/release/hello.wasm`
