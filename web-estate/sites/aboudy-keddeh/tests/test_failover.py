import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from failover import plan_failover


class FailoverTests(unittest.TestCase):
    def candidates(self):
        return [dict(node=name, failure_domain=domain, source_sha256='a' * 64, generation=7,
                     observed_at=100, healthy=True, capacity_admitted=True)
                for name, domain in [('one', 'zone-a'), ('two', 'zone-b')]]

    def test_valid_plan_is_read_only(self):
        result = plan_failover('dns-authoritative', self.candidates(), 101, 7, True, 'a' * 64)
        self.assertTrue(result['proposal_supported']); self.assertFalse(result['acts_on_servers'])
        self.assertFalse(result['all_replica_memory_loss_recovery_verified'])

    def test_stale_generation_health_capacity_and_fencing(self):
        for changes in [{'generation': 6}, {'source_sha256': 'b' * 64}, {'observed_at': 50}, {'observed_at': 102},
                        {'healthy': False}, {'capacity_admitted': False}]:
            candidates = self.candidates(); candidates[0].update(changes)
            self.assertFalse(plan_failover('vfs', candidates, 101, 7, True, 'a' * 64)['proposal_supported'])
        self.assertFalse(plan_failover('website', self.candidates(), 101, 7, False, 'a' * 64)['proposal_supported'])

    def test_same_domain_and_duplicate_identity(self):
        candidates = self.candidates(); candidates[1]['failure_domain'] = 'zone-a'
        self.assertFalse(plan_failover('namespace', candidates, 101, 7, True, 'a' * 64)['proposal_supported'])
        candidates[1]['node'] = 'one'
        with self.assertRaises(ValueError): plan_failover('namespace', candidates, 101, 7, True, 'a' * 64)
