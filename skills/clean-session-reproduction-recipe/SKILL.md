---
name: clean-session-reproduction-recipe
description: "Write a reproduction that starts cold every time, so a reviewer or the sending partner can replay your observation without inheriting your dedup state or stored identifiers. Use when a webhook observation must be handed to an owner or partner who will replay it in a different environment"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [confirm, reproduction, evidence]
---

# Clean Session Reproduction Recipe

> Write a reproduction that starts cold every time, so a reviewer or the sending partner can replay your observation without inheriting your dedup state or stored identifiers

**Use when:** a webhook observation must be handed to an owner or partner who will replay it in a different environment

**Avoid when:** the behaviour is deterministic and cannot depend on stored state, which a repeat delivery already proved

## Procedure

1. Identify every store that could remember your earlier deliveries: deduplication, queues, caches and any rate limiter.
2. State which of those must be empty before step one and how a reader clears or avoids each one.
3. Use a fresh synthetic event identifier for each run so prior runs cannot pre-seed the dedup store.
4. Write the request sequence in order, including waits, so it can be replayed without interpretation.
5. Record the status and response marker for each step so a reader can tell a pass from a divergence.
6. Package the recipe with the observation it produced and mark any step a partner cannot reproduce outside your session.

## Signals

- The reproduction succeeds on your machine but fails for a reviewer with a warm dedup store
- The first delivery of a session behaves differently from every later one
- A step has no recorded status, leaving the state at that point ambiguous
- The recipe depends on an identifier that was already seen by an earlier probe

## Patterns

**1. Recipe block**

```text
precondition: dedup store empty for this identifier
1. POST /hooks/demo (no signature) -> expect 401
2. POST /hooks/demo (valid signature, id test_evt_r1) -> record status
3. repeat step 2 -> record status and marker
record every status
```

**2. Fresh-id rule**

```text
each run uses a new identifier, e.g. suffixed with the run number, so no run inherits another's dedup entry
```

**3. Assumption list**

```text
if a step cannot be replayed outside your session, write it as an environment assumption rather than presenting it as deterministic
```

## Pitfalls

- Writing a reproduction that silently relies on a dedup entry your earlier probe created
- Omitting the empty-store precondition, so the reviewer sees a different result and reports a false negative
- Presenting an environment-dependent sequence as though it were deterministic

## Done when

- A numbered recipe lists every delivery with its status and the stores that must be empty first
- The recipe reproduces in a fresh context without relying on state from earlier runs

## References

- [PortSwigger - Writing reproducible reports](https://portswigger.net/web-security)
- [NIST - Evidence handling guidance](https://csrc.nist.gov/publications/detail/sp/800-86/final)
