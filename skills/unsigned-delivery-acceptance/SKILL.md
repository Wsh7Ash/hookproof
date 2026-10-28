---
name: unsigned-delivery-acceptance
description: "Send one synthetic delivery with no signature at all and record whether the endpoint accepts it, which is the single highest-value check a receiver can fail. Use when an inbound endpoint has not yet been observed rejecting a delivery that carries no signature header"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, signature, baseline]
---

# Unsigned Delivery Acceptance

> Send one synthetic delivery with no signature at all and record whether the endpoint accepts it, which is the single highest-value check a receiver can fail

**Use when:** an inbound endpoint has not yet been observed rejecting a delivery that carries no signature header

**Avoid when:** the endpoint has already returned a rejection for an unsigned delivery in the current build

## Procedure

1. Confirm the boundary permits sending a delivery to this endpoint and record the rate budget you will stay inside.
2. Construct one synthetic event with an invented identifier and no signature header of any kind.
3. Send it once and capture status, body, timing and every response header verbatim.
4. Repeat a second time to confirm the answer is stable rather than a race with a cold handler.
5. Check the receiver's own log or handler code to see which branch produced the observed response.
6. Record the result as accepted or rejected with both response captures, because this is the baseline every later probe reads against.

## Signals

- The endpoint returns 200 for a body that carries no signature header
- The handler processes the event and only logs that a signature was absent
- A rejection is produced by a downstream validator while the receiver already acted
- The first request behaves differently from the second on an unsigned delivery

## Patterns

**1. Baseline pair**

```text
POST /hooks/demo  (no signature header) -> 401 missing signature, 9ms
POST /hooks/demo  (no signature header) -> 401 missing signature, 8ms  <- stable
```

**2. Decision record**

```text
accepted | rejected | rejected-after-processing; the third case is a finding because the effect already happened
```

**3. Branch note**

```text
record which handler branch produced the response: verify middleware, controller check, or downstream worker
```

## Pitfalls

- Recording a 200 that came from an error page or a gateway rather than from the receiver
- Testing against a staging receiver and reporting it as the production behaviour
- Sending one request and calling it stable without the confirming repeat

## Done when

- Two unsigned deliveries return recorded status, body and timing with a stable verdict
- The handler branch responsible for the verdict is identified

## References

- [PortSwigger - Authentication vulnerabilities](https://portswigger.net/web-security/authentication)
- [OWASP - Broken authentication guidance](https://owasp.org/www-project-top-ten/)
