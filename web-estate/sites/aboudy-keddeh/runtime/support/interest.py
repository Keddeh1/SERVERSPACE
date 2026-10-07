"""Private interest-registration primitive awaiting integration into the bound Site.

No public route is enabled here. Consent, idempotency, retention and server-side
validation are explicit. Receipts contain no contact details and send no messages.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import re
import os
from pathlib import Path
import sqlite3
import uuid

from .records import canonical_bytes

FIELDS = {'name', 'email', 'organisation', 'use_case', 'message', 'privacy_consent', 'marketing_consent', 'notice_revision'}
USE_CASES = {'deployment-evidence', 'runtime-integration', 'governed-research', 'website-foundry', 'other'}


def validate(value, notice_revision):
    errors = []
    if not isinstance(value, dict) or set(value) != FIELDS:
        return ['registration fields do not match the contract']
    for name, minimum, maximum in [('name', 1, 120), ('email', 3, 254), ('organisation', 0, 160), ('message', 0, 2000)]:
        field = value[name]
        if not isinstance(field, str) or not minimum <= len(field.strip()) <= maximum or any(ord(c) < 32 and c not in '\n\t' for c in field):
            errors.append(f'{name}: invalid length or characters')
    if not isinstance(value['email'], str) or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value['email']):
        errors.append('email: invalid address format')
    if not isinstance(value['use_case'], str) or value['use_case'] not in USE_CASES:
        errors.append('use_case: unsupported selection')
    if value['privacy_consent'] is not True:
        errors.append('privacy consent must be explicitly supplied')
    if type(value['marketing_consent']) is not bool:
        errors.append('marketing consent must be an explicit boolean')
    if not isinstance(notice_revision, str) or not notice_revision or value['notice_revision'] != notice_revision:
        errors.append('privacy notice revision mismatch')
    return errors


def register(database, value, notice_revision, request_id, now=None, retention_days=90):
    errors = validate(value, notice_revision)
    if errors:
        raise ValueError('; '.join(errors))
    try:
        if str(uuid.UUID(request_id)) != request_id:
            raise ValueError('request_id must be a canonical UUID')
    except (ValueError, TypeError, AttributeError):
        raise ValueError('request_id must be a canonical UUID') from None
    if type(retention_days) is not int or not 1 <= retention_days <= 365:
        raise ValueError('retention days must be between 1 and 365')
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('registration time requires a timezone')
    database = Path(database)
    if database.is_symlink():
        raise ValueError('registration database cannot be a symbolic link')
    database.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(database, os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    os.close(fd)
    if database.stat().st_mode & 0o077:
        raise ValueError('registration database must be private to its owner')
    payload = canonical_bytes(value).decode()
    digest = hashlib.sha256(payload.encode()).hexdigest()
    with sqlite3.connect(database, timeout=5) as connection:
        connection.execute('CREATE TABLE IF NOT EXISTS interests (request_id TEXT PRIMARY KEY, digest TEXT NOT NULL, payload TEXT NOT NULL, observed_at TEXT NOT NULL, delete_after TEXT NOT NULL)')
        connection.execute('BEGIN IMMEDIATE')
        existing = connection.execute('SELECT digest, observed_at, delete_after FROM interests WHERE request_id = ?', (request_id,)).fetchone()
        if existing:
            if existing[0] != digest:
                raise ValueError('idempotency key was reused with different registration data')
            observed, delete_after = existing[1:]
        else:
            observed = now.astimezone(timezone.utc).isoformat()
            delete_after = (now + timedelta(days=retention_days)).astimezone(timezone.utc).isoformat()
            connection.execute('INSERT INTO interests VALUES (?, ?, ?, ?, ?)', (request_id, digest, payload, observed, delete_after))
    return {'registration_id': request_id, 'status': 'recorded', 'observed_at': observed, 'delete_after': delete_after,
            'messages_sent': False, 'notice_revision': notice_revision}


def erase(database, registration_id):
    with sqlite3.connect(database, timeout=5) as connection:
        cursor = connection.execute('DELETE FROM interests WHERE request_id = ?', (registration_id,))
    return {'registration_id': registration_id, 'deleted': cursor.rowcount == 1}


def purge_expired(database, now=None):
    now = now or datetime.now(timezone.utc)
    with sqlite3.connect(database, timeout=5) as connection:
        cursor = connection.execute('DELETE FROM interests WHERE delete_after <= ?', (now.astimezone(timezone.utc).isoformat(),))
    return {'expired_records_deleted': cursor.rowcount}
