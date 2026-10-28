---
name: duplicate-delivery-idempotency
description: "Deliver the same signed event twice and observe whether the second is suppressed, because idempotency is the defence that remains when a signature is valid but the event is not new. Use when the receiver processes events that carry an identifier and the deduplication behaviour has not been observed"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, idempotency, replay]
---

# Duplicate Delivery Idempotency

> Deliver the same signed event twice and observe whether the second is suppressed, because idempotency is the defence that remains when a signature is valid but the event is not new

**Use when:** the receiver processes events that carry an identifier and the deduplication behaviour has not been observed

**Avoid when:** the handler demonstrably deduplicates on a signed identifier and a test confirms the second delivery is suppressed

## Procedure

1. Confirm from the boundary that sending a duplicate delivery of your own synthetic event is permitted.
2. Send a correctly signed synthetic event once and record the response and the processing outcome.
3. Send the identical event again, twice, at the agreed rate, capturing status, body and timing each time.
4. Check whether the deduplication key comes from the signed body or from an unsigned header or timestamp.
5. Determine how long the deduplication store retains identifiers, since a short window equals no protection later.
6. Record the three deliveries with their outcomes and the deduplication key and window you identified.

## Signals

- A second identical delivery is processed exactly like the first
- The deduplication key is an unsigned header rather than a field inside the signature
- The deduplication window is shorter than the sender's own retry schedule
- Duplicates are only logged while side effects run again

## Patterns

**1. Delivery triple**

```text
1st: 200 processed
element: 200 processed  <- no suppression
element: 200 processed
```

**2. Key question**

```text
what identifies a duplicate? record source (signed body, unsigned header, request id) and window length in seconds
```

**3. Window compare**

```text
dedup window vs sender retry schedule: a window shorter than the retry schedule cannot suppress a retry
```

## Pitfalls

- Testing duplicates on an endpoint where the boundary forbids replay
- Concluding deduplication exists because the second request returned a different status without checking the side effect
- Ignoring that a timestamp-keyed dedup window resets whenever the timestamp differs

## Done when

- Three deliveries of one event each have a recorded status and processing outcome
- The deduplication key, its source and its window are identified

## References

- [Stripe - Idempotency in webhooks](https://docs.stripe.com/webhooks#handle-retry-events)
- [CWE-294 - Authentication bypass by capture-replay](https://cwe.mitre.org/data/definitions/294.html)
