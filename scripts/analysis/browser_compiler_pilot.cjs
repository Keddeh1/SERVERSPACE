/* Actual browser execution of admitted owner P03 and portable compiler paths. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const site=path.resolve(__dirname,'../../web-estate/sites/aboudy-keddeh');
const {chromium}=require(path.join(site,'node_modules/playwright'));
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',chromiumSandbox:process.env.SITE_BROWSER_SANDBOX!=='0'});
 try{
  const context=await browser.newContext();await context.route('**/*',r=>r.abort());const page=await context.newPage();
  await page.setContent('<script id="p03-compiler-chain" type="application/json"></script><script id="p03-direct-proof" type="application/json">{}</script><script id="p04-action-plan" type="application/json">{}</script>');
  await page.evaluate(model=>document.getElementById('p03-compiler-chain').textContent=JSON.stringify(model),JSON.parse(fs.readFileSync(path.join(site,'runtime/kex-contract.json'))));
  await page.addScriptTag({content:fs.readFileSync(path.join(site,'tests/fixtures/p03-reference.js'),'utf8')});
  await page.addScriptTag({content:fs.readFileSync(path.join(site,'dist/assets/kex-engine.js'),'utf8')});
  const result=await page.evaluate(()=>{
   const source='SELECT X2\nPRINT NUMBER X2\nHALT',samples=[];
   const owner=()=>KEXCompilerChain.packageKEXE('PILOT_WORK','kex',source).executable;
   const portable=()=>KEXEngine.pack('PILOT_WORK',source).executable;
   if(JSON.stringify(owner())!==JSON.stringify(portable()))throw Error('executable divergence');
   for(let warm=0;warm<100;warm++){owner();portable();}
   for(let round=0;round<12;round++)for(const name of(round%2?['portable','owner']:['owner','portable'])){
    const f=name==='owner'?owner:portable,start=performance.now();let last;
    for(let i=0;i<250;i++)last=f();samples.push({path:name,round,programs:250,milliseconds:performance.now()-start,checksum:last.checksum});
   }
   let calls=0;const runner=KEXEngine.runner(portable(),{SELECT:()=>calls++,PRINT:()=>calls++});while(!runner.step()){}
   if(calls!==2)throw Error('admitted execution mismatch');
   return{samples,equivalence:'exact executable bytes and checksum',programs_per_path:3000,admitted_handler_calls:calls,
     scope:'Chromium compile/assemble/package microbenchmark; not whole HTML computer or enterprise deployment'};
  });
  assert.equal(new Set(result.samples.map(s=>s.checksum)).size,1);
  result.chromiumSandbox=process.env.SITE_BROWSER_SANDBOX!=='0';result.energyJoulesMeasured=null;
  console.log(JSON.stringify(result,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
