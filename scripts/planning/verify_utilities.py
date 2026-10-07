#!/usr/bin/env python3
"""Read back native planning records and validate generated task/roadmap structure."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
folder = ROOT / 'docs/planning'
plan = json.loads((folder / 'UTILITY_PLAN.json').read_text())
native = json.loads((folder / 'NATIVE_READBACK.json').read_text())
errors, checks = [], []

def api(path):
    response = subprocess.run(['gh', 'api', path], text=True, capture_output=True, check=True, timeout=30)
    return json.loads(response.stdout)

for repo in plan['repositories']:
    labels = {item['name'] for item in api('repos/' + repo + '/labels?per_page=100')}
    for item in plan['labels']:
        if item['name'] not in labels:
            errors.append('missing label: ' + repo + ' ' + item['name'])
    checks.append('labels read back: ' + repo)
for key, item in native['milestones'].items():
    observed = api('repos/' + item['repository'] + '/milestones/' + str(item['number']))
    required = next(m for m in plan['milestones'] if m['id'] == key)
    if observed['title'] != required['title']:
        errors.append('milestone mismatch: ' + key)
    checks.append('milestone read back: ' + key)
for key, item in native['issues'].items():
    observed = api('repos/' + item['repository'] + '/issues/' + str(item['number']))
    required = next(i for i in plan['issues'] if i['id'] == key)
    if observed['title'] != required['title'] or not set(required['labels']) <= {label['name'] for label in observed['labels']}:
        errors.append('issue mismatch: ' + key)
    if not set(required['assignees']) <= {owner['login'] for owner in observed['assignees']}:
        errors.append('issue owner mismatch: ' + key)
    checks.append('issue read back: ' + key)

cache = {}
def resolve(key):
    if key in native['issues']:
        return native['issues'][key]
    repo, number = plan['existing'][key]
    return {'repository': repo, 'number': number}
for relation in plan['relationships']:
    parent, child = resolve(relation['from']), resolve(relation['to'])
    path = 'repos/' + parent['repository'] + '/issues/' + str(parent['number'])
    path += '/sub_issues' if relation['kind'] == 'subissue' else '/dependencies/blocked_by'
    if path not in cache:
        cache[path] = api(path)
    expected = 'https://github.com/' + child['repository'] + '/issues/' + str(child['number'])
    if expected not in {item['html_url'] for item in cache[path]}:
        errors.append('relationship missing: ' + expected)
    checks.append('native relationship read back: ' + relation['from'] + ' ' + relation['kind'] + ' ' + relation['to'])

programme = json.loads((folder / 'PROGRAMME_SNAPSHOT.json').read_text())
if [step['id'] for step in programme['steps']] != list(range(1, 101)):
    errors.append('programme snapshot must contain ordered steps 1..100')
calendar = (folder / 'PROGRAMME_TASKS.ics').read_bytes()
lines = calendar.decode().split('\r\n')
if calendar.count(b'BEGIN:VTODO') != 100 or calendar.count(b'END:VTODO') != 100:
    errors.append('calendar must contain 100 complete task records')
if any(len(line.encode()) > 75 for line in lines):
    errors.append('calendar physical line exceeds RFC5545 folding limit')
if any(line.startswith(('DUE:', 'DUE;', 'DTSTART:', 'DTSTART;')) for line in lines):
    errors.append('unapproved schedule dates populated')
checks.append('100 task records, line folding and undated scheduling verified')
receipt = {'checks': checks, 'errors': errors, 'native_project_active': False,
           'discussions_active': False, 'hosted_ci_passed': False,
           'paid_capability_activated': False}
(folder / 'VERIFICATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'checks': len(checks), 'errors': errors}, indent=2))
raise SystemExit(bool(errors))
