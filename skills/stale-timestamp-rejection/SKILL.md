---
name: stale-timestamp-rejection
description: "Send a signature built over an old timestamp to see whether the tolerance is enforced, since an unenforced window turns every captured delivery into a reusable one. Use when the scheme signs a timestamp and the tolerance has been identified but not exercised"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, timestamp, replay]
---

# Stale Timestamp Rejection

> Send a signature built over an old timestamp to see whether the tolerance is enforced, since an unenforced window turns every captured delivery into a reusable one

**Use when:** the scheme signs a timestamp and the tolerance has been identified but not exercised

**Avoid when:** the boundary forbids replaying signed deliveries, in which case this test is recorded as skipped

## Procedure

1. Re-read the boundary: if replaying a signed delivery is forbidden, record this test as skipped with the reason and stop.
2. Otherwise compute a signature over a timestamp older than the documented tolerance using a synthetic body you own.
3. Send it once and capture status, body and timing, then repeat to confirm stability.
4. Send a second value just inside the tolerance and a third just outside it to find the boundary the handler actually enforces.
5. Compare the enforced boundary with the documented tolerance, since deployments often differ from documentation.
6. Record three rows: inside, at the boundary and outside, each with its verdict.

## Signals

- A timestamp well beyond the documented tolerance is accepted
- The enforced boundary differs noticeably from the configured value
- Stale deliveries are accepted while future ones are rejected without limit
- The tolerance is never checked because the handler only compares the signature

## Patterns

**1. Boundary rows**

```text
offset | expected | observed
-120s (inside 300s) | accept | accept
-301s (outside) | reject | reject
-3600s | reject | accept  <- tolerance not enforced
```

**2. Skip record**

```text
replay of signed deliveries forbidden by boundary -> skipped, reason recorded, no request sent
```

**3. Symmetry note**

```text
record whether the same bound applies to future timestamps; an asymmetric check leaves a different hole
```

## Pitfalls

- Running a replay test the boundary explicitly forbids and turning a pass into a scope breach
- Testing only one stale offset and never locating the actual enforced boundary
- Concluding the tolerance is enforced when a signature over an unsigned timestamp was simply replaced

## Done when

- Inside, boundary and outside offsets each have a recorded verdict, or the test is recorded as skipped with a reason
- The enforced boundary is compared against the documented tolerance in the report

## References

- [Stripe - Timestamp tolerance](https://docs.stripe.com/webhooks/signature)
- [CWE-294 - Authentication bypass by capture-replay](https://cwe.mitre.org/data/definitions/294.html)
