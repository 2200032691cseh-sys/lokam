# LOK-026 Travel and map

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify travel and map for [brief sections 5.8, 9, 13](../docs/requirements.md).

## Purpose

Accessible location list works without map script or mandatory visit date.

## Dependencies

[LOK-024](LOK-024-history.md), [LOK-025](LOK-025-culture-and-heritage.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [requirements](../docs/requirements.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Build destinations, statuses and collections; use Leaflet with permitted tiles and text fallback.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-001 through ADR-004 on module boundaries, data, authorization and background work.

## Files to create or modify

apps/catalogue/, templates/libraries/travel.html, static/js/. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

Add or revise Place and coordinate checks using the [schema contract](../docs/database.md). Verify constraints against PostgreSQL.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Build destinations, statuses and collections; use Leaflet with permitted tiles and text fallback.
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

Verify the travel and map workflow, its applicable unauthorized or invalid path, and any stated fallback. Test constraints, migration and applicable transaction or retry behavior.

## Acceptance criteria

- Accessible location list works without map script or mandatory visit date.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_026` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [requirements](../docs/requirements.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Keep reads compatible during migration. Use the recovery runbook for irreversible data changes and verify linked references.
