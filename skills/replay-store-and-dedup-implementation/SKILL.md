---
name: replay-store-and-dedup-implementation
description: "Give the receiver a real memory of deliveries it has already processed, keyed on a signed identifier and bounded by a window that outlasts the sender's retries. Use when duplicates are processed twice because no dedup store exists or its key comes from an unsigned source"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [harden, idempotency, replay]
---

# Replay Store and Dedup Implementation

> Give the receiver a real memory of deliveries it has already processed, keyed on a signed identifier and bounded by a window that outlasts the sender's retries

**Use when:** duplicates are processed twice because no dedup store exists or its key comes from an unsigned source

**Avoid when:** a dedup store keyed on a signed field already suppresses duplicates with a reviewed window

## Procedure

1. Choose the deduplication key from inside the signed payload, such as an event identifier the sender signs.
2. Write the key to the store only after the side effect commits, so a failure between the two cannot lose the record.
3. Set the retention window longer than the sender's full retry schedule plus the tolerance window.
4. Make the write atomic with the check, so two concurrent deliveries of one event cannot both pass.
5. Confirm a second delivery returns a suppression response rather than a fresh success that hides the duplicate.
6. Re-run the duplicate probe and record the suppression behaviour and the window you configured.

## Signals

- The deduplication key comes from an unsigned header rather than the signed body
- The retention window is shorter than the sender's retry schedule
- Two concurrent duplicates both reach the side effect
- A suppressed duplicate is reported to the sender as a fresh success

## Patterns

**1. Key and window**

```text
key: signed event_id | written: post-commit | retention: 86400s | sender horizon: 7200s | atomic: yes
```

**2. Concurrency rule**

```text
check and write must be one atomic operation; separate read-then-write lets two duplicates through on a busy receiver
```

**3. Retest expectation**

```text
three deliveries of one identifier: first processed, second suppressed, third suppressed; record the three statuses
```

## Pitfalls

- Keying dedup on a timestamp, which resets the store's memory on every retry
- Recording the key before the side effect commits and losing events when processing fails
- Reporting success to the sender on a suppression, which hides a real duplicate from their dashboard

## Done when

- The key source, write ordering, retention window and concurrency approach are recorded
- A three-delivery retest shows processing followed by suppression each time

## References

- [Stripe - Idempotency keys](https://docs.stripe.com/api/idempotent_requests)
- [CWE-294 - Authentication bypass by capture-replay](https://cwe.mitre.org/data/definitions/294.html)
