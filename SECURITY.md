# Security

The only remote endpoint in the runtime is `imap.qq.com:993`. TLS uses `ssl.create_default_context()` with certificate-chain and hostname checks. Selection uses EXAMINE (`readonly=True`); body retrieval uses UID FETCH with BODY.PEEK. There is no SMTP, STORE, COPY, MOVE, APPEND, EXPUNGE, delete or marking tool, and no runtime configuration tool for host, credentials or TLS.

Inputs use a tool-argument allowlist, bounded UID and page sizes, quoted mailbox names and control-character rejection before encoding. Raw messages are bounded to 2 MiB, headers to 64 KiB and server literals to 2 MiB+1; oversize responses are rejected rather than presented as complete. Socket I/O has a 15-second timeout and one reconnection attempt. The implementation does not yet provide a whole-operation deadline, cancellation, sandboxed MIME parsing or malicious-server fuzz testing.

Emails and HTML are untrusted data. The server does not execute scripts or load external links. Prompt-injection resistance also depends on the client; a boolean marker and Skill instructions alone are not a security sandbox. A notification or financial notice must not trigger payments, cancellation or account changes automatically.

The application logs no mail or credentials. Errors exposed to the client are controlled codes; do not enable IMAP debug logging. Local file permissions restrict newly created state, but state is not encrypted. Keep one process per state directory and protect local access. The MCP server is stdio only and trusts the local client; do not expose it through an unauthenticated proxy.

For security issues, do not include secrets or personal mail in public reports. Use GitHub private vulnerability reporting if enabled, or an available private contact on the maintainer's public profile. Only sanitized issues belong in the public issue tracker.
