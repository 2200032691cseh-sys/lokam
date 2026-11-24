# LOK-066 Full regression

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify full regression for [brief sections 24, 32](../docs/requirements.md).

## Purpose

Evidence matrix covers every production readiness clause.

## Dependencies

[LOK-031](LOK-031-activities-and-experiences.md), [LOK-037](LOK-037-statistics.md), [LOK-055](LOK-055-imports.md), [LOK-056](LOK-056-exports.md), [LOK-059](LOK-059-help-and-policy-pages.md), [LOK-061](LOK-061-backup-and-restore-drills.md), [LOK-063](LOK-063-accessibility-verification.md), [LOK-064](LOK-064-security-verification.md), [LOK-065](LOK-065-performance-verification.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [testing](../docs/testing.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Run supported feature, migration, failure and browser suites; include optional flag-off path.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-006 and launch evidence.

## Files to create or modify

tests/end_to_end/, docs/testing.md. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

No additional tables planned. Review existing constraints and indexes.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Run supported feature, migration, failure and browser suites; include optional flag-off path.
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

Verify the full regression workflow, its applicable unauthorized or invalid path, and any stated fallback.

## Acceptance criteria

- Evidence matrix covers every production readiness clause.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_066` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [testing](../docs/testing.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Revert the scoped change or restore prior configuration. Verify the affected entry point after rollback.
