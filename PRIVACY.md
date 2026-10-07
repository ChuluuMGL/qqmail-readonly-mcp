# Privacy

This is user-operated local software, not a hosted mail service. Chuluu does not receive users' authorization codes or messages through a project backend. The runtime has no telemetry, analytics or hosted credential database.

The process sends each user's account and authorization code to QQ's fixed IMAP host over certificate-verified TLS. It reads folders and selected mail according to client tool calls. Native macOS input keeps credentials in process memory and does not persist them. Environment-based input relies on the user's credential provider and operating-system security. Python strings are not guaranteed to be securely zeroized.

Selected headers and text/HTML bodies are returned to the user's MCP client. That client may send them to a model provider under its own settings and policies. Users should review the client's data controls and minimize the mail range they expose. This software cannot guarantee the client's downstream retention or use.

Local SQLite state contains account-name digests in filenames and folder/UIDVALIDITY/UID/receipt/snapshot metadata. It does not contain mail bodies, subjects, senders or authorization codes. State has no automatic expiry; the user controls retention and can stop the process and remove the state directory. Doing so resets delivery progress. A one-shot smoke-check report contains counts, dates and check status only and is ignored by Git.

Public GitHub issues and contributions are visible to others. Never submit credentials, real mail, SQLite state or smoke reports. Use synthetic examples. GitHub and QQ operate under their own terms and policies.
