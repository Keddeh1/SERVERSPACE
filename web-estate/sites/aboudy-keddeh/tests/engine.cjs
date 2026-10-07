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

for (let bank = 1; bank <= 9; bank++) for (let address = 1; address <= 256; address++) {
  const location = engine.memoryLocation(bank, address);
  assert.equal(location.bank_offset, bank - 1);
  assert.equal(engine.originAddress(location.word_offset, 256), address);
}
for (const bad of [0, -1, 257, 1.5, NaN, Infinity, '1', null]) assert.throws(() => engine.originOffset(bad, 256));
for (const bad of [0, 10, 1.5, '1']) assert.throws(() => engine.memoryLocation(bad, 1));
assert.equal(engine.originOffset(16777216, 16777216), 16777215);
assert.throws(() => engine.originOffset(16777217, 16777216));
const contexts = [];
const mapped = engine.runner(engine.pack('ORIGIN_TEST', 'READ X1\nREAD X2\nHALT').executable, {READ: (operand, context) => contexts.push(context)});
while (!mapped.step()) {}
assert.deepEqual(contexts.map(row => row.instruction_address), [1, 2]);
assert.deepEqual(contexts.map(row => row.instruction), [0, 1]);
assert.ok(contexts.every(row => row.address_origin === 1));
console.log(JSON.stringify({oneOriginMapping: 'passed', exhaustiveBankWordMappings: 2304, serializedEntry: 0}));

for (const bad of [-1, 256, 1.5, NaN, Infinity, '0', null]) assert.throws(() => engine.originAddress(bad, 256));
for (const bad of [0, -1, 1.5, NaN, Infinity, 16777217, '256']) assert.throws(() => engine.originOffset(1, bad));
