# LOK-069 Public release

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify public release for [brief sections 29, 32](../docs/requirements.md).

## Purpose

Public registration, discovery, publication and recovery verified on live deployment.

## Dependencies

[LOK-068](LOK-068-production-readiness-and-legal-review.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [testing](../docs/testing.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Deploy approved revision, run live smoke checks and monitor rollback triggers.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-006 and launch evidence.

## Files to create or modify

scripts/deployment/, docs/operations.md. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

No additional tables planned. Review existing constraints and indexes.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Deploy approved revision, run live smoke checks and monitor rollback triggers.
3. Verify the workflow through its normal entry point and record the evidence.

## Security considerations

Verify live registration, recovery, save, publishing and discovery after rollout.

## Privacy considerations

Apply profile, page, container and item policy to any personal data handled by this task. Exercise owner and unrelated-member cases.

## Accessibility considerations

Keep affected controls operable by keyboard with readable labels and error states; expose job or operator status as text. Evaluate affected UI at narrow widths and without JavaScript for core workflows.

## Failure handling

Handle the first unavailable dependency with a clear safe error or fallback. Keep writes atomic or retryable and verify that retries preserve user data.

## Required tests

Verify live registration, recovery, save, publishing and discovery after rollout.

## Acceptance criteria

- Public registration, discovery, publication and recovery verified on live deployment.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_069` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [testing](../docs/testing.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Restore the previous deployment after verifying schema compatibility, then rerun live smoke tests.
