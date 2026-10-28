---
name: secret-comparison-timing
description: "Look for a comparison whose duration depends on how many leading bytes match, since a timing signal on a signature comparison is a slow but real path to recovering a secret. Use when the verifier compares signatures or secrets with a generic equality operation on attacker-supplied input"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, timing, cryptography]
---

# Secret Comparison Timing

> Look for a comparison whose duration depends on how many leading bytes match, since a timing signal on a signature comparison is a slow but real path to recovering a secret

**Use when:** the verifier compares signatures or secrets with a generic equality operation on attacker-supplied input

**Avoid when:** the code uses a constant-time comparison helper and a reading of the call confirms it

## Procedure

1. Read the comparison call and record whether it uses a constant-time helper or a language-level equality operator.
2. If a live timing test is within scope, gather many samples for a correct prefix and for a wrong first byte at the agreed rate.
3. Compute a simple distribution for each group rather than relying on a single measurement.
4. Separate network and scheduling variance by interleaving the two groups rather than running them in blocks.
5. Record the code observation as the primary evidence, with any timing data as supporting context only.
6. State the practical reachability honestly: sample count, observed spread and whether it could support a claim.

## Signals

- The comparison uses a generic equality operator on attacker-controlled bytes
- A correct prefix produces a measurably different distribution from a wrong first byte
- The handler compares the secret itself rather than a hash of it
- Only a handful of samples were collected before a conclusion was drawn

## Patterns

**1. Code verdict**

```text
compare(a, b) using a constant-time helper -> safe by inspection
equality operator on signature bytes -> record the call site as the finding
```

**2. Sampling note**

```text
groups: correct-prefix and wrong-first-byte, interleaved, N samples each; record N and the spread so a reader can judge it
```

**3. Honest sentence**

```text
write what the data supports: a difference was or was not separable at N samples on this network, without claiming more
```

## Pitfalls

- Reporting a timing vulnerability from two or three measurements on a noisy network
- Measuring your own client's latency and calling it endpoint behaviour
- Treating a constant-time helper as sufficient when the value is compared before decoding

## Done when

- The comparison call site is recorded with a constant-time or generic verdict
- Any timing data states sample count, grouping method and observed spread

## References

- [CWE-208 - Observable timing discrepancy](https://cwe.mitre.org/data/definitions/208.html)
- [PortSwigger - Timing attacks in practice](https://portswigger.net/web-security/authentication)
