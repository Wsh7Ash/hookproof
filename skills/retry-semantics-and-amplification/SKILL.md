---
name: retry-semantics-and-amplification
description: "Establish which responses make a sender retry and how aggressively, because the retry schedule multiplies every rejection your tests produce into partner-visible volume. Use when the sending provider's retry behaviour has not been recorded and probes will cause rejections"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, retries, operations]
---

# Retry Semantics and Amplification

> Establish which responses make a sender retry and how aggressively, because the retry schedule multiplies every rejection your tests produce into partner-visible volume

**Use when:** the sending provider's retry behaviour has not been recorded and probes will cause rejections

**Avoid when:** the provider documents its retry classes and your tests stay inside a single delivery each

## Procedure

1. Read the provider's retry documentation and record which status classes trigger a retry and the backoff schedule.
2. Ask the owner whether the receiver returns a status in a retried class for a verification failure.
3. Estimate your effective volume: deliveries you send multiplied by the retry count for the status you will produce.
4. Set a stop condition that fires on repeated deliveries of the same event identifier.
5. Check whether rejected deliveries are queued for later redelivery, which extends the effect past your session.
6. Record the retry class, schedule and your measured effective volume beside the plan.

## Signals

- A verification failure returns 500, which the sender treats as transient and retries
- Retries continue after your session ends because the queue holds the event
- The same event identifier arrives several times within seconds of one test
- No one on the team knows the sender's backoff schedule

## Patterns

**1. Amplification line**

```text
1 delivery x 401 -> no retry; 1 delivery x 500 -> up to N retries over T; choose the status you produce accordingly
```

**2. Queue check**

```text
record queue depth before and after the probe family; growth that outlives the session must be reported as a side effect you caused
```

**3. Stop rule**

```text
stop after M deliveries of one event identifier and record M, rather than finishing the planned step count
```

## Pitfalls

- Choosing a response that triggers retries and unintentionally multiplying your own volume
- Measuring volume without knowing the backoff schedule and underestimating it
- Leaving queued retries to drain after the assessment ends without telling the owner

## Done when

- The retry class, schedule and estimated effective volume are recorded before the first probe
- A stop condition keyed to repeated event identifiers is defined and observed

## References

- [Stripe - Webhook retry schedule](https://docs.stripe.com/webhooks#handle-retry-events)
- [GitHub - Failed webhook delivery retries](https://docs.github.com/en/webhooks/using-webhooks)
