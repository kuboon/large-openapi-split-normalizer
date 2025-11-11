require 'wasmtime'

module HelloWasm
  class Hello
    def initialize
      # Load the WASM module
      wasm_path = File.expand_path('../../core/target/wasm/release/hello.wasm', __dir__)
      engine = Wasmtime::Engine.new
      @store = Wasmtime::Store.new(engine)
      wasm_bytes = File.binread(wasm_path)
      mod = Wasmtime::Module.new(engine, wasm_bytes)
      @instance = Wasmtime::Instance.new(@store, mod, [])
      @memory = @instance.export('memory').to_memory
    end
    
    def greet(name)
      # Write name to WASM memory at offset 0
      name_ptr = 0
      @memory.write(name_ptr, name)
      
      # Call the exported greet function
      greet_func = @instance.export('greet').to_func
      result_ptr = greet_func.call(name_ptr, name.bytesize)
      
      # Get result length
      greet_len_func = @instance.export('greet_len').to_func
      result_len = greet_len_func.call(name.bytesize)
      
      # Read the result from WASM memory
      @memory.read(result_ptr, result_len)
    end
    
    def add(a, b)
      # Call the exported add function
      add_func = @instance.export('add').to_func
      add_func.call(a, b)
    end
  end
end
