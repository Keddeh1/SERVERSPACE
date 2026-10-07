/* Bounded ES5 adaptation of owner P03 KEX-IR-1 / KEX-ISA-1 / KEXE-1.
 * Source custody: research/kex-compiler-custody.json. Checksum is not authority.
 */
(function (root) {
  'use strict';
  var OPS = { SELECT: 1, ORIGIN: 2, LANE: 3, RESOLVE: 4, WRITE: 5, READ: 6, SPAWN: 7, SEND: 8, MIRROR: 9, PRINT: 10, HALT: 255 };
  function fail(code) { throw new Error(code); }
  function hex(value) { return ('00000000' + (value >>> 0).toString(16)).slice(-8).toUpperCase(); }
  function imul(a, b) { return (((a & 65535) * (b & 65535)) + ((((a >>> 16) * (b & 65535) + (a & 65535) * (b >>> 16)) & 65535) << 16)) | 0; }
  function checksum(text) {
    var bytes = unescape(encodeURIComponent(text)), hash = 2166136261;
    for (var i = 0; i < bytes.length; i += 1) hash = imul(hash ^ bytes.charCodeAt(i), 16777619) >>> 0;
    return hex(hash);
  }
  function operand(value) {
    if (/^X[1-9]$/.test(value)) return Number(value.slice(1));
    if (/^[0-9]+$/.test(value)) {
      if (value.length > 8 || Number(value) > 16777215) fail('E_OPERAND_RANGE');
      return Number(value);
    }
    var result = 0;
    for (var i = 0; i < value.length; i += 1) result = ((result * 33) ^ value.charCodeAt(i)) & 16777215;
    return result;
  }
  function originOffset(address, capacity) {
    if (typeof capacity !== 'number' || capacity % 1 !== 0 || capacity < 1 || capacity > 16777216 || typeof address !== 'number' || address % 1 !== 0 || address < 1 || address > capacity) fail('E_ORIGIN_ADDRESS');
    return address - 1;
  }
  function originAddress(offset, capacity) {
    if (typeof offset !== 'number' || offset % 1 !== 0 || offset < 0) fail('E_ORIGIN_OFFSET');
    originOffset(offset + 1, capacity); return offset + 1;
  }
  function memoryLocation(bank, address) {
    return { bank: bank, address: address, bank_offset: originOffset(bank, 9), word_offset: originOffset(address, 256) };
  }
  function validate(records) {
    if (!Array.isArray(records) || records.length < 1 || records.length > 256) fail('E_IR_SHAPE');
    for (var i = 0; i < records.length; i += 1) {
      var row = records[i];
      if (!row || !Object.prototype.hasOwnProperty.call(OPS, row.op) || !Array.isArray(row.args) || row.args.length > 8) fail('E_IR_RECORD');
      for (var j = 0; j < row.args.length; j += 1) if (typeof row.args[j] !== 'string' || row.args[j].length > 128) fail('E_IR_ARGUMENT');
    }
    return records;
  }
  function compile(source) {
    if (typeof source !== 'string' || source.length > 16384) fail('E_SOURCE_LIMIT');
    var lines = source.split(/\n/), records = [];
    for (var i = 0; i < lines.length; i += 1) {
      var line = lines[i].replace(/^\s+|\s+$/g, '');
      if (!line) continue;
      if (/(^|\s)0(\s|$)/.test(line)) fail('E_BARE_ZERO');
      var parts = line.split(/\s+/), op = parts.shift().toUpperCase();
      records.push({ op: op, args: parts, source_line: i + 1 });
    }
    return { language: 'kex', frontend: 'FE_KEX', ir: 'KEX-IR-1', records: validate(records) };
  }
  function assemble(records) {
    validate(records); var words = [];
    for (var i = 0; i < records.length; i += 1) words.push(hex((OPS[records[i].op] << 24) | operand(records[i].args[0] || '')));
    return words;
  }
  function decode(word) {
    if (typeof word !== 'string' || !/^[0-9A-F]{8}$/.test(word)) fail('E_MRAM_WORD');
    var value = parseInt(word, 16) >>> 0, opcode = value >>> 24, name = null;
    for (var key in OPS) if (Object.prototype.hasOwnProperty.call(OPS, key) && OPS[key] === opcode) name = key;
    if (!name) fail('E_ISA_OPCODE');
    return { op: name, operand: value & 16777215 };
  }
  function pack(program, source) {
    if (typeof program !== 'string' || !/^[A-Z][A-Z0-9_]{2,31}$/.test(program)) fail('E_PROGRAM_ID');
    var bundle = compile(source), payload = assemble(bundle.records);
    var header = { magic: 'KEXE', version: 1, program: program, language: 'kex', count: payload.length, entry: 0 };
    return { source_identity: 'source://' + program, bundle: bundle,
      executable: { header: header, payload: payload, checksum: checksum(JSON.stringify({ header: header, payload: payload })) } };
  }
  function load(executable) {
    if (!executable || Object.keys(executable).sort().join(',') !== 'checksum,header,payload') fail('E_EXEC_SHAPE');
    var h = executable.header, p = executable.payload;
    if (!h || Object.keys(h).sort().join(',') !== 'count,entry,language,magic,program,version' || h.magic !== 'KEXE' || h.version !== 1 || h.language !== 'kex' || h.entry !== 0 || typeof h.program !== 'string' || !/^[A-Z][A-Z0-9_]{2,31}$/.test(h.program)) fail('E_EXEC_HEADER');
    if (!Array.isArray(p) || p.length < 1 || p.length > 256 || h.count !== p.length) fail('E_MRAM_ADDR');
    var header = { magic: h.magic, version: h.version, program: h.program, language: h.language, count: h.count, entry: h.entry };
    for (var i = 0; i < p.length; i += 1) decode(p[i]);
    if (checksum(JSON.stringify({ header: header, payload: p })) !== executable.checksum) fail('E_EXEC_CHECKSUM');
    return { format: 'KEXE-1', source_identity: 'source://' + h.program, words: p.slice(0), checksum: executable.checksum };
  }
  function runner(executable, handlers) {
    var image = load(executable), pc = 0, halted = false;
    if (!handlers || typeof handlers !== 'object') fail('E_TARGET_ADAPTER_REQUIRED');
    for (var i = 0; i < image.words.length; i += 1) {
      var row = decode(image.words[i]);
      if (row.op !== 'HALT' && (!Object.prototype.hasOwnProperty.call(handlers, row.op) || typeof handlers[row.op] !== 'function')) fail('E_TARGET_OPCODE_NOT_ADMITTED');
    }
    return { source_identity: image.source_identity,
      step: function () {
        if (halted || pc >= image.words.length) return true;
        var row = decode(image.words[pc]); pc += 1;
        if (row.op === 'HALT') { halted = true; return true; }
        handlers[row.op](row.operand, { source_identity: image.source_identity, instruction: pc - 1, instruction_address: originAddress(pc - 1, image.words.length), address_origin: 1 });
        return pc >= image.words.length;
      } };
  }
  var api = { version: '1.1.0', originOffset: originOffset, originAddress: originAddress, memoryLocation: memoryLocation, compile: compile, assemble: assemble, decode: decode, pack: pack, load: load, runner: runner, checksum: checksum };
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.KEXEngine = api;
}(this));
