#!/usr/bin/env python3
"""Matched durable-journal pilot; measures time, not electrical energy."""
import json
import statistics
import sys
import tempfile
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'web-estate/sites/aboudy-keddeh/runtime'))
from context_continuation import Continuation
from incremental_continuation import IncrementalContinuation
C={'origin':'fixture://solar','ordinance':'fixture://policy','municipality':'fixture','region':'AU-fixture','vector':'fixture://solar/1','frame':'fixture://measurement','unit':'unit://1','revision':'1'}
def timed(fn):
    a=time.perf_counter_ns();b=time.process_time_ns();value=fn()
    return value,{'wall_ms':(time.perf_counter_ns()-a)/1e6,'cpu_ms':(time.process_time_ns()-b)/1e6}
def sample(cls,n,path):
    r=cls(path,[C]);r.create('a')
    def advance():
        head=None
        for i in range(n):
            axis,k=[('+X',4),('-Y',5),('+Y',5),('-X',4)][i%4]
            head=r.advance('a',head,C,axis,k)['head']
        return head
    head,build=timed(advance)
    cold,cold_time=timed(lambda:cls(path,[C]).read('a',C))
    r.read('a',C)
    warm,warm_time=timed(lambda:[r.read('a',C) for _ in range(16)])
    oracle=Continuation(path,[C]).read('a',C)
    assert oracle==cold==warm[-1] and oracle['head']==head
    return {'head':head,'build':build,'cold_read':cold_time,'warm_16_reads':warm_time}
def main():
    rows=[]
    with tempfile.TemporaryDirectory() as tmp:
        for n in [64,128]:
            for pair in range(8):
                row={'events':n,'pair':pair,'order':['full','incremental'] if pair%2==0 else ['incremental','full']}
                for name in row['order']:
                    cls=Continuation if name=='full' else IncrementalContinuation
                    row[name]=sample(cls,n,Path(tmp)/f'{n}-{pair}-{name}.sqlite')
                assert row['full']['head']==row['incremental']['head']
                rows.append(row)
    summary=[]
    for n in [64,128]:
        group=[r for r in rows if r['events']==n]
        for stage in ['build','cold_read','warm_16_reads']:
            summary.append({'events':n,'stage':stage,'paired_median_wall_ratio_full_over_incremental':statistics.median(r['full'][stage]['wall_ms']/r['incremental'][stage]['wall_ms'] for r in group),'full_median_wall_ms':statistics.median(r['full'][stage]['wall_ms'] for r in group),'incremental_median_wall_ms':statistics.median(r['incremental'][stage]['wall_ms'] for r in group)})
    print(json.dumps({'schema':'kex.incremental-replay-pilot.v1','pairs_per_size':8,'warm_reads':16,'all_oracle_checks_passed':True,'energy_measured':False,'samples':rows,'summary':summary},indent=2))
if __name__=='__main__':main()
