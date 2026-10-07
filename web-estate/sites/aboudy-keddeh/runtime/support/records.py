"""Governed primitives: bounded immutable reads, confined paths, strict JSON.

Attribution: CPython 3.12 os/json APIs; see research/source-index.json.
Contract: regular files only; no symbolic links; no duplicate or nonfinite JSON.
"""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat

MAX_RECORD_BYTES = 1024 * 1024
MAX_EVIDENCE_BYTES = 64 * 1024 * 1024


@contextmanager
def regular_file(path, root=None, limit=MAX_RECORD_BYTES):
    path = Path(path)
    if root is None:
        root = path.absolute().parent
        path = Path(path.name)
    root = Path(root).resolve()
    if path.is_absolute() or not path.parts or any(p in ('.', '..') for p in path.parts):
        raise ValueError('path is outside repository or contains traversal')
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open(root, directory_flags)
    file_fd = None
    try:
        for part in path.parts[:-1]:
            child = os.open(part, directory_flags, dir_fd=fd)
            os.close(fd)
            fd = child
        file_fd = os.open(path.parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        before = os.fstat(file_fd)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError('input must be a regular file')
        if before.st_size > limit:
            raise ValueError(f'input exceeds {limit}-byte limit')
        with os.fdopen(file_fd, 'rb') as stream:
            file_fd = None
            yield stream
            after = os.fstat(stream.fileno())
            if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise ValueError('input changed while being read')
    finally:
        os.close(fd)
        if file_fd is not None:
            os.close(file_fd)


def read_bytes(path, limit=MAX_RECORD_BYTES, root=None):
    with regular_file(path, root, limit) as stream:
        data = stream.read(limit + 1)
        if len(data) > limit:
            raise ValueError(f'input exceeds {limit}-byte limit')
    return data


def digest_file(path, root=None, limit=MAX_EVIDENCE_BYTES):
    digest, size = hashlib.sha256(), 0
    with regular_file(path, root, limit) as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            size += len(block)
            if size > limit:
                raise ValueError(f'input exceeds {limit}-byte limit')
            digest.update(block)
    return digest.hexdigest(), size


def decode_json(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'duplicate JSON key: {key}')
            result[key] = value
        return result
    def finite(value):
        raise ValueError(f'nonfinite JSON number: {value}')
    try:
        return json.loads(data, object_pairs_hook=unique, parse_constant=finite)
    except (RecursionError, UnicodeError) as error:
        raise ValueError('invalid JSON encoding or nesting') from error


def read_json(path, root=None):
    return decode_json(read_bytes(path, root=root))


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()
