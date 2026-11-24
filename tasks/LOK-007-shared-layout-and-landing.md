# LOK-007 Shared layout and landing

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify shared layout and landing for [brief sections 6, 12](../docs/requirements.md).

## Purpose

Keyboard and no-JS layout smoke passes at narrow and wide sizes.

## Dependencies

[LOK-006](LOK-006-django-repository-and-ci.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [database](../docs/database.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Create document layout, platform navigation, forms, empty/error states and landing page.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-001 through ADR-004 on module boundaries, data, authorization and background work.

## Files to create or modify

templates/platform/, templates/components/, static/css/. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

No additional tables planned. Review existing constraints and indexes.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Create document layout, platform navigation, forms, empty/error states and landing page.
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

Verify the shared layout and landing workflow, its applicable unauthorized or invalid path, and any stated fallback.

## Acceptance criteria

- Keyboard and no-JS layout smoke passes at narrow and wide sizes.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_007` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [database](../docs/database.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Revert the scoped change or restore prior configuration. Verify the affected entry point after rollback.
