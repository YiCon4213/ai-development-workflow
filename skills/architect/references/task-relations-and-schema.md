# Task Relations and Schema

Read this reference when creating, splitting, merging or reordering task cards.

## Relations

Task cards use typed `relations`; do not use a plain dependency list for new work.

| Type | Blocks Coding Owner start | Required fields |
| --- | --- | --- |
| `hard` | Yes | `task`, `reason`, `required_artifact` |
| `integration_order` | No | `task`, `reason`, `verification_gate` |
| `coordination` | No | `task`, `reason`, `shared_surfaces` |

- `hard`: the task must consume a concrete predecessor contract, migration, interface or runtime capability.
- `integration_order`: implementations can proceed independently, but integration or E2E evidence waits.
- `coordination`: logic is independent, but files, test data, environment or deployment resources overlap.

Only `hard` affects readiness. A chosen release sequence or user preference may set `parallelism.mode: serial`, but it is not a fabricated hard relation.

## Parallelism

Every new task declares:

```yaml
parallelism:
  mode: parallel       # parallel | isolated | serial
  reason: "Uses the stable public API and touches no shared state"
```

- `parallel`: safe in the same workspace with normal coordination.
- `isolated`: logically parallel but requires separate worktrees, file ownership or separate mutable resources.
- `serial`: work itself must wait, not merely final integration.

## New task example

```yaml
schema_version: 2
task:
  id: TASK-003
  title: "Render the new report contract"
  status: pending
  goal: >
    Display the approved report response without changing its public fields.

  scope:
    in:
      - "report result rendering"
      - "loading and failure states"
    out:
      - "report generation logic"

  constraints:
    - "Preserve the existing public response contract"
  forbidden:
    - "Do not infer missing values in the client"

  acceptance:
    - id: AC-001
      expect: "A successful response renders every approved field."
    - id: AC-002
      expect: "A failed response remains visible and no stale result is shown."

  relations:
    - task: TASK-001
      type: hard
      reason: "Consumes the approved report schema"
      required_artifact: "versioned report response contract"
    - task: TASK-002
      type: integration_order
      reason: "Both sides implement the stable contract independently"
      verification_gate: "Cross-layer E2E waits for the backend implementation"
    - task: TASK-004
      type: coordination
      reason: "Both tasks edit shared result-card styles"
      shared_surfaces:
        - "src/components/result-card"

  parallelism:
    mode: isolated
    reason: "Implementation can overlap, but TASK-004 shares style files"

  risk_level: L2
  investigation_hints:
    - "public report types and existing result-card tests"
  escalation_conditions:
    - "The public report contract must change"

  verification:
    required: true
    status: pending
    spec: ".tasks/verification/TASK-003.yaml"
    designed_by: null
    designed_at: null
    basis_fingerprint: null
    waiver_reason: null

  result:
    owner: null
    attempts: 0
    completed_at: null
    accepted_at: null
    evidence_ref: ".tasks/evidence/TASK-003.yaml"
```

Create `.tasks/evidence/TASK-003.yaml` with `schema_version: 1`, `task_id: TASK-003`, and empty `records`, `verification_deviations`, and `follow_up_candidates` lists. Rebuild the index with `taskctl reindex`.

This single example demonstrates all relation shapes. A real task includes only relations that actually apply.

## Readiness

A task is `ready` only when:

```text
all hard relations are done
AND verification.status is ready or a justified waiver
```

Otherwise it remains `pending`. `integration_order` may delay only its named verification gate. `coordination` requires a working arrangement, not artificial serialization.

## Verification metadata

Code and user-visible behavior default to:

```yaml
verification:
  required: true
  status: pending
  spec: ".tasks/verification/TASK-ID.yaml"
  designed_by: null
  designed_at: null
  basis_fingerprint: null
  waiver_reason: null
```

Use `status: waived` only for pure documentation, records, or deterministic mechanical work fully covered by a structural check. Record a concrete `waiver_reason`; risk level alone never grants a waiver.

## Status and risk

Statuses: `pending`, `ready`, `in_progress`, `awaiting_acceptance`, `blocked`, `needs_arch_review`, `done`, `failed`.

Risk levels:

- L1: local/internal;
- L2: cross-module;
- L3: contract, data or runtime sensitive;
- L4: architecture, security or critical-system sensitive.

Risk guides Verification Owner's evidence depth. It does not replace acceptance intent or force an LLM review for every task.

## Quality checks

- IDs and relation targets exist; no cycle or self-edge.
- Every hard relation names a concrete artifact.
- Non-hard edges do not block implementation readiness.
- Each task outcome can be independently verified.
- Scope is cohesive and not split by file.
- Acceptance IDs are stable and observable.
- Implementation hints remain hints.
- Verification metadata and parallelism are explicit.
