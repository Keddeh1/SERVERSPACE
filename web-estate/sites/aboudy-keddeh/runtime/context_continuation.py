"""Exact arithmetic continuation with registered context and replayed lineage.

Owner ray/continuation semantics are attributed in docs/engineering/number-line.
Policy registrations are operator inputs, not evidence of regional consensus.
"""
import copy
from contextlib import contextmanager
from fractions import Fraction
import hashlib
import json
import sqlite3
import re

FIELDS = {'origin', 'ordinance', 'municipality', 'region', 'vector', 'frame', 'unit', 'revision'}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def context(value):
    if not isinstance(value, dict) or set(value) != FIELDS:
        raise ValueError('complete governed context required')
    if any(type(v) is not str or not v or len(v) > 256 for v in value.values()):
        raise ValueError('bounded explicit context identities required')
    return copy.deepcopy(value)


def operate(value, axis, parameter):
    if type(parameter) is not int or not 1 <= parameter <= 2**24 - 1:
        raise ValueError('positive exact arithmetic parameter required')
    if axis == '+X': return value + parameter
    if axis == '-X': return value - parameter
    if axis == '+Y': return value * parameter
    if axis == '-Y': return value / parameter
    raise ValueError('unregistered arithmetic ray')


def conjugate(address, operation):
    if type(address) is not int or not 1 <= address <= 2**24:
        raise ValueError('active address outside bounded one-origin contract')
    legacy = address - 1
    if operation == 'identity': result = legacy
    elif operation == 'increment': result = legacy + 1
    elif operation == 'double': result = legacy * 2
    else: raise ValueError('unadmitted compatibility operation')
    mapped = result + 1
    if mapped > 2**24: raise ValueError('translated address overflow')
    return mapped


class Continuation:
    def __init__(self, database, contexts, transitions=()):
        self.contexts = {digest(context(c)): context(c) for c in contexts}
        if not self.contexts: raise ValueError('registered context required')
        self.transitions = frozenset(transitions)
        if any(a not in self.contexts or b not in self.contexts for a,b in self.transitions):
            raise ValueError('transition references unregistered contexts')
        self.database = str(database)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS continuation (id TEXT PRIMARY KEY, head TEXT, genesis_context TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS lineage (hash TEXT PRIMARY KEY, body TEXT NOT NULL)')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.database, timeout=10)
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA synchronous=FULL')
        try:
            with db:
                yield db
        finally:
            db.close()

    def admitted(self, requested):
        c = context(requested); key = digest(c)
        if self.contexts.get(key) != c: raise ValueError('context is not registered')
        return key

    def create(self, identifier, initial_context=None):
        if type(identifier) is not str or not identifier or len(identifier) > 128:
            raise ValueError('bounded continuation identity required')
        if initial_context is None:
            if len(self.contexts) != 1: raise ValueError('explicit genesis context required')
            initial_context = next(iter(self.contexts.values()))
        genesis = self.admitted(initial_context)
        with self.connect() as db:
            db.execute('INSERT INTO continuation VALUES (?,NULL,?)', (identifier,genesis))

    def _replay(self, db, identifier, head):
        genesis = db.execute('SELECT genesis_context FROM continuation WHERE id=?',(identifier,)).fetchone()
        if genesis is None or genesis[0] not in self.contexts: raise ValueError('unregistered genesis context')
        chain = []; cursor = head; seen = set()
        while cursor is not None:
            if cursor in seen or len(chain) >= 4096: raise ValueError('cyclic or oversized predecessor lineage')
            seen.add(cursor)
            row = db.execute('SELECT body FROM lineage WHERE hash=?', (cursor,)).fetchone()
            if row is None: raise ValueError('broken predecessor lineage')
            body = json.loads(row[0])
            if not isinstance(body,dict) or set(body) != {'continuation','parent','sequence','context','axis','parameter','input','result'}:
                raise ValueError('lineage frame mismatch')
            if body['parent'] is not None and (type(body['parent']) is not str or re.fullmatch('[0-9a-f]{64}',body['parent']) is None):
                raise ValueError('invalid predecessor reference')
            if digest(body) != cursor or body.get('continuation') != identifier:
                raise ValueError('lineage body/continuation mismatch')
            chain.append(body); cursor = body['parent']
        value = Fraction(1); prior_context = genesis[0]
        for step, body in enumerate(reversed(chain), 1):
            if set(body) != {'continuation','parent','sequence','context','axis','parameter','input','result'}:
                raise ValueError('lineage frame mismatch')
            current = self.admitted(body['context'])
            if prior_context is not None and current != prior_context and (prior_context,current) not in self.transitions:
                raise ValueError('cross-origin transition is not admitted')
            if type(body['sequence']) is not int or body['sequence'] != step or body['input'] != str(value):
                raise ValueError('lineage sequence/input mismatch')
            value = operate(value,body['axis'],body['parameter'])
            if value.numerator.bit_length() > 4096 or value.denominator.bit_length() > 4096:
                raise ValueError('arithmetic representation budget exceeded')
            if body['result'] != str(value): raise ValueError('coordinate vector does not match predecessor operation')
            prior_context = current
        return value, len(chain), prior_context

    def read(self, identifier, expected_context):
        expected = self.admitted(expected_context)
        with self.connect() as db:
            db.execute('BEGIN')
            row = db.execute('SELECT head FROM continuation WHERE id=?',(identifier,)).fetchone()
            if row is None: raise ValueError('unknown continuation')
            value,count,last = self._replay(db,identifier,row[0])
            if last is not None and last != expected: raise ValueError('requested jurisdiction differs from lineage head')
            return {'head':row[0],'value':str(value),'sequence':count,'context':copy.deepcopy(expected_context)}

    def advance(self, identifier, expected_head, requested_context, axis, parameter):
        current = self.admitted(requested_context)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT head FROM continuation WHERE id=?',(identifier,)).fetchone()
            if row is None or row[0] != expected_head: raise ValueError('stale continuation head')
            value,count,last = self._replay(db,identifier,expected_head)
            if count >= 4096: raise ValueError('continuation budget exceeded')
            if last is not None and current != last and (last,current) not in self.transitions:
                raise ValueError('cross-origin transition is not admitted')
            result = operate(value,axis,parameter)
            if max(result.numerator.bit_length(), result.denominator.bit_length()) > 4096:
                raise ValueError('arithmetic representation budget exceeded')
            body = {'continuation':identifier,'parent':expected_head,'sequence':count+1,
                    'context':context(requested_context),'axis':axis,'parameter':parameter,
                    'input':str(value),'result':str(result)}
            key = digest(body)
            db.execute('INSERT INTO lineage VALUES (?,?)',(key,canonical(body)))
            db.execute('UPDATE continuation SET head=? WHERE id=?',(key,identifier))
            return {'head':key,'value':str(result),'sequence':count+1,'context':context(requested_context)}


def resolve_equivalent(candidates, identifier, expected_head, requested_context):
    """Try alternate local stores only for exactly the requested lineage head/context."""
    failures=[]
    for index,candidate in enumerate(candidates):
        try:
            receipt=candidate.read(identifier,requested_context)
            if receipt['head'] != expected_head: raise ValueError('alternate lineage is stale or different')
            return {**receipt,'path':index+1,'failed_paths':failures,'fallback_used':bool(failures)}
        except (ValueError,sqlite3.DatabaseError,KeyError,TypeError): failures.append(index+1)
    raise ValueError('no equivalent admitted lineage path')


def resolve_bound_cell(candidates, memory, identifier, expected_head, requested_context, source, target):
    """Compose lineage admission with the owner's independently verified VFS field."""
    from relational_memory import location
    loc = location(source,target)
    if context(requested_context)['vector'] != loc['vfs_address']:
        raise ValueError('governed vector does not identify requested VFS coordinate')
    lineage = resolve_equivalent(candidates,identifier,expected_head,requested_context)
    cell = memory.read_with_receipt(source,target)
    return {'lineage':lineage,'memory':cell,'coordinate':loc}
