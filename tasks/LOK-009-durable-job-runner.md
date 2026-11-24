# LOK-009 Durable job runner

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify durable job runner for [brief sections 17](../docs/requirements.md).

## Purpose

Concurrent claims and expired leases produce one committed outcome.

## Dependencies

[LOK-003](LOK-003-schema-review.md), [LOK-008](LOK-008-custom-identity.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [database](../docs/database.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Implement leasing, fencing, backoff, cancellation and capped command.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-001 through ADR-004 on module boundaries, data, authorization and background work.

## Files to create or modify

apps/jobs/. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

Add or revise BackgroundJob, lease token, due-time index and unique dedup key using the [schema contract](../docs/database.md). Verify constraints against PostgreSQL.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Implement leasing, fencing, backoff, cancellation and capped command.
3. Verify the workflow through its normal entry point and record the evidence.

## Security considerations

Kill a worker after claim and prove stale completion cannot overwrite a reclaimed job.

## Privacy considerations

Apply profile, page, container and item policy to any personal data handled by this task. Exercise owner and unrelated-member cases.

## Accessibility considerations

Keep affected controls operable by keyboard with readable labels and error states; expose job or operator status as text. Evaluate affected UI at narrow widths and without JavaScript for core workflows.

## Failure handling

Handle the first unavailable dependency with a clear safe error or fallback. Keep writes atomic or retryable and verify that retries preserve user data.

## Required tests

Kill a worker after claim and prove stale completion cannot overwrite a reclaimed job. Test constraints, migration and applicable transaction or retry behavior.

## Acceptance criteria

- Concurrent claims and expired leases produce one committed outcome.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_009` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [database](../docs/database.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Keep reads compatible during migration. Use the recovery runbook for irreversible data changes and verify linked references.
