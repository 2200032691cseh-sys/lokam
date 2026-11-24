# LOK-004 Provider due diligence

**Status** Complete. Official data and API documentation inform the [enablement gates](../docs/integrations.md#initial-adapter-gates). Runtime access and asset rights remain gated.

## Problem being solved

Deliver and verify provider due diligence for [brief sections 9, 20, 23, 27](../docs/requirements.md).

## Purpose

Each enabled source has recorded rights and quotas.

## Dependencies

[LOK-002](LOK-002-architecture-approval.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [architecture](../docs/architecture.md). Inspect the existing entry points and verify completed dependency evidence. Prepare source and decision evidence for review.

## Scope

Record per-field display, cache, copy, export and commercial rights and live smoke prerequisites.

## Explicitly excluded scope

Feature coding and infrastructure provisioning.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-001 through ADR-004 on module boundaries, data, authorization and background work.

## Files to create or modify

docs/integrations.md. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

No additional tables planned. Review existing constraints and indexes.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Record per-field display, cache, copy, export and commercial rights and live smoke prerequisites.
3. Verify the workflow through its normal entry point and record the evidence.

## Security considerations

Validate inputs, scope mutations to authorized actors, and redact secrets and personal content from diagnostic output.

## Privacy considerations

Apply profile, page, container and item policy to any personal data handled by this task. Exercise owner and unrelated-member cases.

## Accessibility considerations

Keep affected controls operable by keyboard with readable labels and error states; expose job or operator status as text. Evaluate affected UI at narrow widths and without JavaScript for core workflows.

## Failure handling

Record unavailable evidence and the decisions it blocks.

## Required tests

Verify the provider due diligence workflow, its applicable unauthorized or invalid path, and any stated fallback.

## Acceptance criteria

- Each enabled source has recorded rights and quotas.
- Verification evidence is recorded against this task.

## Verification commands

Run `rg -n "LOK-" tasks/README.md` and verify the linked sections, decisions and source evidence.

## Documentation updates

Update [architecture](../docs/architecture.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Revert the scoped change or restore prior configuration. Verify the affected entry point after rollback.
