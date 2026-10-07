import subprocess
import unittest
from unittest.mock import patch
from qqmail_mcp.secure_probe import Cancelled, credentials, dialog, normalize_account
from qqmail_mcp.core import MailError

class SecureInputTests(unittest.TestCase):
    def test_secret_never_in_command_arguments(self):
        with patch('qqmail_mcp.secure_probe.subprocess.run', return_value=subprocess.CompletedProcess([], 0, 'secret-code\n', '')) as run:
            self.assertEqual(dialog('display dialog "fixed prompt"'), 'secret-code')
            self.assertNotIn('secret-code', str(run.call_args.args))
            self.assertTrue(run.call_args.kwargs['capture_output'])
    def test_qq_number_account(self):
        self.assertEqual(normalize_account(' 12345678 '), '12345678@qq.com')
        self.assertEqual(normalize_account('test@qq.com'), 'test@qq.com')
        with self.assertRaises(MailError): normalize_account('not-an-account')
    def test_cancel(self):
        with patch('qqmail_mcp.secure_probe.subprocess.run', return_value=subprocess.CompletedProcess([], 1, '', 'user cancelled')):
            with self.assertRaises(Cancelled): dialog('fixed')
    def test_invalid_account_before_secret(self):
        with patch('qqmail_mcp.secure_probe.dialog', return_value='bad@example.test') as prompts:
            with self.assertRaisesRegex(MailError, 'INVALID_QQ_ADDRESS'): credentials()
            self.assertEqual(prompts.call_count, 1)
    def test_masked_password_dialog(self):
        with patch('qqmail_mcp.secure_probe.dialog', side_effect=['test@qq.com', 'fake-code']) as prompts:
            self.assertEqual(credentials(), ('test@qq.com','fake-code'))
            self.assertIn('with hidden answer', prompts.call_args.args[0])
