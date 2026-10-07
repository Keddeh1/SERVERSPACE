#!/usr/bin/env python3
"""Render maps and undated RFC5545 tasks from the pinned programme snapshot."""
from datetime import datetime, timezone
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
directory = ROOT / 'docs/planning'
programme = json.loads((directory / 'PROGRAMME_SNAPSHOT.json').read_text())
tracking = json.loads((directory / 'NATIVE_READBACK.json').read_text())
plan = json.loads((directory / 'UTILITY_PLAN.json').read_text())

def escaped(value):
    return value.replace('\\', '\\\\').replace('\n', '\\n').replace(';', '\\;').replace(',', '\\,')

def folded(line):
    segments, current = [], ''
    for char in line:
        if len((current + char).encode()) > 74:
            segments.append(current)
            current = ' ' + char
        else:
            current += char
    segments.append(current)
    return '\r\n'.join(segments)

timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
calendar = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Keddeh//Governed Programme Tasks//EN',
            'CALSCALE:GREGORIAN', 'X-WR-CALNAME:Keddeh programme — undated tasks', 'X-WR-TIMEZONE:Australia/Adelaide']
for task in programme['steps']:
    state = {'completed': 'COMPLETED', 'in_progress': 'IN-PROCESS'}.get(task['status'], 'NEEDS-ACTION')
    calendar += ['BEGIN:VTODO', 'UID:programme-step-' + str(task['id']) + '@keddeh.com',
                 'DTSTAMP:' + timestamp, 'SUMMARY:' + escaped(str(task['id']) + '. ' + task['title']),
                 'STATUS:' + state, 'PERCENT-COMPLETE:' + ('100' if state == 'COMPLETED' else '0'),
                 'URL:https://github.com/Keddeh1/KEDDEH-SOVEREIGN-NAMESPACE-RUNTIME/issues/' + str(16 + task['batch']),
                 'DESCRIPTION:' + escaped('Source revision ' + programme['canonical_revision'] + '. Due date unset; this is a task export, not an agreed delivery commitment.')]
    calendar += ['RELATED-TO;RELTYPE=DEPENDS-ON:programme-step-' + str(dep) + '@keddeh.com' for dep in task['depends_on']]
    calendar.append('END:VTODO')
calendar.append('END:VCALENDAR')
(directory / 'PROGRAMME_TASKS.ics').write_bytes(('\r\n'.join(folded(line) for line in calendar) + '\r\n').encode())

roadmap = '# Programme roadmap and calendar\n\nCanonical source revision: `' + programme['canonical_revision'] + '`.\n'
roadmap += 'Snapshot: ' + str(sum(s['status'] == 'completed' for s in programme['steps'])) + '/100 completed; next step ' + str(programme['next_step']) + '.\n\n'
roadmap += 'The ICS export contains 100 VTODO records. It supplies dependencies and source links,\nnot fabricated start/due dates. Task-capable calendar clients can import it; ordinary\nevent-only calendars may not display VTODOs. Australia/Adelaide is the planning timezone.\n\n'
roadmap += '| Batch | Scope | Task state | Native issue |\n| --- | --- | --- | --- |\n'
for group in programme['groups']:
    tasks = [s for s in programme['steps'] if s['batch'] == group['id']]
    done = sum(s['status'] == 'completed' for s in tasks)
    roadmap += '| ' + str(group['id']) + ' | ' + group['title'] + ' | ' + str(done) + '/10 completed | [Batch ' + str(group['id']) + '](https://github.com/Keddeh1/KEDDEH-SOVEREIGN-NAMESPACE-RUNTIME/issues/' + str(group['id'] + 16) + ') |\n'
(directory / 'ROADMAP.md').write_text(roadmap)
diagram = '# Dependency and repository map\n\n```mermaid\nflowchart TD\n'
diagram += '  Programme["Canonical 100-step programme"]\n'
for group in programme['groups']:
    diagram += '  Programme --> B' + str(group['id']) + '["Batch ' + str(group['id']) + ': ' + group['title'] + '"]\n'
for index in range(1, 10):
    diagram += '  B' + str(index) + ' --> B' + str(index + 1) + '\n'
diagram += '  Projects["Projects capability: denied"] --> Planning["Native utilities + versioned alternatives"]\n'
diagram += '  Memory["100 TB physical RAM acceptance"] --> B4\n  Protocol["TOT / 0.297 failure-envelope qualification"] --> B10\n'
diagram += '  Canonical["Canonical compiler / multiplexer contract"] --> Device["TV / Android / 32-bit targets"]\n'
diagram += '  Canonical --> Personal["Exact personal Site native promotion"]\n```\n\n'
diagram += 'This diagram describes dependencies; it does not assert a provisioned host, active\nProject or promoted Site. Native edges are separately read back.\n\n'
diagram += '| Repository family | Responsibility |\n| --- | --- |\n'
roles = ['Owner BRAINK source and runtime integration', 'Canonical programme, namespace and evidence', 'Bounded private VFS implementation', 'Estate bindings, APEX and personal Site source', 'External server/family admission', 'Deployment queue and release coordination', 'Bounded private VFS implementation', 'Foundry schema/contracts', 'Company frontage candidate']
for repo, role in zip(plan['repositories'], roles):
    diagram += '| [' + repo + '](https://github.com/' + repo + ') | ' + role + ' |\n'
(directory / 'DEPENDENCY_MAP.md').write_text(diagram)
print(json.dumps({'calendar_tasks': len(programme['steps']), 'roadmap_groups': len(programme['groups']), 'repository_families': len(plan['repositories'])}))
