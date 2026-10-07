#!/usr/bin/env python3
"""Controlled loopback reference: per-event vs batched governed delta delivery."""
import argparse
import hashlib
import http.client
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import multiprocessing as mp
from pathlib import Path
import resource
import secrets
import statistics
import sys
import tempfile
import threading
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'web-estate/sites/aboudy-keddeh/runtime'))
from context_continuation import Continuation,canonical
from context_connector import export_delta,accept_delta,MAX_PACKET_BYTES

C={'origin':'pilot://energy/solar','ordinance':'pilot://fixture-policy','municipality':'fixture',
   'region':'AU-fixture','vector':'vfs://kex/relational-field/column/2/cell/1',
   'frame':'pilot://read-only-simulation','unit':'unit://1','revision':'1'}


def worker(pipe,database):
    journal=Continuation(database,[C]);journal.create('same-object');token=secrets.token_urlsafe(32)
    metrics={'accepted_requests':0,'payload_bytes':0}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            status=200
            try:
                if self.path!='/delta':raise ValueError('unknown route')
                if not secrets.compare_digest(self.headers.get('X-Pilot-Capability',''),token):
                    self.send_error(403);return
                n=int(self.headers.get('Content-Length','0'))
                if not 0<n<=MAX_PACKET_BYTES:raise ValueError('packet budget')
                raw=self.rfile.read(n)
                if len(raw)!=n:raise ValueError('incomplete packet')
                packet=json.loads(raw)
                if packet.get('continuation')!='same-object':raise ValueError('capability scope mismatch')
                receipt=accept_delta(journal,packet)
                metrics['accepted_requests']+=1;metrics['payload_bytes']+=n
            except (ValueError,TypeError,KeyError):status=409;receipt={'error':'packet rejected'}
            payload=json.dumps(receipt).encode();self.send_response(status)
            self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=lambda:server.serve_forever(poll_interval=.01),daemon=True);thread.start()
    pipe.send((server.server_port,token))
    while True:
        command=pipe.recv()
        if command=='sample':pipe.send({**metrics,'cpu_ns':time.process_time_ns(),
            'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        elif command=='verify':
            with journal.connect() as db:count=db.execute('SELECT count(*) FROM lineage').fetchone()[0]
            pipe.send({'receipt':journal.read('same-object',C),'events':count})
        elif command=='stop':break
    server.shutdown();server.server_close();thread.join();pipe.close()


def run(mode,steps,batch_size=None):
    batch_size=batch_size or steps
    with tempfile.TemporaryDirectory() as work:
        root=Path(work);parent,child=mp.Pipe();process=mp.Process(target=worker,args=(child,str(root/'remote.sqlite')))
        process.start();child.close();connection=None
        try:
            if not parent.poll(10):raise RuntimeError('reference receiver startup timeout')
            port,token=parent.recv();connection=http.client.HTTPConnection('127.0.0.1',port,timeout=10)
            def send(packet):
                payload=canonical(packet).encode();connection.request('POST','/delta',payload,
                    {'Content-Type':'application/json','X-Pilot-Capability':token})
                response=connection.getresponse();body=json.loads(response.read())
                if response.status!=200:raise ValueError('receiver rejected pilot delta')
                return body
            parent.send('sample');before=parent.recv();cpu=time.process_time_ns();start=time.perf_counter_ns()
            local=Continuation(root/'local.sqlite',[C]);local.create('same-object');head=None
            operations=[('+X',4),('-Y',5),('+Y',5),('-X',4)]
            sent_head=None
            for i in range(steps):
                base=head;axis,k=operations[i%4];head=local.advance('same-object',head,C,axis,k)['head']
                if mode=='per-event':receipt=send(export_delta(local,'same-object',base,head,C))
                elif (i+1)%batch_size==0:
                    receipt=send(export_delta(local,'same-object',sent_head,head,C));sent_head=head
            elapsed=time.perf_counter_ns()-start;client_cpu=time.process_time_ns()-cpu
            parent.send('sample');after=parent.recv();parent.send('verify');verified=parent.recv()
            assert receipt['head']==head and verified['receipt']['head']==head
            assert verified['events']==steps and verified['receipt']['value']=='1'
            # Lost acknowledgement retry must preserve exactly the same committed state.
            retry=send(export_delta(local,'same-object',None,head,C));assert retry['duplicate']
            parent.send('verify');again=parent.recv();assert again==verified
            return {'mode':mode,'steps':steps,'batch_size':1 if mode=='per-event' else batch_size,'wall_ns':elapsed,'client_cpu_ns':client_cpu,
                'server_cpu_ns':after['cpu_ns']-before['cpu_ns'],'server_peak_rss_kib':after['peak_rss_kib'],
                'requests':after['accepted_requests']-before['accepted_requests'],
                'json_payload_bytes':after['payload_bytes']-before['payload_bytes'],'final_head':head,
                'final_value':verified['receipt']['value'],'authoritative_events':verified['events'],'lost_ack_retry_idempotent':True}
        finally:
            if connection:connection.close()
            if process.is_alive():parent.send('stop');process.join(10)
            if process.is_alive():process.terminate();process.join()
            parent.close()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pairs',type=int,default=8);p.add_argument('--steps',type=int,default=64);p.add_argument('--batch-size',type=int);a=p.parse_args()
    if not 2<=a.pairs<=32 or not 4<=a.steps<=128 or a.steps%4:p.error('pairs 2..32; steps 4..128 in multiples of four')
    if a.batch_size is not None and (not 1<=a.batch_size<=a.steps or a.steps%a.batch_size):p.error('batch size must divide steps')
    samples=[]
    for i in range(a.pairs):
        for mode in (['per-event','batched'] if i%2==0 else ['batched','per-event']):samples.append(run(mode,a.steps,a.batch_size))
    assert len({s['final_head'] for s in samples})==1
    summary={mode:{metric:statistics.median(s[metric] for s in samples if s['mode']==mode)
        for metric in ['wall_ns','client_cpu_ns','server_cpu_ns','server_peak_rss_kib','requests','json_payload_bytes']}
        for mode in ['per-event','batched']}
    print(json.dumps({'scope':'synthetic same-host HTTP connector reference; both arms use the same KEX journal and independent receiver replay',
       'paired_rounds':a.pairs,'steps_per_session':a.steps,'batch_size':a.batch_size or a.steps,'order':'alternating','samples':samples,'summary':summary,
       'equivalence':'identical object, context, final head, exact value and authoritative event set',
       'acknowledgement_semantics':'per-event acknowledges each event; batch acknowledges entire session atomically; only session-final acknowledgement is compared',
       'physical_energy_joules_measured':None,'actual_customer_cloud_savings':None,
       'actuation':'none; fixture arithmetic and temporary journals only'},indent=2))

if __name__=='__main__':main()
