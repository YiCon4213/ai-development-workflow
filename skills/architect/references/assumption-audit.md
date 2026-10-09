# Assumption Audit

Read this reference when a request contains a proposed technology, claimed cause, mandated order, capacity belief, compatibility belief or other statement that could change the architecture or task graph.

## Classification

Classify each material statement:

| Class | Meaning | Evidence expectation |
| --- | --- | --- |
| `fact` | Observable repository or runtime condition | Cite the file, contract, measurement or confirmed decision |
| `goal` | Outcome the user wants | Express as observable success, not a mechanism |
| `constraint` | Boundary the authorized decision-maker chooses not to violate | Name its source and cost |
| `proposal` | Suggested solution, technology or sequence | Compare with at least one viable alternative |
| `assumption` | Unverified causal, behavioral, capacity or compatibility claim | Give a counterexample or falsification check |

Use this output for material statements:

```markdown
| Statement | Class | Evidence | Challenge | Decision |
| --- | --- | --- | --- | --- |
| Redis will fix search latency | assumption | No timing breakdown yet | Bottleneck may be database query or model call | Measure first; do not make cache a hard prerequisite |
```

## Challenge rules

For each architecture-significant `proposal` or `assumption`, do at least one:

- show a plausible counterexample;
- name a smaller or safer alternative;
- define evidence that would falsify it;
- separate a user scheduling choice from a technical dependency.

Then decide one of:

- `accept_as_constraint`: the user has authority and chooses the trade-off; record the cost and do not call it a fact;
- `validate_before_commit`: evidence is missing and the decision is expensive or hard to reverse;
- `accept_with_guard`: proceed with an explicit rollback, compatibility or measurement guard;
- `replace`: evidence favors another approach;
- `decision_needed`: alternatives change product behavior, risk or authorization.

## Avoid performative disagreement

Do not challenge stable facts, low-impact wording preferences or reversible local implementation choices merely to appear creative. The purpose is to expose consequential bias, not to create debate.

Do not use the user's preferred solution as the only option and then “prove” it. Keep the goal independent from the mechanism until the comparison is complete.

## Ordering test

When a requested sequence is presented, ask:

1. Does the later task consume a concrete artifact that cannot be specified beforehand?
2. Can both implementations use an already stable interface?
3. Is the only conflict a shared file, environment or person?
4. Must only integration or end-to-end verification wait?

Only the first condition normally creates a hard dependency. The second supports parallel work, the third is coordination, and the fourth is integration order.
