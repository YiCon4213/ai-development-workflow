---
name: coding-owner
description: Use when executing one repository task whose architecture and pre-implementation verification handoff are ready.
---

# Coding Owner

## Purpose

Own one task from claim through implementation, developer tests, verification execution, repair and user acceptance.

```text
claim -> implement -> developer tests -> execute verification spec
      -> repair -> automated acceptance -> detailed user acceptance
      -> awaiting_acceptance -> user decision -> done -> stop
```

Verification Owner designs independent proof before coding. Coding Owner executes that proof and retains all later operational ownership; ordinary failures never bounce back to Verification Owner.

## Rule Precedence

Apply, in order:

1. the user's current explicit instruction;
2. applicable repository instructions;
3. approved architecture, task card and verification specification;
4. this skill;
5. local implementation choices.

Use the more specific compatible rule without expanding authorization. A frozen oracle or architecture conflict requires a decision, not a silent compromise.

## Read Progressively

1. Read the repository router and task-workflow rules.
2. Locate the named task. Read only its task block, hard relations, referenced verification spec and relevant architecture section.
3. Read affected module rules, entry points, call path and adjacent tests as needed.
4. Load detailed references only at their trigger below.

Do not read the full task history, all architecture sections or every module manual by default.

## Claim Eligibility

A new or unstarted code task is claimable only when:

- its main status is `ready`;
- every hard relation is `done`;
- `verification.status` is `ready` and the referenced file exists; or it is `waived` with a concrete valid reason;
- no other Coding Owner owns it.

If verification is missing, remain unclaimed and report the missing handoff. Do not design the supposedly independent oracle yourself.

For an existing `in_progress` task, confirm recorded ownership and the approved verification basis before continuing. Missing pre-implementation verification must be reported, not manufactured after coding.

Persist a valid claim before editing:

```yaml
status: in_progress
result:
  owner: "<current coding agent>"
  attempts: 0
```

Own one primary task. When several tasks are eligible and the user did not name one, present the candidates and ask which to claim.

## Form Working Intent

Before the first meaningful change, state briefly:

```markdown
## Current Understanding
## Change Point
## Implementation Intent
## Verification Handoff
```

Treat this as a working hypothesis, not a second architecture report. Repository evidence controls local implementation details while frozen outcomes and boundaries remain authoritative.

## Implement Within Scope

Prefer the smallest coherent change:

```text
reuse existing design > extend abstraction > local refactor > new abstraction > new subsystem
```

Classify discoveries as required now, follow-up candidate or unrelated. Do not turn the task into general cleanup. Preserve the goal, scope, constraints, forbidden behavior, acceptance IDs and escalation conditions.

Use test-driven development for new behavior and bug fixes: failing developer test, minimal change, passing focused test, refactor while green. Developer tests follow implementation structure; they complement rather than replace independent verification cases.

## Execute Verification and Repair

When implementation behavior is ready, read [references/verification-execution.md](references/verification-execution.md). Run the cheapest relevant feedback first, then every required case and broader regression gate named by the specification.

Coding Owner may adapt commands, files, fixtures, selectors and an equivalent or stronger test layer. Record the original mechanism, replacement, repository evidence and equivalence argument.

Do not change without Architect/user decision:

- expected business or forbidden outcomes;
- security, permission, privacy or data-integrity boundaries;
- required risk cases;
- a stronger evidence class to a weaker one without demonstrated equivalence;
- approved task scope or public contract.

Diagnose and repair implementation, fixture, test-environment and ordinary regression failures in the same ownership context. Do not return them to Verification Owner.

## Failure Classification

Classify before changing anything:

- `IMPLEMENTATION_BUG`
- `WRONG_ASSUMPTION`
- `INCOMPLETE_SCOPE`
- `REGRESSION`
- `TEST_ENVIRONMENT`
- `DEPENDENCY_ISSUE`
- `STALE_VERIFICATION_MECHANISM`
- `FROZEN_ORACLE_CONFLICT`
- `ARCHITECTURE_CONFLICT`

Adapt wrong assumptions only inside the approved boundary. Set `blocked` only for a real unavailable external requirement. Set `needs_arch_review` when frozen truth, public contracts, data/security boundaries or substantial scope must change.

An effective repair attempt has a revised hypothesis, targeted change and new verification evidence. Retry while evidence supports a path; repeated guessing is not repair.

## Automated Acceptance

Before handoff:

- every AC and VER identifier has an explicit result;
- required commands ran against the recorded workspace snapshot;
- `skipped`, `no_tests`, flaky retry, baseline failure, environment blocked and unverified remain distinct from pass;
- no forbidden shortcut or unapproved boundary change was introduced;
- relevant regression, build and runtime checks passed or are reported truthfully.

Persist concise evidence or artifact references, not large raw logs.

## User Acceptance

After automated acceptance passes, read [references/user-acceptance.md](references/user-acceptance.md). Convert the verification spec into a complete, task-specific E2E checklist with prerequisites, data, ordered steps, expected observations, evidence and cleanup.

Set `status: awaiting_acceptance`, persist automated evidence, present the checklist and stop. Never mark `done` before the user's explicit overall confirmation.

If the user rejects acceptance, return to `in_progress`, diagnose, repair and rerun affected automation before issuing an updated checklist. Retain ownership; do not send the task back to Verification Owner.

After user acceptance, record `accepted_at` plus one user-acceptance evidence item, mark `done`, refresh dependent readiness and stop. Do not claim the next task.

## Documentation and Git

Update only authoritative task, verification-deviation and required project documents. Do not create duplicate summaries or next-task prompts.

Git actions are authorization-driven. Default: do not commit, push, merge or open a pull request. Completion never grants that permission.

## Completion Report

Report final status, implemented outcomes, AC/VER evidence, user acceptance evidence, affected areas, recorded deviations, follow-up candidates and Git state. The task is complete only after required automated evidence and explicit user acceptance are persisted.
