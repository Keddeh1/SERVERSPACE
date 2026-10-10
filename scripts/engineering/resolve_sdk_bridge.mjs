// Delegate to the pinned owner RESOLVE SDK; preserve its VFS and substrate contracts.
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StreamableHTTPClientTransport} from '@modelcontextprotocol/sdk/client/streamableHttp.js';
const instances={'auth-canary':19091,replica:19092,primary:19093};
const instance={type:'string',enum:Object.keys(instances)};
export const resolveTools=[
 {name:'owner_resolve_q32',description:'Run the owner Q32.32 module through its authenticated substrate and independent VFS; no inferred warrant.',inputSchema:{type:'object',properties:{instance,request_id:{type:'string',pattern:'^[A-Za-z0-9._-]{1,128}$'},levels:{type:'array',maxItems:4096,items:{type:'integer',enum:[1,2,3,4]}},environment:{type:'string',minLength:1,maxLength:256},family:{type:'string',minLength:1,maxLength:256},custody:{type:'string',minLength:1,maxLength:256}},required:['instance','request_id','levels','environment','family','custody'],additionalProperties:false}},
 {name:'owner_resolve_read_receipt',description:'Read the owner RESOLVE retained result and verify its independent receipt chain.',inputSchema:{type:'object',properties:{instance,artifact_digest:{type:'string',pattern:'^[0-9a-f]{64}$'}},required:['instance','artifact_digest'],additionalProperties:false}}
];
export async function callOwnerResolve(params){
 const definition=resolveTools.find(tool=>tool.name===params.name);
 if(!definition)throw Error('Unknown owner operation');
 const args=params.arguments??{},allowed=Object.keys(definition.inputSchema.properties);
 if(Object.keys(args).some(k=>!allowed.includes(k)) || definition.inputSchema.required.some(k=>!(k in args)) || !Object.hasOwn(instances,args.instance))throw Error('Explicit admitted instance and fields required');
 const {instance:chosen,...body}=args;
 if(params.name==='owner_resolve_q32'){
  if(typeof body.request_id!=='string'||!/^[A-Za-z0-9._-]{1,128}$/.test(body.request_id)||!Array.isArray(body.levels)||body.levels.length>4096||body.levels.some(n=>!Number.isInteger(n)||n<1||n>4))throw Error('Invalid explicit warrant submission');
  for(const key of ['environment','family','custody'])if(typeof body[key]!=='string'||body[key].length<1||body[key].length>256)throw Error('Explicit bounded context required');
 }else if(typeof body.artifact_digest!=='string'||!/^[0-9a-f]{64}$/.test(body.artifact_digest))throw Error('Invalid receipt identity');
 const client=new Client({name:'kex-owner-resolve-bridge',version:'1.0.0'});
 try{
  await client.connect(new StreamableHTTPClientTransport(new URL('http://127.0.0.1:'+instances[chosen]+'/mcp')));
  return await client.callTool({name:params.name==='owner_resolve_q32'?'resolve_q32':'read_resolve_receipt',arguments:body});
 }finally{await client.close();}
}
