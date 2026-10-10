"""Live SDK failure/recovery checks restricted to the newly restored owner estate."""
import asyncio
import http.client
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from start_owner_resolve import RUNTIME, SOFTWARE, owners, health


def unpack(result):
    if result.isError: raise AssertionError('SDK tool returned an error')
    return json.loads(result.content[0].text)


async def read_receipt(url, artifact):
    async with streamable_http_client(url) as (reader, writer, _):
        async with ClientSession(reader, writer) as client:
            await client.initialize()
            return unpack(await client.call_tool('read_resolve_receipt', {'artifact_digest':artifact}))


async def offline_commit_test(row, config):
    command = config['substrate']['command']
    found = owners(command)
    if len(found) != 1: raise RuntimeError('substrate owner not uniquely identified')
    pid = found[0]
    artifact = row['qualification']['artifact_digest']
    previous = await read_receipt(row['url'], artifact)
    os.kill(pid, signal.SIGSTOP)
    try:
        async with streamable_http_client(row['url']) as (reader, writer, _):
            async with ClientSession(reader, writer) as client:
                await client.initialize()
                result = await client.call_tool('resolve_q32', {'request_id':'offline-'+str(time.time_ns()),
                    'levels':[1,2], 'environment':'offline-fault-test','family':'SERVERSPACE/RESOLVE','custody':'owner-test'})
                if not result.isError: raise AssertionError('new commit admitted without authenticated substrate')
                # Durable reads remain available; they do not pretend substrate freshness.
                observed = unpack(await client.call_tool('read_resolve_receipt', {'artifact_digest':artifact}))
                if observed != previous: raise AssertionError('failed new commit changed the retained receipt chain')
    finally:
        # Only the exact fresh owner process whose identity was checked above.
        if owners(command) == [pid]: os.kill(pid, signal.SIGCONT)
    return {'new_commit_rejected_while_substrate_paused':True,'retained_readback_unchanged':True}


async def main():
    deployment = json.loads((RUNTIME/'resolve-deployment.json').read_text())
    row = deployment['instances'][0]
    estate = RUNTIME/'resolve-supervision-auth-canary'
    config = json.loads((estate/'services.json').read_text())
    before = await read_receipt(row['url'], row['qualification']['artifact_digest'])
    found = owners(config['resolve']['command'])
    if len(found) != 1: raise RuntimeError('SDK owner not uniquely identified')
    killed = found[0]
    os.kill(killed, signal.SIGKILL)
    deadline = time.monotonic()+15
    while True:
        try:
            current = owners(config['resolve']['command'])
            if len(current) == 1 and current[0] != killed:
                health(19091, row['identity']); break
        except (OSError, ValueError, KeyError): pass
        if time.monotonic() >= deadline: raise AssertionError('SDK supervisor did not restore readiness')
        await asyncio.sleep(.1)
    after = await read_receipt(row['url'],row['qualification']['artifact_digest'])
    if after != before: raise AssertionError('SDK restart changed persisted result or receipt chain')
    offline = await offline_commit_test(row,config)
    deadline = time.monotonic()+5
    while True:
        try: health(19091,row['identity']); break
        except (OSError, ValueError, KeyError):
            if time.monotonic() >= deadline: raise AssertionError('substrate did not resume')
            await asyncio.sleep(.1)
    # New SDK listener must not bind if the substrate has never authenticated.
    with tempfile.TemporaryDirectory(prefix='resolve-start-gate-') as directory:
        with socket.socket() as probe:
            probe.bind(('127.0.0.1',0)); port = probe.getsockname()[1]
        gated = subprocess.run([sys.executable,str(SOFTWARE/'resolve_mcp.py'),'--root',str(Path(directory)/'resolve'),
            '--substrate-root',str(Path(directory)/'absent-substrate'),'--identity','startup-gate-test','--port',str(port)],
            env=dict(os.environ,PYTHONPATH=str(SOFTWARE/'dependencies'),PYTHONDONTWRITEBYTECODE='1'),
            capture_output=True,timeout=10)
        if gated.returncode == 0: raise AssertionError('listener started without substrate')
        with socket.socket() as probe: probe.bind(('127.0.0.1',port))
    # Re-run the owner's exact protocol qualification on all independent instances.
    sys.path.insert(0,str(SOFTWARE))
    from qualify_resolve_mcp import qualify
    verified = [await qualify(item['url'],item['identity']) for item in deployment['instances']]
    if len({item['artifact_digest'] for item in verified}) != 3: raise AssertionError('independent contexts merged')
    report = {'schema':'kex.owner-resolve-live-qualification.v1','scope':deployment['scope'],
        'source_commit':deployment['source_commit'],'sdk_restart_recovered':True,
        'identical_receipt_after_restart':True,'startup_withheld_without_substrate':True,
        **offline,'instances':verified,'independent_contexts_retained':True}
    path = RUNTIME/'resolve-fault-qualification.json'
    path.write_text(json.dumps(report,indent=2)+'\n');path.chmod(0o600)
    print(json.dumps(report,indent=2))


if __name__ == '__main__': asyncio.run(main())
