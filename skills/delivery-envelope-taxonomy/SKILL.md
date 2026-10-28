---
name: delivery-envelope-taxonomy
description: "Classify the shapes a delivery can take: single JSON, form-encoded, multipart or batch array, because each shape changes what the signature must cover. Use when the receiver accepts more than one content type or a provider batches several events into one request"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [identify, content-type, parsing]
---

# Delivery Envelope Taxonomy

> Classify the shapes a delivery can take: single JSON, form-encoded, multipart or batch array, because each shape changes what the signature must cover

**Use when:** the receiver accepts more than one content type or a provider batches several events into one request

**Avoid when:** exactly one content type is accepted and verification covers the entire body

## Procedure

1. List every content type the receiver accepts, including defaults it falls back to when the header is absent.
2. For each type, record how the body reaches application code: parsed object, raw string, file upload or key-value pairs.
3. Identify whether a batch envelope carries multiple events under one signature or one signature per item.
4. Check whether an absent or unusual content type triggers a different code path with weaker verification.
5. Record which envelope shapes the provider actually sends today, so untested shapes are visible as gaps.
6. Write a taxonomy table with one row per accepted content type and the verification treatment it receives.

## Signals

- The receiver accepts both JSON and form-encoded bodies on the same path
- A batch endpoint signs the array header but not the individual items inside it
- An unexpected content type falls through to a handler that skips verification
- Multipart parsing produces fields the signature never covered

## Patterns

**1. Taxonomy row**

```text
content-type | accepted | reaches code as | signed coverage
application/json | yes | parsed dict | whole raw body
application/x-www-form-urlencoded | yes | parsed dict | whole raw body
multipart/form-data | unknown | - | not tested
```

**2. Batch rule**

```text
one signature over an array -> record whether item-level fields are covered; an unsigned item inside a signed array is a finding
```

**3. Fallback note**

```text
what happens with no content-type at all? record the status and which handler ran
```

## Pitfalls

- Testing only the default JSON path when the receiver also answers to a second content type
- Assuming a batch signature covers each item without checking what bytes it hashes
- Missing the fallback handler that runs when a header is absent or malformed

## Done when

- A taxonomy table lists every accepted content type with its verification treatment
- Batch behaviour records whether signature coverage is array-level or item-level

## References

- [IETF RFC 7578 - Multipart form data](https://www.rfc-editor.org/rfc/rfc7578)
- [MDN - Content-Type header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Type)
