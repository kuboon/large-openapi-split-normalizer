# Python Bindings for MoonBit WASM Module

Python bindings for the MoonBit hello WASM module using the Wasmtime package.

## Requirements

- Python 3.9 or higher

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from src.hello import Hello

# Create a new Hello instance
hello = Hello()

# Use the functions
print(hello.greet('World'))  # Output: "Hello, World!"
print(hello.add(5, 3))       # Output: 8
```

## Testing

```bash
pytest
```

Or with verbose output:

```bash
pytest -v
```

## API

### `class Hello`

#### `__init__()`

Creates a new Hello instance and loads the WASM module.

#### `greet(name: str) -> str`

Returns a greeting message.

**Parameters:**
- `name` - The name to greet

**Returns:** A string like "Hello, {name}!"

#### `add(a: int, b: int) -> int`

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

## Dependencies

- `wasmtime` (>=26.0.0) - WebAssembly runtime
- `pytest` (>=8.0.0) - Testing framework
