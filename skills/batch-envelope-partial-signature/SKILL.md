---
name: batch-envelope-partial-signature
description: "Examine whether a batch delivery signs every item it carries or only the envelope, since an unsigned item riding inside a signed array is an unauthenticated event. Use when the receiver accepts an array or batch of events under one signature"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, batch, integrity]
---

# Batch Envelope Partial Signature

> Examine whether a batch delivery signs every item it carries or only the envelope, since an unsigned item riding inside a signed array is an unauthenticated event

**Use when:** the receiver accepts an array or batch of events under one signature

**Avoid when:** each item carries its own signature and the handler verifies each one independently

## Procedure

1. Confirm whether the receiver accepts a batch envelope and record the exact shape it parses.
2. Determine what the signature covers: the whole array, a header field, or only the first item.
3. Send a batch where one item differs from what the signature covers and observe whether it is rejected or processed.
4. Send a batch with an extra item appended and note whether the signature still validates.
5. Check whether items are processed independently, so a single unverified item reaches application logic.
6. Record coverage as envelope-only, item-level or mixed, with the delivery that demonstrated it.

## Signals

- Appending an item to a signed array does not invalidate the signature
- Items are processed independently after one envelope-level check
- Only the first item's fields appear in the signed bytes
- A modified item inside a batch is processed while the envelope signature passes

## Patterns

**1. Coverage verdict**

```text
envelope signed over full array -> append test fails signature
envelope signed over a header field -> appended item processed unverified
per-item signature -> each item checked separately
```

**2. Append test**

```text
add one synthetic item to a correctly signed batch and record status plus how many items were processed
```

**3. Process count**

```text
the number of items processed is the evidence; record it beside the status code rather than relying on the status alone
```

## Pitfalls

- Reporting batch risk without confirming the receiver actually accepts a batch shape
- Assuming envelope coverage includes items without testing an appended item
- Judging by status code when the meaningful evidence is how many items ran

## Done when

- Coverage is labelled envelope-only, item-level or mixed with a demonstrating delivery
- An appended-item test records status and the count of items processed

## References

- [CWE-345 - Insufficient verification of data authenticity](https://cwe.mitre.org/data/definitions/345.html)
- [Stripe - Batch and event objects](https://docs.stripe.com/webhooks)
