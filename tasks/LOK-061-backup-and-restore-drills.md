# LOK-061 Backup and restore drills

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify backup and restore drills for [brief sections 25–26](../docs/requirements.md).

## Purpose

Measured RPO ≤24h and RTO ≤4h with linked media.

## Dependencies

[LOK-057](LOK-057-account-erasure.md), [LOK-060](LOK-060-staging-infrastructure.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [recovery](../docs/recovery.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Automate encrypted backups, manifests and erasure replay; restore in isolation.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-006 and launch evidence.

## Files to create or modify

scripts/backup/, scripts/restore/, docs/recovery.md. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

No additional tables planned. Review existing constraints and indexes.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Automate encrypted backups, manifests and erasure replay; restore in isolation.
3. Verify the workflow through its normal entry point and record the evidence.

## Security considerations

Run a timed database/media restore, compare hashes and apply erasure replay.

## Privacy considerations

Apply profile, page, container and item policy to any personal data handled by this task. Exercise owner and unrelated-member cases.

## Accessibility considerations

Keep affected controls operable by keyboard with readable labels and error states; expose job or operator status as text. Evaluate affected UI at narrow widths and without JavaScript for core workflows.

## Failure handling

Handle the first unavailable dependency with a clear safe error or fallback. Keep writes atomic or retryable and verify that retries preserve user data.

## Required tests

Run a timed database/media restore, compare hashes and apply erasure replay.

## Acceptance criteria

- Measured RPO ≤24h and RTO ≤4h with linked media.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_061` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [recovery](../docs/recovery.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Revert the scoped change or restore prior configuration. Verify the affected entry point after rollback.
