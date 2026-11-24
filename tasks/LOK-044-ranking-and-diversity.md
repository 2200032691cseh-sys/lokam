# LOK-044 Ranking and diversity

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify ranking and diversity for [brief sections 8.6](../docs/requirements.md).

## Purpose

Deterministic mixed result set with measurable diversity.

## Dependencies

[LOK-041](LOK-041-full-candidate-sources.md), [LOK-043](LOK-043-semantic-retrieval.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [recommendation-engine](../docs/recommendation-engine.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Normalize scores, cap repeated creators/types, handle missing components and duplicate aliases.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-002 and ADR-005 on catalogue and ranking.

## Files to create or modify

apps/discovery/. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

No additional tables planned. Review existing constraints and indexes.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Normalize scores, cap repeated creators/types, handle missing components and duplicate aliases.
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

Verify the ranking and diversity workflow, its applicable unauthorized or invalid path, and any stated fallback.

## Acceptance criteria

- Deterministic mixed result set with measurable diversity.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_044` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [recommendation-engine](../docs/recommendation-engine.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Revert the scoped change or restore prior configuration. Verify the affected entry point after rollback.
