#!/usr/bin/env python3
"""Offline release checks; not a replacement for official plugin certification."""
import json
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parent.parent

def validate():
    manifest = json.loads((ROOT / 'plugin.json').read_text())
    legacy = json.loads((ROOT / '.codex-plugin/plugin.json').read_text())
    portable_mcp = json.loads((ROOT / 'mcp.json').read_text())
    legacy_mcp = json.loads((ROOT / '.mcp.json').read_text())
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']
    assert ROOT.name == manifest['name'] == legacy['name'] == project['name']
    assert manifest['version'] == legacy['version'] == project['version'] == '0.1.0'
    assert manifest['author']['name'] == legacy['author']['name'] == 'Chuluu'
    assert manifest['license'] == legacy['license'] == project['license'] == 'MIT'
    assert manifest['repository'] == 'https://github.com/ChuluuMGL/qqmail-readonly-mcp'
    assert legacy['skills'] == './skills/' and legacy['mcpServers'] == './.mcp.json'
    assert (ROOT / 'skills/qqmail-subscriptions/SKILL.md').read_text().startswith('---\nname: qqmail-subscriptions\n')
    server = portable_mcp['mcpServers']['qqmail-readonly']
    assert server['type'] == 'stdio'
    assert server['command'] == 'python3'
    assert server['args'] == ['${PLUGIN_ROOT}/scripts/run_mcp.py', '--secure']
    assert {k:v for k,v in server.items() if k != 'type'} == legacy_mcp['mcpServers']['qqmail-readonly']
    assert (ROOT / 'scripts/run_mcp.py').is_file()
    assert project['dependencies'] == []
    for name in ('LICENSE','NOTICE','PRIVACY.md','SECURITY.md','THIRD_PARTY_NOTICES.md','README.md','README.zh-CN.md','TESTING.md','docs/INSTALL.md'):
        assert (ROOT / name).is_file(), name
    for name in ('LICENSE','NOTICE'):
        assert 'Copyright (c) 2026 Chuluu' in (ROOT / name).read_text()
    ignored = (ROOT / '.gitignore').read_text()
    for pattern in ('.state/', '*.sqlite3*', '.env*', 'live-verification.json', 'test-results.txt'):
        assert pattern in ignored
    checked = 0
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if any(p in {'.git','.state','.local','__pycache__','.venv','build','dist'} or p.endswith('.egg-info') for p in relative.parts): continue
        if not path.is_file() or path.name in ('.DS_Store','test-results.txt','live-verification.json') or path.suffix == '.pyc': continue
        text = path.read_text()
        # Assemble patterns so the validator itself doesn't trip them.
        private_roots = ('/' + 'Users/', '/' + 'Library/Frameworks/', '/' + 'Volumes/')
        assert not any(p in text for p in private_roots), f'Private path: {relative}'
        assert not re.search('gh' + '[pousr]_[A-Za-z0-9]{25,}', text), f'Possible token: {relative}'
        assert not re.search('sk' + '-[A-Za-z0-9]{32,}', text), f'Possible token: {relative}'
        checked += 1
    return checked

if __name__ == '__main__':
    print(f'Package consistency and publication checks passed ({validate()} text files).')
