# Contributing

Use synthetic mail fixtures and keep the project small and read-only. Run `python3 -m unittest discover -s tests -v`, `python3 -m compileall -q qqmail_mcp scripts tests`, `python3 scripts/validate_package.py`, and `git diff --check` before submitting.

Do not make tests contact QQ, SMTP or other real mailbox servers. The core offline suite blocks socket connection creation. New tests must also run offline and must not use machine-specific accounts or credentials.

Explain the problem, behavior change and relevant validation in each pull request. Mailbox mutation, shared credential storage, automatic background services and public hosting are outside the current release scope.

Contributions are accepted under the project's MIT license. Include required notices for any third-party material. Never commit credentials, state databases, private machine paths, genuine mail or live-check reports.
