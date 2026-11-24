# Contributing

Keep `main` stable. Use a short-lived branch for a coherent change. Review the diff and run relevant checks before staging and committing. Use Conventional Commits and group related implementation, migrations and tests when they represent one independently verifiable change. Use the configured Git identity. Preserve licence attribution.

Push completed branches, open concise pull requests that describe the actual change and verification, and merge only after required checks pass. Continue through tasks already approved for implementation. Architecture approval precedes feature work. Get approval for significant architecture changes, destructive actions, paid services, visibility changes and public production deployment. Keep the repository private until publication is explicitly approved. Never force-push `main` or rewrite existing history without approval.

Run `python scripts/check_docs.py` for planning changes. Follow the [testing plan](docs/testing.md) for implementation. Record decisions in the relevant documentation and completed changes in the changelog where useful. Keep secrets, personal data, local artifacts and private working notes out of Git.
