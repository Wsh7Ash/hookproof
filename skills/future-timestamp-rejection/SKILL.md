---
name: future-timestamp-rejection
description: "Check whether a timestamp far ahead of the receiver's clock is rejected, since an unbounded future window lets a captured delivery be staged for later use. Use when the tolerance is applied to stale values and its behaviour on future values has not been observed"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, timestamp, replay]
---

# Future Timestamp Rejection

> Check whether a timestamp far ahead of the receiver's clock is rejected, since an unbounded future window lets a captured delivery be staged for later use

**Use when:** the tolerance is applied to stale values and its behaviour on future values has not been observed

**Avoid when:** the handler compares against an explicit two-sided window and a test confirms both sides

## Procedure

1. Confirm from the boundary that constructing a signature over a synthetic future-timestamped body is permitted.
2. Send a delivery signed with a timestamp moderately ahead of now, then one far ahead, at the agreed rate.
3. Capture status, body and timing for each and note which side of the clock the handler appears to enforce.
4. Check the code path for a symmetric window or two separate comparisons, since many implementations only bound the past.
5. Record whether a future value would let an attacker stage a delivery for later consumption.
6. Write the result as symmetric, past-only or unbounded, with the two offsets you actually tested.

## Signals

- A timestamp hours ahead is accepted while a stale one of the same age is rejected
- The code subtracts the received time from now with no absolute bound
- Future acceptance means a delivery captured today can be replayed later at will
- Only one comparison exists where a two-sided window was assumed

## Patterns

**1. Symmetry table**

```text
offset | status
-3600s (past) | 401
+3600s (future) | 200  <- past-only enforcement
+86400s | 200
```

**2. Code shape**

```text
look for abs(now - ts) <= tolerance; two separate comparisons or a single signed subtraction indicates one-sided enforcement
```

**3. Impact sentence**

```text
state it plainly: a delivery captured at T can be delivered at T + N without detection, with N measured from your test
```

## Pitfalls

- Assuming symmetry because the documentation describes a window rather than a direction
- Reporting the theoretical risk without the offsets you actually observed
- Forgetting that an unsigned timestamp makes this test meaningless, since the value can just be rewritten

## Done when

- Past and future offsets are each tested with recorded status and timing
- The result is labelled symmetric, past-only or unbounded with the offsets shown

## References

- [CWE-294 - Authentication bypass by capture-replay](https://cwe.mitre.org/data/definitions/294.html)
- [IETF RFC 9110 - Date header semantics](https://www.rfc-editor.org/rfc/rfc9110)
