# LOK-017 Baseline candidates and cross-domain slice

**Status** Complete. Live one-user acquisition and adaptation smoke test passed.

## Problem being solved

Deliver and verify baseline candidates and cross-domain slice for [brief sections 7, 8](../docs/requirements.md).

## Purpose

Single user sees an attributed different-domain result after save.

## Dependencies

[LOK-010](LOK-010-authentication-and-recovery.md), [LOK-015](LOK-015-personal-library-and-acquisition.md), [LOK-016](LOK-016-graph-and-wikidata.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [requirements](../docs/requirements.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Use graph traversal and weighted attribute candidates; connect signup, real metadata save and one-user book-to-film discovery.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-001 through ADR-004 on module boundaries, data, authorization and background work.

## Files to create or modify

apps/discovery/, tests/recommendations/. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

No additional tables planned. Review existing constraints and indexes.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Use graph traversal and weighted attribute candidates; connect signup, real metadata save and one-user book-to-film discovery.
3. Verify the workflow through its normal entry point and record the evidence.

## Security considerations

Use one member, a sourced adaptation and a real metadata provider read.

## Privacy considerations

Apply profile, page, container and item policy to any personal data handled by this task. Exercise owner and unrelated-member cases.

## Accessibility considerations

Keep affected controls operable by keyboard with readable labels and error states; expose job or operator status as text. Evaluate affected UI at narrow widths and without JavaScript for core workflows.

## Failure handling

Fall back to saved catalogue data and manual entry during outage; omit unsupported recommendations.

## Required tests

Use one member, a sourced adaptation and a real metadata provider read.

## Acceptance criteria

- Single user sees an attributed different-domain result after save.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_017` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [requirements](../docs/requirements.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Revert the scoped change or restore prior configuration. Verify the affected entry point after rollback.
