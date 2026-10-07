"""Owner 64x64 one-origin relational memory/VFS coordinate adapter.

Derived from KEDDEH_64x64_MEMORY_VFS.json; originals stay in private custody.
"""
import copy
import hashlib
import json


def ordinal(value, limit=64):
    if type(value) is not int or not 1 <= value <= limit:
        raise ValueError('one-origin ordinal outside its exact integer extent')
    return value


def location(source, target):
    source, target = ordinal(source), ordinal(target)
    return {'linear_address': (source - 1) * 64 + target,
            'matrix_address': [source + 1, target + 1],
            'source_index': source, 'target_index': target,
            'vfs_address': f'vfs://kex/relational-field/column/{target}/cell/{source}'}


def coordinates(address):
    address = ordinal(address, 4096)
    return ((address - 1) // 64 + 1, (address - 1) % 64 + 1)


class RelationalMemory:
    """Validate then resolve allocated owner cells without conflating unbound/absent."""
    def __init__(self, document):
        self.document = copy.deepcopy(document)
        d = self.document
        expected = {'schema': 'kex.memory-vfs.64x64.v1', 'singular_apex': [1, 1],
                    'first_payload_cell': [2, 2], 'payload_extent': [64, 64],
                    'address_capacity': 4096, 'allocated_address_count': 4096}
        if any(d.get(key) != value for key, value in expected.items()):
            raise ValueError('owner field geometry mismatch')
        cells, columns = d.get('cells'), d.get('columns')
        if not isinstance(cells, list) or len(cells) != 4096 or not isinstance(columns, dict) or len(columns) != 64:
            raise ValueError('incomplete allocated field')
        identities = {}
        for identity, column in columns.items():
            index = ordinal(column['column_index'])
            if index in identities or column['column_axis_address'] != [1, index + 1] or column['page_address'] != f'vfs://kex/relational-field/column/{index}':
                raise ValueError('column identity or axis mismatch')
            if column['cell_addresses'] != [location(source, index)['vfs_address'] for source in range(1, 65)]:
                raise ValueError('column cell orientation mismatch')
            identities[index] = identity
        self.identities = dict(identities)
        self.cells = {}
        bound = 0
        for cell in cells:
            loc = location(cell['source_index'], cell['target_index'])
            if any(cell.get(key) != value for key, value in loc.items()) or loc['linear_address'] in self.cells:
                raise ValueError('cell coordinate alias or mismatch')
            if cell['source_identity'] != identities[loc['source_index']] or cell['target_identity'] != identities[loc['target_index']]:
                raise ValueError('cell identity mismatch')
            relations = cell.get('relations')
            if not isinstance(relations, list) or any(not isinstance(x, str) or not x for x in relations):
                raise ValueError('invalid relations')
            state = 'ALLOCATED_RELATION_BOUND' if relations else 'ALLOCATED_UNBOUND'
            if cell.get('allocation_state') != state:
                raise ValueError('allocation state mismatch')
            bound += bool(relations)
            self.cells[loc['linear_address']] = cell
        if d.get('relation_bound_count') != bound or d.get('allocated_unbound_count') != 4096 - bound:
            raise ValueError('allocation census mismatch')

        self.coordinate_cells = {(cell['source_index'], cell['target_index']): copy.deepcopy(cell) for cell in self.cells.values()}
        self.digests = {address: self._digest(cell) for address, cell in self.cells.items()}

    @staticmethod
    def _digest(cell):
        return hashlib.sha256(json.dumps(cell, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

    def read_with_receipt(self, source, target):
        loc = location(source, target)
        address = loc['linear_address']
        failures = []
        for path in ('linear', 'coordinate'):
            try:
                cell = self.cells[address] if path == 'linear' else self.coordinate_cells[(source, target)]
                if not isinstance(cell, dict) or any(cell.get(key) != value for key, value in loc.items()):
                    raise ValueError('candidate logical coordinate frame mismatch')
                if cell.get('source_identity') != self.identities[source] or cell.get('target_identity') != self.identities[target]:
                    raise ValueError('candidate logical identity frame mismatch')
                relations = cell.get('relations')
                if not isinstance(relations, list) or any(not isinstance(x, str) or not x for x in relations):
                    raise ValueError('candidate relation frame mismatch')
                expected_state = 'ALLOCATED_RELATION_BOUND' if relations else 'ALLOCATED_UNBOUND'
                if cell.get('allocation_state') != expected_state:
                    raise ValueError('candidate allocation frame mismatch')
                if self._digest(cell) != self.digests[address]:
                    raise ValueError('cell integrity mismatch')
                return {'cell': copy.deepcopy(cell), 'resolution_path': path,
                        'fallback_used': bool(failures), 'failed_paths': failures,
                        'digest': self.digests[address]}
            except (KeyError, ValueError, TypeError, OverflowError):
                failures.append(path)
        raise ValueError('both relational resolution paths failed integrity/readback')

    def read(self, source, target):
        return self.read_with_receipt(source, target)['cell']
