# LOK-040 Global multilingual search

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify global multilingual search for [brief sections 6, 16](../docs/requirements.md).

## Purpose

Telugu/English fixtures, privacy matrix and indexed query plans pass.

## Dependencies

[LOK-032](LOK-032-learning-and-exploration.md), [LOK-034](LOK-034-cross-domain-collections.md), [LOK-039](LOK-039-entity-deduplication-and-merges.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [recommendation-engine](../docs/recommendation-engine.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Implement exact/prefix/trigram/FTS, filters, alias/creator/subject search and authorized personal and public scopes.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-002 and ADR-005 on catalogue and ranking.

## Files to create or modify

apps/search/, templates/platform/search.html. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

Add or revise pg_trgm and normalized search keys/indexes using the [schema contract](../docs/database.md). Verify constraints against PostgreSQL.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Implement exact/prefix/trigram/FTS, filters, alias/creator/subject search and authorized personal and public scopes.
3. Verify the workflow through its normal entry point and record the evidence.

## Security considerations

Measure English and Telugu results, EXPLAIN plans, and privacy of suggestions/counts.

## Privacy considerations

Apply viewer policy before query rank, counts, snippets and autocomplete.

## Accessibility considerations

Keep affected controls operable by keyboard with readable labels and error states; expose job or operator status as text. Evaluate affected UI at narrow widths and without JavaScript for core workflows.

## Failure handling

Handle the first unavailable dependency with a clear safe error or fallback. Keep writes atomic or retryable and verify that retries preserve user data.

## Required tests

Measure English and Telugu results, EXPLAIN plans, and privacy of suggestions/counts. Test constraints, migration and applicable transaction or retry behavior.

## Acceptance criteria

- Telugu/English fixtures, privacy matrix and indexed query plans pass.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_040` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [recommendation-engine](../docs/recommendation-engine.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Keep reads compatible during migration. Use the recovery runbook for irreversible data changes and verify linked references.
