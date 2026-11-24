# Testing strategy

Use pytest/pytest-django for rules, PostgreSQL constraints, migrations and transaction races. Use Factory Boy where fixtures recur and Hypothesis for high-risk invariants. Contract-test recorded permitted provider fixtures alongside credentialed, bounded live smoke tests before releasing adapters. Test provider failure and fallback. Use Playwright/axe for auth, onboarding, metadata save, one-user recommendations, all 20 pages, publishing, follows/blocks, media, import/export/delete and keyboard workflows. Run Ruff, dependency audit and CI on schema changes.

Test cross-user and indirect leaks, block/visibility transitions, private media, sessions, unsafe imports/uploads, scoped admin and optional inference. Validate recommendation quality, provenance, diversity, feedback and sparse/multilingual profiles. Test provider migration, restore and rollback drills.

Measure on target staging with a documented dataset and workload. Initial acceptance targets are p75 LCP ≤2.5s, INP ≤200ms, CLS ≤0.1 and indexed search p95 ≤500ms; compare warm and cold runs separately and report mix. Proposed bounded recommendation API baseline p95 ≤750ms warm on a capped candidate set; record worker backlog and refresh latency separately. Record query counts and missing indexes. Backup daily; drill RPO ≤24h and RTO ≤4h. Record evidence and gaps before release.
