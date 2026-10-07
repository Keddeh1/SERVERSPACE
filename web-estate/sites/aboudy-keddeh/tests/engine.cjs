const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const engine = require('../dist/assets/kex-engine.js');
const model = require('../runtime/kex-contract.json');
const reference = { TextEncoder, document: { getElementById: id => ({ textContent: JSON.stringify(id === 'p03-compiler-chain' ? model : {}) }) } };
vm.createContext(reference);
vm.runInContext(fs.readFileSync(path.join(__dirname, 'fixtures/p03-reference.js'), 'utf8'), reference, { timeout: 1000 });
let checks = 0;
for (const source of ['SELECT X2\nPRINT NUMBER X2\nHALT', 'MIRROR X9\nHALT', 'ORIGIN X1\nLANE X2\nRESOLVE X3\nWRITE X4\nREAD X5\nSPAWN X6\nSEND X7\nHALT']) {
  const one = engine.pack('CONFORMANCE', source);
  const expected = reference.KEXCompilerChain.packageKEXE('CONFORMANCE', 'kex', source);
  assert.deepEqual(one.executable, JSON.parse(JSON.stringify(expected.executable)));
  assert.deepEqual(one.bundle, JSON.parse(JSON.stringify(expected.bundle)));
  assert.equal(engine.load(one.executable).words.length, one.executable.header.count); checks++;
}
for (const source of ['', 'SELECT 0', 'UNKNOWN X1', 'SELECT 16777216', 'SELECT X1\n'.repeat(257), 'a'.repeat(16385)]) {
  assert.throws(() => engine.pack('REJECT_TEST', source)); checks++;
}
const program = engine.pack('RUN_TEST', 'SELECT X2\nPRINT NUMBER X2\nHALT');
assert.equal(program.executable.payload[0], '01000002');
assert.equal(program.executable.payload[1], '0A851903');
assert.equal(program.executable.payload[2], 'FF000000');
for (const mutate of [x => x.payload[0] = '01000003', x => x.header.count++, x => x.header.magic = 'OTHER', x => x.extra = true]) {
  const copy = JSON.parse(JSON.stringify(program.executable)); mutate(copy); assert.throws(() => engine.load(copy)); checks++;
}
assert.throws(() => engine.runner(program.executable, {})); checks++;
let selected = null, output = [];
const run = engine.runner(program.executable, { SELECT: value => selected = value, PRINT: value => output.push({ selected, encodedOperand: value }) });
assert.equal(run.step(), false); assert.equal(run.step(), false); assert.equal(run.step(), true); assert.equal(run.step(), true);
assert.equal(selected, 2); assert.deepEqual(output, [{ selected: 2, encodedOperand: 0x851903 }]); checks++;
console.log(JSON.stringify({ status: 'passed', checks, conformance: 'exact owner P03 IR, words and KEXE checksum', runner: 'explicit admitted software handlers', physicalTargetVerified: false }));
