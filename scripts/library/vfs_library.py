#!/usr/bin/env python3
"""Private persistent document catalogue; identities survive carrier relocation."""
import argparse,hashlib,json,os,sqlite3,uuid
from datetime import datetime,timezone
from pathlib import Path
DEFAULT=Path('/workspace/keddeh-private-vfs-library')
SECTORS=['SECTOR_FOUNDATIONS','SECTOR_MATHEMATICAL_LATTICE','SECTOR_SYSTEMS_ARCHITECTURE','SECTOR_EMPIRICAL_BENCHMARKS']
def sha(raw):return hashlib.sha256(raw).hexdigest()
class Library:
    def __init__(self,root):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.blobs=self.root/'objects';self.blobs.mkdir(exist_ok=True,mode=0o700)
        self.db=sqlite3.connect(self.root/'catalogue.sqlite');os.chmod(self.root/'catalogue.sqlite',0o600)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS document(identity TEXT PRIMARY KEY,source TEXT UNIQUE,title TEXT,sector TEXT,hash TEXT,bytes INTEGER,acquired TEXT,provenance TEXT)')
        self.db.execute('CREATE TABLE IF NOT EXISTS revision(identity TEXT,hash TEXT,acquired TEXT,PRIMARY KEY(identity,hash))');self.db.commit()
    def add(self,path,sector,source=None,provenance='workspace file; no original provider revision established'):
        if sector not in SECTORS:raise ValueError('unknown sector')
        p=Path(path);raw=p.read_bytes();h=sha(raw);source=source or str(p.resolve());now=datetime.now(timezone.utc).isoformat()
        prior=self.db.execute('SELECT identity FROM document WHERE source=?',(source,)).fetchone()
        identity=prior[0] if prior else 'kex::1x/library/'+uuid.uuid4().hex
        target=self.blobs/h
        if target.exists():
            if sha(target.read_bytes())!=h:raise ValueError('existing carrier corrupted')
        else:
            temp=self.blobs/(h+'.'+uuid.uuid4().hex+'.tmp')
            with open(temp,'xb') as f:
                os.chmod(temp,0o600);f.write(raw);f.flush();os.fsync(f.fileno())
            os.replace(temp,target)
            fd=os.open(self.blobs,os.O_RDONLY)
            try:os.fsync(fd)
            finally:os.close(fd)
        with self.db:
            self.db.execute('INSERT INTO document VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(source) DO UPDATE SET title=excluded.title,sector=excluded.sector,hash=excluded.hash,bytes=excluded.bytes,acquired=excluded.acquired,provenance=excluded.provenance',(identity,source,p.name,sector,h,len(raw),now,provenance))
            self.db.execute('INSERT OR IGNORE INTO revision VALUES(?,?,?)',(identity,h,now))
        return identity
    def records(self):
        self.db.row_factory=sqlite3.Row
        return [dict(r) for r in self.db.execute('SELECT * FROM document ORDER BY sector,title')]
    def get(self,identity):
        row=self.db.execute('SELECT hash FROM document WHERE identity=?',(identity,)).fetchone()
        if row is None:raise KeyError('unknown logical identity')
        raw=(self.blobs/row[0]).read_bytes()
        if sha(raw)!=row[0]:raise ValueError('carrier integrity failure')
        return raw
    def verify(self):
        failures=[]
        for identity,h in self.db.execute('SELECT identity,hash FROM revision'):
            p=self.blobs/h
            if not p.is_file() or sha(p.read_bytes())!=h:failures.append({'identity':identity,'hash':h})
        return failures
    def close(self):self.db.close()
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=DEFAULT);s=p.add_subparsers(dest='cmd',required=True)
    a=s.add_parser('add');a.add_argument('path');a.add_argument('--sector',choices=SECTORS,required=True);a.add_argument('--source');a.add_argument('--provenance')
    a=s.add_parser('search');a.add_argument('query',nargs='?',default='')
    a=s.add_parser('get');a.add_argument('identity');a.add_argument('--output',type=Path,required=True)
    s.add_parser('verify');args=p.parse_args();lib=Library(args.root)
    try:
        if args.cmd=='add':print(lib.add(args.path,args.sector,args.source,args.provenance or 'workspace source'))
        elif args.cmd=='search':print(json.dumps([r for r in lib.records() if args.query.lower() in (r['title']+' '+r['sector']+' '+r['source']).lower()],indent=2))
        elif args.cmd=='get':
            raw=lib.get(args.identity)
            with open(args.output,'xb') as f:os.chmod(args.output,0o600);f.write(raw)
        else:
            errors=lib.verify();print(json.dumps({'documents':len(lib.records()),'integrity_failures':errors},indent=2))
            if errors:raise SystemExit(1)
    finally:lib.close()
if __name__=='__main__':main()
