# MoonBit WASM Multi-Language Bindings

A demonstration project showing how to build a MoonBit WebAssembly module and bind it to multiple programming languages (JavaScript, Ruby, and Python).

## Project Overview

This project provides a simple "hello world" WASM module implemented in MoonBit, with bindings for:
- **JavaScript** (Node.js)
- **Ruby** (using Wasmtime)
- **Python** (using Wasmtime)

The core functionality includes:
- `greet(name)` - Returns a greeting message
- `add(a, b)` - Adds two integers

## Project Structure

```
.
├── core/                    # MoonBit source code and WASM build
│   ├── src/lib/
│   │   └── hello.mbt        # MoonBit implementation
│   ├── moon.mod.json        # MoonBit module config
│   └── moon.pkg.json        # MoonBit package config
│
├── js/                      # JavaScript bindings
│   ├── src/hello.js         # JS bindings
│   └── test/hello.test.js   # JS tests
│
├── ruby/                    # Ruby bindings
│   ├── lib/hello.rb         # Ruby bindings
│   └── test/test_hello.rb   # Ruby tests
│
├── python/                  # Python bindings
│   ├── src/hello.py         # Python bindings
│   └── tests/test_hello.py  # Python tests
│
└── .github/workflows/ci.yml # CI/CD pipeline
```

## Prerequisites

- **MoonBit**: Install from https://www.moonbitlang.com/download/
- **Node.js**: v18+ (for JavaScript bindings)
- **Ruby**: v3.0+ (for Ruby bindings)
- **Python**: v3.9+ (for Python bindings)

### Installation

#### MoonBit (Unix/Linux/macOS)
```bash
curl -fsSL https://cli.moonbitlang.com/install/unix.sh | bash
```

#### Node.js
```bash
# Using nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
```

#### Ruby
System Ruby (3.0+) or via rbenv/rvm

#### Python
System Python (3.9+) or via pyenv

## Quick Start

### 1. Build the WASM Module

```bash
cd core
moon build --target wasm
```

This generates `core/target/wasm/release/hello.wasm`

### 2. Test JavaScript Bindings

```bash
cd js
npm test
```

### 3. Test Ruby Bindings

```bash
cd ruby
bundle install
bundle exec ruby test/test_hello.rb
```

### 4. Test Python Bindings

```bash
cd python
pip install -r requirements.txt
pytest
```

## Usage Examples

### JavaScript

```javascript
import { loadHelloWasm, Hello } from './js/src/hello.js';

const wasmExports = await loadHelloWasm();
const hello = new Hello(wasmExports);

console.log(hello.greet('World'));  // "Hello, World!"
console.log(hello.add(5, 3));       // 8
```

### Ruby

```ruby
require_relative 'ruby/lib/hello'

hello = HelloWasm::Hello.new
puts hello.greet('World')  # "Hello, World!"
puts hello.add(5, 3)       # 8
```

### Python

```python
from python.src.hello import Hello

hello = Hello()
print(hello.greet('World'))  # "Hello, World!"
print(hello.add(5, 3))       # 8
```

## Development

After making changes to the MoonBit code:

1. Rebuild WASM: `cd core && moon build --target wasm`
2. Run all tests:
   - JavaScript: `cd js && npm test`
   - Ruby: `cd ruby && bundle exec ruby test/test_hello.rb`
   - Python: `cd python && pytest`

## CI/CD

The project includes a GitHub Actions workflow that:
1. Builds the WASM module
2. Runs tests for all three language bindings
3. Ensures cross-platform compatibility

## License

MIT License - see LICENSE file for details

## References

- [MoonBit Documentation](https://docs.moonbitlang.com/)
- [WebAssembly Specification](https://webassembly.github.io/spec/)
- [Wasmtime Documentation](https://docs.wasmtime.dev/)
