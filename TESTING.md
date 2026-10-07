# Testing

## Commands

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q qqmail_mcp scripts tests
python3 scripts/validate_package.py
git diff --check
```

Core offline tests cover Chinese MIME, inert HTML, date command generation, decoded sender/subject filters, UID snapshots across arrival/deletion/restart, UIDVALIDITY changes, incremental replay/deduplication, acknowledgment transaction rollback, invalid UIDs, timeout/abort reconnection, response limits, strict TLS settings, EXAMINE/PEEK, argument boundaries, redacted errors, state metadata and stdio discovery.

Secure-input tests use fake values and mocked dialogs, including masked input, cancellation, address validation and QQ-number normalization. Session/launcher tests verify credential-memory cleanup, no credential output, relocation and no-credential discovery without network.

The core suite blocks socket connection creation. GitHub Actions runs only offline checks on Linux/macOS and Python 3.13/3.14. Do not add mailbox credentials to CI.

## Actual verification

Maintainer's local Python 3.13 run: **38 tests passed, 0 failed**; compile checks and the offline publication validator passed. The portable plugin and MCP manifests also passed validation against their official Agent Plugins 1.0.0 JSON schemas. A wheel was built and installed offline into a fresh local virtual environment; its installed stdio entrypoint successfully discovered all five tools from another working directory. These checks do not guarantee every client/platform. The maintainer's separately authorized real QQ smoke check passed TLS/login/LIST, date search, a second page, bounded MIME reads, FLAGS before/after comparison and temporary-state pending replay. Private account, message metadata, counts and reports are deliberately not distributed.

The versioned ZIP was extracted to a fresh directory; package validation and relocated stdio discovery passed. ZIP contents were checked for excluded state, private reports and Git internals. Release assets include SHA-256 checksums.

Public distribution changes are tested offline; the real-mail smoke result applies to the underlying IMAP core, not a complete third-party installation acceptance test.

## Not run or not implemented

- Actual desktop plugin install/ingestion and official full MCP conformance suite.
- Independent-user QQ acceptance, real UIDVALIDITY changes, rate limits and live disconnect recovery.
- Linux/headless secure credential provider, full-operation cancellation/deadline and snapshot pruning.
- Official directory submission, Tunnel, automatic notifications or persistent service.
- The plugin-creator bundled scaffold/validator scripts were unavailable in the provided skill resource; package structure is assembled from the official format and checked by this repository's validator. This does not claim official certification.

MCPB 0.3 manifest validation passed using the specification repository's `@anthropic-ai/mcpb@2.1.2` CLI. Two additional offline checks cover reproducible archive bytes and extracted-bundle initialization/tool discovery/read refusal without credentials. The bundle allowlist excludes tests, Git metadata, caches and state. Native macOS prompts and actual Smithery/Glama upload are not exercised by these tests.
