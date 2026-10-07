"""VFS allocation planning and backing admission; does not provision host resources."""
import os

REQUESTED_BYTES_PER_SERVER = 100_000_000_000_000  # 100 decimal TB, owner target
WINDOW_BYTES = 256 * 1024 * 1024


def integer(value, name):
    if type(value) is not int or not 0 <= value <= 2**53 - 1:
        raise ValueError(name + ' must be an exact nonnegative interoperable integer')
    return value


def allocation_plan(pool_bytes, services, backing_kind, observed_backing_bytes=None):
    integer(pool_bytes, 'pool_bytes')
    if pool_bytes == 0 or backing_kind not in {'address-space', 'persistent-storage', 'physical-ram'}:
        raise ValueError('positive pool and explicit backing kind required')
    if not isinstance(services, dict) or len(services) > 256:
        raise ValueError('service allocation map exceeds its contract')
    assigned = 0
    for name, size in services.items():
        if not isinstance(name, str) or not name or len(name) > 128 or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in name):
            raise ValueError('service identifiers must be canonical bounded labels')
        integer(size, 'service_bytes')
        if size == 0:
            raise ValueError('service allocations must be positive')
        assigned += size
    if assigned > pool_bytes:
        raise ValueError('service allocations exceed parent VFS pool')
    if observed_backing_bytes is not None:
        integer(observed_backing_bytes, 'observed_backing_bytes')
    physically_covered = observed_backing_bytes is not None and pool_bytes <= observed_backing_bytes
    return {'pool_bytes': pool_bytes, 'services': dict(sorted(services.items())),
            'assigned_bytes': assigned, 'unassigned_bytes': pool_bytes - assigned,
            'backing_kind': backing_kind, 'observed_backing_bytes': observed_backing_bytes,
            'backing_capacity_sufficient': physically_covered,
            'status': 'logical-plan' if backing_kind == 'address-space' else ('capacity-check-passed' if physically_covered else 'backing-required'),
            'provisioned': False, 'resident_memory_allocated': False,
            'runtime_quota_enforced': False, 'mesh_connectivity_verified': False}


def observe_storage(directory):
    volume = os.statvfs(directory)
    return {'available_bytes': volume.f_bavail * volume.f_frsize,
            'total_bytes': volume.f_blocks * volume.f_frsize,
            'kind': 'filesystem-observation', 'reservation': False}


def window_address(offset, extent_bytes, window_bytes=WINDOW_BYTES):
    integer(offset, 'offset'); integer(extent_bytes, 'extent_bytes'); integer(window_bytes, 'window_bytes')
    if not 1 <= window_bytes <= 2**31 - 1 or offset >= extent_bytes:
        raise ValueError('address outside admitted extent or invalid 32-bit window')
    return {'window_index': offset // window_bytes, 'window_offset': offset % window_bytes,
            'window_bytes': window_bytes,
            'bytes_remaining_in_window': min(window_bytes - offset % window_bytes, extent_bytes - offset)}
