---
name: dual-secret-rotation-with-overlap
description: "Rotate signing secrets through a period where two are accepted, so a key change becomes a scheduled operation instead of a coordinated outage with every partner. Use when a secret needs changing, or rotation currently requires every sender to switch at the same instant"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [harden, secrets, rotation]
---

# Dual Secret Rotation With Overlap

> Rotate signing secrets through a period where two are accepted, so a key change becomes a scheduled operation instead of a coordinated outage with every partner

**Use when:** a secret needs changing, or rotation currently requires every sender to switch at the same instant

**Avoid when:** the verifier already accepts multiple secrets per provider with a documented overlap

## Procedure

1. Add a second accepted secret for the provider while keeping the current one active, and verify both compute identical results.
2. Publish the new secret to the sender through the agreed channel and record when it was acknowledged.
3. Switch verification to prefer the new secret while still accepting the old one for the overlap period.
4. Monitor verification failures during the overlap, since a sender that missed the message will surface there.
5. Retire the old secret once the overlap ends, and confirm deliveries with it are now rejected.
6. Record the rotation with both secret identifiers, the overlap window and the confirmation of retirement.

## Signals

- Only one secret can be accepted at a time, so rotation is a synchronised event
- Verification failures spike whenever a secret is changed
- No monitoring exists that would reveal a sender still using a retired secret
- The overlap period has never been exercised or measured

## Patterns

**1. Rotation timeline**

```text
T0: add new secret, both accepted | T1: sender acknowledges | T2: prefer new | T3: retire old, confirm rejection
```

**2. Failure watch**

```text
monitor verification failure rate across T0..T3; a spike at T3 means a sender never moved and the retirement is premature
```

**3. Inventory update**

```text
update the secret inventory row for both identifiers and the dates, so the next rotation starts from an accurate list
```

## Pitfalls

- Retiring the old secret before every sender has acknowledged the new one
- Adding a second secret without monitoring, so a straggler is discovered as an outage
- Leaving both secrets accepted indefinitely because the retirement step never happened

## Done when

- Both secrets were accepted during a measured overlap window with dates recorded
- Retirement is confirmed by an observed rejection of a delivery signed with the old secret

## References

- [NIST SP 800-57 - Key rotation recommendations](https://csrc.nist.gov/pubs/sp/800/57/r5/final)
- [Stripe - Rotating endpoint secrets](https://docs.stripe.com/webhooks#rotate-endpoint-secret)
