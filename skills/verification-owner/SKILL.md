---
name: verification-owner
description: Use when an approved repository task needs an independent pre-implementation verification specification before a Coding Owner may claim it.
---

# Verification Owner

## Purpose

Turn one approved task's acceptance intent into an implementation-independent verification specification. Work once, before coding, then hand off to Coding Owner and stop.

```text
Architect-approved task -> independent oracle -> executable verification spec -> Coding Owner
```

Verification Owner does not implement production code, claim `result.owner`, run post-implementation acceptance, repair failures or return after handoff.

## Rule Precedence

Apply, in order:

1. the user's current explicit instruction;
2. applicable repository instructions;
3. the approved architecture boundary and task card;
4. this skill;
5. verification-mechanism choices.

No source may expand user authorization. If the task's expected behavior conflicts with a security, permission, data-integrity or architecture boundary, stop with one explicit decision request instead of inventing an oracle.

## Eligibility

Design a specification only when:

- the task is approved but not yet under implementation;
- its verification is required and not already `ready`;
- required oracle sources are available;
- no Coding Owner has claimed it.

Do not backfill an “independent” specification for a task already `in_progress`. For pure documentation or mechanical work, accept `verification.status: waived` only when the task records a concrete waiver reason.

## Read Progressively

1. Read the repository router and task-workflow rules only when they apply.
2. Locate the named task; read its card, relevant architecture section and oracle sources. Do not load the whole task history.
3. Establish expected truth before inspecting implementation details.
4. Then inspect only public contracts, affected boundaries and existing test conventions needed to make the checks executable.

Existing code may change how a behavior is tested. It must not define what the correct business behavior is.

## Workflow

1. Confirm scope, hard dependencies, risk level and verification eligibility.
2. Map each acceptance statement to a stable AC identifier. Preserve its meaning verbatim.
3. Derive normal, boundary, failure, permission/security and regression cases proportional to risk.
4. Select the lowest test layer that can prove each case; add higher layers only for cross-layer risks.
5. Separate deterministic engineering checks from model-output evaluation for LLM or Agent behavior.
6. Define detailed user acceptance for behavior automation cannot fully judge.
7. Record the exact task-card basis and write `.tasks/verification/<TASK-ID>.yaml`.
8. Update the task card's `verification` metadata to `ready`. Recompute main readiness: set `status: ready` when every hard relation is `done`; otherwise leave it `pending`. Do not write execution ownership or results, then stop.

Read [references/verification-spec.md](references/verification-spec.md) when writing the artifact. Read [references/risk-and-test-matrix.md](references/risk-and-test-matrix.md) when selecting layers, sizing a risk level, or verifying LLM/Agent behavior.

## Frozen and Adaptable Boundaries

Freeze:

- expected business outcomes and forbidden outcomes;
- security, permission, privacy and data-integrity boundaries;
- required risk scenarios;
- acceptance-to-evidence mapping.

Allow Coding Owner to adapt:

- commands, test files, fixtures and selectors;
- execution paths changed by repository reality;
- test layer only when the replacement provides equivalent or stronger evidence.

The verification artifact must state both lists. Coding Owner records any adaptation and its equivalence argument; it does not return ordinary test failures to Verification Owner.

## Stop Conditions

Stop without marking verification `ready` when:

- acceptance sources contradict each other;
- correct behavior requires an architecture or authorization decision;
- a hard dependency's required artifact is unavailable;
- the task is already under implementation;
- meaningful verification is impossible with the available observable interface.

Report the smallest missing decision or artifact. Do not propose implementation details as a substitute.

## Completion

Verification design is complete only when the specification is traceable, risk-proportionate, executable in the repository, detailed enough to drive user acceptance, and bound to the task snapshot. After setting `verification.status: ready`, report the spec path and hand off to Coding Owner. Do not perform later execution or review.
