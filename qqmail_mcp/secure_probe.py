"""One-shot local QQ smoke test. Credentials stay inside this process, never stdout."""
import datetime as dt
import imaplib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from zoneinfo import ZoneInfo
from .core import Imap, MailError, Service
from .server import dispatch

REPORT = Path(__file__).resolve().parent.parent / 'live-verification.json'

class Cancelled(Exception):
    pass

def dialog(script):
    completed = subprocess.run(['/usr/bin/osascript', '-e', script], capture_output=True, text=True, timeout=600)
    if completed.returncode: raise Cancelled()
    return completed.stdout.rstrip('\r\n')

def normalize_account(user):
    user = user.strip()
    if re.fullmatch(r'[0-9]{5,12}', user): user += '@qq.com'
    if not re.fullmatch(r'[A-Za-z0-9._+\-]+@(qq\.com|vip\.qq\.com|foxmail\.com)', user, re.I):
        raise MailError('INVALID_QQ_ADDRESS')
    return user

def credentials(session=False):
    user = dialog('''tell application "System Events"
activate
set response to display dialog "第 1 步：只填写 QQ 邮箱地址（例如 12345678@qq.com），或你的 QQ 号码。这里不要填写授权码。下一步才会要求授权码。" default answer "" with title "第 1 步：邮箱地址（不是授权码）" buttons {"取消", "继续"} default button "继续" cancel button "取消"
return text returned of response
end tell''').strip()
    user = normalize_account(user)
    secret_prompt = ('只读 MCP 会话：请输入 QQ 邮箱 IMAP 授权码。授权码只留在当前进程内存；邮件范围由随后获批准的工具调用确定。取消可退出。' if session else '第 2 步：现在填写 QQ 邮箱 IMAP 授权码（不是邮箱地址，也不是网页登录密码）。点击联调只读检查收件箱最近 7 天、最多 3 封，授权码不保存。')
    password = dialog('''tell application "System Events"
activate
set response to display dialog "SECRET_PROMPT" default answer "" with hidden answer with title "第 2 步：授权码（遮蔽输入）" buttons {"取消", "联调"} default button "联调" cancel button "取消"
return text returned of response
end tell'''.replace('SECRET_PROMPT', secret_prompt)).strip()
    if not password: raise Cancelled()
    return user, password

def tool(service, name, args=None):
    response = dispatch(service, {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': name, 'arguments': args or {}}})['result']
    if response['isError']: raise MailError(response['content'][0]['text'])
    return json.loads(response['content'][0]['text'])

def flags(imap, validity, uid):
    def action(client):
        if imap.selected(client, 'INBOX') != validity: raise MailError('UIDVALIDITY_CHANGED')
        rows = imap.ok(client.uid('FETCH', str(uid), '(UID FLAGS)'))
        for row in rows:
            if isinstance(row, bytes):
                found = re.search(rb'\bUID (\d+)\b', row)
                if found and int(found[1]) == uid: return sorted(imaplib.ParseFlags(row))
        raise MailError('UID_NOT_FOUND')
    return imap.run(action)

def probe(service):
    today = dt.datetime.now(ZoneInfo('Asia/Shanghai')).date()
    since, before = (today - dt.timedelta(days=6)).isoformat(), (today + dt.timedelta(days=1)).isoformat()
    summary = {'status': 'running', 'since': since, 'before': before, 'checks': {}, 'mail_bodies_saved': False, 'credentials_saved': False, 'background_service_installed': False}
    checks = summary['checks']
    folders = tool(service, 'list_folders')
    checks['tls_login_list'] = 'passed'
    summary['folder_count'] = len(folders)
    page = tool(service, 'search_mail', {'folder': 'INBOX', 'since': since, 'before': before, 'limit': 2})
    checks['readonly_date_search'] = 'passed'
    summary['messages_in_date_range'] = page['total']
    if page['cursor']:
        second = tool(service, 'search_mail', {'cursor': page['cursor'], 'limit': 2})
        if set(page['uids']) & set(second['uids']): raise MailError('PAGING_DUPLICATE')
        checks['second_page'] = 'passed'
    else: checks['second_page'] = 'not_run_insufficient_messages'
    validity, ids = service.transport.uids('INBOX', since, before)
    if validity != page['uidvalidity']: raise MailError('UIDVALIDITY_CHANGED')
    read_count, skipped, unmodified = 0, 0, True
    for uid in ids[-3:]:
        try:
            prior = flags(service.transport, validity, uid)
            result = tool(service, 'read_mail', {'folder': 'INBOX', 'uidvalidity': validity, 'uid': uid})
            after = flags(service.transport, validity, uid)
            if not result.get('untrusted'): raise MailError('MISSING_UNTRUSTED_MARKER')
            read_count += 1
            unmodified = unmodified and prior == after
            del result
        except MailError as exc:
            if str(exc) in ('MESSAGE_TOO_LARGE', 'UID_NOT_FOUND'):
                skipped += 1
            else: raise
    summary['bodies_read_count'] = read_count
    summary['skipped_large_or_deleted_count'] = skipped
    checks['peek_mime_read'] = 'passed' if read_count else 'not_run_no_readable_messages'
    checks['flags_unchanged'] = ('passed' if unmodified else 'failed') if read_count else 'not_run_no_readable_messages'
    if not unmodified: raise MailError('FLAGS_CHANGED_DURING_CHECK')
    # Local scratch checkpoint only; do not consume a production delivery checkpoint.
    batch = tool(service, 'check_incremental', {'limit': 2})
    if batch['receipt']:
        replay = tool(service, 'check_incremental', {'limit': 2})
        if batch != replay: raise MailError('PENDING_REPLAY_MISMATCH')
        checks['incremental_pending_replay'] = 'passed'
    else: checks['incremental_pending_replay'] = 'not_run_empty_mailbox'
    summary['status'] = 'passed'
    return summary

def main():
    os.umask(0o077)
    transport = None
    summary = {'status': 'not_started'}
    try:
        user, password = credentials()
        transport = Imap(user, password)
        del user, password
        with tempfile.TemporaryDirectory(prefix='qqmail-live-') as root:
            service = Service(transport, str(Path(root) / 'scratch.sqlite3'))
            try: summary = probe(service)
            finally: service.db.close()
    except Cancelled:
        summary = {'status': 'cancelled', 'credentials_saved': False}
    except MailError as exc:
        summary = {'status': 'failed', 'error_code': str(exc), 'credentials_saved': False, 'mail_bodies_saved': False}
    except Exception:
        summary = {'status': 'failed', 'error_code': 'LIVE_PROBE_FAILED', 'credentials_saved': False, 'mail_bodies_saved': False}
    finally:
        if transport:
            transport.password = ''
            transport.drop()
    summary['checked_at'] = dt.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
    REPORT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary, ensure_ascii=False))

if __name__ == '__main__': main()
