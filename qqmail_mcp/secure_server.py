"""Session-only macOS credential prompt, then stdio. No daemon or credential storage."""
import hashlib
import os
from pathlib import Path
import sys
from .core import Imap, Service
from .secure_probe import Cancelled, credentials
from .server import serve

def main():
    if sys.platform != 'darwin':
        print('Secure native input requires macOS. Use a trusted credential provider with the standard server.', file=sys.stderr)
        return 1
    os.umask(0o077)
    transport = None
    try:
        user, password = credentials(session=True)
        root = Path(os.environ.get('QQMAIL_STATE_DIR', os.environ.get('PLUGIN_DATA', str(Path.home() / '.local' / 'share' / 'qqmail-readonly-mcp'))))
        root.mkdir(mode=0o700, parents=True, exist_ok=True)
        account = hashlib.sha256(user.strip().casefold().encode()).hexdigest()[:24]
        transport = Imap(user, password)
        del user, password
        service = Service(transport, str(root / f'delivery-{account}.sqlite3'))
        serve(service)
        return 0
    except Cancelled:
        print('Credential input cancelled.', file=sys.stderr)
        return 1
    except Exception:
        print('Secure session failed. No credential or mail content is logged.', file=sys.stderr)
        return 1
    finally:
        if transport:
            transport.password = ''
            transport.drop()

if __name__ == '__main__': raise SystemExit(main())
