from wasmtime import Store, Module, Instance, Engine
from pathlib import Path

class Hello:
    def __init__(self):
        # Load the WASM module
        wasm_path = Path(__file__).parent.parent.parent / "core" / "target" / "wasm" / "release" / "hello.wasm"
        engine = Engine()
        self.store = Store(engine)
        with open(wasm_path, 'rb') as f:
            wasm_bytes = f.read()
        module = Module(engine, wasm_bytes)
        self.instance = Instance(self.store, module, [])
        self.memory = self.instance.exports(self.store)["memory"]
        
    def greet(self, name: str) -> str:
        """Call the greet function from WASM module"""
        # Write name to WASM memory at offset 0
        name_bytes = name.encode('utf-8')
        name_ptr = 0
        memory_data = self.memory.data_ptr(self.store)
        for i, byte in enumerate(name_bytes):
            memory_data[name_ptr + i] = byte
        
        # Call greet function
        greet_func = self.instance.exports(self.store)["greet"]
        result_ptr = greet_func(self.store, name_ptr, len(name_bytes))
        
        # Get result length
        greet_len_func = self.instance.exports(self.store)["greet_len"]
        result_len = greet_len_func(self.store, len(name_bytes))
        
        # Read result from memory
        result_bytes = bytes(memory_data[result_ptr:result_ptr + result_len])
        return result_bytes.decode('utf-8')
    
    def add(self, a: int, b: int) -> int:
        """Call the add function from WASM module"""
        add_func = self.instance.exports(self.store)["add"]
        return add_func(self.store, a, b)
