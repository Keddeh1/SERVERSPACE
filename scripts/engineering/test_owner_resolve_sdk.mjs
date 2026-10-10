import assert from 'node:assert/strict';
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StdioClientTransport} from '@modelcontextprotocol/sdk/client/stdio.js';
const client=new Client({name:'owner-resolve-estate-qualification',version:'1.0.0'});
await client.connect(new StdioClientTransport({command:process.execPath,args:['/workspace/.keddeh-environment/mcp-sdk/server.mjs'],stderr:'inherit'}));
try{
 const listed=(await client.listTools()).tools;
 for(const name of ['coordinate_resolve','vfs_document_read','runtime_service_health','owner_resolve_q32','owner_resolve_read_receipt'])assert(listed.some(t=>t.name===name));
 async function call(name,args){const r=await client.callTool({name,arguments:args});assert(!r.isError,JSON.stringify(r));return JSON.parse(r.content[0].text);}
 const digests=[];
 for(const instance of ['auth-canary','replica','primary']){
  const args={instance,request_id:'bridge-qualification-v1',levels:[1,2,3,4],environment:'owner-local-qualification',family:'SERVERSPACE/RESOLVE',custody:'source://754b1de/consilience'};
  const first=await call('owner_resolve_q32',args), replay=await call('owner_resolve_q32',args);
  assert.equal(first.result.arithmetic.raw_q32,13649637264);
  assert.equal(first.result.unity_variable,'X');assert.equal(first.result.unity_assignment,null);
  assert.equal(first.result.request.instance,'serverspace/resolve-'+instance);
  assert(replay.replayed);assert.equal(first.artifact_digest,replay.artifact_digest);
  const read=await call('owner_resolve_read_receipt',{instance,artifact_digest:first.artifact_digest});
  assert.deepEqual(read.result,first.result);assert(read.chain.verified);
  const conflict=await client.callTool({name:'owner_resolve_q32',arguments:{...args,levels:[4]}});assert(conflict.isError);
  for(const levels of [[0],[true],['2']]){const invalid=await client.callTool({name:'owner_resolve_q32',arguments:{...args,request_id:'invalid-bridge',levels}});assert(invalid.isError);}
  const after=await call('owner_resolve_read_receipt',{instance,artifact_digest:first.artifact_digest});assert.deepEqual(after,read);
  digests.push(first.artifact_digest);
 }
 assert.equal(new Set(digests).size,3);
 const absent=await client.callTool({name:'owner_resolve_read_receipt',arguments:{instance:'foreign',artifact_digest:digests[0]}});assert(absent.isError);
 assert((await client.listResources()).resources.length>0);
 console.log(JSON.stringify({sdk_tools:listed.length,instances:3,expected_q32_verified:true,retained_readback:true,replay:true,conflict_rejected:true,zero_boolean_and_string_levels_rejected:true,unassigned_unity_preserved:true,independent_contexts:true,legacy_contracts_retained:true}));
}finally{await client.close();}
