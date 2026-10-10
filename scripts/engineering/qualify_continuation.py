#!/usr/bin/env python3
"""Local qualification using a privately retained owner field; no external service calls."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'web-estate/sites/aboudy-keddeh/runtime'))
from relational_memory import RelationalMemory, coordinates, location
from context_continuation import Continuation, resolve_bound_cell

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--memory-file',type=Path,required=True)
args=parser.parse_args()
raw=args.memory_file.read_bytes();memory=RelationalMemory(json.loads(raw))
for address in range(1,4097):
    source,target=coordinates(address)
    assert memory.read(source,target)['linear_address']==address
c={'origin':'local-review://one','ordinance':'local-review://fixture-policy','municipality':'fixture',
   'region':'fixture-region','vector':location(1,2)['vfs_address'],'frame':'local-review://software-test',
   'unit':'unit://1','revision':'1'}
with tempfile.TemporaryDirectory() as work:
    root=Path(work);primary=Continuation(root/'primary.sqlite',[c]);primary.create('qualification')
    first=primary.advance('qualification',None,c,'+X',4)
    second=primary.advance('qualification',first['head'],c,'-Y',5)
    with sqlite3.connect(primary.database) as source,sqlite3.connect(root/'secondary.sqlite') as target:source.backup(target)
    secondary=Continuation(root/'secondary.sqlite',[c])
    with sqlite3.connect(primary.database) as db:db.execute('DELETE FROM lineage WHERE hash=?',(first['head'],))
    del memory.cells[2]
    result=resolve_bound_cell([primary,secondary],memory,'qualification',second['head'],c,1,2)
    assert result['lineage']['fallback_used'] and result['memory']['fallback_used']
    assert result['lineage']['value']=='1' and result['lineage']['head']==second['head']
    print(json.dumps({'status':'passed','source_sha256':hashlib.sha256(raw).hexdigest(),
        'owner_cells_admitted':4096,'lineage_steps_replayed':2,'exact_arithmetic_result':'1',
        'lineage_fallback_path':result['lineage']['path'],'memory_fallback_path':result['memory']['resolution_path'],
        'scope':'same-host software qualification; temporary fixture policy; no regional consensus assertion'},indent=2))
