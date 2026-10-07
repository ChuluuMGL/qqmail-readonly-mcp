import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from qqmail_mcp import secure_server
from qqmail_mcp.secure_probe import Cancelled, credentials

ROOT = Path(__file__).resolve().parent.parent

class ReleaseTests(unittest.TestCase):
    def test_relocated_source_launcher_no_credentials(self):
        env = dict(os.environ)
        env.pop('QQMAIL_USER', None); env.pop('QQMAIL_AUTH_CODE', None)
        request = json.dumps({'jsonrpc':'2.0','id':1,'method':'tools/list'}) + '\n'
        with tempfile.TemporaryDirectory() as cwd:
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/run_mcp.py')], input=request, capture_output=True, text=True, cwd=cwd, env=env, timeout=5)
        self.assertEqual(result.returncode, 0); self.assertEqual(result.stderr, '')
        self.assertEqual(len(json.loads(result.stdout)['result']['tools']), 5)
    def test_session_prompt_does_not_claim_probe_scope(self):
        with patch('qqmail_mcp.secure_probe.dialog', side_effect=['12345678','fake-code']) as prompts:
            self.assertEqual(credentials(session=True), ('12345678@qq.com','fake-code'))
            self.assertIn('只读 MCP 会话', prompts.call_args.args[0])
            self.assertNotIn('最多 3 封', prompts.call_args.args[0])
            self.assertIn('with hidden answer', prompts.call_args.args[0])
    def test_secure_session_retains_only_in_memory(self):
        with tempfile.TemporaryDirectory() as state:
            captured = []
            def serve(service):
                captured.append(service.transport)
                self.assertEqual(service.transport.password, 'fake-code')
                service.db.close()
            output = io.StringIO()
            with patch.object(secure_server.sys, 'platform','darwin'), patch.object(secure_server,'credentials',return_value=('fake@qq.com','fake-code')), patch.object(secure_server,'serve',side_effect=serve), patch.dict(os.environ, {'QQMAIL_STATE_DIR':state}), contextlib.redirect_stdout(output):
                self.assertEqual(secure_server.main(),0)
            self.assertEqual(captured[0].password,'')
            self.assertEqual(output.getvalue(),'')
            for path in Path(state).iterdir():
                self.assertNotIn(b'fake-code',path.read_bytes())
                self.assertNotIn(b'fake@qq.com',path.read_bytes())
    def test_cancelled_session_has_no_secret_output(self):
        output = io.StringIO()
        with patch.object(secure_server.sys,'platform','darwin'), patch.object(secure_server,'credentials',side_effect=Cancelled()), contextlib.redirect_stderr(output):
            self.assertEqual(secure_server.main(),1)
        self.assertEqual(output.getvalue(),'Credential input cancelled.\n')
    def test_non_macos_does_not_request_credentials(self):
        with patch.object(secure_server.sys,'platform','linux'), patch.object(secure_server,'credentials') as prompt, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(secure_server.main(),1)
            prompt.assert_not_called()
