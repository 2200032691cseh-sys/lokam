# LOK-014 Provider adapters for books and screen

**Status** Live TMDB verification pending. Open Library live search and local provider contract tests passed.

## Problem being solved

Deliver and verify provider adapters for books and screen for [brief sections 7, 9](../docs/requirements.md).

## Purpose

Bounded recorded contracts and credentialed real read documented.

## Dependencies

[LOK-009](LOK-009-durable-job-runner.md), [LOK-013](LOK-013-identifiers-and-provenance.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [database](../docs/database.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Implement HTTPX contracts and Open Library/TMDB permitted search and import.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-001 through ADR-004 on module boundaries, data, authorization and background work.

## Files to create or modify

apps/integrations/. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

No additional tables planned. Review existing constraints and indexes.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Implement HTTPX contracts and Open Library/TMDB permitted search and import.
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

Verify the provider adapters for books and screen workflow, its applicable unauthorized or invalid path, and any stated fallback.

## Acceptance criteria

- Bounded recorded contracts and credentialed real read documented.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_014` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [database](../docs/database.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Revert the scoped change or restore prior configuration. Verify the affected entry point after rollback.
