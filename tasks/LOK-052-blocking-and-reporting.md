# LOK-052 Blocking and reporting

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify blocking and reporting for [brief sections 6, 11, 18–19](../docs/requirements.md).

## Purpose

Blocks suppress all authenticated indirect surfaces and cancel relationships.

## Dependencies

[LOK-049](LOK-049-follows-and-requests.md), [LOK-050](LOK-050-public-discovery-and-sharing.md), [LOK-051](LOK-051-shared-interests.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [privacy](../docs/privacy.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Serialize block/follow state, expose blocked settings and reporting with throttles.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-003 and ADR-004 on access and asynchronous work.

## Files to create or modify

apps/social/, apps/moderation/. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

Add or revise Block and Report using the [schema contract](../docs/database.md). Verify constraints against PostgreSQL.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Serialize block/follow state, expose blocked settings and reporting with throttles.
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

Verify the blocking and reporting workflow, its applicable unauthorized or invalid path, and any stated fallback. Test constraints, migration and applicable transaction or retry behavior.

## Acceptance criteria

- Blocks suppress all authenticated indirect surfaces and cancel relationships.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_052` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [privacy](../docs/privacy.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Keep reads compatible during migration. Use the recovery runbook for irreversible data changes and verify linked references.
