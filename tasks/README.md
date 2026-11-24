# Dependency-ordered implementation backlog

**Architecture approved November 24, 2026.** Execution is authorized across the backlog. Complete each dependency and record verification evidence before marking a task done. Tasks without a status below are pending.

| Task | Status | Evidence or next action |
|---|---|---|
| LOK-001 | Complete | Product acceptance matrix and task index cover the brief. `python scripts/check_docs.py` checks all task links, ordering and release dependencies. |
| LOK-002 | Complete | Repository owner approved the proposed architecture and authorized execution of the backlog in dependency order. |
| LOK-003 | Complete | The database design records lock order, lossless merge rules, owner-scoped references and retry-safe erasure. Implementation and regression tests are in the dependent tasks. |
| LOK-004 | Complete | Initial field rules, rights holds and enrollment gates are recorded in the integration plan. Provider enablement and live verification remain LOK-014 and LOK-016 checks. |
| LOK-005 | Complete | Verified uv 0.13.9, CPython 3.13.18, locked dependency sync and a SCRAM-authenticated connection to PostgreSQL 17.12 on Windows. |
| LOK-006 | Complete | Django system checks and two configuration/database tests passed locally and in Linux CI with PostgreSQL 17. |
| LOK-007 | Complete | Landing and 404 integration tests passed. Edge verified keyboard navigation and reflow at 320px and 1280px with JavaScript disabled. |
| LOK-008 | Complete | The initial custom user migration applied on PostgreSQL 17. Tests cover normalized identity, duplicate rejection and Argon2 verification. |
| LOK-009 | Complete | PostgreSQL tests cover competing claims, reclaimed leases, stale completion, retry exhaustion, deduplication and owner-only cancellation. A command test exercises handler dispatch. |
| LOK-010 | Complete | Account verification, recovery, replay, expiry, CSRF, throttling and old-session revocation passed against PostgreSQL and Django’s test mail backend. Production email remains a deployment gate. |
| LOK-011 | Complete | Tests cover 20 private-by-default slots, public preview, composed visibility, owner editing and position changes without affecting another user. |
| LOK-012 | Complete | Tests cover typed canonical items, Unicode aliases, public-only credits, pagination and the database prohibition on publishing owner-only records. |
| LOK-013 | Complete | Verified exact identifier resolution, ISBN conversion and checksum, conflicting bindings, and revision-linked source credits. |
| LOK-014 | Complete | Live book, film and TV reads passed with Open Library and Wikidata. Contract tests cover typed responses, rate limits and idempotent imports. |
| LOK-015 | Complete | Browser entry points cover local-first search, signed external confirmation, manual fallback, idempotent saves, typed state and scoped library display. |
| LOK-016 | Complete | PostgreSQL tests cover typed edges, revisioned evidence, exact-ID mapping, review and withdrawal. A live Wikidata import supplied the adaptation evidence used in the milestone. |
| LOK-017 | Complete | Live end-to-end test registered and verified one account, saved Open Library work OL66554W, and recommended film Q270385 from reviewed Wikidata and distributor evidence. Regression covers content evidence, filtering and withdrawal of unreviewed edges. |

LOK-017 tests the architecture end to end with one user. LOK-058 is optional. LOK-067 is private beta and LOK-068 is the public launch gate.

| Task | Title | Dependencies | Requirements sections |
|---|---|---|---|
| [LOK-001](LOK-001-product-trace-and-acceptance.md) | Product trace and acceptance | — | 1–7, 29–33 |
| [LOK-002](LOK-002-architecture-approval.md) | Architecture approval | LOK-001 | 13–15, 22, 28 |
| [LOK-003](LOK-003-schema-review.md) | Schema review | LOK-002 | 15 |
| [LOK-004](LOK-004-provider-due-diligence.md) | Provider due diligence | LOK-002 | 9, 20, 23, 27 |
| [LOK-005](LOK-005-windows-development-setup.md) | Windows development setup | LOK-002 | 13, 22 |
| [LOK-006](LOK-006-django-repository-and-ci.md) | Django repository and CI | LOK-005 | 22, 24 |
| [LOK-007](LOK-007-shared-layout-and-landing.md) | Shared layout and landing | LOK-006 | 6, 12 |
| [LOK-008](LOK-008-custom-identity.md) | Custom identity | LOK-003, LOK-006 | 3, 15, 19 |
| [LOK-009](LOK-009-durable-job-runner.md) | Durable job runner | LOK-003, LOK-008 | 17 |
| [LOK-010](LOK-010-authentication-and-recovery.md) | Authentication and recovery | LOK-007, LOK-008, LOK-009 | 6, 19 |
| [LOK-011](LOK-011-profiles-and-centralized-policy.md) | Profiles and centralized policy | LOK-007, LOK-010 | 4, 5.1, 18 |
| [LOK-012](LOK-012-catalogue-schema-and-details.md) | Catalogue schema and details | LOK-003, LOK-011 | 6, 15 |
| [LOK-013](LOK-013-identifiers-and-provenance.md) | Identifiers and provenance | LOK-004, LOK-012 | 8.3–8.4, 15 |
| [LOK-014](LOK-014-provider-adapters-for-books-and-screen.md) | Provider adapters for books and screen | LOK-009, LOK-013 | 7, 9 |
| [LOK-015](LOK-015-personal-library-and-acquisition.md) | Personal library and acquisition | LOK-011, LOK-014 | 5.2–5.14, 7 |
| [LOK-016](LOK-016-graph-and-wikidata.md) | Graph and Wikidata | LOK-013, LOK-014 | 8.3, 9 |
| [LOK-017](LOK-017-baseline-candidates-and-cross-domain-slice.md) | Baseline candidates and cross-domain slice | LOK-010, LOK-015, LOK-016 | 7, 8 |
| [LOK-018](LOK-018-media-and-image-credits.md) | Media and image credits | LOK-007, LOK-009, LOK-011, LOK-013 | 5.15, 19–20 |
| [LOK-019](LOK-019-home-and-profile-settings.md) | Home and profile settings | LOK-011, LOK-015, LOK-018 | 5.1, 6 |
| [LOK-020](LOK-020-books.md) | Books | LOK-015, LOK-017, LOK-018 | 5.2 |
| [LOK-021](LOK-021-movies.md) | Movies | LOK-015, LOK-017, LOK-018 | 5.3 |
| [LOK-022](LOK-022-tv-shows.md) | TV Shows | LOK-021 | 5.4 |
| [LOK-023](LOK-023-music.md) | Music | LOK-016, LOK-018 | 5.5, 9 |
| [LOK-024](LOK-024-history.md) | History | LOK-016, LOK-018 | 5.6 |
| [LOK-025](LOK-025-culture-and-heritage.md) | Culture and heritage | LOK-024 | 5.7 |
| [LOK-026](LOK-026-travel-and-map.md) | Travel and map | LOK-024, LOK-025 | 5.8, 9, 13 |
| [LOK-027](LOK-027-food-and-cuisine.md) | Food and cuisine | LOK-025, LOK-026 | 5.9 |
| [LOK-028](LOK-028-languages.md) | Languages | LOK-025 | 5.10 |
| [LOK-029](LOK-029-mythology-and-folklore.md) | Mythology and folklore | LOK-024, LOK-025 | 5.11 |
| [LOK-030](LOK-030-philosophy-and-psychology.md) | Philosophy and psychology | LOK-024 | 5.12 |
| [LOK-031](LOK-031-activities-and-experiences.md) | Activities and experiences | LOK-026 | 5.13 |
| [LOK-032](LOK-032-learning-and-exploration.md) | Learning and exploration | LOK-028, LOK-030 | 5.14, 8.1 |
| [LOK-033](LOK-033-photography-and-memories.md) | Photography and memories | LOK-018, LOK-019 | 5.15 |
| [LOK-034](LOK-034-cross-domain-collections.md) | Cross-domain collections | LOK-015, LOK-018, LOK-019 | 5.16 |
| [LOK-035](LOK-035-favourites.md) | Favourites | LOK-019, LOK-020 | 5.17 |
| [LOK-036](LOK-036-lifetime-bucket-list.md) | Lifetime bucket list | LOK-019, LOK-034 | 5.18 |
| [LOK-037](LOK-037-statistics.md) | Statistics | LOK-020, LOK-025, LOK-028, LOK-035 | 5.19 |
| [LOK-038](LOK-038-personal-timeline.md) | Personal timeline | LOK-033, LOK-034 | 5.20 |
| [LOK-039](LOK-039-entity-deduplication-and-merges.md) | Entity deduplication and merges | LOK-016, LOK-022, LOK-023, LOK-034, LOK-038 | 8.4 |
| [LOK-040](LOK-040-global-multilingual-search.md) | Global multilingual search | LOK-032, LOK-034, LOK-039 | 6, 16 |
| [LOK-041](LOK-041-full-candidate-sources.md) | Full candidate sources | LOK-017, LOK-027, LOK-029, LOK-032, LOK-034, LOK-039 | 8.1–8.5 |
| [LOK-042](LOK-042-embedding-evaluation.md) | Embedding evaluation | LOK-041 | 8.5, 13 |
| [LOK-043](LOK-043-semantic-retrieval.md) | Semantic retrieval | LOK-009, LOK-042 | 8.5, 13 |
| [LOK-044](LOK-044-ranking-and-diversity.md) | Ranking and diversity | LOK-041, LOK-043 | 8.6 |
| [LOK-045](LOK-045-explanations.md) | Explanations | LOK-044 | 8.7, 18 |
| [LOK-046](LOK-046-discover-and-onboarding.md) | Discover and onboarding | LOK-035, LOK-040, LOK-045 | 6–8 |
| [LOK-047](LOK-047-feedback-and-reset.md) | Feedback and reset | LOK-046 | 8.8–8.9 |
| [LOK-048](LOK-048-recommendation-evaluation.md) | Recommendation evaluation | LOK-047 | 8.10, 24 |
| [LOK-049](LOK-049-follows-and-requests.md) | Follows and requests | LOK-011, LOK-019 | 6, 11 |
| [LOK-050](LOK-050-public-discovery-and-sharing.md) | Public discovery and sharing | LOK-040, LOK-049 | 6, 11 |
| [LOK-051](LOK-051-shared-interests.md) | Shared interests | LOK-035, LOK-049, LOK-050 | 5.1, 11 |
| [LOK-052](LOK-052-blocking-and-reporting.md) | Blocking and reporting | LOK-049, LOK-050, LOK-051 | 6, 11, 18–19 |
| [LOK-053](LOK-053-moderator-and-administrator-tools.md) | Moderator and administrator tools | LOK-039, LOK-052 | 3, 6, 19, 27 |
| [LOK-054](LOK-054-essential-notifications.md) | Essential notifications | LOK-009, LOK-049, LOK-052, LOK-053 | 6, 11 |
| [LOK-055](LOK-055-imports.md) | Imports | LOK-009, LOK-015, LOK-039, LOK-046 | 6–7, 21 |
| [LOK-056](LOK-056-exports.md) | Exports | LOK-009, LOK-018, LOK-038, LOK-055 | 6, 21 |
| [LOK-057](LOK-057-account-erasure.md) | Account erasure | LOK-054, LOK-056 | 6, 21 |
| [LOK-058](LOK-058-optional-conversation.md) | Optional conversation | LOK-045, LOK-052, LOK-057 | 10 |
| [LOK-059](LOK-059-help-and-policy-pages.md) | Help and policy pages | LOK-004, LOK-053, LOK-057 | 6, 27 |
| [LOK-060](LOK-060-staging-infrastructure.md) | Staging infrastructure | LOK-004, LOK-009, LOK-018, LOK-054 | 23, 26 |
| [LOK-061](LOK-061-backup-and-restore-drills.md) | Backup and restore drills | LOK-057, LOK-060 | 25–26 |
| [LOK-062](LOK-062-operational-monitoring.md) | Operational monitoring | LOK-060, LOK-061 | 26 |
| [LOK-063](LOK-063-accessibility-verification.md) | Accessibility verification | LOK-038, LOK-054, LOK-059, LOK-060 | 12, 24–25 |
| [LOK-064](LOK-064-security-verification.md) | Security verification | LOK-052, LOK-054, LOK-057, LOK-060 | 18–21, 24 |
| [LOK-065](LOK-065-performance-verification.md) | Performance verification | LOK-048, LOK-060, LOK-062 | 24–25 |
| [LOK-066](LOK-066-full-regression.md) | Full regression | LOK-031, LOK-036, LOK-037, LOK-055, LOK-056, LOK-059, LOK-061, LOK-063, LOK-064, LOK-065 | 24, 32 |
| [LOK-067](LOK-067-private-beta.md) | Private beta | LOK-062, LOK-066 | 29, 32 |
| [LOK-068](LOK-068-production-readiness-and-legal-review.md) | Production readiness and legal review | LOK-058, LOK-067 | 27, 32 |
| [LOK-069](LOK-069-public-release.md) | Public release | LOK-068 | 29, 32 |

## Scope review

Home is LOK-019, domain pages LOK-020–032, and remaining personal pages LOK-033–038. Page controls ship in LOK-011. Featured data are connected by the respective page and social tasks. Account settings are covered by LOK-010–011 and personal saved items by LOK-015. Search, sharing and follower access depend on common scoped policies. Free-host constraints can block launch while preserving private beta. Legal, coverage, quota and model uncertainties are tracked in the architecture and provider documents.
