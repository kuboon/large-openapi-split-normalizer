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
