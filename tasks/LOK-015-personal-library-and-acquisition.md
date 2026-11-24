# LOK-015 Personal library and acquisition

**Status** Complete. Local-first acquisition, repeat saves and personal record access passed PostgreSQL integration tests.

## Problem being solved

Deliver and verify personal library and acquisition for [brief sections 5.2–5.14, 7](../docs/requirements.md).

## Purpose

Retrying save yields one relationship; private manual data stays scoped.

## Dependencies

[LOK-011](LOK-011-profiles-and-centralized-policy.md), [LOK-014](LOK-014-provider-adapters-for-books-and-screen.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [database](../docs/database.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Local first search, provider match selection, manual owner item, typed states and annotations.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-001 through ADR-004 on module boundaries, data, authorization and background work.

## Files to create or modify

apps/libraries/, templates/libraries/. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

Add or revise UserItem and typed annotations using the [schema contract](../docs/database.md). Verify constraints against PostgreSQL.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Local first search, provider match selection, manual owner item, typed states and annotations.
3. Verify the workflow through its normal entry point and record the evidence.

## Security considerations

Cover ambiguous match, timeout, manual fallback and repeat save.

## Privacy considerations

Apply profile, page, container and item policy to any personal data handled by this task. Exercise owner and unrelated-member cases.

## Accessibility considerations

Keep affected controls operable by keyboard with readable labels and error states; expose job or operator status as text. Evaluate affected UI at narrow widths and without JavaScript for core workflows.

## Failure handling

Handle the first unavailable dependency with a clear safe error or fallback. Keep writes atomic or retryable and verify that retries preserve user data.

## Required tests

Cover ambiguous match, timeout, manual fallback and repeat save. Test constraints, migration and applicable transaction or retry behavior.

## Acceptance criteria

- Retrying save yields one relationship; private manual data stays scoped.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_015` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [database](../docs/database.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Keep reads compatible during migration. Use the recovery runbook for irreversible data changes and verify linked references.
