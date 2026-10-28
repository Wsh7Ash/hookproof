---
name: constant-time-comparison-enforcement
description: "Replace generic equality on signature bytes with a constant-time comparison, closing the timing signal before anyone tries to measure it. Use when the verifier compares signatures or secrets with a language-level equality operator"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [harden, cryptography, timing]
---

# Constant-Time Comparison Enforcement

> Replace generic equality on signature bytes with a constant-time comparison, closing the timing signal before anyone tries to measure it

**Use when:** the verifier compares signatures or secrets with a language-level equality operator

**Avoid when:** a constant-time helper is already used and a reading of the call confirms it

## Procedure

1. Find every comparison of a signature, secret or derived value against attacker-controlled input and record its call site.
2. Replace generic equality with the standard library's constant-time comparison helper for each of those sites.
3. Check the comparison runs on decoded bytes of equal expected length, not on a raw string of attacker-chosen length.
4. Add a length check before the comparison so a mismatched length fails fast without leaking prefix information.
5. Re-run the timing probe groups and record that the code path now uses the helper, with the measurement as support.
6. Record the changed call sites so a later refactor cannot quietly reintroduce an equality operator.

## Signals

- A signature is compared with a generic equality operator
- Comparison runs before a length check, on bytes of attacker-chosen length
- A hand-rolled comparison loop compares and returns early on the first differing byte
- Only one of several verification paths was converted

## Patterns

**1. Call-site list**

```text
file/function | current comparison | replacement
hooks/verify.py:signature_eq | == | constant_time_compare
hooks/jwt.py:claim_eq | == | constant_time_compare
```

**2. Length rule**

```text
check decoded length first, then compare in constant time; both steps recorded as separate code positions
```

**3. Retest instruction**

```text
re-run the interleaved timing groups from the probe phase and note the code change alongside whatever the measurements now show
```

## Pitfalls

- Converting one comparison while a second path in the same handler still uses equality
- Comparing hex strings of different lengths without a length check in front
- Claiming the timing signal is gone without re-running the measurement you took before

## Done when

- Every comparison against attacker-controlled input uses a constant-time helper with a preceding length check
- The retest result is recorded next to the call-site list

## References

- [CWE-208 - Observable timing discrepancy](https://cwe.mitre.org/data/definitions/208.html)
- [PortSwigger - Timing attacks](https://portswigger.net/web-security/authentication)
