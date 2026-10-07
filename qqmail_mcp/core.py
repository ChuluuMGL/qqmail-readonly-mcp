"""Read-only IMAP and durable local delivery state. Email is untrusted data."""
import base64
import datetime as dt
import email.policy
from email.parser import BytesParser
import imaplib
import json
import re
import sqlite3
import ssl
import uuid

MAX_BODY = 2 * 1024 * 1024
MAX_HEADER = 64 * 1024
MAX_UIDS = 100000

class MailError(Exception):
    pass

def quoted(value):
    if not isinstance(value, str) or len(value) > 1024 or any(ord(c) < 32 for c in value):
        raise MailError('INVALID_INPUT')
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'

def mutf7(value):
    def encode(m):
        s = m.group().encode('utf-16be')
        return '&' + base64.b64encode(s).decode().rstrip('=').replace('/', ',') + '-'
    return re.sub(r'[^\x20-\x7e]+', encode, value.replace('&', '&-'))

def decode_folder(value):
    def decode(m):
        s = m.group(1)
        if not s: return '&'
        return base64.b64decode(s.replace(',', '/') + '=' * (-len(s) % 4)).decode('utf-16be')
    return re.sub(r'&([^-]*)-', decode, value)

class BoundedIMAP(imaplib.IMAP4_SSL):
    def read(self, size):
        # Refuse an oversized literal even if a server ignores partial FETCH.
        if size > MAX_BODY + 1: raise MailError('SERVER_LITERAL_TOO_LARGE')
        return super().read(size)

class Imap:
    def __init__(self, user, password, timeout=15):
        self.user, self.password, self.timeout = user, password, timeout
        self.client = None
    def connect(self):
        self.client = BoundedIMAP('imap.qq.com', 993, ssl_context=ssl.create_default_context(), timeout=self.timeout)
        self.client.sock.settimeout(self.timeout)
        self.client.login(self.user, self.password)
    def drop(self):
        if self.client:
            try: self.client.shutdown()
            except Exception: pass
        self.client = None
    def run(self, action):
        for attempt in range(2):
            try:
                if self.client is None: self.connect()
                return action(self.client)
            except (OSError, imaplib.IMAP4.abort):
                self.drop()
                if attempt: raise MailError('CONNECTION_FAILED') from None
            except MailError:
                self.drop()
                raise
            except imaplib.IMAP4.error:
                self.drop()
                raise MailError('IMAP_FAILED') from None
    @staticmethod
    def ok(result):
        if result[0] != 'OK': raise MailError('IMAP_FAILED')
        return result[1]
    def folders(self):
        rows = self.run(lambda c: self.ok(c.list()))
        result = []
        for row in rows:
            if isinstance(row, tuple): prefix, name = row
            elif isinstance(row, bytes):
                m = re.fullmatch(rb'\((.*?)\) (NIL|"(?:[^"\\]|\\.)*") (.*)', row)
                if not m: raise MailError('UNSUPPORTED_LIST_RESPONSE')
                prefix, name = m.group(1), m.group(3)
            else: continue
            if name.startswith(b'"'):
                name = re.sub(rb'\\(.)', rb'\1', name[1:-1])
            result.append({'folder': decode_folder(name.decode('ascii')), 'selectable': b'\\Noselect' not in prefix})
        return result
    def selected(self, c, folder):
        quoted(folder)
        self.ok(c.select(quoted(mutf7(folder)), readonly=True))
        values = c.response('UIDVALIDITY')[1]
        if not values or not values[0]: raise MailError('MISSING_UIDVALIDITY')
        return str(int(values[0]))
    def uids(self, folder, since=None, before=None):
        criteria = []
        for key, val in [('SINCE', since), ('BEFORE', before)]:
            if val is not None:
                day = dt.date.fromisoformat(val)
                criteria += [key, day.strftime('%d-%b-%Y')]
        def action(c):
            validity = self.selected(c, folder)
            rows = self.ok(c.uid('SEARCH', None, *(criteria or ['ALL'])))
            ids = sorted(set(int(x) for x in (rows[0] or b'').split()))
            if len(ids) > MAX_UIDS: raise MailError('SNAPSHOT_LIMIT_USE_DATE_FILTER')
            return validity, ids
        return self.run(action)
    def fetch(self, folder, validity, uid, headers=False):
        if type(uid) is not int or uid < 1 or uid > 4294967295: raise MailError('INVALID_UID')
        cap = MAX_HEADER if headers else MAX_BODY
        section = 'HEADER' if headers else ''
        def action(c):
            if self.selected(c, folder) != str(validity): raise MailError('UIDVALIDITY_CHANGED')
            rows = self.ok(c.uid('FETCH', str(uid), f'(UID RFC822.SIZE BODY.PEEK[{section}]<0.{cap + 1}>)'))
            literals = [r for r in rows if isinstance(r, tuple)]
            if not literals: raise MailError('UID_NOT_FOUND')
            meta, raw = literals[0]
            found = re.search(rb'\bUID (\d+)', meta)
            if not found or int(found[1]) != uid: raise MailError('UID_MISMATCH')
            if len(raw) > cap: raise MailError('MESSAGE_TOO_LARGE')
            if not headers:
                size = re.search(rb'RFC822.SIZE (\d+)', meta)
                if not size or int(size[1]) > cap: raise MailError('MESSAGE_TOO_LARGE')
            return raw
        return self.run(action)

def parse(raw, body=True):
    msg = BytesParser(policy=email.policy.default).parsebytes(raw)
    result = {k: str(msg.get(k, '')) for k in ('subject', 'from', 'to', 'date', 'message-id')}
    result['untrusted'] = True
    if body:
        parts = []
        for part in msg.walk():
            if part.get_content_type() in ('text/plain', 'text/html') and part.get_content_disposition() != 'attachment':
                try: content = part.get_content()
                except (LookupError, UnicodeError): content = (part.get_payload(decode=True) or b'').decode('utf-8', 'replace')
                parts.append({'type': part.get_content_type(), 'content': content})
        result['parts'] = parts  # HTML is inert data; never render or follow links here.
    return result

class Service:
    def __init__(self, transport, path):
        self.transport = transport
        self.db = sqlite3.connect(path)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS snapshots(id TEXT PRIMARY KEY, folder TEXT, validity TEXT, uids TEXT);
        CREATE TABLE IF NOT EXISTS checkpoints(folder TEXT PRIMARY KEY, validity TEXT, uid INTEGER);
        CREATE TABLE IF NOT EXISTS pending(folder TEXT PRIMARY KEY, receipt TEXT, validity TEXT, high INTEGER, result TEXT);''')
    @staticmethod
    def limit(n):
        if type(n) is not int or not 1 <= n <= 100: raise MailError('INVALID_LIMIT')
    def search(self, folder='INBOX', since=None, before=None, sender=None, subject=None, limit=50, cursor=None):
        self.limit(limit)
        if cursor:
            try:
                ident, offset = cursor.split(':'); offset = int(offset)
                row = self.db.execute('SELECT folder,validity,uids FROM snapshots WHERE id=?', (ident,)).fetchone()
                if row is None or offset < 0: raise ValueError()
                folder, validity, encoded = row; ids = json.loads(encoded)
                if offset > len(ids): raise ValueError()
            except (ValueError, TypeError): raise MailError('INVALID_CURSOR') from None
            current, _ = self.transport.uids(folder)
            if current != validity: raise MailError('UIDVALIDITY_CHANGED')
        else:
            for val in (sender, subject):
                if val is not None: quoted(val)
            validity, ids = self.transport.uids(folder, since, before)
            if sender is not None or subject is not None:
                matched = []
                for uid in ids:
                    try: h = parse(self.transport.fetch(folder, validity, uid, True), False)
                    except MailError as e:
                        if str(e) == 'UID_NOT_FOUND': continue
                        raise
                    if (sender is None or sender.casefold() in h['from'].casefold()) and (subject is None or subject.casefold() in h['subject'].casefold()): matched.append(uid)
                ids = matched
            ident, offset = uuid.uuid4().hex, 0
            with self.db: self.db.execute('INSERT INTO snapshots VALUES(?,?,?,?)', (ident, folder, validity, json.dumps(ids)))
        end = min(offset + limit, len(ids))
        return {'folder': folder, 'uidvalidity': validity, 'uids': ids[offset:end], 'cursor': f'{ident}:{end}' if end < len(ids) else None, 'total': len(ids)}
    def read(self, folder, uidvalidity, uid):
        return {'folder': folder, 'uidvalidity': uidvalidity, 'uid': uid, **parse(self.transport.fetch(folder, uidvalidity, uid))}
    def check(self, folder='INBOX', limit=50):
        self.limit(limit)
        validity, ids = self.transport.uids(folder)
        row = self.db.execute('SELECT validity,uid FROM checkpoints WHERE folder=?', (folder,)).fetchone()
        pending = self.db.execute('SELECT validity,result FROM pending WHERE folder=?', (folder,)).fetchone()
        if pending and pending[0] == validity: return json.loads(pending[1])
        reset = bool((row and row[0] != validity) or (pending and pending[0] != validity))
        last = row[1] if row and row[0] == validity else 0
        batch = [u for u in ids if u > last][:limit]
        result = {'folder': folder, 'uidvalidity': validity, 'uids': batch, 'reset': reset, 'receipt': uuid.uuid4().hex if batch else None}
        with self.db:
            self.db.execute('DELETE FROM pending WHERE folder=?', (folder,))
            if batch: self.db.execute('INSERT INTO pending VALUES(?,?,?,?,?)', (folder, result['receipt'], validity, max(batch), json.dumps(result)))
            elif reset: self.db.execute('INSERT OR REPLACE INTO checkpoints VALUES(?,?,0)', (folder, validity))
        return result
    def acknowledge(self, folder, receipt):
        # Local delivery bookkeeping only. Never changes remote mail.
        row = self.db.execute('SELECT receipt,validity,high FROM pending WHERE folder=?', (folder,)).fetchone()
        if row is None or row[0] != receipt: raise MailError('INVALID_RECEIPT')
        validity, _ = self.transport.uids(folder)
        if validity != row[1]: raise MailError('UIDVALIDITY_CHANGED')
        with self.db:
            self.db.execute('INSERT OR REPLACE INTO checkpoints VALUES(?,?,?)', (folder, row[1], row[2]))
            self.db.execute('DELETE FROM pending WHERE folder=?', (folder,))
        return {'acknowledged': True}
