# Installation and client setup

## Development, execution and access

The GitHub repository holds source code and a local plugin bundle. IMAP runs on each user's machine. An AI client's MCP configuration launches a child process there; installation does not copy one developer's account or connect a cloud product to that machine.

Requirements: Python 3.13+; outbound TLS access to `imap.qq.com:993`; an IMAP-enabled QQ account and its authorization code. Use your own account. Chromium/Chrome web login does not authenticate IMAP. Enablement and authorization-code creation remain user actions in QQ Mail's own security interface.

## Direct stdio connection (recommended initial route)

Clone the repository, run the offline tests, and obtain the absolute path to your own clone. In macOS Codex, a manually reviewed configuration can look like:

```toml
[mcp_servers.qqmail_readonly]
command = "python3"
args = ["/absolute/path/to/qqmail-readonly-mcp/scripts/run_mcp.py", "--secure"]
startup_timeout_sec = 600
```

Replace the example path. `python3` must resolve to Python 3.13+ in the client's environment; if necessary use that interpreter's absolute path. The long startup timeout allows the user to complete native credential dialogs. The launcher inserts its own source root, so it is independent of the client's working directory.

The first native window asks for an email address or QQ number. The second masks the IMAP authorization code. Credentials remain in process memory until EOF/exit; canceling aborts startup. Once started, tools can read user-authorized folders and date ranges. Approval settings belong to the client.

The macOS secure launcher does not provision persistent access, read Keychain, open ports or install launchd. The default state directory is `~/.local/share/qqmail-readonly-mcp`; `QQMAIL_STATE_DIR` or, for a plugin session, `PLUGIN_DATA` can override it. State files are per-account, based on an account-name digest. Back up state while the process is stopped; deleting it invalidates cursors and restarts incremental discovery.

## Standard server and other systems

`python3 scripts/run_mcp.py` or `python3 -m qqmail_mcp.server` uses `QQMAIL_USER` and `QQMAIL_AUTH_CODE` inherited from the environment. Supply these only through an approved secure credential provider. Do not put actual values into TOML, JSON, shell history or chat. Linux/headless users must supply their own secure provider; this project does not include one.

Optional package installation is `python3 -m pip install .` inside a user-controlled virtual environment; build tooling may be downloaded, though the runtime has no third-party dependencies. The command `qqmail-secure-mcp` starts the native-input session and `qqmail-readonly-mcp` starts the environment-based server. Source launch does not require pip.

## Plugin bundle

- `plugin.json` / `mcp.json`: Agent Plugins portable metadata and stdio server declaration.
- `.codex-plugin/plugin.json` / `.mcp.json`: compatibility fallback.
- `skills/qqmail-subscriptions/SKILL.md`: review workflow and untrusted-data rules.

The stdio declaration uses `${PLUGIN_ROOT}` path expansion and Python on PATH. Install through a client that supports the portable bundle or locally configure the stdio entry above. Native input targets macOS. Plugin manifests and paths are validated locally, but actual Codex/ChatGPT desktop plugin ingestion has not been run; direct stdio subprocess behavior is tested. No personal marketplace configuration is changed by this repository.

GitHub publication is distinct from official directory submission. The current official public MCP submission route requires a remote HTTPS endpoint, or separate local-MCP arrangements with OpenAI. This local stdio repository has not been submitted. Do not deploy it publicly with a shared QQ authorization code. See the [official package guide](https://developers.openai.com/plugins/build/plugins) and [submission guide](https://developers.openai.com/plugins/deploy/submission).

## One-time QQ smoke check

On macOS, explicitly run `python3 -m qqmail_mcp.secure_probe`. This opens local dialogs, checks INBOX over seven calendar days in Asia/Shanghai, reads at most three messages, compares FLAGS and tests pending replay in a temporary database. It writes only counts/status to ignored `live-verification.json`, with no account, UID, header, body or credential. Do not publish that private report.

## Notifications and cloud access

On-demand MCP reads are available while the process runs. Automatic reminders require separately authorized online execution, recovery scans, important-mail rules and a notification destination. IMAP IDLE and notification delivery are not implemented. Secure MCP Tunnel can bridge local MCP but needs extra permissions, runtime credentials and an online machine; it is not configured here. Sites alone cannot open ordinary raw TCP connections to QQ IMAP.
