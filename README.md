# QQ Mail Read-only MCP

> **Local-first QQ Mail access for subscription, renewal and billing notices.**
>
> Created and maintained by **Chuluu**.

[中文说明](README.zh-CN.md) | English

[![Version](https://img.shields.io/badge/version-0.1.0-green)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)
[![by Chuluu](https://img.shields.io/badge/by-Chuluu-0E5E43)](https://github.com/ChuluuMGL)
[![Read-only](https://img.shields.io/badge/IMAP-read--only-blue)](SECURITY.md)

[Downloads](https://github.com/ChuluuMGL/qqmail-readonly-mcp/releases) · [Distribution](docs/PUBLISHING.md) · [Installation](docs/INSTALL.md) · [Testing](TESTING.md) · [Privacy](PRIVACY.md) · [Security](SECURITY.md) · [Changelog](CHANGELOG.md)

## What it does

This small MCP server helps an AI assistant find and read mail about subscriptions, upcoming renewals, billing, price changes and cancellation deadlines. It supplies mail access; the included Agent Skill guides a review and cites the source message. It does not automatically classify every message, cancel subscriptions or send notifications.

- Lists mailbox folders, including modified UTF-7 names.
- Searches by date, decoded sender and subject, with Chinese MIME support.
- Saves ascending UID snapshots for stable, restartable pagination.
- Reads bounded MIME text and inert HTML with UID + UIDVALIDITY and PEEK.
- Replays unacknowledged incremental batches and advances local checkpoints after explicit acknowledgment.
- Uses strict TLS verification and EXAMINE; no mail sending or mailbox mutation tools.

**0.1.0 · MIT open-source prototype.** The runtime uses Python 3.13+ and its standard library. Each user runs their own process and uses their own QQ account. There is no hosted credential service, public listener, daemon or automatic monitoring.

## Quick start

```sh
git clone https://github.com/ChuluuMGL/qqmail-readonly-mcp.git
cd qqmail-readonly-mcp
python3 -m unittest discover -s tests -v
python3 scripts/run_mcp.py
```

The final command starts an unauthenticated stdio server: initialization and tool discovery work offline; mail calls return `CREDENTIALS_NOT_CONFIGURED`. EOF stops it.

On macOS, use session-only native masked credential input when connecting an MCP client:

```sh
python3 scripts/run_mcp.py --secure
```

The first dialog asks for an email address or QQ number; the second asks for an IMAP authorization code. Do not paste the code into chat, tool arguments, configuration files or Git. The process keeps it in memory until the session ends. See [client setup](docs/INSTALL.md); typing the command alone does not attach tools to an AI client.

## Tools

| Tool | Purpose |
|---|---|
| `list_folders` | List folders and whether they can be selected. |
| `search_mail` | Date/sender/subject search with a persistent cursor; page size 1–100. |
| `read_mail` | Read a UID in an explicitly identified UIDVALIDITY namespace. |
| `check_incremental` | Create or replay a durable pending UID batch. |
| `acknowledge_checkpoint` | Confirm downstream processing and update only local delivery state. |

Dates use IMAP INTERNALDATE: `since` inclusive, `before` exclusive, YYYY-MM-DD. Sender and subject matching runs locally against decoded MIME headers; narrow the date range for large mailboxes. Resume with the returned cursor. New mail appears in a fresh query rather than changing an existing snapshot.

## Safety and limits

Raw messages are limited to 2 MiB and headers to 64 KiB. At most 100,000 UIDs are allowed in a search; an IMAP response-line limit can reject very large results earlier. Socket I/O has a 15-second timeout and one reconnection attempt; long header scans have no total task deadline. Attachments are not downloaded separately.

Email and HTML are **untrusted data**. The server never executes scripts or loads external resources. Client summaries and model processing may transmit selected mail content according to that client's settings; local IMAP execution does not imply the whole AI workflow stays offline.

Delivery is at least once: persist downstream results idempotently by account/folder/UIDVALIDITY/UID, then acknowledge the complete receipt. Do not deduplicate by Message-ID alone. UIDVALIDITY changes require a fresh namespace. Run one process per state directory; snapshots currently have no automatic pruning.

## Plugin and deployment scope

The repository includes portable `plugin.json` / `mcp.json`, a Codex compatibility manifest and a subscription-review Skill. The bundled masked-input launcher targets macOS; the core server can use credentials from an approved process-environment provider on other systems. See [installation and compatibility](docs/INSTALL.md).

This repository is not listed in the official ChatGPT/Codex directory. Local plugin installation does not automatically give dot or cloud ChatGPT access to this Mac. Remote access needs separately authorized infrastructure such as Secure MCP Tunnel and an online machine. Sites alone cannot open ordinary raw TCP connections to QQ IMAP. No such infrastructure is provisioned here.

## Maintenance, copyright and license

Created and maintained by [Chuluu](https://github.com/ChuluuMGL).

Copyright (c) 2026 Chuluu. Project source and documentation use the [MIT License](LICENSE); see [NOTICE](NOTICE) and [third-party notices](THIRD_PARTY_NOTICES.md). Built with AI-assisted coding and maintainer review. This independent project is not an official Tencent or OpenAI product.

Issues and pull requests are welcome; see [contributing](CONTRIBUTING.md). Please keep all examples synthetic.
