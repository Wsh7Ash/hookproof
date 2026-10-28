---
name: retry-amplification-confirmation
description: "Confirm from the receiver's own telemetry how many deliveries your rejection actually produced, so the report states measured amplification rather than an estimate from documentation. Use when probes have produced rejections and the provider's documented retry behaviour needs checking against reality"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [confirm, retries, operations]
---

# Retry Amplification Confirmation

> Confirm from the receiver's own telemetry how many deliveries your rejection actually produced, so the report states measured amplification rather than an estimate from documentation

**Use when:** probes have produced rejections and the provider's documented retry behaviour needs checking against reality

**Avoid when:** every probe returned a status the provider never retries

## Procedure

1. Note the delivery count immediately before and after a probe family that produces a chosen rejection status.
2. Query the receiver's logs for repeated deliveries carrying the same event identifier.
3. Record the number of arrivals, their timestamps and the status the receiver returned each time.
4. Compare the measured count with the provider's documented retry expectation for that status.
5. Check whether retries continued past the end of the probe, since queued redelivery extends your footprint.
6. Report the measured multiplier beside the plan, and tell the owner if retries are still draining.

## Signals

- One crafted delivery produced several arrivals with the same event identifier
- Retries continued after the assessment session had ended
- The measured count differs noticeably from the documented expectation
- The receiver's response status sits in a class the provider treats as retryable

## Patterns

**1. Measurement line**

```text
probe at 10:14Z produced 1 delivery; arrivals with id test_evt_r1: 5 total over 90s -> measured multiplier 5x
```

**2. Comparison**

```text
documented expectation for 500: up to N retries over T; observed: M over T2 -> record both, state whether they agree
```

**3. Footprint note**

```text
if retries were still arriving when the session ended, record the drain time and tell the owner, since that is a side effect you caused
```

## Pitfalls

- Quoting the documented retry count instead of measuring what your own test produced
- Counting arrivals across two probe families that reused one identifier
- Ending the session without checking whether retries were still draining

## Done when

- A measured multiplier with arrival timestamps is recorded for at least one rejection status
- Whether retries outlived the session is stated, with a drain note if they did

## References

- [Stripe - Webhook retries and recovery](https://docs.stripe.com/webhooks#handle-retry-events)
- [GitHub - Redelivery of webhooks](https://docs.github.com/en/webhooks/using-webhooks/redelivering-webhooks)
