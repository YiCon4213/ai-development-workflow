# User Acceptance Handoff

Read this reference after all required automated acceptance passes and before setting `awaiting_acceptance`.

## Selection rule

Ask the user to verify what the real environment or human judgment can reveal beyond automation: end-to-end workflow, visual behavior, model communication, real permissions/data, recovery, compatibility and business semantics.

Do not repeat low-level calculations or structure checks already proved by reliable automation unless the deployed environment creates a distinct risk.

## Checklist contract

Present this information for the task as a whole, then one block per UAT case:

```markdown
## 验收对象
- Task / version / Git HEAD or workspace state

## 前置条件
- Environment, account, role, configuration and service state

## 测试数据
- Exact records or known values and how to identify them

## UAT-001 — Purpose
1. Entry point and ordered action
2. Next action

Expected:
- Observable result for each relevant step

Evidence to retain:
- Screenshot, response, record ID or log summary

Cleanup:
- Restore data, configuration or service state

Decision:
- pass / partial / fail / unverified
```

Use actual values and paths; do not leave generic placeholders in the delivered checklist. If the user must choose or supply data, say exactly what property that data needs.

## Coverage families

Select only task-relevant families, but do not omit a material risk:

- primary happy path;
- important empty/minimum/maximum or malformed boundary;
- dependency failure, timeout, cancellation or retry;
- permissions, tenant isolation, sensitive data and audit;
- persistence, refresh, history restoration or restart;
- backward compatibility and affected regression journey;
- rollback, cleanup and recovery.

For L1, one concise UAT may combine happy path and material boundary. L2 requires normal, relevant boundary/failure and regression. L3/L4 include applicable permissions/data, compatibility, recovery, migration, performance or failure exercises.

## AI and Agent cases

For every human Agent Eval case include:

- fixed user prompt;
- page, session and data context;
- expected tool or allowed tool set;
- facts that must appear;
- content that must not appear;
- expected card/page action and real-time/history behavior;
- number of repeated runs and required consistency threshold;
- model, prompt version and relevant parameters to record.

State semantic criteria rather than exact prose unless wording itself is the contract. Privacy, permission and non-hallucination hard gates cannot be averaged away by other successful runs.

## Handoff and decision

Before presenting the checklist:

1. set task status to `awaiting_acceptance`;
2. persist all automated AC/VER evidence and execution snapshot;
3. identify any baseline failure or environmental limitation without calling it pass;
4. include cleanup that prevents test data or fault injection from remaining active.

Then stop. Do not continue implementing, claim another task or mark `done` while waiting.

On rejection, capture the exact case, expected result, actual result and evidence; return to `in_progress`, diagnose, repair and rerun affected automation. Reissue the changed UAT plus any regression case needed by the fix.

On explicit overall acceptance, record one `user_acceptance` evidence item and `accepted_at`, mark `done`, refresh tasks whose hard relations are now satisfied, then stop without claiming them.
