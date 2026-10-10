"""Isolated Linux substrate qualification adapter; not a ServerSpace baseline clone.

Reuses the existing complete-context identity contract. No embedded source commands
are executed. API wrappers launch only after a fresh authenticated UDS exchange.
"""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import hmac
import json
import mmap
import os
from pathlib import Path
import secrets
import resource
import signal
import socket
import stat
import struct
import subprocess
import sys
import tempfile
import time
import zlib

SITE = Path(__file__).resolve().parents[2] / 'web-estate/sites/aboudy-keddeh/runtime'
sys.path.insert(0, str(SITE))
from context_continuation import canonical, context, digest

LIMIT = 65536


class Store:
    def __init__(self, root):
        requested = Path(root).absolute()
        if any(p.is_symlink() for p in [requested, *requested.parents]):
            raise ValueError('runtime directory cannot traverse symlinks')
        requested.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = requested.stat()
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
            raise ValueError('runtime directory must be owner-only 0700')
        self.root = requested

    def open(self, name, flags):
        if '/' in name or name in {'.', '..'}:
            raise ValueError('runtime-relative leaf required')
        fd = os.open(self.root/name, flags | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1:
            os.close(fd)
            raise ValueError('unsafe runtime file')
        return fd

    @contextmanager
    def lock(self, name='writer.lock', nonblocking=False):
        fd = self.open(name, os.O_RDWR | os.O_CREAT)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | (fcntl.LOCK_NB if nonblocking else 0))
            yield
        finally:
            os.close(fd)

    def key(self):
        with self.lock('key.lock'):
            try:
                fd = self.open('peer.key', os.O_RDONLY)
            except FileNotFoundError:
                fd = self.open('peer.key', os.O_WRONLY | os.O_CREAT | os.O_EXCL)
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(secrets.token_bytes(32)); stream.flush(); os.fsync(stream.fileno())
                fd = self.open('peer.key', os.O_RDONLY)
            with os.fdopen(fd, 'rb') as stream:
                value = stream.read()
            if len(value) != 32:
                raise ValueError('invalid peer key')
            return value

    def read(self):
        fd = self.open('canonical.state', os.O_RDONLY)
        with os.fdopen(fd, 'rb') as stream:
            size = os.fstat(stream.fileno()).st_size
            if not 0 < size <= LIMIT:
                raise ValueError('state size out of bounds')
            with mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as view:
                record = json.loads(view[:])
        body = record['body']
        raw = canonical(body).encode()
        if record['sha256'] != hashlib.sha256(raw).hexdigest() or record['crc32'] != zlib.crc32(raw):
            raise ValueError('state integrity failure')
        for identity, item in body['contexts'].items():
            if identity != digest(context(item['context'])):
                raise ValueError('context identity mismatch')
        return record

    def write(self, governed, payload):
        governed = context(governed)
        with self.lock():
            try:
                body = self.read()['body']
            except FileNotFoundError:
                body = {'sequence': 0, 'contexts': {}}
            body['sequence'] += 1
            body['contexts'][digest(governed)] = {'context': governed, 'payload': payload}
            raw = canonical(body).encode()
            record = {'body': body, 'sha256': hashlib.sha256(raw).hexdigest(), 'crc32': zlib.crc32(raw)}
            encoded = canonical(record).encode()
            if len(encoded) > LIMIT:
                raise ValueError('state exceeds bounded canary capacity')
            fd, filename = tempfile.mkstemp(prefix='.state-', dir=self.root)
            try:
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(encoded); stream.flush(); os.fsync(stream.fileno())
                # Existing links are rejected even though rename would replace them.
                if (self.root/'canonical.state').exists() or (self.root/'canonical.state').is_symlink():
                    check = self.open('canonical.state', os.O_RDONLY); os.close(check)
                os.replace(filename, self.root/'canonical.state')
                directory = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
                try: os.fsync(directory)
                finally: os.close(directory)
            finally:
                Path(filename).unlink(missing_ok=True)
            return record


def mac(key, value):
    return hmac.new(key, canonical(value).encode(), hashlib.sha256).hexdigest()


def exact(sock, count):
    data = bytearray()
    while len(data) < count:
        chunk = sock.recv(count-len(data))
        if not chunk:
            raise ValueError('truncated frame')
        data.extend(chunk)
    return bytes(data)


def receive(sock):
    length = struct.unpack('!I', exact(sock, 4))[0]
    if not 0 < length <= LIMIT:
        raise ValueError('frame exceeds bound')
    return json.loads(exact(sock, length))


def send(sock, value):
    data = canonical(value).encode()
    if len(data) > LIMIT:
        raise ValueError('frame exceeds bound')
    sock.sendall(struct.pack('!I', len(data))+data)


def same_uid(sock):
    pid, uid, gid = struct.unpack('3i', sock.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
    if uid != os.getuid():
        raise ValueError('foreign OS peer')
    return pid


def handshake(root, key=None):
    store = Store(root); key = store.key() if key is None else key
    with socket.socket(socket.AF_UNIX) as sock:
        sock.settimeout(1)
        sock.connect(str(store.root/'readiness.sock')); pid = same_uid(sock)
        nonce = secrets.token_hex(32)
        send(sock, {'nonce': nonce})
        reply = receive(sock); proof = reply.pop('proof')
        if reply['nonce'] != nonce or not hmac.compare_digest(proof, mac(key, reply)):
            raise ValueError('substrate proof rejected')
        send(sock, {'proof': mac(key, {'nonce': nonce, 'server_nonce': reply['server_nonce'], 'ack': True})})
        ack = receive(sock); proof = ack.pop('proof')
        if ack.get('nonce') != nonce or ack.get('server_nonce') != reply['server_nonce'] or not hmac.compare_digest(proof, mac(key, ack)) or ack.get('ready_mask') != 7:
            raise ValueError('bidirectional readiness rejected')
        record = store.read()
        if record['sha256'] != reply['state_digest'] or record['crc32'] != reply['crc32']:
            raise ValueError('state changed during handshake; retry')
        return {**reply, 'ready_mask': ack['ready_mask'], 'peer_pid': pid, 'authenticated': True}


def serve(root):
    store = Store(root); key = store.key()
    with store.lock('substrate.lock', nonblocking=True):
        path = store.root/'readiness.sock'
        if path.exists() or path.is_symlink():
            info = path.lstat()
            if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid():
                raise ValueError('unsafe socket path')
            path.unlink()  # Exclusive substrate ownership established above.
        with socket.socket(socket.AF_UNIX) as server:
            server.bind(str(path)); os.chmod(path, 0o600); server.listen(8); server.settimeout(.2)
            while True:
                try: sock, _ = server.accept()
                except socket.timeout: continue
                with sock:
                    sock.settimeout(1)
                    try:
                        same_uid(sock)
                        request = receive(sock)
                        if set(request) != {'nonce'} or not isinstance(request['nonce'], str) or len(request['nonce']) != 64:
                            raise ValueError('invalid challenge')
                        record = store.read()
                        reply = {'nonce': request['nonce'], 'server_nonce': secrets.token_hex(32),
                                 'state_digest': record['sha256'], 'crc32': record['crc32']}
                        send(sock, {**reply, 'proof': mac(key, reply)})
                        ack = receive(sock)
                        expected = {'nonce': reply['nonce'], 'server_nonce': reply['server_nonce'], 'ack': True}
                        if set(ack) != {'proof'} or not hmac.compare_digest(ack['proof'], mac(key, expected)):
                            raise ValueError('client proof rejected')
                        # Bits: 1 verified state, 2 OS/secret authenticated peer,
                        # 4 completed two-way challenge. No unconditional mask.
                        complete = {'nonce': reply['nonce'], 'server_nonce': reply['server_nonce'], 'ready_mask': 1 | 2 | 4}
                        send(sock, {**complete, 'proof': mac(key, complete)})
                    except (OSError, ValueError, KeyError, TypeError):
                        continue


def watchdog(root):
    store = Store(root)
    with store.lock('watchdog.lock', nonblocking=True):
        child = None
        def stop(signum, frame):
            raise KeyboardInterrupt
        signal.signal(signal.SIGTERM, stop)
        try:
            failures = 0
            while True:
                if child is None or child.poll() is not None:
                    child = subprocess.Popen([sys.executable, '-B', __file__, 'serve', str(root)],
                                             preexec_fn=worker_limits)
                    failures = 0
                time.sleep(.3)
                try: handshake(root); failures = 0
                except (OSError, ValueError, KeyError): failures += 1
                if failures >= 5:
                    child.terminate()
                    try: child.wait(timeout=2)
                    except subprocess.TimeoutExpired: child.kill(); child.wait()
        finally:
            if child is not None and child.poll() is None:
                child.terminate()
                try: child.wait(timeout=2)
                except subprocess.TimeoutExpired: child.kill(); child.wait()


def worker_limits():
    """Qualification worker limits, not owner production RAM allocations."""
    resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024, 256*1024*1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['serve', 'watchdog', 'check', 'gate'])
    parser.add_argument('runtime', type=Path)
    parser.add_argument('--timeout', type=float, default=10)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.action == 'serve': serve(args.runtime)
    elif args.action == 'watchdog': watchdog(args.runtime)
    elif args.action == 'check': print(json.dumps(handshake(args.runtime)))
    else:
        deadline = time.monotonic()+args.timeout
        while True:
            try: handshake(args.runtime); break
            except (OSError, ValueError, KeyError):
                if time.monotonic() >= deadline: raise RuntimeError('API start withheld: substrate unavailable')
                time.sleep(.1)
        command = args.command[1:] if args.command[:1] == ['--'] else args.command
        if not command: raise ValueError('explicit reviewed API command required')
        os.execvp(command[0], command)


if __name__ == '__main__': main()
