"""Fault qualification of the isolated bootstrap adapter, never active nodes."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import time
import unittest
from substrate_canary import Store, handshake, receive, send, digest

ENGINE = Path(__file__).with_name('substrate_canary.py')
GOVERNED = {'origin':'1','ordinance':'canary','municipality':'test','region':'AU',
            'vector':'+X','frame':'qualification','unit':'1','revision':'1'}


class Qualification(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kex-canary-')
        self.root = Path(self.temp.name)
        self.store = Store(self.root)
        self.original = self.store.write(GOVERNED, {'counter': 1})
        self.children = []

    def tearDown(self):
        for child in reversed(self.children):
            if child.poll() is None:
                child.terminate()
                try: child.wait(timeout=3)
                except subprocess.TimeoutExpired: child.kill(); child.wait()
        self.temp.cleanup()

    def start(self, action='serve'):
        child = subprocess.Popen([sys.executable, '-B', str(ENGINE), action, str(self.root)],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.children.append(child)
        deadline = time.monotonic()+5
        while time.monotonic() < deadline:
            if child.poll() is not None: self.fail('canary exited before readiness')
            try: return child, handshake(self.root)
            except (OSError, ValueError): time.sleep(.05)
        self.fail('readiness timeout')

    def test_bidirectional_readiness_and_checksums(self):
        child, ready = self.start()
        self.assertEqual(ready['ready_mask'], 7)
        self.assertEqual(ready['state_digest'], self.original['sha256'])
        self.assertEqual(ready['crc32'], self.original['crc32'])
        self.assertEqual(ready['peer_pid'], child.pid)
        self.assertTrue(ready['authenticated'])

    def test_foreign_secret_cannot_complete(self):
        self.start()
        with self.assertRaises(ValueError): handshake(self.root, key=b'x'*32)
        self.assertTrue(handshake(self.root)['authenticated'])

    def test_corrupted_state_blocks_handshake(self):
        self.start()
        value = self.store.read(); value['body']['sequence'] = 300
        (self.root/'canonical.state').write_text(json.dumps(value))
        with self.assertRaises((OSError, ValueError)): handshake(self.root)

    def test_equal_local_unity_keeps_contexts_distinct(self):
        other = dict(GOVERNED, municipality='another-parent')
        self.store.write(other, {'counter': 99})
        record = self.store.read()['body']['contexts']
        self.assertEqual(len(record), 2)
        self.assertEqual(record[digest(GOVERNED)]['payload']['counter'], 1)
        self.assertEqual(record[digest(other)]['payload']['counter'], 99)

    def test_concurrent_canonical_writers(self):
        def write(index):
            Store(self.root).write(dict(GOVERNED, origin=str(index+1)), {'writer':index})
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(write, range(24)))
        record = self.store.read()
        self.assertEqual(record['body']['sequence'], 25)
        self.assertEqual(len(record['body']['contexts']), 24)

    def test_socket_and_state_stay_private(self):
        self.start()
        for name in ['readiness.sock','canonical.state','peer.key']:
            path = self.root/name
            self.assertEqual(path.parent, self.root)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_unsafe_directory_and_symlink_rejected(self):
        os.chmod(self.root, 0o755)
        with self.assertRaises(ValueError): Store(self.root)
        os.chmod(self.root, 0o700)
        link = self.root/'alias'; link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError): Store(link)
        (self.root/'canonical.state').unlink()
        (self.root/'canonical.state').symlink_to(self.root/'peer.key')
        with self.assertRaises(OSError): self.store.read()

    def test_truncation_and_oversize_rejected(self):
        for frame in [struct.pack('!I', 3)+b'{', struct.pack('!I', 65537)]:
            first, second = socket.socketpair()
            with first, second:
                first.sendall(frame); first.shutdown(socket.SHUT_WR)
                with self.assertRaises(ValueError): receive(second)

    def test_fragmented_frames_are_reassembled(self):
        first, second = socket.socketpair()
        with first, second:
            raw = b'{"seed":1}'
            framed = struct.pack('!I', len(raw))+raw
            for byte in framed: first.sendall(bytes([byte]))
            self.assertEqual(receive(second), {'seed':1})

    def test_watchdog_recovers_killed_and_hung_worker_with_identical_state(self):
        watcher, ready = self.start('watchdog')
        for injected_signal in [signal.SIGKILL, signal.SIGSTOP]:
            # Only the fresh authenticated worker belonging to our watchdog.
            previous = ready['peer_pid']
            os.kill(previous, injected_signal)
            deadline = time.monotonic()+8
            while time.monotonic() < deadline:
                try:
                    ready = handshake(self.root)
                    if ready['peer_pid'] != previous: break
                except (OSError, ValueError): pass
                time.sleep(.1)
            else: self.fail('watchdog recovery failed')
            self.assertEqual(ready['state_digest'], self.original['sha256'])
            self.assertEqual(self.store.read(), self.original)

    def test_api_command_withheld_until_handshake(self):
        marker = self.root/'api.started'
        command = [sys.executable,'-B',str(ENGINE),'--timeout','5','gate',str(self.root),'--',
                   sys.executable,'-c','from pathlib import Path; import sys; Path(sys.argv[1]).write_text("started")',str(marker)]
        api = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.children.append(api)
        time.sleep(.3); self.assertFalse(marker.exists()); self.assertIsNone(api.poll())
        self.start()
        self.assertEqual(api.wait(timeout=4), 0); self.assertTrue(marker.exists())

    def test_exclusive_substrate_owner(self):
        first, _ = self.start()
        second = subprocess.run([sys.executable,'-B',str(ENGINE),'serve',str(self.root)],
                                capture_output=True, timeout=3)
        self.assertNotEqual(second.returncode, 0)
        self.assertEqual(handshake(self.root)['peer_pid'], first.pid)

    def test_worker_resource_limits_and_repeated_acknowledgements(self):
        watcher, ready = self.start('watchdog')
        limits = Path('/proc',str(ready['peer_pid']),'limits').read_text()
        self.assertRegex(limits, r'Max address space\s+268435456\s+268435456')
        self.assertRegex(limits, r'Max open files\s+64\s+64')
        for _ in range(100):
            receipt = handshake(self.root)
            self.assertEqual(receipt['state_digest'], self.original['sha256'])
            self.assertEqual(receipt['ready_mask'], 7)


if __name__ == '__main__': unittest.main(verbosity=2)
