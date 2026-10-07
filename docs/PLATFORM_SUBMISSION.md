# Ready-to-submit directory information

- Name: QQ Mail Read-only MCP
- Maintainer: Chuluu / [ChuluuMGL](https://github.com/ChuluuMGL)
- Repository: https://github.com/ChuluuMGL/qqmail-readonly-mcp
- License: MIT; Copyright (c) 2026 Chuluu
- Release: https://github.com/ChuluuMGL/qqmail-readonly-mcp/releases/tag/v0.1.0
- Summary: Review QQ Mail subscription, renewal and billing notices locally on macOS. Strict TLS and PEEK reads; no sending or mailbox changes.
- Transport: local stdio. No public endpoint.
- Bundle: `qqmail-readonly-mcp-0.1.0-macos.mcpb`
- Requirements: macOS, existing Python 3.13+, user's own QQ IMAP access.
- Credentials: session-only native macOS dialogs. Marketplace has no mail password fields.
- Privacy: https://github.com/ChuluuMGL/qqmail-readonly-mcp/blob/main/PRIVACY.md
- Installation: https://github.com/ChuluuMGL/qqmail-readonly-mcp/blob/main/docs/INSTALL.md
- Status: public prototype, on-demand reads; no automatic monitoring. Independent project, not an official Tencent/OpenAI integration.

## Submission status (2026-10-07)

- GitHub: public source and prerelease assets published.
- MCP.so: [request #4851](https://github.com/chatmcp/mcpso/issues/4851) is open with no review response at last check. Do not submit a duplicate or claim acceptance.
- Smithery: MCPB prepared; upload requires the maintainer to authenticate and choose an owned namespace. No authenticated submission performed yet. Use [publish instructions](https://smithery.ai/docs/build/publish), select local MCPB, upload the bundle above. Do not choose shared hosted mail access.
- Glama: public repository submission requires login through [Add Server](https://glama.ai/mcp/servers). No authenticated submission performed yet. Submit only the public repository; no mail credentials or private repository access.
- Official OpenAI directory: not submitted. The current local bundle does not fulfill the normal public HTTPS endpoint route.

Current execution tools do not include browser controls or authenticated Smithery/Glama connectors. Platform login cannot be reused from GitHub CLI authentication. Do not paste platform tokens or mail authorization codes into chat.

## Future official hosted version

Before deployment, review a separate design: Streamable HTTP over TLS with verified domain; per-user authentication and revocation; isolated account/checkpoint state; encryption and access controls for credentials; credential enrollment in a secure interface; bounded reads; privacy and retention policies; synthetic review accounts and operational monitoring. Retain no mail body by default. QQ IMAP still requires network TCP access to port 993; a static site or Sites hosting alone is insufficient.

Do not expose a server bound to the developer's own mailbox, convert native prompts into public credential tools, deploy a daemon, or incur hosting fees as part of local bundle publication. Hosting and real multi-user verification require a separate reviewed deployment decision.
