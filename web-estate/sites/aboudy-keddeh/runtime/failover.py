"""Failover planning from supplied observations; performs no promotion or actuation."""
import re
import math


def plan_failover(service, candidates, now, committed_generation, fencing_verified, committed_source_sha256):
    if service not in {'dns-authoritative', 'namespace', 'vfs', 'website', 'cache'}:
        raise ValueError('service must have a governed template')
    if type(now) not in {int, float} or type(committed_generation) is not int or committed_generation < 0:
        raise ValueError('invalid observation time or generation')
    if not isinstance(candidates, list) or len(candidates) > 256:
        raise ValueError('candidate list exceeds contract')
    if not isinstance(committed_source_sha256, str) or not re.fullmatch('[0-9a-f]{64}', committed_source_sha256) or not math.isfinite(now):
        raise ValueError('exact committed source and finite observation time required')
    admitted, rejected, identities = [], [], set()
    for candidate in candidates:
        required = {'node', 'failure_domain', 'source_sha256', 'generation', 'observed_at', 'healthy', 'capacity_admitted'}
        if not isinstance(candidate, dict) or set(candidate) != required:
            raise ValueError('failover observation shape mismatch')
        node, domain = candidate['node'], candidate['failure_domain']
        if not isinstance(node, str) or not node or node in identities or not isinstance(domain, str) or not domain:
            raise ValueError('unique node and explicit failure domain required')
        identities.add(node)
        if (not isinstance(candidate['source_sha256'], str) or not re.fullmatch('[0-9a-f]{64}', candidate['source_sha256'])
            or type(candidate['generation']) is not int or type(candidate['observed_at']) not in {int, float}
            or type(candidate['healthy']) is not bool or type(candidate['capacity_admitted']) is not bool):
            raise ValueError('malformed failover observation')
        reasons = []
        if not 0 <= now - candidate['observed_at'] <= 30: reasons.append('observation stale or future')
        if not candidate['healthy']: reasons.append('health failed')
        if not candidate['capacity_admitted']: reasons.append('capacity not admitted')
        if candidate['generation'] != committed_generation: reasons.append('generation mismatch')
        if candidate['source_sha256'] != committed_source_sha256: reasons.append('source digest mismatch')
        if reasons: rejected.append({'node': node, 'reasons': reasons})
        else: admitted.append(candidate)
    domains = {candidate['failure_domain'] for candidate in admitted}
    blockers = []
    if len(domains) < 2: blockers.append('two admitted failure domains required')
    if fencing_verified is not True: blockers.append('previous writer fencing must be independently verified')
    return {'service': service, 'eligible_nodes': sorted(candidate['node'] for candidate in admitted),
            'rejected': rejected, 'blockers': blockers, 'proposal_supported': not blockers,
            'acts_on_servers': False, 'all_replica_memory_loss_recovery_verified': False,
            'tot_protocol_verified': False, 'resonance_0297_verified': False}
