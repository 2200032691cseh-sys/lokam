# Lokam

Lokam is a planned personal website and discovery tool for interests spread across books, film, music, history, culture and travel. It aims to give people one place to keep what they find and discover connections across subjects.

## Status

The product specification, architecture proposal and implementation backlog are available. Application features and screenshots will be added as implementation progresses.

## Architecture

The proposal uses Django 5.2 LTS, Python 3.13, PostgreSQL 17, Django templates and plain CSS. A shared catalogue holds canonical information. User-owned records hold saves, annotations and sharing preferences. PostgreSQL also supports search, graph relationships and bounded background work. See the [architecture](docs/architecture.md), [decision register](docs/decisions/README.md) and [database design](docs/database.md).

## Local setup and testing

Clone the private repository with an account that has access. The planning baseline has no runtime dependencies or environment variables. Run `python scripts/check_docs.py` from the repository root to check task structure, dependencies and local documentation links. The same check runs in CI. The [testing plan](docs/testing.md) describes the application test suites.

## Deployment and limitations

The [deployment plan](docs/deployment.md) covers the proposed environment configuration, provider setup and release gates. The [recovery plan](docs/recovery.md) describes backup and restore requirements. Hosting, live integrations and application performance remain unverified.

See [contributing](CONTRIBUTING.md), [security reporting](SECURITY.md) and the [changelog](CHANGELOG.md).
