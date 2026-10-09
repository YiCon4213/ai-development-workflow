# Verification Execution

Read this reference after implementation behavior exists and before claiming automated acceptance.

## Two complementary test lines

**Developer tests** are written by Coding Owner through TDD and follow implementation structure. They prove local branches, calculations, errors and regressions discovered while coding.

**Independent verification cases** come from `.tasks/verification/<TASK-ID>.yaml` and follow acceptance intent and risk. Execute every required `VER-*` case even when developer tests already pass.

Neither line substitutes for the other. A developer test suite can reproduce the implementer's blind spots; an independent case can miss useful implementation-level regressions.

## Pre-run integrity check

1. Confirm the spec `task_id` matches the claimed task.
2. Recompute or compare the task-card fingerprint.
3. Compare current acceptance, forbidden behavior and security/data boundaries with `oracle_sources` and `policy.frozen`.
4. Record current Git HEAD and dirty state.

If frozen content changed, stop with `needs_arch_review` or an explicit user decision. If only repository mechanics changed, record a deviation and continue.

## Execution order

Run the cheapest evidence that can localize failure first:

1. focused unit/component/static check;
2. affected package or module suite;
3. integration and contract checks;
4. build and compatibility checks;
5. E2E, Agent Eval, security, migration, recovery or performance evidence required by risk;
6. broad regression suite named by repository/task rules.

This order optimizes feedback; it does not make later required checks optional.

## Evidence outcomes

Use only these result classes:

| Status | Meaning |
| --- | --- |
| `pass` | Required behavior ran and matched its oracle |
| `fail` | Behavior ran and contradicted its oracle |
| `skipped` | A declared check was intentionally not run |
| `no_tests` | Command succeeded without discovering the expected tests |
| `flaky_retry` | Initial result was unstable; retain every attempt and final classification |
| `baseline_failure` | Reproduced before/current change with comparison evidence |
| `environment_blocked` | Required environment or service was unavailable |
| `unverified` | No sufficient evidence exists |

Only `pass` satisfies a required case. A baseline failure may prove non-causation, not task acceptance; state whether the task's required behavior remains covered elsewhere.

## Mapping results

Record concise evidence in `.tasks/evidence/<TASK-ID>.yaml` (not inline in the task card):

```yaml
schema_version: 1
task_id: TASK-123
verification_snapshot:
  git_head: null
  worktree_state: dirty
  task_card_fingerprint: "SHA-256 of the approved task basis"
records:
  - id: EVID-001
    covers: [AC-001, VER-001]
    type: command
    check: "repository-native command"
    status: pass
    summary: "Named checks and observed result"
    artifact: null
verification_deviations: []
follow_up_candidates: []
```

Before `awaiting_acceptance`, every required `VER-*` case whose `evidence_gate` is `automated` or `both` must have passing automated evidence, and every required `AC-*` must have a traceable automated or UAT path. Cases gated only by `user_acceptance`, and the user portion of `both`, remain explicitly pending in the prepared UAT checklist; do not pre-label them pass. Before `done`, every required UAT item and the user's overall decision must be recorded as pass. Otherwise the task must truthfully remain awaiting acceptance, in progress, blocked or escalated as appropriate.

## Adaptable-mechanism deviation

When a command, fixture, selector, file or layer is stale, record:

```yaml
verification_deviations:
  - id: DEV-001
    affects: [VER-002]
    original: "obsolete npm script"
    replacement: "current Vitest contract-test command"
    reason: "the named script no longer exists; repository uses Vitest"
    equivalence: "both observe the same public response fields and failure semantics"
    evidence: "package.json and passing named contract tests"
```

Do not add a new test framework when an existing repository-native mechanism provides sufficient evidence. Do not call a weaker layer “equivalent” merely because it is easier to run.

## Failure and repair

- Implementation bug: reproduce with a failing test, make the smallest fix, rerun affected and required regression checks.
- Fixture/test bug: prove the oracle still stands, fix only the mechanism, record the deviation when the independent spec changed.
- Environment problem: try an authorized equivalent environment only if evidence remains valid; otherwise classify `environment_blocked`.
- Frozen oracle conflict: do not change the expected result; escalate.
- Model evaluation failure: retain prompt/model/parameter/run evidence, fix deterministic inputs or implementation within scope, then rerun the complete required sample set.

Never delete tests, weaken assertions, hide failures, change permissions, swallow errors, lower thresholds or silently narrow data to manufacture a pass.
