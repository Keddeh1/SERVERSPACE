#!/usr/bin/env python3
"""File technical artefacts by reference under owner sectors with verifiable hashes."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'docs/research-and-development'
SECTORS=['SECTOR_FOUNDATIONS','SECTOR_MATHEMATICAL_LATTICE','SECTOR_SYSTEMS_ARCHITECTURE','SECTOR_EMPIRICAL_BENCHMARKS']
PATHS=['docs/engineering','docs/analysis','docs/planning','docs/research-and-development/sectors',
       'web-estate/sites/aboudy-keddeh/research','web-estate/sites/aboudy-keddeh/runtime',
       'web-estate/sites/aboudy-keddeh/tests','web-estate/sites/aboudy-keddeh/dist/assets','scripts/research-and-development','scripts/library','scripts/analysis','scripts/engineering','scripts/planning']


def sector(path):
    text=str(path).lower();name=path.name.lower()
    for value in SECTORS:
        if value.lower() in text:return value
    if name in {'agents.md','research_protocol.md','index_research.py'}:return SECTORS[0]
    if name=='analyse_connector_case.py':return SECTORS[3]
    if '/tests/' in text or '/scripts/analysis/' in '/'+text or any(v in name for v in ['readback','verification','pilot','scenarios','ray-readback']):
        return SECTORS[3]
    if any(v in name for v in ['source','custody','inventory','decision','action_plan','utility','project_configuration']) or 'docs/planning' in text:
        return SECTORS[0]
    if 'number-line' in text or 'one_origin' in text:return SECTORS[1]
    return SECTORS[2]


def main():
    files={ROOT/'README.md',ROOT/'AGENTS.md',DEST/'README.md',DEST/'RESEARCH_PROTOCOL.md'}
    for base in PATHS:
        for p in (ROOT/base).rglob('*'):
            if p.is_file() and p.suffix.lower() in {'.md','.json','.py','.js','.cjs','.ics','.html','.pdf','.xml','.png'} and '__pycache__' not in p.parts:
                files.add(p)
    rows=[]
    for p in sorted(files):
        relative=p.relative_to(ROOT);raw=p.read_bytes()
        rows.append({'path':str(relative),'primary_sector':sector(relative),
            'document_type':'implementation-or-test' if p.suffix.lower() in {'.py','.js','.cjs'} else 'formal-document-or-record',
            'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
            'evidence_rule':'Consult source scope/result; filing alone confers no qualification.'})
    data={'schema':'kex.formal-rnd-register.v1','filing_method':'canonical source reference plus primary sector; no duplicate authority',
          'source_taxonomy':'owner Cross-Sector Embedded Memory Seed v1.0 four named sectors',
          'coverage_roots':PATHS,'indexed_artefacts':len(rows),'artefacts':rows}
    DEST.mkdir(parents=True,exist_ok=True)
    (DEST/'REGISTRY.json').write_text(json.dumps(data,indent=2)+'\n')
    text='# Formal R&D sector filing index\n\nCanonical artefacts retain their locations. SHA-256 readbacks are in [REGISTRY.json](REGISTRY.json). Filing is not a completion claim.\n'
    for value in SECTORS:
        text+='\n## '+value+'\n\n'
        for row in rows:
            if row['primary_sector']==value:text+=f'- [{row["path"]}](../../{row["path"]})\n'
    (DEST/'INDEX.md').write_text(text)
    assert len({r['path'] for r in rows})==len(rows)
    for row in rows:assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
    print(json.dumps({'indexed_artefacts':len(rows),'missing':0,'hash_mismatches':0,
        'sectors':{s:sum(r['primary_sector']==s for r in rows) for s in SECTORS}},indent=2))

if __name__=='__main__':main()
