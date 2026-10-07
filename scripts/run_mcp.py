#!/usr/bin/env python3
"""Relocatable source launcher. --secure uses local native input on macOS."""
from pathlib import Path
import sys

if sys.version_info < (3, 13):
    print('Python 3.13 or newer is required.', file=sys.stderr)
    raise SystemExit(1)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if sys.argv[1:] == ['--secure']:
    from qqmail_mcp.secure_server import main
elif not sys.argv[1:]:
    from qqmail_mcp.server import main
else:
    print('Usage: run_mcp.py [--secure]', file=sys.stderr)
    raise SystemExit(1)
raise SystemExit(main())
