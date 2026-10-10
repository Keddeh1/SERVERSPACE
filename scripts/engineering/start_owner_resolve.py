"""Restore pinned owner ServerSpace runtimes and connect their official RESOLVE SDK.

Only loopback service interfaces are started. Existing owners are retained;
uploaded instructions are not an executable deployment plan.
"""
import fcntl
import hashlib
import http.client
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time

PIN = '754b1de208dce49631023fd1725f3c0096bc6587'
STAGING = Path('/workspace/staging/resolve-owner-754b1de')
BASE = Path('applications/braink-ide-cli-ci')
VARIANT = BASE/'integrations/serverspace-runtime/variants/authenticated'
RUNTIME = Path('/workspace/braink-setup/families/SERVERSPACE/runtime')
SOFTWARE = RUNTIME/'software'/PIN
SUPERVISOR = Path('/workspace/staging/keddeh-09f4518/scripts/service-estate-supervisor.py')


def owners(command):
    result = []
    for file in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            observed = file.read_bytes().split(b'\0')[:-1]
            if observed == [part.encode() for part in command]: result.append(int(file.parent.name))
        except OSError: pass
    return result


def prepare():
    manifest = json.loads((STAGING/'source-manifest.json').read_text())
    if manifest['commit'] != PIN: raise ValueError('owner source revision differs')
    for row in manifest['files']:
        source = STAGING/'pinned'/row['path']
        if source.is_symlink() or hashlib.sha256(source.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('source custody differs: '+row['path'])
        path = Path(row['path'])
        if path.is_relative_to(VARIANT): target = SOFTWARE/path.relative_to(VARIANT)
        elif path.is_relative_to(BASE/'sectors/core/src/braink_node'):
            target = SOFTWARE/'dependencies/braink_node'/path.relative_to(BASE/'sectors/core/src/braink_node')
        else: continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.is_symlink() or target.read_bytes() != source.read_bytes():
                raise ValueError('installed pinned source differs; retained for review')
        else: shutil.copyfile(source, target)
    # The previously inspected owner supervisor is independently pinned.
    review = json.loads(Path('/workspace/keddeh-estate-inspection/docs/research-and-development/sectors/SECTOR_SYSTEMS_ARCHITECTURE/substrate-bootstrap/STAGING_REVIEW.json').read_text())
    if hashlib.sha256(SUPERVISOR.read_bytes()).hexdigest() != review['files']['scripts/service-estate-supervisor.py']:
        raise ValueError('supervisor source pin differs')
    bridge = Path(__file__).with_name('resolve_sdk_bridge.mjs')
    installed = Path('/workspace/.keddeh-environment/mcp-sdk/resolve-bridge.mjs')
    if installed.exists() and installed.read_bytes() != bridge.read_bytes():
        raise ValueError('existing SDK bridge differs; preserve for review')
    if not installed.exists(): shutil.copyfile(bridge,installed)
    sdk_source = Path(__file__).with_name('owner_resolve_estate_sdk.mjs')
    sdk_server = installed.with_name('server.mjs')
    baseline_sha = '95126c4613e6062e74069eb36b52afac9921f9bfdd2516458ded5e178fb33cb2'
    if sdk_server.read_bytes() != sdk_source.read_bytes():
        if hashlib.sha256(sdk_server.read_bytes()).hexdigest() != baseline_sha:
            raise ValueError('existing SDK entry differs from reviewed baseline; preserve for review')
        backup = installed.with_name('server.before-resolve.mjs')
        if backup.exists() and hashlib.sha256(backup.read_bytes()).hexdigest() != baseline_sha:
            raise ValueError('SDK rollback source differs')
        if not backup.exists(): shutil.copyfile(sdk_server,backup)
        temporary = sdk_server.with_suffix('.pending')
        temporary.write_bytes(sdk_source.read_bytes());temporary.chmod(0o600)
        temporary.replace(sdk_server)
    return manifest


def health(port, identity):
    connection = http.client.HTTPConnection('127.0.0.1', port, timeout=2)
    try:
        connection.request('GET', '/health')
        response = connection.getresponse(); value = json.loads(response.read())
        if response.status != 200 or value['identity'] != identity or value['readiness_mask'] != 7 or value['mutual_authentication'] is not True or not value['receipt_chain']['verified']:
            raise ValueError('RESOLVE readiness or receipt chain differs')
        return value
    finally: connection.close()


def start_supervisor(config, name, environment):
    command = [sys.executable, str(SUPERVISOR), '--config', str(config), '--service', name]
    found = owners(command)
    if len(found) > 1: raise RuntimeError('multiple supervisor owners; preserve for review')
    if found: return found[0]
    log = config.parent/(name+'.log')
    with log.open('ab') as output:
        log.chmod(0o600)
        child = subprocess.Popen(command, cwd=SOFTWARE, env=dict(os.environ, **environment),
                                 stdin=subprocess.DEVNULL, stdout=output, stderr=output, start_new_session=True)
    return child.pid


def main():
    RUNTIME.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (RUNTIME/'resolve-setup.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest = prepare()
        sys.path.insert(0, str(SOFTWARE))
        from hci import RuntimePanel
        instances = []
        for name, port in [('auth-canary',19091),('replica',19092),('primary',19093)]:
            root = RUNTIME/('substrate-'+name)
            identity = 'serverspace/substrate-'+name
            resolve_root = RUNTIME/('resolve-'+name)
            resolve_identity = 'serverspace/resolve-'+name
            estate = RUNTIME/('resolve-supervision-'+name)
            estate.mkdir(mode=0o700, exist_ok=True)
            config = estate/'services.json'
            services = {
                'substrate': {'command':[sys.executable, str(SOFTWARE/'substrate.py'), '--root',str(root),'--identity',identity,'daemon'], 'cwd':str(SOFTWARE)},
                'resolve': {'command':[sys.executable,str(SOFTWARE/'resolve_mcp.py'),'--root',str(resolve_root),'--substrate-root',str(root),'--identity',resolve_identity,'--port',str(port)],'cwd':str(SOFTWARE)}
            }
            if config.exists() and json.loads(config.read_text()) != services:
                raise ValueError('existing service configuration differs; preserve owners')
            config.write_text(json.dumps(services,indent=2)+'\n'); config.chmod(0o600)
            environment = {'PYTHONPATH':str(SOFTWARE/'dependencies'), 'PYTHONDONTWRITEBYTECODE':'1'}
            substrate_supervisor = start_supervisor(config,'substrate',environment)
            deadline = time.monotonic()+15
            while True:
                try:
                    frame = RuntimePanel(root, identity).read()
                    if frame['readiness_mask'] != 7 or not frame['authentication']['mutual']:
                        raise ValueError('substrate handshake incomplete')
                    break
                except (OSError, ValueError, KeyError):
                    if time.monotonic() >= deadline: raise RuntimeError('substrate did not authenticate; RESOLVE listener withheld')
                    time.sleep(.1)
            if not owners(services['resolve']['command']):
                with socket.socket() as check: check.bind(('127.0.0.1',port))
            resolve_supervisor = start_supervisor(config,'resolve',environment)
            deadline = time.monotonic()+15
            while True:
                try: observed = health(port, resolve_identity); break
                except (OSError, ValueError, KeyError):
                    if time.monotonic() >= deadline: raise RuntimeError('RESOLVE failed qualification; stop before next rollout node')
                    time.sleep(.1)
            # Canary qualification gates each subsequent instance.
            import asyncio
            from qualify_resolve_mcp import qualify
            qualified = asyncio.run(qualify('http://127.0.0.1:'+str(port)+'/mcp',resolve_identity))
            instances.append({'identity':resolve_identity,'url':'http://127.0.0.1:'+str(port)+'/mcp',
                              'root':str(resolve_root),'substrate_root':str(root),
                              'substrate_supervisor':substrate_supervisor,'resolve_supervisor':resolve_supervisor,
                              'health':observed,'qualification':qualified})
        receipt = {'source_repository':'Keddeh1/BRAINK-BETA-TEST','source_commit':PIN,
                   'scope':'restored owner software on current managed node; loopback only, no external host claim',
                   'instances':instances,'independent_contexts_retained':len({x['qualification']['artifact_digest'] for x in instances})==3}
        if not receipt['independent_contexts_retained']: raise RuntimeError('instance collapse detected')
        temporary = RUNTIME/'resolve-deployment.pending'
        temporary.write_text(json.dumps(receipt,indent=2)+'\n'); temporary.chmod(0o600)
        temporary.replace(RUNTIME/'resolve-deployment.json')
        print(json.dumps(receipt,indent=2))


if __name__ == '__main__': main()
