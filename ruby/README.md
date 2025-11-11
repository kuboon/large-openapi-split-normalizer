# Ruby Bindings for MoonBit WASM Module

Ruby bindings for the MoonBit hello WASM module using the Wasmtime gem.

## Requirements

- Ruby 3.0 or higher
- Bundler

## Installation

```bash
bundle install
```

## Usage

```ruby
require_relative 'lib/hello'

# Create a new Hello instance
hello = HelloWasm::Hello.new

# Use the functions
puts hello.greet('World')  # Output: "Hello, World!"
puts hello.add(5, 3)       # Output: 8
```

## Testing

```bash
bundle exec ruby test/test_hello.rb
```

## API

### `HelloWasm::Hello`

#### `initialize()`

Creates a new Hello instance and loads the WASM module.

#### `greet(name: String) -> String`

Returns a greeting message.

**Parameters:**
- `name` - The name to greet

**Returns:** A string like "Hello, {name}!"

#### `add(a: Integer, b: Integer) -> Integer`

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

- `wasmtime` (~> 26.0) - WebAssembly runtime
- `minitest` (~> 5.25) - Testing framework
