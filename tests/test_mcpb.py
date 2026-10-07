"""Offline exercise of the real packaged artifact, without credentials or mail."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('package_mcpb', ROOT / 'scripts/package_mcpb.py')
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)

class McpbTests(unittest.TestCase):
    def test_bundle_relocates_and_discovers_without_credentials(self):
        artifact = packager.package()
        manifest = json.loads((ROOT / 'manifest.json').read_text())
        env = {k: v for k, v in os.environ.items() if k not in {'QQMAIL_USER', 'QQMAIL_AUTH_CODE'}}
        with tempfile.TemporaryDirectory() as tmp:
            extracted = Path(tmp) / 'installed'
            extracted.mkdir()
            with zipfile.ZipFile(artifact) as archive:
                names = set(archive.namelist())
                self.assertTrue({'manifest.json', 'LICENSE', 'PRIVACY.md'} <= names)
                self.assertFalse(any(n.startswith(('.git/', '.local/', '.state/', 'tests/')) for n in names))
                self.assertTrue(all(n in packager.DOCS or n.startswith('qqmail_mcp/') and n.endswith('.py') for n in names))
                archive.extractall(extracted)
            entry = extracted / manifest['server']['entry_point']
            requests = '\n'.join(json.dumps(r) for r in [
                {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-06-18'}},
                {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'},
                {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {'name': 'list_folders', 'arguments': {}}}
            ]) + '\n'
            # Offline discovery uses the launcher's nonsecure mode; no native input.
            response = subprocess.run([sys.executable, str(entry)], input=requests, text=True, capture_output=True, env=env, cwd=tmp, timeout=5)
            self.assertEqual(response.returncode, 0)
            self.assertEqual(response.stderr, '')
            replies = [json.loads(line)['result'] for line in response.stdout.splitlines()]
            self.assertEqual(replies[0]['protocolVersion'], '2025-06-18')
            self.assertEqual({t['name'] for t in replies[1]['tools']}, {t['name'] for t in manifest['tools']})
            self.assertTrue(replies[2]['isError'])
            self.assertEqual(replies[2]['content'][0]['text'], 'CREDENTIALS_NOT_CONFIGURED')
            self.assertFalse(list(extracted.rglob('*.sqlite3')))

    def test_bundle_is_reproducible(self):
        first = packager.package().read_bytes()
        self.assertEqual(first, packager.package().read_bytes())
