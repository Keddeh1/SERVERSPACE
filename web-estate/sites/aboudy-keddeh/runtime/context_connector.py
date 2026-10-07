"""Bounded contextual lineage deltas over an existing Continuation journal.

Carrier placement may change; continuation identity and predecessor frames do not.
Transport authentication is the caller's responsibility, independent of lineage checks.
"""
import json
import re
from context_continuation import context, digest, canonical

MAX_EVENTS = 128
MAX_PACKET_BYTES = 256 * 1024
SCHEMA = 'kex.context-delta.v1'
KEYS = {'schema','continuation','base_head','target_head','target_context','events'}
BODY_KEYS = {'continuation','parent','sequence','context','axis','parameter','input','result'}


def export_delta(runtime, identifier, base_head, target_head, target_context):
    expected_context = runtime.admitted(target_context)
    with runtime.connect() as db:
        db.execute('BEGIN')
        row = db.execute('SELECT head FROM continuation WHERE id=?',(identifier,)).fetchone()
        if row is None or row[0] != target_head: raise ValueError('source head does not match requested export')
        _,_,last = runtime._replay(db,identifier,target_head)
        if last != expected_context: raise ValueError('export target jurisdiction mismatch')
        events=[];cursor=target_head
        while cursor != base_head:
            if cursor is None or len(events) >= MAX_EVENTS: raise ValueError('base is not an ancestor or delta exceeds budget')
            row=db.execute('SELECT body FROM lineage WHERE hash=?',(cursor,)).fetchone()
            if row is None: raise ValueError('missing export predecessor')
            body=json.loads(row[0]);events.append({'hash':cursor,'body':body});cursor=body['parent']
        packet={'schema':SCHEMA,'continuation':identifier,'base_head':base_head,'target_head':target_head,
                'target_context':context(target_context),'events':list(reversed(events))}
        if len(canonical(packet).encode()) > MAX_PACKET_BYTES: raise ValueError('packet exceeds byte budget')
        return packet


def accept_delta(runtime, packet):
    if not isinstance(packet,dict) or set(packet) != KEYS or packet['schema'] != SCHEMA:
        raise ValueError('unsupported delta frame')
    if len(canonical(packet).encode()) > MAX_PACKET_BYTES: raise ValueError('packet exceeds byte budget')
    identifier=packet['continuation']
    if type(identifier) is not str or not identifier or len(identifier)>128: raise ValueError('invalid continuation identity')
    for key in ('base_head','target_head'):
        value=packet[key]
        if value is not None and (type(value) is not str or re.fullmatch('[0-9a-f]{64}',value) is None):
            raise ValueError('invalid lineage head reference')
    target_context=runtime.admitted(packet['target_context'])
    events=packet['events']
    if not isinstance(events,list) or len(events)>MAX_EVENTS: raise ValueError('delta event budget exceeded')
    with runtime.connect() as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT head FROM continuation WHERE id=?',(identifier,)).fetchone()
        if row is None: raise ValueError('unknown destination continuation')
        # Lost acknowledgement: verify the repeated packet, not merely the claimed head.
        duplicate=row[0]==packet['target_head']
        if not duplicate and row[0] != packet['base_head']: raise ValueError('destination predecessor conflict')
        runtime._replay(db,identifier,row[0])
        previous=packet['base_head']
        if previous is not None:
            runtime._replay(db,identifier,previous)
        for event in events:
            if not isinstance(event,dict) or set(event)!={'hash','body'}: raise ValueError('invalid event wrapper')
            body=event['body']
            if not isinstance(body,dict) or set(body)!=BODY_KEYS or body['continuation']!=identifier or body['parent']!=previous:
                raise ValueError('delta predecessor/identity mismatch')
            if digest(body)!=event['hash']: raise ValueError('delta body digest mismatch')
            existing=db.execute('SELECT body FROM lineage WHERE hash=?',(event['hash'],)).fetchone()
            if existing is not None and existing[0]!=canonical(body): raise ValueError('stored event collision')
            if duplicate and existing is None: raise ValueError('retry includes uncommitted events')
            if existing is None:db.execute('INSERT INTO lineage VALUES (?,?)',(event['hash'],canonical(body)))
            previous=event['hash']
        if previous != packet['target_head']: raise ValueError('delta target does not match its chain')
        value,count,last=runtime._replay(db,identifier,packet['target_head'])
        if last != target_context: raise ValueError('delta target jurisdiction mismatch')
        if not duplicate:db.execute('UPDATE continuation SET head=? WHERE id=?',(packet['target_head'],identifier))
        return {'schema':SCHEMA,'continuation':identifier,'head':packet['target_head'],'context':context(packet['target_context']),
                'value':str(value),'sequence':count,'accepted_events':len(events),'duplicate':duplicate}
