#!/usr/bin/env python3
"""Matched enquiry pilot against the unchanged review HTTP backend; synthetic data only."""
import argparse
import hashlib
import http.client
import json
import multiprocessing as mp
import os
from pathlib import Path
import resource
import statistics
import sys
import tempfile
import threading
import time
import uuid
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'web-estate/sites/aboudy-keddeh/runtime'))
from server import Server, NOTICE
from support.interest import validate
from context_continuation import Continuation

C={'origin':'pilot://one','ordinance':'pilot://fixture-policy','municipality':'fixture',
   'region':'fixture-only','vector':'vfs://kex/relational-field/column/2/cell/1',
   'frame':'pilot://enquiry','unit':'unit://1','revision':'1'}
PAYLOAD={'name':'Synthetic pilot','email':'pilot@example.invalid','organisation':'Fixture',
   'message':'Synthetic benchmark; no delivery requested.','use_case':'website-foundry',
   'privacy_consent':True,'marketing_consent':False,'notice_revision':NOTICE}
REQUEST_ID=str(uuid.uuid5(uuid.NAMESPACE_URL,'pilot://same-business-outcome'))


def worker(pipe,database):
    server=Server(('127.0.0.1',0),Path(database),True)
    thread=threading.Thread(target=lambda:server.serve_forever(poll_interval=.01),daemon=True);thread.start()
    pipe.send(server.server_port)
    while True:
        command=pipe.recv()
        if command=='sample':pipe.send({'cpu_ns':time.process_time_ns(),
            'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        elif command=='stop':break
    server.shutdown();server.server_close();thread.join();pipe.close()


def request(port,method,path,body=None,headers=None):
    connection=http.client.HTTPConnection('127.0.0.1',port,timeout=10)
    connection.request(method,path,body=body,headers=headers or {})
    response=connection.getresponse();raw=response.read();result=(response.status,json.loads(raw),dict(response.getheaders()),len(raw))
    connection.close();return result


def run(mode):
    with tempfile.TemporaryDirectory() as work:
        root=Path(work);parent,child=mp.Pipe();process=mp.Process(target=worker,args=(child,str(root/'backend.sqlite')));process.start();child.close()
        try:
            if not parent.poll(10):raise RuntimeError('backend startup timed out')
            port=parent.recv();status,cap,headers,size=request(port,'GET','/api/capabilities')
            assert status==200 and cap['capture_enabled']
            submit_headers={'Origin':f'http://127.0.0.1:{port}','Content-Type':'application/json',
              'Cookie':headers['Set-Cookie'].split(';')[0],'X-CSRF-Token':cap['csrf_token'],'Idempotency-Key':REQUEST_ID}
            parent.send('sample');server_before=parent.recv();cpu=time.process_time_ns();start=time.perf_counter_ns()
            assert not validate(PAYLOAD,NOTICE)
            if mode=='kex':
                runtime=Continuation(root/'local.sqlite',[C]);runtime.create('enquiry');head=None
                for axis,k in [('+X',4),('-Y',5),('+Y',5),('-X',4)]:
                    receipt=runtime.advance('enquiry',head,C,axis,k);head=receipt['head']
                reopened=Continuation(root/'local.sqlite',[C]);assert reopened.read('enquiry',C)['head']==head
                assert reopened.read('enquiry',C)['value']=='1'
            raw=json.dumps(PAYLOAD,separators=(',',':')).encode()
            status,result,_,response_bytes=request(port,'POST','/api/interest',raw,submit_headers)
            wall=time.perf_counter_ns()-start;client_cpu=time.process_time_ns()-cpu
            parent.send('sample');server_after=parent.recv()
            assert status==201 and result['status']=='recorded' and result['registration_id']==REQUEST_ID
            import sqlite3
            with sqlite3.connect(root/'backend.sqlite') as db:
                row=db.execute('SELECT digest,payload FROM interests WHERE request_id=?',(REQUEST_ID,)).fetchone()
                assert json.loads(row[1])==PAYLOAD
                count=db.execute('SELECT count(*) FROM interests').fetchone()[0];assert count==1
            # Replay same operation through the existing backend idempotency path.
            replay_status,replay,_,_=request(port,'POST','/api/interest',raw,submit_headers)
            assert replay_status==201 and replay['registration_id']==REQUEST_ID
            with sqlite3.connect(root/'backend.sqlite') as db:assert db.execute('SELECT count(*) FROM interests').fetchone()[0]==1
            return {'mode':mode,'wall_ns':wall,'client_cpu_ns':client_cpu,
                'server_cpu_ns':server_after['cpu_ns']-server_before['cpu_ns'],
                'server_peak_rss_kib':server_after['peak_rss_kib'],
                'client_process_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                'timed_business_requests':1,'timed_json_payload_bytes':len(raw),
                'timed_response_bytes':response_bytes,'persisted_payload_digest':row[0],
                'idempotent_replay_preserved_one_record':True,
                'kex_continuation_reopened':mode=='kex'}
        finally:
            if process.is_alive():parent.send('stop');process.join(10)
            if process.is_alive():process.terminate();process.join()
            parent.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--pairs',type=int,default=12);args=parser.parse_args()
    if not 2<=args.pairs<=100:parser.error('pairs must be 2..100')
    samples=[]
    for i in range(args.pairs):
        for mode in (['baseline','kex'] if i%2==0 else ['kex','baseline']):samples.append(run(mode))
    assert len({s['persisted_payload_digest'] for s in samples})==1
    summary={}
    for mode in ['baseline','kex']:
        rows=[s for s in samples if s['mode']==mode]
        summary[mode]={metric:{'median':statistics.median(r[metric] for r in rows),
             'min':min(r[metric] for r in rows),'max':max(r[metric] for r in rows)}
             for metric in ['wall_ns','client_cpu_ns','server_cpu_ns','server_peak_rss_kib']}
        summary[mode]['completed_business_requests']=len(rows)
    power_files=list(Path('/sys/class/powercap').glob('**/energy_uj')) if Path('/sys/class/powercap').exists() else []
    print(json.dumps({'scope':'local synthetic enquiry qualification; Python orchestration, unchanged existing HTTP backend',
       'paired_rounds':args.pairs,'order':'alternating','samples':samples,'summary':summary,
       'equivalence':'same request identity, input, stored payload digest and one authoritative record; KEX additionally retains four contextual transitions',
       'request_reduction_percent':0,'energy_measurement':{'available_meter_files':len(power_files),'joules_measured':None},
       'actual_cloud_cost_reduction':None,'actual_llm_tokens_or_gpu_flops_measured':False,
       'limitations':['loopback network','synthetic workflow','baseline already validates locally','additional KEX lineage work is not present in baseline',
          'RSS is process high-water mark; parent peak is shared across samples','no browser/device power measurement','no production customer traffic'],
       'checks':'all sessions persisted identical payload; idempotent retries preserved one record; KEX context survived reopen'},indent=2))

if __name__=='__main__':main()
