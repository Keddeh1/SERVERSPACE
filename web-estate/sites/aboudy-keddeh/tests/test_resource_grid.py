from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from resource_grid import allocation_plan, window_address, REQUESTED_BYTES_PER_SERVER, WINDOW_BYTES


class ResourceGridTests(unittest.TestCase):
    def test_parent_and_service_budgets(self):
        result = allocation_plan(1000, {'website': 400, 'cache': 200}, 'address-space')
        self.assertEqual(result['unassigned_bytes'], 400)
        self.assertFalse(result['provisioned']); self.assertFalse(result['runtime_quota_enforced'])
        with self.assertRaises(ValueError):
            allocation_plan(1000, {'website': 900, 'cache': 200}, 'address-space')

    def test_requested_100tb_does_not_fabricate_backing(self):
        result = allocation_plan(REQUESTED_BYTES_PER_SERVER, {'website': 1024}, 'persistent-storage', 4096)
        self.assertEqual(result['status'], 'backing-required')
        self.assertFalse(result['resident_memory_allocated'])
        self.assertFalse(result['mesh_connectivity_verified'])

    def test_invalid_types_labels_and_windows(self):
        for pool in [True, 1.5, -1, 2**53]:
            with self.assertRaises(ValueError): allocation_plan(pool, {}, 'address-space')
        with self.assertRaises(ValueError): allocation_plan(1024, {'../foreign': 1}, 'address-space')
        with self.assertRaises(ValueError): window_address(100, 100)
        with self.assertRaises(ValueError): window_address(0, 100, 2**32)

    def test_large_extent_maps_to_small_windows(self):
        offset = REQUESTED_BYTES_PER_SERVER - 1
        result = window_address(offset, REQUESTED_BYTES_PER_SERVER)
        self.assertEqual(result['window_index'] * WINDOW_BYTES + result['window_offset'], offset)
        self.assertLess(result['window_offset'], 2**31)
        self.assertEqual(result['bytes_remaining_in_window'], 1)
