"""Bounded loopback review runtime for the exact Site; no native publication."""
import argparse
from collections import deque
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import ssl
import threading
import time
from urllib.parse import unquote, urlsplit
from support.interest import register, purge_expired
from support.records import decode_json

ROOT = Path(__file__).resolve().parents[1] / 'dist'
NOTICE = 'portfolio-enquiry-v1'


class Server(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, address, database, enabled):
        super().__init__(address, Handler)
        self.database, self.enabled = database, enabled
        self.scheme = 'http'
        self.sessions, self.rate = {}, deque()
        self.lock = threading.Lock()
        self.slots = threading.BoundedSemaphore(8)

    def process_request(self, request, address):
        if not self.slots.acquire(blocking=False):
            try:
                request.sendall(b'HTTP/1.1 503 Service Unavailable\r\nContent-Length: 0\r\nConnection: close\r\n\r\n')
            finally:
                self.shutdown_request(request)
            return
        try:
            super().process_request(request, address)
        except Exception:
            self.slots.release()
            raise

    def process_request_thread(self, request, address):
        try:
            super().process_request_thread(request, address)
        finally:
            self.slots.release()

    def handle_error(self, request, client_address):
        print('{"event":"site_request_failed"}')


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, *args):
        pass  # no visitor details or submitted data in default logs

    def respond(self, status, data, kind='application/json', cookie=None):
        if isinstance(data, dict):
            data = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(data)

    def authority(self):
        return '127.0.0.1:' + str(self.server.server_port)

    def host_valid(self):
        return self.headers.get('Host') == self.authority()

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if not self.host_valid():
            return self.respond(403, {'error': 'Host is not admitted.'})
        route = urlsplit(self.path)
        if route.query:
            return self.respond(400, {'error': 'Unexpected query parameters.'})
        if route.path == '/healthz':
            return self.respond(200, {'status': 'ok', 'scope': 'local-site-review'})
        if route.path == '/api/capabilities':
            result = {'capture_enabled': self.server.enabled, 'notice_revision': NOTICE,
                      'retention_days': 90, 'native_publication': False}
            if not self.server.enabled:
                return self.respond(200, result)
            session, token = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
            with self.server.lock:
                now = time.monotonic()
                self.server.sessions = {k: v for k, v in self.server.sessions.items() if v[1] > now}
                if len(self.server.sessions) >= 256:
                    return self.respond(503, {'error': 'Please try again later.'})
                self.server.sessions[session] = (token, now + 600)
            result['csrf_token'] = token
            return self.respond(200, result, cookie='site_session=' + session + '; HttpOnly; SameSite=Strict; Path=/; Max-Age=600' + ('; Secure' if self.server.scheme == 'https' else ''))
        if route.path.startswith('/api/'):
            return self.respond(404, {'error': 'Unknown endpoint.'})
        path = unquote(route.path)
        if '\\' in path or '\x00' in path or '..' in path.split('/'):
            return self.respond(400, {'error': 'Invalid path.'})
        target = ROOT / path.lstrip('/')
        if path.endswith('/'):
            target /= 'index.html'
        if not target.resolve().is_relative_to(ROOT.resolve()) or not target.is_file() or target.is_symlink():
            return self.respond(404, {'error': 'Page not found.'})
        kind = {'.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'application/javascript; charset=utf-8'}.get(target.suffix)
        if not kind:
            return self.respond(404, {'error': 'Resource not found.'})
        self.respond(200, target.read_bytes(), kind)

    def do_POST(self):
        if not self.host_valid() or self.headers.get('Origin') != self.server.scheme + '://' + self.authority():
            return self.respond(403, {'error': 'Submission origin is not admitted.'})
        if self.path != '/api/interest':
            return self.respond(404, {'error': 'Unknown endpoint.'})
        if not self.server.enabled:
            return self.respond(503, {'error': 'Online registration is unavailable.'})
        cookie = cookies.SimpleCookie()
        try:
            cookie.load(self.headers.get('Cookie', ''))
            session = cookie['site_session'].value
        except (KeyError, cookies.CookieError):
            return self.respond(403, {'error': 'Reload the form to renew the submission session.'})
        with self.server.lock:
            enrolled = self.server.sessions.get(session)
            token = self.headers.get('X-CSRF-Token', '')
            if not enrolled or enrolled[1] < time.monotonic() or not secrets.compare_digest(enrolled[0], token):
                return self.respond(403, {'error': 'Reload the form to renew the submission session.'})
            now = time.monotonic()
            while self.server.rate and self.server.rate[0] <= now - 60:
                self.server.rate.popleft()
            if len(self.server.rate) >= 20:
                return self.respond(429, {'error': 'Please wait a minute before retrying.'})
            self.server.rate.append(now)
        if self.headers.get('Content-Type') != 'application/json' or self.headers.get('Transfer-Encoding'):
            return self.respond(415, {'error': 'A JSON submission is required.'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 8192:
                return self.respond(413, {'error': 'The enquiry exceeds the allowed size.'})
            payload = self.rfile.read(length)
            if len(payload) != length:
                raise ValueError('Incomplete submission.')
            value = decode_json(payload)
            receipt = register(self.server.database, value, NOTICE, self.headers.get('Idempotency-Key'))
            purge_expired(self.server.database)
        except (ValueError, UnicodeError, TypeError) as error:
            return self.respond(400, {'error': str(error)})
        except Exception:
            return self.respond(503, {'error': 'Storage is unavailable. Retry or use email.'})
        self.respond(201, receipt)

    def do_PUT(self):
        self.respond(405, {'error': 'Method is not supported.'})
    do_DELETE = do_PATCH = do_PUT


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=18766)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--enable-capture', action='store_true', help='Enable reviewed local enquiries; use fixtures for qualification.')
    parser.add_argument('--tls-cert', type=Path)
    parser.add_argument('--tls-key', type=Path)
    args = parser.parse_args()
    if args.database.resolve().is_relative_to(ROOT.parent.resolve()):
        parser.error('private database must be outside the Site source tree')
    os.umask(0o077)
    server = Server(('127.0.0.1', args.port), args.database, args.enable_capture)
    if bool(args.tls_cert) != bool(args.tls_key):
        parser.error('TLS requires both certificate and private key')
    if args.tls_cert:
        if args.tls_key.is_symlink() or args.tls_key.stat().st_mode & 0o077:
            parser.error('TLS private key must be a private regular owner file')
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(args.tls_cert, args.tls_key)
        server.socket = context.wrap_socket(server.socket, server_side=True, do_handshake_on_connect=False)
        server.scheme = 'https'
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
