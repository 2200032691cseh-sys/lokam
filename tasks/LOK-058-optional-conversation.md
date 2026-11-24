# LOK-058 Optional conversation

**Status** Planned. Architecture and task authorization required before implementation.

## Problem being solved

Deliver and verify optional conversation for [brief sections 10](../docs/requirements.md).

## Purpose

Flag remains off unless citation, cross-user isolation, revocation and cost evidence pass.

## Dependencies

[LOK-045](LOK-045-explanations.md), [LOK-052](LOK-052-blocking-and-reporting.md), [LOK-057](LOK-057-account-erasure.md)

## Prerequisites

Read the approved [architecture](../docs/architecture.md) and [conversational-profiles](../docs/conversational-profiles.md). Inspect the existing entry points and verify completed dependency evidence. Confirm the required local or staging services are reachable.

## Scope

Implement consent and scoped grounded retrieval only after model benchmark approval.

## Explicitly excluded scope

Impersonation, arbitrary actions and required production inference.

## Relevant architecture decisions

See [decision register](../docs/decisions/README.md) for ADR-007 and inference isolation.

## Files to create or modify

apps/profiles/, docs/conversational-profiles.md. Add task-specific verification in the closest appropriate suite when code is in scope.

## Database changes

Add or revise Conversation consent and selected record references using the [schema contract](../docs/database.md). Verify constraints against PostgreSQL.

## Implementation instructions

1. Verify the named dependencies and identify the affected model, service, route or operator workflow.
2. Implement consent and scoped grounded retrieval only after model benchmark approval.
3. Verify the workflow through its normal entry point and record the evidence.

## Security considerations

Test prompt injection, unauthorized retrieval, fabricated sources and revocation mid-response.

## Privacy considerations

Retrieve only expressly shared records and reauthorize citations before returning an answer.

## Accessibility considerations

Keep affected controls operable by keyboard with readable labels and error states; expose job or operator status as text. Evaluate affected UI at narrow widths and without JavaScript for core workflows.

## Failure handling

Handle the first unavailable dependency with a clear safe error or fallback. Keep writes atomic or retryable and verify that retries preserve user data.

## Required tests

Test prompt injection, unauthorized retrieval, fabricated sources and revocation mid-response. Test constraints, migration and applicable transaction or retry behavior.

## Acceptance criteria

- Flag remains off unless citation, cross-user isolation, revocation and cost evidence pass.
- Verification evidence is recorded against this task.

## Verification commands

Run `uv run ruff check .` and `uv run pytest -k lok_058` after naming the task's verification tests with that selector. Confirm tests are collected and run relevant integration or operational drills described above.

## Documentation updates

Update [conversational-profiles](../docs/conversational-profiles.md) with task decisions, verified behavior or measured limitations.

## Definition of done

Acceptance checks pass, actual evidence is recorded, and status is updated. Stop before the next unapproved task.

## Rollback considerations

Keep reads compatible during migration. Use the recovery runbook for irreversible data changes and verify linked references.
