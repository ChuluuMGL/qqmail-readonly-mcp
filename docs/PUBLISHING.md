# Distribution and platform submission

## Available distribution

The project is publicly available at [GitHub](https://github.com/ChuluuMGL/qqmail-readonly-mcp). Versioned plugin-source ZIPs and Python wheels are distributed through [GitHub Releases](https://github.com/ChuluuMGL/qqmail-readonly-mcp/releases). Each release includes SHA256SUMS. The ZIP is a portable source/plugin bundle, not a DXT/MCPB installer and not an automatic background-service installation.

Build reviewed source artifacts locally:

```sh
python3 scripts/validate_package.py
python3 scripts/package_plugin.py
python3 -m build --wheel --no-isolation
```

The ZIP packager uses reviewed Git-tracked files only, normalizes ZIP timestamps and refuses state, environment files and symlinks. Do not add private files to Git even if a packager would reject them. Wheel building requires the standard build tooling; runtime dependency count remains zero.

## Official ChatGPT/Codex directory

The current public MCP route requires a remote HTTPS endpoint, domain verification, a verified developer identity and review material. Local MCP exceptions require arrangements with OpenAI. This local stdio prototype is not submitted or listed. Source release does not satisfy endpoint eligibility. See the [official package guide](https://developers.openai.com/plugins/build/plugins) and [submission guide](https://developers.openai.com/plugins/deploy/submission).

Do not convert a user's local authorization code into a shared public mail service. A future hosted product needs separately designed per-user authentication and data isolation and is outside this release.

## Third-party discovery

- **Glama:** a public GitHub repository can be submitted through its Add Server workflow; the current form requires a signed-in account. Listing and ownership claims are separate from running mail tools. Do not authorize access to private repositories or mail as a condition of indexing this public code.
- **MCP.so:** its current web submission offers a paid listing. No payment is authorized or required by this project. Its public FAQ also documents GitHub Issue submission; a request is not acceptance or a live listing. See the [directory](https://mcp.so/) for its current workflow.
- **Official MCP Registry:** stores metadata, not your source artifacts. Publishing needs a supported underlying package distribution and publisher authentication; GitHub source alone is not a registered server. This project has not been published to PyPI or that registry. See the [registry quickstart](https://modelcontextprotocol.io/registry/quickstart).

Never claim a platform listing, verification badge or review acceptance before the platform confirms it. Platform submissions contain only project name, public repository, maintainer identity, MIT license, transport, capabilities and installation links. Each user supplies their own credentials locally.

## Local MCPB distribution

An additional macOS MCPB 0.3 bundle is prepared with `manifest.json` and `scripts/package_mcpb.py`. It requires an existing Python 3.13+ runtime and session-only native credential input. It is distinct from the portable Agent Plugins ZIP. [Smithery supports local MCPB uploads](https://smithery.ai/docs/build/publish); publication needs the maintainer's authenticated namespace. See [submission information and status](PLATFORM_SUBMISSION.md). Credentials and runtime state are excluded using an explicit allowlist; no Python runtime or persistent credential provider is bundled.
