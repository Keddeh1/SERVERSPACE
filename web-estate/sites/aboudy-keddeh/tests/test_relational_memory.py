import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from relational_memory import RelationalMemory, location, coordinates


def fixture():
    columns = {f'fixture://{i}': {'column_index': i, 'column_axis_address': [1, i+1],
        'page_address': f'vfs://kex/relational-field/column/{i}',
        'cell_addresses': [location(s, i)['vfs_address'] for s in range(1, 65)]} for i in range(1, 65)}
    cells = [{**location(s,t), 'source_identity': f'fixture://{s}', 'target_identity': f'fixture://{t}',
        'relations': [], 'allocation_state': 'ALLOCATED_UNBOUND'} for s in range(1,65) for t in range(1,65)]
    return {'schema':'kex.memory-vfs.64x64.v1','singular_apex':[1,1],'first_payload_cell':[2,2],
        'payload_extent':[64,64],'address_capacity':4096,'allocated_address_count':4096,
        'relation_bound_count':0,'allocated_unbound_count':4096,'columns':columns,'cells':cells}


class RelationalMemoryTests(unittest.TestCase):
    def test_all_coordinates(self):
        m=RelationalMemory(fixture())
        for address in range(1,4097):
            s,t=coordinates(address)
            self.assertEqual(m.read(s,t)['linear_address'],address)
            self.assertEqual(m.read(s,t)['vfs_address'],f'vfs://kex/relational-field/column/{t}/cell/{s}')
        self.assertEqual(m.read(1,1)['matrix_address'],[2,2])
        self.assertEqual(m.read(64,64)['matrix_address'],[65,65])

    def test_invalid_ordinals(self):
        for bad in [0,-1,65,True,1.5,'1',None]:
            with self.assertRaises(ValueError): location(bad,1)
        for bad in [0,4097,False,1.5,'1']:
            with self.assertRaises(ValueError): coordinates(bad)

    def test_mutated_geometry_identity_state(self):
        for key,value in [('linear_address',2),('matrix_address',[1,1]),('source_identity','fixture://2'),
                          ('vfs_address','vfs://kex/relational-field/column/2/cell/1'),('allocation_state','ABSENT')]:
            d=fixture();d['cells'][0][key]=value
            with self.assertRaises(ValueError): RelationalMemory(d)

    def test_allocated_unbound_and_defensive_reads(self):
        d=fixture();m=RelationalMemory(d);c=m.read(1,2)
        self.assertEqual(c['allocation_state'],'ALLOCATED_UNBOUND')
        c['relations'].append('MUTATED');d['cells'][1]['relations'].append('MUTATED')
        self.assertEqual(m.read(1,2)['relations'],[])

    def test_bound_census(self):
        d=fixture();d['cells'][0]['relations']=['RELATED_TO'];d['cells'][0]['allocation_state']='ALLOCATED_RELATION_BOUND'
        d['relation_bound_count']=1;d['allocated_unbound_count']=4095
        self.assertEqual(RelationalMemory(d).read(1,1)['relations'],['RELATED_TO'])
        d['relation_bound_count']=2
        with self.assertRaises(ValueError): RelationalMemory(d)

    def test_primary_loss_and_corruption_fallback(self):
        for corrupt in (False, True):
            m=RelationalMemory(fixture())
            if corrupt: m.cells[2]['source_identity']='fixture://wrong'
            else: del m.cells[2]
            receipt=m.read_with_receipt(1,2)
            self.assertTrue(receipt['fallback_used'])
            self.assertEqual(receipt['resolution_path'],'coordinate')
            self.assertEqual(receipt['cell']['source_identity'],'fixture://1')
            self.assertEqual(receipt['failed_paths'],['linear'])

    def test_secondary_loss_primary_still_works(self):
        m=RelationalMemory(fixture());del m.coordinate_cells[(1,2)]
        self.assertFalse(m.read_with_receipt(1,2)['fallback_used'])

    def test_both_paths_failed_no_transposition(self):
        m=RelationalMemory(fixture());del m.cells[2]
        m.coordinate_cells[(1,2)]=m.read(2,1)
        with self.assertRaises(ValueError): m.read(1,2)

    def test_logical_frame_rejects_even_with_recomputed_digest(self):
        m=RelationalMemory(fixture())
        m.cells[2]['allocation_state']='ABSENT'
        m.digests[2]=m._digest(m.cells[2])
        m.coordinate_cells[(1,2)]=dict(m.cells[2])
        with self.assertRaises(ValueError): m.read(1,2)
