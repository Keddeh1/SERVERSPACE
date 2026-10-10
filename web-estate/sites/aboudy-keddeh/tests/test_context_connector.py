import copy
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
from context_continuation import Continuation,digest
from context_connector import export_delta,accept_delta

C={'origin':'fixture://solar','ordinance':'fixture://policy','municipality':'fixture','region':'AU-fixture',
   'vector':'fixture://solar/1','frame':'fixture://measurement','unit':'unit://1','revision':'1'}


class ConnectorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();root=Path(self.tmp.name)
        self.source=Continuation(root/'source.sqlite',[C]);self.target=Continuation(root/'target.sqlite',[C])
        for r in [self.source,self.target]:r.create('same-object')
        head=None
        for axis,k in [('+X',4),('-Y',5),('+Y',5),('-X',4)]:
            head=self.source.advance('same-object',head,C,axis,k)['head']
        self.packet=export_delta(self.source,'same-object',None,head,C)
    def tearDown(self):self.tmp.cleanup()
    def assert_empty(self):
        self.assertIsNone(self.target.read('same-object',C)['head'])
        with self.target.connect() as db:self.assertEqual(db.execute('SELECT count(*) FROM lineage').fetchone()[0],0)

    def test_atomic_handoff_retry_and_placement(self):
        r=accept_delta(self.target,self.packet);self.assertEqual(r['value'],'1');self.assertFalse(r['duplicate'])
        again=accept_delta(self.target,self.packet);self.assertTrue(again['duplicate'])
        self.assertEqual(self.target.read('same-object',C)['head'],self.source.read('same-object',C)['head'])
        with self.target.connect() as db:self.assertEqual(db.execute('SELECT count(*) FROM lineage').fetchone()[0],4)

    def test_stale_destination_cannot_overwrite(self):
        r=self.target.advance('same-object',None,C,'+X',9)
        with self.assertRaises(ValueError):accept_delta(self.target,self.packet)
        self.assertEqual(self.target.read('same-object',C)['head'],r['head'])

    def test_each_corrupted_event_rolls_back_entire_delta(self):
        for i in range(4):
            p=copy.deepcopy(self.packet);p['events'][i]['body']['result']='999'
            with self.assertRaises(ValueError):accept_delta(self.target,p)
            self.assert_empty()

    def test_rehashed_false_vector_rolls_back(self):
        p=copy.deepcopy(self.packet);p['events'][-1]['body']['result']='999'
        p['events'][-1]['hash']=digest(p['events'][-1]['body']);p['target_head']=p['events'][-1]['hash']
        with self.assertRaises(ValueError):accept_delta(self.target,p)
        self.assert_empty()

    def test_cross_field_and_reordered_chain_rejected(self):
        p=copy.deepcopy(self.packet);p['target_context']['origin']='fixture://grid'
        with self.assertRaises(ValueError):accept_delta(self.target,p)
        p=copy.deepcopy(self.packet);p['events'].reverse()
        with self.assertRaises(ValueError):accept_delta(self.target,p)
        self.assert_empty()

    def test_retry_requires_actual_packet_evidence(self):
        accept_delta(self.target,self.packet);p=copy.deepcopy(self.packet);p['events'][1]['hash']='wrong'
        with self.assertRaises(ValueError):accept_delta(self.target,p)
        self.assertEqual(self.target.read('same-object',C)['head'],self.packet['target_head'])

    def test_incremental_delta_and_nonancestor_export(self):
        accept_delta(self.target,self.packet);base=self.packet['target_head']
        next_head=self.source.advance('same-object',base,C,'-Y',5)['head']
        delta=export_delta(self.source,'same-object',base,next_head,C)
        self.assertEqual(accept_delta(self.target,delta)['value'],'1/5')
        with self.assertRaises(ValueError):export_delta(self.source,'same-object','0'*64,next_head,C)

    def test_malformed_heads_and_oversized_frames_rejected(self):
        for bad in [{}, [], True, 'wrong']:
            p=copy.deepcopy(self.packet);p['base_head']=bad
            with self.assertRaises(ValueError):accept_delta(self.target,p)
        p=copy.deepcopy(self.packet);p['events']=p['events']*33
        with self.assertRaises(ValueError):accept_delta(self.target,p)
        self.assert_empty()

    def test_explicit_energy_handoff_keeps_object_identity(self):
        grid={**C,'origin':'fixture://grid','vector':'fixture://grid/1'}
        permissions=[(digest(C),digest(grid))]
        source=Continuation(Path(self.tmp.name)/'source-handoff.sqlite',[C,grid],permissions)
        target=Continuation(Path(self.tmp.name)/'target-handoff.sqlite',[C,grid],permissions)
        for r in [source,target]:r.create('same-object',C)
        first=source.advance('same-object',None,C,'+X',4)
        last=source.advance('same-object',first['head'],grid,'-Y',5)
        packet=export_delta(source,'same-object',None,last['head'],grid)
        receipt=accept_delta(target,packet)
        self.assertEqual(receipt['continuation'],'same-object')
        self.assertEqual(receipt['head'],last['head'])
        self.assertEqual(receipt['context'],grid)
        with self.assertRaises(ValueError):target.read('same-object',C)

    def test_source_derived_replay_cost_model(self):
        import context_continuation as module
        from unittest.mock import patch
        for batch in [1,4,16,64]:
            source=Continuation(Path(self.tmp.name)/f'model-source-{batch}.sqlite',[C])
            target=Continuation(Path(self.tmp.name)/f'model-target-{batch}.sqlite',[C])
            source.create('model');target.create('model');head=None;base=None;packets=[]
            operations=[('+X',4),('-Y',5),('+Y',5),('-X',4)]
            for i in range(64):
                axis,k=operations[i%4];head=source.advance('model',head,C,axis,k)['head']
                if (i+1)%batch==0:
                    packets.append(export_delta(source,'model',base,head,C));base=head
            original=module.operate;count=[0]
            def counted(*args):count[0]+=1;return original(*args)
            with patch.object(module,'operate',counted):
                for packet in packets:accept_delta(target,packet)
            self.assertEqual(count[0],(3*64*64//batch-64)//2)
            self.assertEqual(target.read('model',C)['head'],head)
