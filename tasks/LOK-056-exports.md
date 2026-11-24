# LOK-056 Exports

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify exports for [brief sections 6, 21](../docs/requirements.md).

## Purpose

Export is documented and own-data roundtrip passes.

## Dependencies

[LOK-009](LOK-009-durable-job-runner.md), [LOK-018](LOK-018-media-and-image-credits.md), [LOK-038](LOK-038-personal-timeline.md), [LOK-055](LOK-055-imports.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [privacy](../docs/privacy.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Build versioned authorized export, rights-aware media references and expiring downloads.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-003 and ADR-004 on access and asynchronous work.

## Files to create or modify

apps/portability/, templates/platform/export.html. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

Add or revise ExportJob and artifact metadata using the [schema contract](../docs/database.md). Verify constraints against PostgreSQL.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Build versioned authorized export, rights-aware media references and expiring downloads.
3. Verify the workflow through its normal entry point and record the evidence.

## Security considerations

Test artifact expiry, spreadsheet safety, rights filtering and cross-user download attempts.

## Privacy considerations

Restrict export generation and download to the reauthenticated owner.

## Accessibility considerations

Keep affected controls operable by keyboard with readable labels and error states; expose job or operator status as text. Evaluate affected UI at narrow widths and without JavaScript for core workflows.

## Failure handling

Handle the first unavailable dependency with a clear safe error or fallback. Keep writes atomic or retryable and verify that retries preserve user data.

## Required tests

Test artifact expiry, spreadsheet safety, rights filtering and cross-user download attempts. Test constraints, migration and applicable transaction or retry behavior.

## Acceptance criteria

- Export is documented and own-data roundtrip passes.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_056` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [privacy](../docs/privacy.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Keep reads compatible during migration. Use the recovery runbook for irreversible data changes and verify linked references.
