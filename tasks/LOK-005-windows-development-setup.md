# LOK-005 Windows development setup

**Status** Complete. Verified dependency sync and a local Windows PostgreSQL connection. See [local setup](../README.md#local-setup-and-testing).

## Problem being solved

Deliver and verify windows development setup for [brief sections 13, 22](../docs/requirements.md).

## Purpose

Fresh Windows checkout can sync locked dependencies and connect.

## Dependencies

[LOK-002](LOK-002-architecture-approval.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [architecture](../docs/architecture.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Pin compatible Python and PostgreSQL; document local DB and console email setup.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-001 through ADR-004 on module boundaries, data, authorization and background work.

## Files to create or modify

README.md, pyproject.toml, uv.lock, .env.example. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

No additional tables planned. Review existing constraints and indexes.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Pin compatible Python and PostgreSQL; document local DB and console email setup.
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

Verify the windows development setup workflow, its applicable unauthorized or invalid path, and any stated fallback.

## Acceptance criteria

- Fresh Windows checkout can sync locked dependencies and connect.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv --version`, `uv sync --locked` and `psql --version`.

## Documentation updates

Update [architecture](../docs/architecture.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Revert the scoped change or restore prior configuration. Verify the affected entry point after rollback.
