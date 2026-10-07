import http.client
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from server import Server, NOTICE
from support.interest import erase, purge_expired


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / 'enquiries.sqlite'
        self.server = Server(('127.0.0.1', 0), self.database, True)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_port
        self.value = {'name': 'Fixture', 'email': 'fixture@example.invalid', 'organisation': '',
                      'message': '', 'use_case': 'website-foundry', 'privacy_consent': True,
                      'marketing_consent': False, 'notice_revision': NOTICE}
        status, result, headers = self.request('GET', '/api/capabilities')
        self.headers = {'Origin': 'http://127.0.0.1:' + str(self.port), 'Content-Type': 'application/json',
                        'Cookie': headers['Set-Cookie'].split(';')[0], 'X-CSRF-Token': result['csrf_token'],
                        'Idempotency-Key': str(uuid.uuid4())}

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(); self.temp.cleanup()

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=5)
        connection.request(method, path, body, headers or {})
        response = connection.getresponse(); content = response.read()
        result = json.loads(content) if 'application/json' in response.getheader('Content-Type', '') else content
        status, fields = response.status, dict(response.getheaders()); connection.close()
        return status, result, fields

    def submit(self, value=None, headers=None):
        return self.request('POST', '/api/interest', json.dumps(value or self.value), headers or self.headers)

    def test_static_routes_and_security_headers(self):
        for route in json.loads((Path(__file__).resolve().parents[1] / 'content.json').read_text()):
            status, body, headers = self.request('GET', route)
            self.assertEqual(status, 200); self.assertIn(b'<h1', body)
            self.assertNotIn('unsafe-inline', headers['Content-Security-Policy'])
        self.assertEqual(self.request('GET', '/missing/')[0], 404)
        self.assertEqual(self.request('GET', '/%2e%2e/SOURCE.json')[0], 400)
        self.assertEqual(self.request('GET', '/contact/?unexpected=1')[0], 400)
        self.assertEqual(self.request('PUT', '/api/interest')[0], 405)

    def test_persisted_idempotent_receipt_and_erasure(self):
        one = self.submit(); two = self.submit()
        self.assertEqual(one[0], 201); self.assertEqual(one[1], two[1])
        self.assertNotIn('email', json.dumps(one[1])); self.assertFalse(one[1]['messages_sent'])
        self.assertEqual(self.database.stat().st_mode & 0o077, 0)
        with sqlite3.connect(self.database) as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM interests').fetchone()[0], 1)
        self.assertTrue(erase(self.database, one[1]['registration_id'])['deleted'])

    def test_origin_and_csrf_rejected(self):
        for changes in [{'Origin': 'https://foreign.invalid'}, {'X-CSRF-Token': 'altered'}, {'Cookie': ''}]:
            self.assertEqual(self.submit(headers=dict(self.headers, **changes))[0], 403)
        self.assertFalse(self.database.exists())

    def test_consent_notice_and_field_limits(self):
        for changes in [{'privacy_consent': False}, {'notice_revision': 'old'}, {'marketing_consent': 'yes'},
                        {'message': 'a' * 2001}, {'email': 'invalid'}, {'use_case': 'unknown'}]:
            self.assertEqual(self.submit(dict(self.value, **changes))[0], 400)
        self.assertFalse(self.database.exists())

    def test_changed_retry_and_expiry(self):
        self.assertEqual(self.submit()[0], 201)
        self.assertEqual(self.submit(dict(self.value, message='changed'))[0], 400)
        from datetime import datetime, timedelta, timezone
        self.assertEqual(purge_expired(self.database, datetime.now(timezone.utc) + timedelta(days=91))['expired_records_deleted'], 1)

    def test_disabled_and_capacity_contracts(self):
        self.server.enabled = False
        self.assertFalse(self.request('GET', '/api/capabilities')[1]['capture_enabled'])
        self.assertEqual(self.submit()[0], 503)
        self.server.enabled = True
        self.server.rate.extend([__import__('time').monotonic()] * 20)
        self.assertEqual(self.submit()[0], 429)

    def test_ambiguous_json_size_and_session_expiry(self):
        self.assertEqual(self.request('POST', '/api/interest', '{"name":1,"name":2}', self.headers)[0], 400)
        self.assertEqual(self.request('POST', '/api/interest', 'x' * 8193, self.headers)[0], 413)
        self.server.sessions.clear()
        self.assertEqual(self.submit()[0], 403)

    def test_tls_verification_and_secure_cookie(self):
        import ssl
        import subprocess
        certificate = Path(self.temp.name) / 'fixture.crt'
        key = Path(self.temp.name) / 'fixture.key'
        subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '1',
                        '-subj', '/CN=127.0.0.1', '-addext', 'subjectAltName=IP:127.0.0.1',
                        '-keyout', str(key), '-out', str(certificate)], check=True, capture_output=True)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(certificate, key)
        secure = Server(('127.0.0.1', 0), self.database, True)
        secure.socket = context.wrap_socket(secure.socket, server_side=True, do_handshake_on_connect=False)
        secure.scheme = 'https'
        thread = threading.Thread(target=secure.serve_forever, daemon=True); thread.start()
        try:
            connection = http.client.HTTPSConnection('127.0.0.1', secure.server_port,
                context=ssl.create_default_context(cafile=str(certificate)), timeout=5)
            connection.request('GET', '/api/capabilities')
            response = connection.getresponse()
            self.assertEqual(response.status, 200); self.assertIn('Secure', response.getheader('Set-Cookie'))
            response.read(); connection.close()
            untrusted = http.client.HTTPSConnection('127.0.0.1', secure.server_port, timeout=5)
            with self.assertRaises(ssl.SSLCertVerificationError):
                untrusted.request('GET', '/healthz')
            untrusted.close()
        finally:
            secure.shutdown(); secure.server_close(); thread.join()
