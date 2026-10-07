#!/usr/bin/env python3
"""Deterministic MCPB archive using a small explicit Git-tracked allowlist."""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent.parent
DOCS = {'manifest.json', 'LICENSE', 'NOTICE', 'PRIVACY.md', 'SECURITY.md',
        'THIRD_PARTY_NOTICES.md', 'README.md', 'README.zh-CN.md',
        'docs/INSTALL.md', 'scripts/run_mcp.py'}

def package():
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    tracked = set(filter(None, subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')))
    names = DOCS | {n for n in tracked if n.startswith('qqmail_mcp/') and n.endswith('.py')}
    if not names <= tracked: raise ValueError('Bundle members must be reviewed and Git-tracked')
    if not any(n.endswith('/server.py') for n in names): raise ValueError('Missing server')
    out = ROOT / 'dist' / f"qqmail-readonly-mcp-{manifest['version']}-macos.mcpb"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, 'w') as archive:
        for name in sorted(names):
            source = ROOT / name
            if source.is_symlink(): raise ValueError('Symlink release member')
            member = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            member.compress_type = zipfile.ZIP_DEFLATED
            member.external_attr = 0o100644 << 16
            archive.writestr(member, source.read_bytes())
    return out

if __name__ == '__main__':
    artifact = package()
    print(artifact.name + ' SHA256 ' + hashlib.sha256(artifact.read_bytes()).hexdigest())
