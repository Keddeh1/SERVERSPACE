#!/usr/bin/env python3
"""Deterministic paired bootstrap; descriptive local intervals only."""
import json,random,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'docs/research-and-development/sectors/SECTOR_EMPIRICAL_BENCHMARKS/incremental-replay-case-study'
data=json.loads((P/'RAW_DATA.json').read_text());rng=random.Random(20261008);out=[]
for row in data['summary']:
    n=row['events'];stage=row['stage']
    ratios=[r['full'][stage]['wall_ms']/r['incremental'][stage]['wall_ms'] for r in data['samples'] if r['events']==n]
    draws=sorted(statistics.median(rng.choices(ratios,k=len(ratios))) for _ in range(10000))
    out.append({**row,'paired_ratios':ratios,'descriptive_paired_bootstrap_95_interval':[draws[249],draws[9749]]})
print(json.dumps({'seed':20261008,'resamples':10000,'method':'paired ratio median, percentile bootstrap; no population guarantee','results':out},indent=2))
