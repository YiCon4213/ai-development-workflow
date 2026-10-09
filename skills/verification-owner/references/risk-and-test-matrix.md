# Risk and Test Matrix

Read this reference when choosing verification depth, resolving which layer is sufficient, or designing checks for an LLM/Agent feature.

## Core rule

Use the lowest layer that can prove the behavior. Add a higher layer only when the lower layer cannot observe a material cross-component, runtime, security or model-quality risk. New tools require a recurring verified gap, not generic best-practice preference.

## Risk depth

| Risk | Minimum design depth |
| --- | --- |
| L1 local/internal | Core normal path, one material boundary, affected regression, short UAT if behavior is user-visible |
| L2 cross-module | AC traceability, normal/boundary/failure paths, component or integration evidence, explicit regression surface |
| L3 contract/data/runtime-sensitive | L2 plus contract and applicable permission, data, compatibility, recovery or Agent Eval cases; snapshot-bound evidence |
| L4 architecture/security/critical | L3 plus applicable security, migration, failure exercise or performance threshold and an architecture decision gate |

Risk sets depth, not test count. Omit an inapplicable category rather than create ceremonial tests; record why a category that appears relevant is omitted.

## Layer selection

| Layer | Use it to prove |
| --- | --- |
| Static/build | syntax, types, packaging, forbidden references and build compatibility |
| Unit | pure decisions, calculations, validation and local error branches |
| Component | UI state, rendering and interaction within one component boundary |
| Integration | database transactions, migrations, framework wiring and real subsystem collaboration |
| Contract | request/response, schema, event, plugin and compatibility promises |
| E2E | critical user journey and cross-layer state in a realistic environment |
| Agent Eval | tool choice, grounded facts, instruction following and prohibited model output across repeated runs |
| Security | authorization, tenant isolation, data minimization, injection and fail-closed behavior |
| Performance | stated latency/throughput/resource threshold under a defined workload |
| Migration | forward/rollback behavior and old-data compatibility |
| Recovery | retry, resume, rollback, degraded mode and state restoration |

Mocks are appropriate for branch isolation and unstable third parties. Use real infrastructure where the risk is the infrastructure contract itself: database constraints/transactions/migrations, serialization, framework wiring or cross-layer state.

## Case families

For each AC, consider and include only material families:

- normal and representative data;
- empty, minimum, maximum and malformed boundaries;
- dependency failure, timeout, cancellation and retry;
- permissions, tenant boundaries and sensitive data;
- backward compatibility and regression consumers;
- concurrency, ordering, idempotency and recovery;
- observability: failures are distinguishable from skipped, no-tests, flaky retry and unavailable environment.

## LLM and Agent dual verification

Treat model features as two coupled systems.

### Deterministic engineering

Verify tool availability and selection constraints, parameter mapping, authorization, returned data, data minimization, card/UI state, persistence, real-time/history restoration and explicit failure behavior.

### Model output quality

Define:

- fixed prompts and page/context state;
- required tools or allowed tool set;
- facts that must appear and content that must not appear;
- acceptable semantic variation rather than exact prose;
- repeated-run count proportional to risk: any feature that invokes a non-deterministic model runs at least twice and normally three times; L3 runs at least three; L4 uses a stated sample set and threshold. A deterministic simulation may run once but is engineering evidence, not model-output evaluation;
- model, prompt version and relevant parameters to record;
- scoring rule or rubric and the threshold for pass/partial/fail.

A deterministic unit test cannot prove that the model will communicate the result correctly. A conversational demonstration cannot prove permissions, data scope or deterministic calculations. Require both lines when both risks exist.

## Evidence integrity

Distinguish these outcomes: `pass`, `fail`, `skipped`, `no_tests`, `flaky_retry`, `baseline_failure`, `environment_blocked`, `unverified`. Never report the latter six as pass. Bind reports to task fingerprint and execution worktree state so evidence cannot silently outlive the code or requirement it assessed.
