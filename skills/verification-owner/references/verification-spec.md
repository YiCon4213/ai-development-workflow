# Verification Specification Contract

Read this reference only when creating or repairing a pre-implementation verification artifact.

## Location and authority

Store one artifact per task at `.tasks/verification/<TASK-ID>.yaml`. The task registry remains the status authority; the verification file is the authority for test intent and evidence requirements.

Use this shape:

```yaml
version: 1
task_id: TASK-123
designed_by: "<agent identity>"
designed_at: "<ISO-8601 timestamp>"

basis:
  architecture: ".tasks/architecture.md#relevant-heading"
  fingerprint_algorithm: "canonical-json-v1"
  task_card_fingerprint: "<SHA-256 of the canonical immutable-basis JSON defined below>"
  git_head: "<commit SHA or null when unavailable>"
  worktree_state: "clean | dirty"

oracle_sources:
  - id: AC-001
    source: ".tasks/cards/active/TASK-123.yaml acceptance AC-001"
    statement: "Observable behavior that must be true"

policy:
  frozen:
    - "business outcomes and forbidden outcomes"
    - "security, permission, privacy and data-integrity boundaries"
    - "required risk scenarios and evidence class"
  adaptable:
    - "commands, test files, fixtures and selectors"
    - "equivalent or stronger test layer with a recorded reason"

cases:
  - id: VER-001
    maps_to: [AC-001]
    evidence_gate: "automated | user_acceptance | both"
    risk: "Failure this case prevents"
    layer: "unit | component | integration | contract | e2e | agent_eval | security | performance | migration | recovery"
    setup:
      - "Exact precondition or fixture"
    action:
      - "Operation performed"
    expected:
      - "Observable result"
    forbidden:
      - "Result that must never occur"
    evidence:
      type: "test_report | response | screenshot | log_summary | metric"
      locator: "How Coding Owner identifies the result"

required_automation:
  - id: AUTO-001
    covers: [VER-001]
    run: "repository-native command"
    expected: "pass condition, including test count or named checks when known"

user_acceptance:
  - id: UAT-001
    covers: [VER-001]
    purpose: "Why a person adds evidence beyond automation"
    prerequisites:
      - "environment, account, permission and configuration"
    test_data:
      - "specific data and known expected values"
    steps:
      - "entry point and ordered action"
    expected:
      - "observable result for each relevant step"
    evidence:
      - "screenshot, response or record to retain"
    cleanup:
      - "how to restore changed data or state"
    decision: "pass | partial | fail | unverified"
```

Use actual values in a produced specification; angle-bracket text above explains fields and must not remain in the task artifact.

## Oracle-first two-pass design

Pass 1 reads only the user-approved goal, relevant architecture boundary, task scope/constraints/forbidden items and public business contract. Write `oracle_sources`, expected outcomes, forbidden outcomes and risk cases before reading implementation internals.

Pass 2 inspects the minimum public interfaces, existing test conventions and runnable commands needed to select layers, fixtures and evidence. If repository reality contradicts the oracle, preserve the conflict and request an architecture/user decision; do not silently conform the oracle to current code.

## Stable mapping

- Reuse acceptance IDs already present in the task card.
- If an approved task lacks AC IDs, return it for stable identifiers before verification design.
- Every AC must map to at least one `VER-*` case or an explicit `not_testable` decision requiring user/architecture resolution.
- Every `VER-*` case must name its evidence locator.
- UAT must not repeat low-level checks that automation already proves unless the real environment can expose a distinct failure.

## Snapshot binding

Calculate `task_card_fingerprint` from the task's verification basis: `id`, `goal`, `scope`, `constraints`, `forbidden`, `acceptance`, `relations` (the tool also includes `dependencies` when present), `parallelism`, `risk_level` and `escalation_conditions`. Parse those fields as data, normalize line endings inside strings to LF, recursively sort mapping keys by Unicode code point, preserve array order, serialize as minified JSON with literal UTF-8 characters and no BOM or trailing newline, then calculate SHA-256 over those bytes. Record this algorithm as `canonical-json-v1` in the artifact when a repository helper does not already implement an equivalent named format. Exclude mutable workflow fields: main `status`, `verification`, `started_at`, `result`, owners, attempts, timestamps and evidence. Record current Git HEAD when available and whether the working tree is dirty. Coding Owner applies the same algorithm and separately records the final execution snapshot, so normal claim and evidence updates do not make the specification stale.

## Task-card update

After the file is complete, update the verification handoff:

```yaml
verification:
  required: true
  status: ready
  spec: ".tasks/verification/TASK-123.yaml"
  designed_by: "<agent identity>"
  designed_at: "<ISO-8601 timestamp>"
  basis_fingerprint: "<same task-card SHA-256>"
  waiver_reason: null
```

Then refresh the task's main status from the readiness formula. If all hard relations are `done`, change `pending` to `ready`; otherwise keep `pending`. Do not set `result.owner`, `status: in_progress`, automated evidence or completion timestamps.

When blocked by contradictory oracle sources or a missing architecture decision, leave verification pending and report one decision request. A missing test tool is not automatically a blocker: choose the lowest sufficient repository-native evidence before proposing a new dependency.
