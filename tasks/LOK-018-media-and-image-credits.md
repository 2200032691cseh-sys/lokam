# LOK-018 Media and image credits

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify media and image credits for [brief sections 5.15, 19–20](../docs/requirements.md).

## Purpose

Public derivatives lack EXIF and private objects are inaccessible across users.

## Dependencies

[LOK-007](LOK-007-shared-layout-and-landing.md), [LOK-009](LOK-009-durable-job-runner.md), [LOK-011](LOK-011-profiles-and-centralized-policy.md), [LOK-013](LOK-013-identifiers-and-provenance.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [security](../docs/security.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Build rights-aware provider image delivery, upload quarantine, variants, quota, cleanup and authorized download.

## Explicitly excluded scope

Adjacent capabilities assigned to other tasks, unrelated refactors and new services outside approved architecture.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-001 through ADR-004 on module boundaries, data, authorization and background work.

## Files to create or modify

apps/media/, templates/platform/credits.html. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

Add or revise MediaAsset and derivative lifecycle using the [schema contract](../docs/database.md). Verify constraints against PostgreSQL.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Build rights-aware provider image delivery, upload quarantine, variants, quota, cleanup and authorized download.
3. Verify the workflow through its normal entry point and record the evidence.

## Security considerations

Verify EXIF stripping, truncated input, storage failure and cross-user access.

## Privacy considerations

Apply profile, page, container and item policy to any personal data handled by this task. Exercise owner and unrelated-member cases.

## Accessibility considerations

Keep affected controls operable by keyboard with readable labels and error states; expose job or operator status as text. Evaluate affected UI at narrow widths and without JavaScript for core workflows.

## Failure handling

Handle the first unavailable dependency with a clear safe error or fallback. Keep writes atomic or retryable and verify that retries preserve user data.

## Required tests

Verify EXIF stripping, truncated input, storage failure and cross-user access. Test constraints, migration and applicable transaction or retry behavior.

## Acceptance criteria

- Public derivatives lack EXIF and private objects are inaccessible across users.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_018` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [security](../docs/security.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Keep reads compatible during migration. Use the recovery runbook for irreversible data changes and verify linked references.
