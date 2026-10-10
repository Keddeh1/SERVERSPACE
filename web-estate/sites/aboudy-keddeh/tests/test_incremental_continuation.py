from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
from context_continuation import Continuation,digest,canonical
from incremental_continuation import IncrementalContinuation
from test_context_connector import C


class IncrementalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();p=Path(self.tmp.name)
        self.full=Continuation(p/'full.sqlite',[C]);self.fast=IncrementalContinuation(p/'fast.sqlite',[C])
        for r in [self.full,self.fast]:r.create('a')
    def tearDown(self):self.tmp.cleanup()
    def populate(self):
        heads=[None,None]
        for i in range(32):
            axis,k=[('+X',4),('-Y',5),('+Y',5),('-X',4)][i%4]
            for j,r in enumerate([self.full,self.fast]):heads[j]=r.advance('a',heads[j],C,axis,k)['head']
        self.assertEqual(heads[0],heads[1]);return heads[0]
    def test_equivalence_restart_and_cached_arithmetic(self):
        import incremental_continuation as module
        head=self.populate();self.assertEqual(self.fast.read('a',C),self.full.read('a',C))
        original=module.operate;calls=[]
        counted=lambda *args:(calls.append(args),original(*args))[1]
        with patch.object(module,'operate',counted),patch('context_continuation.operate',counted):
            self.fast.read('a',C);self.assertEqual(len(calls),0)
            self.fast.advance('a',head,C,'-Y',5);self.assertEqual(len(calls),1)
        reopened=IncrementalContinuation(self.fast.database,[C]);self.assertEqual(reopened.read('a',C)['value'],'1/5')
    def test_cached_ancestor_corruption_and_missing_row_rejected(self):
        self.populate();self.fast.read('a',C)
        with self.fast.connect() as db:
            row=db.execute('SELECT hash,body FROM lineage ORDER BY rowid LIMIT 1').fetchone()
            body=__import__('json').loads(row[1]);body['result']='999'
            db.execute('UPDATE lineage SET body=? WHERE hash=?',(canonical(body),row[0]))
        with self.assertRaises(ValueError):self.fast.read('a',C)
        with self.fast.connect() as db:db.execute('DELETE FROM lineage WHERE hash=?',(row[0],))
        with self.assertRaises(ValueError):self.fast.read('a',C)
    def test_policy_revocation_invalidates_cache(self):
        self.populate();self.fast.read('a',C);self.fast.contexts.clear()
        with self.assertRaises(ValueError):self.fast.read('a',C)
    def test_stale_head_rejected_without_cache_shortcut(self):
        self.populate();self.fast.read('a',C)
        with self.assertRaises(ValueError):self.fast.advance('a',None,C,'+X',1)

    def test_cache_budget_eviction_preserves_verified_reads(self):
        for i in range(8):
            name=f'field-{i}';self.fast.create(name);self.fast.read(name,C)
        self.assertLessEqual(len(self.fast._verified),4)
        self.assertEqual(self.fast.read('field-0',C)['value'],'1')

    def test_context_changes_invalidate_cached_semantics(self):
        grid={**C,'origin':'fixture://grid'};permissions=[(digest(C),digest(grid))]
        runtime=IncrementalContinuation(Path(self.tmp.name)/'permissions.sqlite',[C,grid],permissions)
        runtime.create('a',C);a=runtime.advance('a',None,C,'+X',4)
        runtime.advance('a',a['head'],grid,'-Y',5);runtime.read('a',grid)
        runtime.transitions=frozenset()
        with self.assertRaises(ValueError):runtime.read('a',grid)

    def test_advance_arithmetic_counts_against_source_model(self):
        import incremental_continuation as module
        import context_continuation as base
        original=base.operate
        for runtime,expected in [(self.full,2080),(self.fast,127)]:
            calls=[]
            def counted(*args):calls.append(args);return original(*args)
            head=None
            with patch.object(module,'operate',counted),patch.object(base,'operate',counted):
                for i in range(64):
                    axis,k=[('+X',4),('-Y',5),('+Y',5),('-X',4)][i%4]
                    head=runtime.advance('a',head,C,axis,k)['head']
            self.assertEqual(len(calls),expected)
