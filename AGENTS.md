# AGENTS.md - MoonBit WASM Multi-Language Bindings Project

## Project Overview

This project provides a tool for analyzing and reorganizing large OpenAPI schema YAML files that are split across multiple files using `$ref` references (typically 100+ files). The core functionality is implemented in MoonBit and compiled to WebAssembly (WASM) for cross-platform compatibility. The tool loads the entire schema into memory, analyzes dependencies between components, and reorganizes them for optimal structure.

The WASM module is bound to multiple runtime environments (JavaScript, Ruby, and Python), enabling the tool to be used across different platforms and integrated into various workflows. This architecture demonstrates the power of WASM for building portable, high-performance tools that can be consumed from any language ecosystem.

## Project Structure

```
.
├── core/                    # MoonBit source code and WASM build
│   ├── src/
│   │   └── lib/
│   │       └── hello.mbt    # Main MoonBit source file
│   ├── moon.mod.json        # MoonBit module configuration
│   ├── moon.pkg.json        # MoonBit package configuration
│   └── target/              # Build output directory
│       └── wasm/
│           └── release/
│               └── hello.wasm
│
├── js/                      # JavaScript bindings and tests
│   ├── src/
│   │   └── hello.js         # JS bindings for WASM module
│   ├── test/
│   │   └── hello.test.js    # JS test suite
│   ├── package.json         # Node.js dependencies
│   └── README.md
│
├── ruby/                    # Ruby bindings and tests
│   ├── lib/
│   │   └── hello.rb         # Ruby bindings for WASM module
│   ├── test/
│   │   └── test_hello.rb    # Ruby minitest suite
│   ├── Gemfile              # Ruby dependencies
│   └── README.md
│
├── python/                  # Python bindings and tests
│   ├── src/
│   │   └── hello.py         # Python bindings for WASM module
│   ├── tests/
│   │   └── test_hello.py    # Python test suite
│   ├── requirements.txt     # Python dependencies
│   └── README.md
│
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/CD pipeline
│
├── README.md                # Main project README
└── AGENTS.md               # This file - detailed specifications
```

## Component Specifications

### 1. Core - MoonBit WASM Module

#### Purpose
Implement a simple hello world function in MoonBit that can be compiled to WASM and called from multiple language runtimes.

#### Implementation Details

**File: `core/src/lib/hello.mbt`**
```moonbit
// Export a function that returns a greeting message
pub fn greet(name : String) -> String {
  "Hello, " + name + "!"
}

// Export a simple addition function for testing
pub fn add(a : Int, b : Int) -> Int {
  a + b
}
```

**File: `core/moon.mod.json`**
```json
{
  "name": "kuboon/hello",
  "version": "0.1.0",
  "deps": {},
  "readme": "README.md",
  "repository": "",
  "license": "MIT",
  "keywords": [],
  "description": "A simple hello world module in MoonBit"
}
```

**File: `core/moon.pkg.json`**
```json
{
  "is_main": false,
  "import": [],
  "wbtest-import": []
}
```

#### Build Process
1. Install MoonBit toolchain (moon)
2. Navigate to `core/` directory
3. Run `moon build --target wasm` to compile to WASM
4. Output will be generated in `core/target/wasm/release/hello.wasm`

#### Exported Functions
- `greet(name: String) -> String`: Returns a greeting message
- `add(a: Int, b: Int) -> Int`: Adds two integers

---

### 2. JavaScript Bindings

#### Purpose
Provide JavaScript bindings to load and interact with the WASM module in Node.js and browser environments.

#### Implementation Details

**File: `js/package.json`**
```json
{
  "name": "@kuboon/hello-wasm-js",
  "version": "0.1.0",
  "description": "JavaScript bindings for MoonBit hello WASM module",
  "type": "module",
  "main": "src/hello.js",
  "scripts": {
    "test": "node test/hello.test.js"
  },
  "devDependencies": {},
  "engines": {
    "node": ">=18"
  }
}
```

**File: `js/src/hello.js`**
```javascript
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
  }
  
  greet(name) {
    // Call the WASM greet function
    return this.exports.greet(name);
  }
  
  add(a, b) {
    return this.exports.add(a, b);
  }
}
```

**File: `js/test/hello.test.js`**
```javascript
import { loadHelloWasm, Hello } from '../src/hello.js';
import assert from 'assert';

async function runTests() {
  console.log('Loading WASM module...');
  const wasmExports = await loadHelloWasm();
  const hello = new Hello(wasmExports);
  
  console.log('Running tests...');
  
  // Test 1: greet function
  const greeting = hello.greet('World');
  assert.strictEqual(greeting, 'Hello, World!', 'Greet function should return correct greeting');
  console.log('✓ Test 1 passed: greet("World") =', greeting);
  
  // Test 2: add function
  const sum = hello.add(5, 3);
  assert.strictEqual(sum, 8, 'Add function should return sum');
  console.log('✓ Test 2 passed: add(5, 3) =', sum);
  
  console.log('\nAll tests passed! ✨');
}

runTests().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
```

#### Testing
- Run `npm test` in the `js/` directory
- Tests validate basic WASM function calls
- Uses Node.js built-in `assert` module

---

### 3. Ruby Bindings

#### Purpose
Provide Ruby bindings using the Wasmtime gem to interact with the WASM module.

#### Implementation Details

**File: `ruby/Gemfile`**
```ruby
source 'https://rubygems.org'

gem 'wasmtime', '~> 26.0'
gem 'minitest', '~> 5.25'
```

**File: `ruby/lib/hello.rb`**
```ruby
require 'wasmtime'

module HelloWasm
  class Hello
    def initialize
      # Load the WASM module
      wasm_path = File.expand_path('../../core/target/wasm/release/hello.wasm', __dir__)
      engine = Wasmtime::Engine.new
      @store = Wasmtime::Store.new(engine)
      mod = Wasmtime::Module.from_file(@store.engine, wasm_path)
      @instance = Wasmtime::Instance.new(@store, mod, [])
    end
    
    def greet(name)
      # Call the exported greet function
      greet_func = @instance.exports(@store)['greet']
      greet_func.call(@store, name)
    end
    
    def add(a, b)
      # Call the exported add function
      add_func = @instance.exports(@store)['add']
      add_func.call(@store, a, b)
    end
  end
end
```

**File: `ruby/test/test_hello.rb`**
```ruby
require 'minitest/autorun'
require_relative '../lib/hello'

class TestHello < Minitest::Test
  def setup
    @hello = HelloWasm::Hello.new
  end
  
  def test_greet
    result = @hello.greet('World')
    assert_equal 'Hello, World!', result
  end
  
  def test_add
    result = @hello.add(5, 3)
    assert_equal 8, result
  end
end
```

#### Testing
- Install dependencies: `bundle install` in the `ruby/` directory
- Run tests: `bundle exec ruby test/test_hello.rb`
- Uses Ruby's minitest framework

---

### 4. Python Bindings

#### Purpose
Provide Python bindings using the wasmtime package to interact with the WASM module.

#### Implementation Details

**File: `python/requirements.txt`**
```
wasmtime>=26.0.0
pytest>=8.0.0
```

**File: `python/src/hello.py`**
```python
from wasmtime import Store, Module, Instance
from pathlib import Path

class Hello:
    def __init__(self):
        # Load the WASM module
        wasm_path = Path(__file__).parent.parent.parent / "core" / "target" / "wasm" / "release" / "hello.wasm"
        self.store = Store()
        module = Module.from_file(self.store.engine, str(wasm_path))
        self.instance = Instance(self.store, module, [])
        
    def greet(self, name: str) -> str:
        """Call the greet function from WASM module"""
        greet_func = self.instance.exports(self.store)["greet"]
        return greet_func(self.store, name)
    
    def add(self, a: int, b: int) -> int:
        """Call the add function from WASM module"""
        add_func = self.instance.exports(self.store)["add"]
        return add_func(self.store, a, b)
```

**File: `python/tests/test_hello.py`**
```python
import pytest
from src.hello import Hello

def test_greet():
    hello = Hello()
    result = hello.greet("World")
    assert result == "Hello, World!"

def test_add():
    hello = Hello()
    result = hello.add(5, 3)
    assert result == 8
```

#### Testing
- Install dependencies: `pip install -r requirements.txt` in the `python/` directory
- Run tests: `pytest` in the `python/` directory
- Uses pytest framework

---

## CI/CD Pipeline

**File: `.github/workflows/ci.yml`**

The CI pipeline should:
1. Set up MoonBit toolchain
2. Build the WASM module in `core/`
3. Run JavaScript tests
4. Run Ruby tests
5. Run Python tests

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-wasm:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup MoonBit
        run: |
          curl -fsSL https://cli.moonbitlang.com/install/unix.sh | bash
          echo "$HOME/.moon/bin" >> $GITHUB_PATH
      
      - name: Build WASM
        run: |
          cd core
          moon build --target wasm
      
      - name: Upload WASM artifact
        uses: actions/upload-artifact@v4
        with:
          name: hello-wasm
          path: core/target/wasm/release/hello.wasm
  
  test-js:
    needs: build-wasm
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Download WASM artifact
        uses: actions/download-artifact@v4
        with:
          name: hello-wasm
          path: core/target/wasm/release/
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Run JS tests
        run: |
          cd js
          npm test
  
  test-ruby:
    needs: build-wasm
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Download WASM artifact
        uses: actions/download-artifact@v4
        with:
          name: hello-wasm
          path: core/target/wasm/release/
      
      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.3'
          bundler-cache: true
          working-directory: ruby
      
      - name: Run Ruby tests
        run: |
          cd ruby
          bundle exec ruby test/test_hello.rb
  
  test-python:
    needs: build-wasm
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Download WASM artifact
        uses: actions/download-artifact@v4
        with:
          name: hello-wasm
          path: core/target/wasm/release/
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          cd python
          pip install -r requirements.txt
      
      - name: Run Python tests
        run: |
          cd python
          pytest
```

---

## Documentation

### Main README.md

Should include:
- Project overview and purpose
- Prerequisites (MoonBit, Node.js, Ruby, Python)
- Quick start guide
- Directory structure explanation
- Build and test instructions for each language
- License information

### Language-specific READMEs

Each subdirectory (`js/`, `ruby/`, `python/`) should have its own README with:
- Setup instructions
- Usage examples
- Testing instructions
- API documentation

---

## Development Workflow

1. **Make changes to MoonBit code** in `core/src/lib/hello.mbt`
2. **Build WASM**: `cd core && moon build --target wasm`
3. **Test bindings**:
   - JavaScript: `cd js && npm test`
   - Ruby: `cd ruby && bundle exec ruby test/test_hello.rb`
   - Python: `cd python && pytest`
4. **Commit changes** and push
5. **CI pipeline** runs automatically

---

## Key Design Decisions

1. **MoonBit as the source language**: Chosen for its excellent WASM compilation output with minimal binary size
2. **Wasmtime for Ruby and Python**: Consistent runtime across these languages, well-maintained by Bytecode Alliance
3. **Native WebAssembly API for JavaScript**: Node.js and modern browsers have built-in WASM support
4. **Simple hello world**: Keeps the example minimal and focused on the multi-language binding pattern
5. **Separate test frameworks**: Uses idiomatic testing tools for each language (assert/Node.js, minitest, pytest)

---

## Future Enhancements

1. Add browser-based JavaScript example
2. Support for more complex data types (structs, arrays)
3. WebAssembly Component Model integration
4. WASI (WebAssembly System Interface) examples
5. Performance benchmarks across languages
6. Additional language bindings (Go, Rust host, etc.)

---

## Prerequisites

### Required Software

- **MoonBit**: Install from https://www.moonbitlang.com/download/
- **Node.js**: v18+ (for JavaScript bindings)
- **Ruby**: v3.0+ (for Ruby bindings)
- **Python**: v3.9+ (for Python bindings)
- **Git**: For version control

### Installation Commands

```bash
# MoonBit (Unix/Linux/macOS)
curl -fsSL https://cli.moonbitlang.com/install/unix.sh | bash

# Node.js (via nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20

# Ruby (via rbenv)
rbenv install 3.3.0
rbenv global 3.3.0

# Python (via pyenv)
pyenv install 3.12
pyenv global 3.12
```

---

## Troubleshooting

### WASM Module Not Found
- Ensure you've built the WASM module: `cd core && moon build --target wasm`
- Check that `core/target/wasm/release/hello.wasm` exists

### JavaScript Tests Fail
- Verify Node.js version is 18+: `node --version`
- Check WASM file path in `js/src/hello.js`

### Ruby Tests Fail
- Install bundler: `gem install bundler`
- Install dependencies: `cd ruby && bundle install`
- Ensure Wasmtime gem is compatible with your system

### Python Tests Fail
- Create a virtual environment: `python -m venv venv`
- Activate: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
- Install dependencies: `pip install -r requirements.txt`

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## References

- [MoonBit Documentation](https://docs.moonbitlang.com/)
- [WebAssembly Specification](https://webassembly.github.io/spec/)
- [Wasmtime Documentation](https://docs.wasmtime.dev/)
- [WebAssembly Component Model](https://component-model.bytecodealliance.org/)
