#!/usr/bin/env python3
"""Create a deterministic source/plugin ZIP from reviewed Git-tracked files only."""
import hashlib
from pathlib import Path
import subprocess
import tomllib
import zipfile
from validate_package import validate

ROOT = Path(__file__).resolve().parent.parent

def package():
    validate()
    version = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']['version']
    names = subprocess.check_output(['git','ls-files','-z'], cwd=ROOT).decode().split('\0')
    out = ROOT / 'dist' / f'qqmail-readonly-mcp-{version}-plugin.zip'
    out.parent.mkdir(exist_ok=True)
    forbidden = {'.git','.state','.local','__pycache__','.venv','build','dist'}
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(filter(None, names)):
            path = Path(name)
            if forbidden.intersection(path.parts) or path.name in {'live-verification.json','test-results.txt'} or '.sqlite3' in name or path.name.startswith('.env'):
                raise ValueError('Forbidden release member')
            source = ROOT / path
            if source.is_symlink(): raise ValueError('Symlink release member')
            member = zipfile.ZipInfo(name, date_time=(1980,1,1,0,0,0))
            member.compress_type = zipfile.ZIP_DEFLATED
            member.external_attr = 0o100644 << 16
            archive.writestr(member, source.read_bytes())
    return out

if __name__ == '__main__':
    artifact = package()
    print(artifact.name + ' SHA256 ' + hashlib.sha256(artifact.read_bytes()).hexdigest())
