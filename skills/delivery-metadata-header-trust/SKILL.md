---
name: delivery-metadata-header-trust
description: "Establish which delivery metadata the handler treats as authoritative, since a client-controlled event identifier or tenant claim redirects the effect of an otherwise valid delivery. Use when the receiver derives account, tenant or event identity from headers or top-level fields rather than from the signed body"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [identify, routing, trust]
---

# Delivery Metadata Header Trust

> Establish which delivery metadata the handler treats as authoritative, since a client-controlled event identifier or tenant claim redirects the effect of an otherwise valid delivery

**Use when:** the receiver derives account, tenant or event identity from headers or top-level fields rather than from the signed body

**Avoid when:** all routing decisions are made from fields the signature demonstrably covers

## Procedure

1. Trace where the receiver obtains tenant, account and event identifiers, and mark each source as signed or unsigned.
2. Send a synthetic delivery where an unsigned metadata value differs from the signed one, and observe which the handler uses.
3. Check whether the handler trusts a header that any client can set when reaching the origin directly.
4. Note whether downstream workers read metadata the receiver wrote after verification, since that boundary can be crossed.
5. Record which values are derived from verified content and which are taken at face value.
6. Write a trust table: value, source, signed coverage, who consumes it.

## Signals

- The tenant used for processing comes from a header rather than from the signed body
- An event identifier used for deduplication is never part of the signature
- A worker trusts a field the receiver populated after verification finished
- A client-supplied header reaches the handler when the request bypasses the gateway

## Patterns

**1. Trust table**

```text
value | source | signed | consumer
tenant_id | body field | yes | handler
event_id | header | no | dedup store
target_url | request field | no | outbound sender
```

**2. Split probe**

```text
same signed body, different unsigned metadata: whichever value the handler acts on is the one it trusts
```

**3. Boundary note**

```text
record the point where the receiver writes metadata for downstream use, because anything added after verification carries no signature
```

## Pitfalls

- Verifying a signature correctly and then routing the event on an unsigned identifier
- Assuming a header was stripped at the edge without checking the direct-to-origin path
- Missing that a downstream worker re-reads metadata the verification step never saw

## Done when

- A trust table marks each routing value as signed or unsigned with its consumer
- A split probe confirms which source the handler actually acts on

## References

- [OWASP - Mass assignment and untrusted input](https://owasp.org/www-project-web-security-testing-guide/)
- [PortSwigger - HTTP request header injection](https://portswigger.net/web-security/request-smuggling)
