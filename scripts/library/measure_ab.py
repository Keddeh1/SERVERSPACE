"""Measure synthetic full samples and explicitly bounded attachment prefixes."""
import json,sys
from pathlib import Path
from ab_codec import pack,unpack
rows=[]
samples=[('synthetic-zero',b'\0'*1024),('synthetic-alternation',b'\xaa'*1024)]
samples += [(p.name,p.read_bytes()[:256]) for p in sorted(Path('/workspace/attachments').rglob('*')) if p.is_file()]
for title,raw in samples:
    current=raw;sizes=[]
    for depth in range(1,4):
        previous=current;current=pack(previous);assert unpack(current)==previous;sizes.append(len(current))
    rows.append({'source':title,'scope':'complete synthetic sample' if title.startswith('synthetic') else 'first 256 bytes or shorter; not whole-document compression','input_bytes':len(raw),'layer_bytes':sizes})
print(json.dumps({'definition':'A counts ones; B counts zeros; ASCII count framing AB1','encryption':False,'all_round_trips_passed':True,'samples':rows},indent=2))
