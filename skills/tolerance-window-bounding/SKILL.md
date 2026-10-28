---
name: tolerance-window-bounding
description: "Set the acceptance window to the smallest value that still covers the sender's clock skew, and make it two-sided, so the replay window stops being an unbounded convenience. Use when the timestamp tolerance is wide, one-sided, or taken from a default no one has reviewed"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [harden, timestamp, replay]
---

# Tolerance Window Bounding

> Set the acceptance window to the smallest value that still covers the sender's clock skew, and make it two-sided, so the replay window stops being an unbounded convenience

**Use when:** the timestamp tolerance is wide, one-sided, or taken from a default no one has reviewed

**Avoid when:** the window is already two-sided, deliberately chosen and smaller than the sender's retry horizon

## Procedure

1. Record the current tolerance, its directionality and where the value comes from in configuration.
2. Measure the actual clock skew between sender and receiver so the replacement value has evidence behind it.
3. Choose a window comfortably larger than measured skew but smaller than the sender's own retry horizon.
4. Enforce the window symmetrically, rejecting both stale and far-future timestamps.
5. Confirm the timestamp is inside the signed bytes so it cannot simply be rewritten.
6. Re-run the stale and future probes and record the enforced boundaries as they now behave.

## Signals

- The tolerance is larger than the provider's own retry horizon, so a retry can never fail the window
- Only stale values are rejected while future values are unbounded
- The timestamp sits outside the signed byte set
- The value is a framework default nobody has reviewed since integration

## Patterns

**1. Window record**

```text
before: 3600s, past-only, unsigned timestamp
after: 300s, two-sided, signed timestamp
measured skew: 2s; sender retry horizon: 7200s
```

**2. Constraint order**

```text
window <= sender retry horizon, and window >> measured skew; write both inequalities with the numbers you used
```

**3. Retest expectation**

```text
stale at -3600s -> reject, future at +3600s -> reject, control at 0s -> accept; all three recorded
```

## Pitfalls

- Tightening the window until legitimate deliveries start failing because skew was never measured
- Enforcing a symmetric window while the timestamp remains unsigned and replaceable
- Leaving the old value in one environment while changing another

## Done when

- The new window, its directionality and its signing status are recorded with measured skew
- Stale, future and control probes each show the expected verdict after the change

## References

- [Stripe - Signature tolerance](https://docs.stripe.com/webhooks/signature)
- [CWE-294 - Authentication bypass by capture-replay](https://cwe.mitre.org/data/definitions/294.html)
