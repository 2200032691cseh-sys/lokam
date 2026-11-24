# LOK-060 Staging infrastructure

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify staging infrastructure for [brief sections 23, 26](../docs/requirements.md).

## Purpose

Staging smoke records verified account, storage, provider and app capabilities.

## Dependencies

[LOK-004](LOK-004-provider-due-diligence.md), [LOK-009](LOK-009-durable-job-runner.md), [LOK-018](LOK-018-media-and-image-credits.md), [LOK-054](LOK-054-essential-notifications.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [deployment](../docs/deployment.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Provision approved providers, verify billing/quota, worker cadence, email and rollback.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-006 and launch evidence.

## Files to create or modify

scripts/deployment/, config/settings/production.py. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

No additional tables planned. Review existing constraints and indexes.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Provision approved providers, verify billing/quota, worker cadence, email and rollback.
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

Verify the staging infrastructure workflow, its applicable unauthorized or invalid path, and any stated fallback.

## Acceptance criteria

- Staging smoke records verified account, storage, provider and app capabilities.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_060` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [deployment](../docs/deployment.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Revert the scoped change or restore prior configuration. Verify the affected entry point after rollback.
