import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
from context_continuation import Continuation, conjugate, digest, canonical, resolve_equivalent

C={'origin':'fixture://one','ordinance':'policy://agreed/1','municipality':'fixture-city',
   'region':'AU-SA','vector':'route://fixture','frame':'measurement://fixture','unit':'unit://1','revision':'1'}


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'primary.sqlite'
        self.runtime=Continuation(self.path,[C]);self.runtime.create('a')
    def tearDown(self):self.tmp.cleanup()
    def advance(self,axis,k,head=None):return self.runtime.advance('a',head,C,axis,k)
    def replica(self):
        p=Path(self.tmp.name)/'secondary.sqlite'
        with sqlite3.connect(self.path) as source,sqlite3.connect(p) as target:source.backup(target)
        return Continuation(p,[C])

    def test_four_rays_exact_signed_zero(self):
        for axis,k,expected in [('+X',5,'6'),('-X',5,'-4'),('+Y',5,'5'),('-Y',5,'1/5'),('-X',1,'0')]:
            self.runtime.create(axis+str(k));r=self.runtime.advance(axis+str(k),None,C,axis,k)
            self.assertEqual(r['value'],expected)
            self.assertEqual(self.runtime.read(axis+str(k),C)['value'],expected)

    def test_restart_replay_and_reentry(self):
        a=self.advance('+X',4);b=self.advance('-X',4,a['head'])
        self.assertEqual(b['value'],'1')
        restarted=Continuation(self.path,[C]);self.assertEqual(restarted.read('a',C)['head'],b['head'])
        c=restarted.advance('a',b['head'],C,'-Y',5)
        self.assertEqual(c['value'],'1/5')

    def test_stale_head_cannot_commit(self):
        r=self.advance('+X',1)
        with self.assertRaises(ValueError):self.advance('+Y',2)
        self.assertEqual(self.runtime.read('a',C)['head'],r['head'])

    def test_context_substitution_and_unadmitted_transition(self):
        d={**C,'region':'different'}
        with self.assertRaises(ValueError):self.runtime.advance('a',None,d,'+X',1)
        runtime=Continuation(self.path,[C,d]);r=self.advance('+X',1)
        with self.assertRaises(ValueError):runtime.advance('a',r['head'],d,'+X',1)
        with self.assertRaises(ValueError):runtime.read('a',d)

    def test_explicit_cross_origin_transition_preserves_context(self):
        d={**C,'origin':'fixture://two','region':'NZ'}
        runtime=Continuation(self.path,[C,d],[(digest(C),digest(d))])
        a=runtime.advance('a',None,C,'+X',1);b=runtime.advance('a',a['head'],d,'-Y',2)
        self.assertEqual(runtime.read('a',d)['value'],'1')
        with self.assertRaises(ValueError):runtime.read('a',C)
        with self.assertRaises(ValueError):runtime.advance('a',b['head'],C,'+X',1)

    def test_missing_predecessor_fallback_and_double_failure(self):
        a=self.advance('+X',1);b=self.advance('+Y',3,a['head']);secondary=self.replica()
        with sqlite3.connect(self.path) as db:db.execute('DELETE FROM lineage WHERE hash=?',(a['head'],))
        r=resolve_equivalent([self.runtime,secondary],'a',b['head'],C)
        self.assertTrue(r['fallback_used']);self.assertEqual(r['path'],2);self.assertEqual(r['value'],'6')
        with sqlite3.connect(secondary.database) as db:db.execute('DELETE FROM lineage WHERE hash=?',(a['head'],))
        with self.assertRaises(ValueError):resolve_equivalent([self.runtime,secondary],'a',b['head'],C)

    def test_rehashed_logically_false_vector_rejected(self):
        a=self.advance('+X',1)
        with sqlite3.connect(self.path) as db:
            body=json.loads(db.execute('SELECT body FROM lineage WHERE hash=?',(a['head'],)).fetchone()[0])
            body['result']='500';key=digest(body)
            db.execute('INSERT INTO lineage VALUES (?,?)',(key,canonical(body)))
            db.execute('UPDATE continuation SET head=? WHERE id=?',(key,'a'))
        with self.assertRaises(ValueError):self.runtime.read('a',C)

    def test_alternate_stale_or_equal_scalar_lineage_rejected(self):
        secondary=self.replica();a=self.advance('+X',4)
        alternate=secondary.advance('a',None,C,'+Y',5)
        self.assertEqual(a['value'],alternate['value']);self.assertNotEqual(a['head'],alternate['head'])
        with self.assertRaises(ValueError):resolve_equivalent([secondary],'a',a['head'],C)

    def test_conjugation_is_operation_translation(self):
        self.assertEqual(conjugate(1,'double'),1)
        self.assertEqual(conjugate(3,'double'),5)
        self.assertEqual(conjugate(1,'increment'),2)
        for bad in [0,-1,True,1.5,'1']:
            with self.assertRaises(ValueError):conjugate(bad,'identity')
        with self.assertRaises(ValueError):conjugate(2**24,'increment')

    def test_invalid_parameter_rolls_back(self):
        for bad in [0,-1,True,1.5,'1']:
            with self.assertRaises(ValueError):self.advance('-Y',bad)
        with self.assertRaises(ValueError):self.advance('unknown',1)
        self.assertEqual(self.runtime.read('a',C)['sequence'],0)

    def test_vfs_coordinate_bound_to_context_and_lineage(self):
        from test_relational_memory import fixture
        from relational_memory import RelationalMemory, location
        from context_continuation import resolve_bound_cell
        memory=RelationalMemory(fixture());d={**C,'vector':location(1,2)['vfs_address']}
        runtime=Continuation(Path(self.tmp.name)/'bound.sqlite',[d]);runtime.create('bound')
        r=runtime.advance('bound',None,d,'-Y',5)
        del memory.cells[2]
        readback=resolve_bound_cell([runtime],memory,'bound',r['head'],d,1,2)
        self.assertEqual(readback['lineage']['value'],'1/5')
        self.assertTrue(readback['memory']['fallback_used'])
        with self.assertRaises(ValueError):resolve_bound_cell([runtime],memory,'bound',r['head'],d,2,1)

    def test_competing_writers_commit_one_successor(self):
        from concurrent.futures import ThreadPoolExecutor
        def writer(k):
            try:return self.advance('+X',k)
            except ValueError:return None
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(writer,[2,3]))
        self.assertEqual(sum(r is not None for r in results),1)
        self.assertEqual(self.runtime.read('a',C)['sequence'],1)

    def test_genesis_context_cannot_be_substituted(self):
        d={**C,'origin':'fixture://second'};runtime=Continuation(self.path,[C,d])
        with self.assertRaises(ValueError):runtime.read('a',d)
        with self.assertRaises(ValueError):runtime.create('ambiguous')
        runtime.create('explicit',d)
        self.assertEqual(runtime.read('explicit',d)['value'],'1')

    def test_bad_lineage_shape_is_rejected_and_fallback_works(self):
        a=self.advance('+X',1);secondary=self.replica()
        with sqlite3.connect(self.path) as db:db.execute('UPDATE lineage SET body=? WHERE hash=?',('[]',a['head']))
        r=resolve_equivalent([self.runtime,secondary],'a',a['head'],C)
        self.assertTrue(r['fallback_used'])
