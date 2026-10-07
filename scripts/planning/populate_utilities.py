#!/usr/bin/env python3
"""Idempotent native planning population; no spending, merges or production actuation."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--apply', action='store_true')
args = parser.parse_args()
if not args.apply:
    print('Read docs/planning/UTILITY_PLAN.json; use --apply to populate authorised GitHub records.')
    raise SystemExit(0)
plan = json.loads((ROOT / 'docs/planning/UTILITY_PLAN.json').read_text())
results = {'labels': [], 'milestones': {}, 'issues': {}, 'relationships': [], 'failures': []}

def api(path, method='GET', payload=None):
    command = ['gh', 'api', path, '-X', method]
    if payload is not None:
        command += ['--input', '-']
    result = subprocess.run(command, input=json.dumps(payload) if payload is not None else None,
                            text=True, capture_output=True, timeout=45)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or 'GitHub operation failed')
    return json.loads(result.stdout) if result.stdout.strip() else None

for repo in plan['repositories']:
    try:
        existing = {label['name'] for label in api('repos/' + repo + '/labels?per_page=100')}
        for label in plan['labels']:
            if label['name'] not in existing:
                api('repos/' + repo + '/labels', 'POST', label)
            results['labels'].append({'repository': repo, 'name': label['name']})
    except RuntimeError as error:
        results['failures'].append({'operation': 'labels', 'repository': repo, 'error': str(error)})
for milestone in plan['milestones']:
    repo = milestone['repository']
    existing = api('repos/' + repo + '/milestones?state=all&per_page=100')
    match = next((m for m in existing if m['title'] == milestone['title']), None)
    if match is None:
        match = api('repos/' + repo + '/milestones', 'POST', {'title': milestone['title'], 'description': milestone['description']})
    results['milestones'][milestone['id']] = {'repository': repo, 'number': match['number'], 'url': match['html_url']}
for issue in plan['issues']:
    repo = issue['repository']
    existing = api('repos/' + repo + '/issues?state=all&per_page=100')
    match = next((i for i in existing if i['title'] == issue['title'] and 'pull_request' not in i), None)
    if match is None:
        payload = {key: issue[key] for key in ('title', 'body', 'labels', 'assignees')}
        if issue.get('milestone'):
            payload['milestone'] = results['milestones'][issue['milestone']]['number']
        match = api('repos/' + repo + '/issues', 'POST', payload)
    missing_labels = set(issue['labels']) - {label['name'] for label in match['labels']}
    if missing_labels:
        api('repos/' + repo + '/issues/' + str(match['number']) + '/labels', 'POST', {'labels': sorted(missing_labels)})
    missing_owners = set(issue['assignees']) - {owner['login'] for owner in match['assignees']}
    if missing_owners:
        api('repos/' + repo + '/issues/' + str(match['number']) + '/assignees', 'POST', {'assignees': sorted(missing_owners)})
    results['issues'][issue['id']] = {'repository': repo, 'number': match['number'], 'node_id': match['node_id'], 'url': match['html_url']}
for relation in plan['relationships']:
    def resolve(key):
        if key in results['issues']:
            return results['issues'][key]
        repo, number = plan['existing'][key]
        record = api('repos/' + repo + '/issues/' + str(number))
        return {'repository': repo, 'number': number, 'node_id': record['node_id']}
    try:
        parent_record, child_record = resolve(relation['from']), resolve(relation['to'])
        endpoint = 'sub_issues' if relation['kind'] == 'subissue' else 'dependencies/blocked_by'
        present = api('repos/' + parent_record['repository'] + '/issues/' + str(parent_record['number']) + '/' + endpoint + '?per_page=100')
        if any(item['node_id'] == child_record['node_id'] for item in present):
            results['relationships'].append(dict(relation, existing=True))
            continue
        parent, child = parent_record['node_id'], child_record['node_id']
        if relation['kind'] == 'subissue':
            query = 'mutation($p:ID!,$c:ID!){addSubIssue(input:{issueId:$p,subIssueId:$c,replaceParent:false}){__typename}}'
        else:
            query = 'mutation($p:ID!,$c:ID!){addBlockedBy(input:{issueId:$p,blockingIssueId:$c}){__typename}}'
        response = api('graphql', 'POST', {'query': query, 'variables': {'p': parent, 'c': child}})
        if response.get('errors'):
            raise RuntimeError('; '.join(item['message'] for item in response['errors']))
        results['relationships'].append(relation)
    except RuntimeError as error:
        if any(word in str(error).lower() for word in ('already', 'exists')):
            results['relationships'].append(dict(relation, existing=True))
        else:
            results['failures'].append({'operation': relation, 'error': str(error)})
(ROOT / 'docs/planning/NATIVE_READBACK.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps({'labels': len(results['labels']), 'milestones': len(results['milestones']),
                  'issues': len(results['issues']), 'relationships': len(results['relationships']),
                  'failures': results['failures']}, indent=2))
