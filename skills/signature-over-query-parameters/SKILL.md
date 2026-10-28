---
name: signature-over-query-parameters
description: "Check whether query parameters that influence routing or tenant selection are covered by the signature, since an unsigned parameter redirects a correctly verified delivery. Use when the receiver reads tenant, account or mode from the query string on the webhook path"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, routing, signature]
---

# Signature Over Query Parameters

> Check whether query parameters that influence routing or tenant selection are covered by the signature, since an unsigned parameter redirects a correctly verified delivery

**Use when:** the receiver reads tenant, account or mode from the query string on the webhook path

**Avoid when:** the canonical string demonstrably includes the full request target and a test confirms it

## Procedure

1. List every query parameter the receiver reads and mark which of them affect routing or processing.
2. Send a correctly signed delivery to the canonical path with no query parameters, as the control case.
3. Send the same signed delivery with one routing parameter added and a second with its value changed.
4. Capture status, body and timing for each, and note which value the handler acted on.
5. Check the canonical string from your earlier audit to confirm whether the target path was included at all.
6. Record each parameter with a covered or uncovered verdict and the observed effect of changing it.

## Signals

- A tenant or account parameter lives in the query string while the canonical string covers only the body
- Adding a query parameter does not invalidate an otherwise correct signature
- Changing a routing parameter redirects processing while verification still passes
- The canonical string includes the path but not the query component of the target

## Patterns

**1. Coverage table**

```text
parameter | in query | affects routing | signed
mode | yes | yes | no  <- uncovered
id | yes | no | no
n/a | path only | - | yes
```

**2. Control-and-variant**

```text
control: signed delivery to bare path; variant: same bytes plus ?tenant=other; the difference in behaviour is the entire evidence
```

**3. Canonical reminder**

```text
the signature covers <timestamp>.<body>; if the target is not in that string, no query parameter can be covered by it
```

## Pitfalls

- Testing only path parameters when the receiver actually routes on the query string
- Reporting an uncovered parameter that has no effect on processing
- Forgetting the control case, so a rejection cannot be attributed to the added parameter

## Done when

- Every query parameter the receiver reads has a coverage verdict and an observed effect
- A control delivery to the bare path is recorded alongside each variant

## References

- [RFC 3986 - URI query component](https://www.rfc-editor.org/rfc/rfc3986)
- [PortSwigger - Web cache poisoning key confusion](https://portswigger.net/web-security/web-cache-poisoning)
