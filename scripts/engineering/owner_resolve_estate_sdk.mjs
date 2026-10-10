import {Server} from '@modelcontextprotocol/sdk/server/index.js';
import {StdioServerTransport} from '@modelcontextprotocol/sdk/server/stdio.js';
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StdioClientTransport} from '@modelcontextprotocol/sdk/client/stdio.js';
import {ListToolsRequestSchema,CallToolRequestSchema,ListResourcesRequestSchema,ReadResourceRequestSchema} from '@modelcontextprotocol/sdk/types.js';
import {execFile} from 'node:child_process';
import {resolveTools,callOwnerResolve} from './resolve-bridge.mjs';
const original=new Client({name:'kex-contract-sdk-adapter',version:'1.0.0'});
await original.connect(new StdioClientTransport({command:process.execPath,args:['/workspace/KEDDEH--/mcp/server.mjs'],stderr:'inherit'}));
const additions=[
{name:'vfs_catalogue_search',description:'Search held documents through the existing private VFS catalogue.',inputSchema:{type:'object',properties:{query:{type:'string'}},additionalProperties:false}},
{name:'vfs_document_read',description:'Resolve an existing logical identity and return digest-verified bytes (maximum 1 MiB).',inputSchema:{type:'object',properties:{identity:{type:'string'}},required:['identity'],additionalProperties:false}},
{name:'runtime_service_health',description:'Read authenticated CA-verified registry or circuit service health.',inputSchema:{type:'object',properties:{service:{enum:['registry','circuits']}},required:['service'],additionalProperties:false}},
{name:'runtime_circuit_execute',description:'Execute through the existing circuit service and reconcile its persisted registry receipt.',inputSchema:{type:'object',properties:{job_id:{type:'string'},circuit:{type:'object'}},required:['job_id','circuit'],additionalProperties:false}}
];
const server=new Server({name:'keddeh-vfs-runtime-sdk',version:'1.0.0'},{capabilities:{tools:{},resources:{}}});
server.setRequestHandler(ListToolsRequestSchema,async()=>({tools:[...(await original.listTools()).tools,...additions,...resolveTools]}));
server.setRequestHandler(CallToolRequestSchema,async({params})=>{
 if(resolveTools.some(t=>t.name===params.name)){
  try{return await callOwnerResolve(params);}
  catch{return {isError:true,content:[{type:'text',text:'Owner RESOLVE request failed; reconcile its request identity against retained receipts before retrying.'}]};}
 }
 if(!additions.some(t=>t.name===params.name))return original.callTool(params);
 try{const result=await new Promise((resolve,reject)=>{const c=execFile('python3',['-B','/workspace/.keddeh-environment/mcp-sdk/backing.py'],{timeout:20000,maxBuffer:4*1024*1024},(e,out)=>e?reject(e):resolve(JSON.parse(out)));c.stdin.end(JSON.stringify(params));});return {content:[{type:'text',text:JSON.stringify(result)}]};}
 catch{return {isError:true,content:[{type:'text',text:'Backing operation failed; inspect private service state.'}]};}
});
server.setRequestHandler(ListResourcesRequestSchema,()=>original.listResources());
server.setRequestHandler(ReadResourceRequestSchema,({params})=>original.readResource(params));
await server.connect(new StdioServerTransport());
process.on('SIGTERM',async()=>{await original.close();await server.close();process.exit(0)});
