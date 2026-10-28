---
name: signature-header-vocabulary-mapping
description: "Map every header a delivery can carry and classify which are provider-set, which are client-controlled, and which the handler actually reads. Use when a delivery arrives with several candidate headers and it is unclear which of them the receiver trusts"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [identify, headers, trust]
---

# Signature Header Vocabulary Mapping

> Map every header a delivery can carry and classify which are provider-set, which are client-controlled, and which the handler actually reads

**Use when:** a delivery arrives with several candidate headers and it is unclear which of them the receiver trusts

**Avoid when:** the receiver reads exactly one documented header and all others are stripped at the edge

## Procedure

1. Capture the full header list from a provider-generated delivery and label each header with its likely producer.
2. Re-send a synthetic delivery with one candidate header added or altered to see whether the handler's decision changes.
3. Separate headers the sender sets from headers a client can set on any request reaching your edge.
4. Note headers that duplicate the signature information in a weaker form, such as an unsigned summary of the payload.
5. Record which header the handler reads for its verification decision, and which headers it merely logs or passes downstream.
6. Write a mapping table so later tests know which header they are manipulating and which one carries the verdict.

## Signals

- Two headers both claim to carry a signature and only one is verified
- A header that identifies the sender is copied from a value any client can supply
- The handler reads a header the edge never strips from external traffic
- A downstream worker trusts a header the receiver set after verification

## Patterns

**1. Header map**

```text
header | producer | read for verdict | stripped at edge
stripe-signature | provider | yes | no
x-forwarded-for | client | no | no
x-internal-user | receiver | downstream only | no
```

**2. Mutate test**

```text
add one candidate header to a synthetic delivery and observe whether the accept or reject decision changes; that header carries authority
```

**3. Boundary note**

```text
which headers arrive already stripped by the gateway? record them, because a header stripped upstream can never be the defect you are hunting
```

## Pitfalls

- Assuming a header named signature is the one the handler actually checks
- Mutating two headers in one delivery and losing the attribution for the changed decision
- Forgetting that a header set by your own edge can be spoofed by a client that reaches the origin directly

## Done when

- A header map lists producer, verdict authority and edge treatment for every candidate
- A mutate test confirms which header actually drives the accept or reject decision

## References

- [MDN - HTTP headers overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers)
- [OWASP - Input validation cheat sheet](https://cheatsheetseries.owasp.org/)
