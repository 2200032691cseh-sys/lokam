# LOK-023 Music

**Status** Complete for music catalogue, discovery input and personal annotations. Memories and playlists connect in their owning tasks.

## Problem being solved

Deliver and verify music for [brief sections 5.5, 9](../docs/requirements.md).

## Purpose

Recording/work identities and soundtrack edges persist without hosting audio.

## Dependencies

[LOK-016](LOK-016-graph-and-wikidata.md), [LOK-018](LOK-018-media-and-image-credits.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [requirements](../docs/requirements.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Connect MusicBrainz and approved artwork; render artists, composers, work/recording/release, styles, moods, memories and legitimate listening links.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-001 through ADR-004 on module boundaries, data, authorization and background work.

## Files to create or modify

apps/integrations/, apps/catalogue/, templates/libraries/music.html. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

Add or revise Artist, work, recording and release using the [schema contract](../docs/database.md). Verify constraints against PostgreSQL.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Connect MusicBrainz and approved artwork; render artists, composers, work/recording/release, styles, moods, memories and legitimate listening links.
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

Verify the music workflow, its applicable unauthorized or invalid path, and any stated fallback. Test constraints, migration and applicable transaction or retry behavior.

## Acceptance criteria

- Recording/work identities and soundtrack edges persist without hosting audio.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_023` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [requirements](../docs/requirements.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Keep reads compatible during migration. Use the recovery runbook for irreversible data changes and verify linked references.
