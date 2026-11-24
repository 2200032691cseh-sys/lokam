# LOK-043 Semantic retrieval

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify semantic retrieval for [brief sections 8.5, 13](../docs/requirements.md).

## Purpose

One vector per item/version, lexical fallback after failure and no private text.

## Dependencies

[LOK-009](LOK-009-durable-job-runner.md), [LOK-042](LOK-042-embedding-evaluation.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [recommendation-engine](../docs/recommendation-engine.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Precompute canonical vectors and query pgvector under feature flag and a time budget.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-002 and ADR-005 on catalogue and ranking.

## Files to create or modify

apps/discovery/, apps/jobs/. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

Add or revise vector extension and versioned CatalogueEmbedding using the [schema contract](../docs/database.md). Verify constraints against PostgreSQL.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Precompute canonical vectors and query pgvector under feature flag and a time budget.
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

Verify the semantic retrieval workflow, its applicable unauthorized or invalid path, and any stated fallback. Test constraints, migration and applicable transaction or retry behavior.

## Acceptance criteria

- One vector per item/version, lexical fallback after failure and no private text.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_043` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [recommendation-engine](../docs/recommendation-engine.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Keep reads compatible during migration. Use the recovery runbook for irreversible data changes and verify linked references.
