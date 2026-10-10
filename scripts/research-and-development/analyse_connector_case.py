#!/usr/bin/env python3
"""Descriptive paired bootstrap for predeclared batch-size sensitivity runs."""
import hashlib
import argparse
import json
from pathlib import Path
import random
import statistics

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/research-and-development/sectors/SECTOR_EMPIRICAL_BENCHMARKS/connector-case-study'


def paired(samples,metric):
    ratios=[]
    for i in range(0,len(samples),2):
        pair={s['mode']:s for s in samples[i:i+2]}
        assert set(pair)=={'per-event','batched'}
        assert pair['per-event']['final_head']==pair['batched']['final_head']
        ratios.append(pair['per-event'][metric]/pair['batched'][metric])
    return ratios


def describe(ratios):
    rng=random.Random(20261008)
    draws=sorted(statistics.median(rng.choices(ratios,k=len(ratios))) for _ in range(10000))
    return {'paired_ratios':ratios,'paired_median_ratio':statistics.median(ratios),
      'descriptive_95_percentile_bootstrap_interval':[draws[int(.025*(len(draws)-1))],draws[int(.975*(len(draws)-1))]],
      'resamples':10000,'seed':20261008}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input-dir',type=Path,default=OUT);parser.add_argument('--pattern',default='batch-{batch}.json');args=parser.parse_args()
    rows=[];all_heads=set()
    for batch in [1,4,16,64]:
        source=args.input_dir/args.pattern.format(batch=batch);raw=source.read_bytes();d=json.loads(raw)
        assert d['paired_rounds']==6 and d['steps_per_session']==64 and d['batch_size']==batch
        all_heads.update(s['final_head'] for s in d['samples'])
        for s in d['samples']:
            assert s['authoritative_events']==64 and s['lost_ack_retry_idempotent'] and s['final_value']=='1'
            assert s['requests']==(64 if s['mode']=='per-event' else 64//batch)
        (OUT/f'batch-{batch}.json').write_bytes(raw)
        rows.append({'batch_size':batch,'receiver_replay_operations_source_model':(3*64*64//batch-64)//2,
          'requests_per_session':64//batch,'source_sha256':hashlib.sha256(raw).hexdigest(),
          'observed_medians':d['summary'],
          'wall_ratio':describe(paired(d['samples'],'wall_ns')),
          'receiver_cpu_ratio':describe(paired(d['samples'],'server_cpu_ns'))})
    assert len(all_heads)==1
    result={'research_id':'RND-CONNECTOR-001','final_sessions':48,'final_pairs':24,
      'operations_per_session':64,'control':'B=1 uses equivalent delivery paths',
      'analysis':'paired per-round ratios; descriptive percentile bootstrap; no general p-value or p99 claim',
      'inference_limits':['six pairs per size','one shared host','loopback transport','local storage profile',
        'session-final vs per-event acknowledgement contract','not a browser/whole-enterprise measurement'],
      'all_final_heads_equal':True,'results':rows}
    (OUT/'ANALYSIS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({r['batch_size']:{'wall_ratio':r['wall_ratio']['paired_median_ratio'],
      'wall_interval':r['wall_ratio']['descriptive_95_percentile_bootstrap_interval'],
      'receiver_cpu_ratio':r['receiver_cpu_ratio']['paired_median_ratio']} for r in rows},indent=2))

if __name__=='__main__':main()
