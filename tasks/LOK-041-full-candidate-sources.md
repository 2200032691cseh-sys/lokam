# LOK-041 Full candidate sources

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify full candidate sources for [brief sections 8.1–8.5](../docs/requirements.md).

## Purpose

All discovery categories map to canonical types and candidate evidence.

## Dependencies

[LOK-017](LOK-017-baseline-candidates-and-cross-domain-slice.md), [LOK-027](LOK-027-food-and-cuisine.md), [LOK-029](LOK-029-mythology-and-folklore.md), [LOK-032](LOK-032-learning-and-exploration.md), [LOK-034](LOK-034-cross-domain-collections.md), [LOK-039](LOK-039-entity-deduplication-and-merges.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [recommendation-engine](../docs/recommendation-engine.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Add shared creator/subject, provider suggestions, typed domain coverage and discovery of public collections.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-002 and ADR-005 on catalogue and ranking.

## Files to create or modify

apps/discovery/. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

Add or revise ProviderSuggestion using the [schema contract](../docs/database.md). Verify constraints against PostgreSQL.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Add shared creator/subject, provider suggestions, typed domain coverage and discovery of public collections.
3. Verify the workflow through its normal entry point and record the evidence.

## Security considerations

Validate inputs, scope mutations to authorized actors, and redact secrets and personal content from diagnostic output.

## Privacy considerations

Apply profile, page, container and item policy to any personal data handled by this task. Exercise owner and unrelated-member cases.

## Accessibility considerations

Keep affected controls operable by keyboard with readable labels and error states; expose job or operator status as text. Evaluate affected UI at narrow widths and without JavaScript for core workflows.

## Failure handling

Handle the first unavailable dependency with a clear safe error or fallback. Keep writes atomic or retryable and verify that retries preserve user data.

## Required tests

Verify the full candidate sources workflow, its applicable unauthorized or invalid path, and any stated fallback. Test constraints, migration and applicable transaction or retry behavior.

## Acceptance criteria

- All discovery categories map to canonical types and candidate evidence.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_041` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [recommendation-engine](../docs/recommendation-engine.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Keep reads compatible during migration. Use the recovery runbook for irreversible data changes and verify linked references.
