"""Start/reconcile the private qualification canary without changing live nodes."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from substrate_canary import Store, handshake

ROOT = Path('/workspace/.keddeh-environment/substrate-canary')


def main():
    store = Store(ROOT)
    with store.lock('launcher.lock', nonblocking=True):
        try:
            ready = handshake(ROOT)
        except (OSError, ValueError):
            # A live watchdog owns its lock even if unhealthy. Never replace it.
            with store.lock('watchdog.lock', nonblocking=True):
                pass
            try: store.read()
            except FileNotFoundError:
                store.write({'origin':'1','ordinance':'qualification-only',
                    'municipality':'isolated-canary','region':'local-test',
                    'vector':'+X','frame':'bootstrap-canary','unit':'1','revision':'1'},
                    {'classification':'fixture; not ServerSpace production state'})
            fd = store.open('watchdog.log', os.O_WRONLY | os.O_CREAT | os.O_APPEND)
            with os.fdopen(fd, 'ab') as output:
                child = subprocess.Popen([sys.executable, '-B', str(Path(__file__).with_name('substrate_canary.py')),
                                          'watchdog', str(ROOT)], stdout=output, stderr=output,
                                          stdin=subprocess.DEVNULL, start_new_session=True)
            for _ in range(60):
                if child.poll() is not None: raise RuntimeError('canary watchdog failed; inspect private log')
                try: ready = handshake(ROOT); break
                except (OSError, ValueError): time.sleep(.1)
            else:
                child.terminate(); child.wait(timeout=3)
                raise RuntimeError('canary readiness timed out')
    print(json.dumps({'scope':'isolated local qualification canary', 'runtime':str(ROOT), **ready}, indent=2))


if __name__ == '__main__': main()
