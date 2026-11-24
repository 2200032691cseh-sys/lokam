# LOK-055 Imports

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify imports for [brief sections 6–7, 21](../docs/requirements.md).

## Purpose

Supported real fixture imports without personal dates and retries preserve records.

## Dependencies

[LOK-009](LOK-009-durable-job-runner.md), [LOK-015](LOK-015-personal-library-and-acquisition.md), [LOK-039](LOK-039-entity-deduplication-and-merges.md), [LOK-046](LOK-046-discover-and-onboarding.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [privacy](../docs/privacy.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Preview and validate bulk text, CSV, JSON and approved Goodreads/Letterboxd files; use per-row idempotency.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-003 and ADR-004 on access and asynchronous work.

## Files to create or modify

apps/portability/, templates/platform/import.html. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

Add or revise ImportJob and row outcomes using the [schema contract](../docs/database.md). Verify constraints against PostgreSQL.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Preview and validate bulk text, CSV, JSON and approved Goodreads/Letterboxd files; use per-row idempotency.
3. Verify the workflow through its normal entry point and record the evidence.

## Security considerations

Test malicious or oversized files, supported real sanitized export samples and interrupted imports.

## Privacy considerations

Apply profile, page, container and item policy to any personal data handled by this task. Exercise owner and unrelated-member cases.

## Accessibility considerations

Keep affected controls operable by keyboard with readable labels and error states; expose job or operator status as text. Evaluate affected UI at narrow widths and without JavaScript for core workflows.

## Failure handling

Handle the first unavailable dependency with a clear safe error or fallback. Keep writes atomic or retryable and verify that retries preserve user data.

## Required tests

Test malicious or oversized files, supported real sanitized export samples and interrupted imports. Test constraints, migration and applicable transaction or retry behavior.

## Acceptance criteria

- Supported real fixture imports without personal dates and retries preserve records.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_055` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [privacy](../docs/privacy.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Keep reads compatible during migration. Use the recovery runbook for irreversible data changes and verify linked references.
