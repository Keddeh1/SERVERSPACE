import json
from pathlib import Path
from ab_codec import pack,compact_pack,compact_unpack
samples=[('synthetic-zero',b'\0'*1024),('synthetic-alternation',b'\xaa'*1024)]
samples += [(p.name,p.read_bytes()[:256]) for p in sorted(Path('/workspace/attachments').rglob('*')) if p.is_file()]
rows=[]
for name,raw in samples:
    compact=compact_pack(raw);assert compact_unpack(compact)==raw
    rows.append({'source':name,'scope':'synthetic complete' if name.startswith('synthetic') else 'first 256 bytes or shorter','input_bytes':len(raw),'decimal_ab_bytes':len(pack(raw)),'compact_bytes':len(compact)})
print(json.dumps({'mapping':{'ones':'C-K = 1-9','zeros':'L-T = 1-9'},'all_round_trips_passed':True,'samples':rows},indent=2))
