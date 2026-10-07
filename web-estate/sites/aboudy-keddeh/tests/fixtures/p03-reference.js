(()=>{
  "use strict";
  const MODEL=JSON.parse(document.getElementById('p03-compiler-chain').textContent);
  const PROOF=JSON.parse(document.getElementById('p03-direct-proof').textContent);
  const NEXT=JSON.parse(document.getElementById('p04-action-plan').textContent);
  const OPS=MODEL.isa.opcodes;
  const enc=new TextEncoder();
  const clone=x=>JSON.parse(JSON.stringify(x));
  const hex32=n=>(Number(n)>>>0).toString(16).padStart(8,'0').toUpperCase();
  function checksum32(text){let h=2166136261>>>0;for(const b of enc.encode(String(text))){h^=b;h=Math.imul(h,16777619)>>>0}return hex32(h)}
  function normIR(op,args=[]){return {op:String(op).toUpperCase(),args:args.map(String)}}
  function splitArgs(raw){return raw.trim()?raw.split(',').map(v=>v.trim().replace(/^["']|["']$/g,'')):[]}
  function compileKEX(source){
    const rows=[];
    String(source).split(/\n+/).forEach((raw,i)=>{
      const line=raw.trim(); if(!line)return;
      if(/(^|\s)0(\s|$)/.test(line))throw Error(`line ${i+1}: bare 0 illegal; 0. is reference token`);
      const [op,...args]=line.split(/\s+/); rows.push({...normIR(op,args),source_line:i+1});
    });
    if(!rows.length)throw Error('E_IR_SHAPE'); return rows;
  }
  function subsetCalls(source,lang){
    const re=(lang==='c'||lang==='cpp')?/kex_(select|mirror|halt|print)\s*\(([^)]*)\)\s*;/gi:/kex\s*\.\s*(select|mirror|halt|print)\s*\(([^)]*)\)\s*;?/gi;
    const records=[];let m;
    while((m=re.exec(String(source)))){
      const fn=m[1].toLowerCase(),a=splitArgs(m[2]);
      if(fn==='select')records.push(normIR('SELECT',[a[0]]));
      else if(fn==='mirror')records.push(normIR('MIRROR',[a[0]]));
      else if(fn==='print')records.push(normIR('PRINT',a));
      else records.push(normIR('HALT',[]));
    }
    if(!records.length)throw Error(`E_FRONTEND_${lang.toUpperCase()} unsupported source subset`);
    return records;
  }
  function frontendCompile(lang,source){
    const fe=MODEL.frontends[lang]; if(!fe)throw Error('E_FRONTEND_LANGUAGE');
    const records=lang==='kex'?compileKEX(source):subsetCalls(source,lang);
    const bundle={language:lang,frontend:fe.id,ir:MODEL.ir.identity,records}; validateIR(bundle); return bundle;
  }
  function validateIR(b){
    if(b.ir!==MODEL.ir.identity||!Array.isArray(b.records)||!b.records.length)throw Error('E_IR_SHAPE');
    const legal=new Set(Object.keys(OPS));
    b.records.forEach((r,i)=>{if(!legal.has(r.op)||!Array.isArray(r.args))throw Error(`E_IR_RECORD_${i}`)});
    return b;
  }
  function operand(a=''){
    if(/^X[1-9]$/.test(a))return Number(a.slice(1));
    if(/^[0-9]+$/.test(a))return Number(a)&0xFFFFFF;
    let v=0;for(let i=0;i<a.length;i++)v=((v*33)^a.charCodeAt(i))&0xFFFFFF;return v;
  }
  function isaEncode(record){
    const code=OPS[record.op]; if(code===undefined)throw Error(`E_ISA_OPCODE ${record.op}`);
    return hex32(((code&0xFF)<<24)|(operand(record.args[0]||'')&0xFFFFFF));
  }
  function isaDecode(word){
    const n=parseInt(String(word),16)>>>0,opcode=(n>>>24)&255;
    const name=Object.entries(OPS).find(([,v])=>v===opcode)?.[0]||'UNKNOWN';
    return {word:hex32(n),opcode,name,operand:n&0xFFFFFF};
  }
  function lowerIR(bundle){validateIR(bundle);return {target:MODEL.lowering.output,instructions:clone(bundle.records),words:bundle.records.map(isaEncode)}}
  function packageKEXE(program,lang,source){
    if(!/^[A-Z][A-Z0-9_]{2,31}$/.test(program))throw Error('E_PROGRAM_ID');
    const bundle=frontendCompile(lang,source),low=lowerIR(bundle);
    const header={magic:'KEXE',version:1,program,language:lang,count:low.words.length,entry:0};
    const payload=low.words;
    const checksum=checksum32(JSON.stringify({header,payload}));
    return {source_identity:`source://${program}`,bundle,lowered:low,executable:{header,payload,checksum}};
  }
  const MRAM=Array.from({length:9},()=>Array(256).fill(undefined)); let nextBank=1;
  function load(executable){
    const exe=clone(executable);
    if(exe.header?.magic!=='KEXE')throw Error('E_EXEC_MAGIC');
    if(checksum32(JSON.stringify({header:exe.header,payload:exe.payload}))!==exe.checksum)throw Error('E_EXEC_CHECKSUM');
    const bank=nextBank; nextBank=nextBank%9+1; const start=0;
    if(exe.payload.length>256)throw Error('E_MRAM_ADDR');
    exe.payload.forEach((w,i)=>{if(!/^[0-9A-F]{8}$/.test(w))throw Error('E_MRAM_WORD');MRAM[bank-1][start+i]=w});
    return {format:'KEXE-1',bank,start,words:exe.payload.length,checksum:exe.checksum,state:'LOADED'};
  }
  function buildAndLoad(program,lang,source){
    try{const b=packageKEXE(program,lang,source);return {status:'COMMITTED',...b,load:load(b.executable)}}
    catch(e){return {status:'REJECT',reason:String(e.message||e),source_identity:`source://${program}`}}
  }
  function selectTarget(sourceIdentity,target='machine://kex/isa1'){
    const row=MODEL.target_selector.targets.find(t=>t.target===target);
    if(!row||row.status!=='ADMITTED_NOW')return {status:'REJECT',reason:'TARGET_ADAPTER_NOT_ADMITTED',source_identity:sourceIdentity,target};
    return {status:'ACTIVE',source_identity:sourceIdentity,target};
  }
  globalThis.KEXCompilerChain=Object.freeze({model:MODEL,proof:PROOF,frontendCompile,validateIR,lowerIR,isaEncode,isaDecode,packageKEXE,load,buildAndLoad,selectTarget,nextPlan:NEXT});
})();
