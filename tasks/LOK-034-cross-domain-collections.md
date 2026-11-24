# LOK-034 Cross-domain collections

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify cross-domain collections for [brief sections 5.16](../docs/requirements.md).

## Purpose

Public collection cannot expose private save and bookmark revocation works.

## Dependencies

[LOK-015](LOK-015-personal-library-and-acquisition.md), [LOK-018](LOK-018-media-and-image-credits.md), [LOK-019](LOK-019-home-and-profile-settings.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [requirements](../docs/requirements.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Build ordering, cover, publication, sharing and bookmarks that reauthorize.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-001 through ADR-004 on module boundaries, data, authorization and background work.

## Files to create or modify

apps/collections/, templates/profiles/collections.html. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

Add or revise Collection, ordered entries and Bookmark using the [schema contract](../docs/database.md). Verify constraints against PostgreSQL.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Build ordering, cover, publication, sharing and bookmarks that reauthorize.
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

Verify the cross-domain collections workflow, its applicable unauthorized or invalid path, and any stated fallback. Test constraints, migration and applicable transaction or retry behavior.

## Acceptance criteria

- Public collection cannot expose private save and bookmark revocation works.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_034` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [requirements](../docs/requirements.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Keep reads compatible during migration. Use the recovery runbook for irreversible data changes and verify linked references.
