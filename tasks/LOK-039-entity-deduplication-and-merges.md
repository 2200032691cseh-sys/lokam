# LOK-039 Entity deduplication and merges

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify entity deduplication and merges for [brief sections 8.4](../docs/requirements.md).

## Purpose

Ambiguous records remain separate and annotations survive merge.

## Dependencies

[LOK-016](LOK-016-graph-and-wikidata.md), [LOK-022](LOK-022-tv-shows.md), [LOK-023](LOK-023-music.md), [LOK-034](LOK-034-cross-domain-collections.md), [LOK-038](LOK-038-personal-timeline.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [requirements](../docs/requirements.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Rank secondary matches for review and transactionally rewire approved duplicates.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-001 through ADR-004 on module boundaries, data, authorization and background work.

## Files to create or modify

apps/catalogue/, apps/moderation/. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

Add or revise Catalogue merge redirects and review state using the [schema contract](../docs/database.md). Verify constraints against PostgreSQL.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Rank secondary matches for review and transactionally rewire approved duplicates.
3. Verify the workflow through its normal entry point and record the evidence.

## Security considerations

Prove conflicting identifiers stay separate and existing references survive merge.

## Privacy considerations

Apply profile, page, container and item policy to any personal data handled by this task. Exercise owner and unrelated-member cases.

## Accessibility considerations

Keep affected controls operable by keyboard with readable labels and error states; expose job or operator status as text. Evaluate affected UI at narrow widths and without JavaScript for core workflows.

## Failure handling

Handle the first unavailable dependency with a clear safe error or fallback. Keep writes atomic or retryable and verify that retries preserve user data.

## Required tests

Prove conflicting identifiers stay separate and existing references survive merge. Test constraints, migration and applicable transaction or retry behavior.

## Acceptance criteria

- Ambiguous records remain separate and annotations survive merge.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_039` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [requirements](../docs/requirements.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Keep reads compatible during migration. Use the recovery runbook for irreversible data changes and verify linked references.
