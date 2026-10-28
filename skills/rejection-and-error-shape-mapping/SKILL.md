---
name: rejection-and-error-shape-mapping
description: "Record how the endpoint reports a failed verification in status, body and timing, since those differences both leak verification state and determine how a provider retries. Use when the endpoint's behaviour on a rejected delivery has not been observed and later probes depend on reading that response"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [identify, errors, responses]
---

# Rejection and Error Shape Mapping

> Record how the endpoint reports a failed verification in status, body and timing, since those differences both leak verification state and determine how a provider retries

**Use when:** the endpoint's behaviour on a rejected delivery has not been observed and later probes depend on reading that response

**Avoid when:** the receiver returns one fixed response for every rejection and the provider's retry policy is documented

## Procedure

1. Capture the response for a delivery with no signature at all, including status, body and the time taken.
2. Capture the same for a malformed signature and for a well-formed signature with the wrong key.
3. Compare the three: an endpoint that distinguishes them tells an attacker how close they are to a valid value.
4. Check whether the response body names the failing check, which decides what a sending partner sees in their dashboard.
5. Note which statuses the provider treats as retryable, since a 500 on a bad signature creates a retry storm.
6. Record the response map beside the boundary so later probes can be read against it without re-deriving the baseline.

## Signals

- The body says signature expired for one case and signature missing for another
- A bad signature returns 500, which the provider interprets as a transient failure worth retrying
- Rejection timing is visibly different from acceptance timing
- The error body includes a stack trace or a fragment of the secret comparison

## Patterns

**1. Response map**

```text
case | status | body marker | median ms
no signature | 401 | missing signature | 9
malformed | 401 | malformed header | 8
wrong key | 401 | invalid signature | 10
valid | 200 | ok | 34
```

**2. Retry class**

```text
4xx usually terminal, 5xx usually retried; record which class this endpoint uses for a bad signature
```

**3. Leak check**

```text
if bodies differ per failure reason, record the exact markers so the fix (one uniform response) has evidence to point at
```

## Pitfalls

- Reporting a timing difference without enough samples to separate it from normal variance
- Missing that a 500 on rejection causes a partner to retry, which is a real operational impact
- Reading your own client's added latency as endpoint behaviour

## Done when

- A response map records status, body marker and timing for at least three rejection cases
- The retry class for each rejection status is stated with the provider policy it comes from

## References

- [OWASP - Error handling guidance](https://owasp.org/www-project-web-security-testing-guide/)
- [Stripe - Webhook retries](https://docs.stripe.com/webhooks#handle-retry-events)
