---
name: content-type-parsing-confusion
description: "Vary the declared content type while keeping bytes identical, because a handler that parses differently per header verifies one representation and acts on another. Use when the receiver accepts more than one content type or falls back to a parser when the header is absent"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, content-type, parsing]
---

# Content-Type Parsing Confusion

> Vary the declared content type while keeping bytes identical, because a handler that parses differently per header verifies one representation and acts on another

**Use when:** the receiver accepts more than one content type or falls back to a parser when the header is absent

**Avoid when:** exactly one content type is accepted and a test confirms others are rejected before parsing

## Procedure

1. Send the identical signed body under each accepted content type and with the header absent entirely.
2. Capture status, body and timing for each case, plus which parsed structure the handler produced.
3. Check whether an unexpected content type routes to a different handler with its own verification step.
4. Note whether any path parses the body before verification, since that reintroduces the decode-order problem.
5. Confirm which content type the real provider sends, so low-risk cases can be ranked honestly.
6. Record a table of declared type, status, handler reached and verification treatment.

## Signals

- Omitting the content type falls through to a handler that skips verification
- Two content types produce different parsed structures from identical bytes
- An unexpected type returns 200 while a missing one returns 401
- A second parser runs on the same bytes and produces a different field set

## Patterns

**1. Type table**

```text
declared type | status | handler | verified
application/json | 200 | main | yes
absent | 200 | fallback | no  <- finding
form-encoded | 401 | main | yes
text/plain | 500 | unknown | parse error
```

**2. Bytes-identical rule**

```text
hold the body bytes constant across every case so the only variable is the header the handler reads
```

**3. Provider reality check**

```text
rank each row by whether the real sender can produce it; a type no provider sends is lower risk, not zero risk
```

## Pitfalls

- Changing the body along with the header and losing the ability to attribute the difference
- Ranking a fallback path as critical when no provider can trigger it, or as harmless when any client can
- Missing that a second parser sees different fields from the same bytes

## Done when

- A type table records status, handler and verification for every accepted and absent content type
- Each row notes whether a real sender can produce that case

## References

- [IETF RFC 9110 - Content-Type semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [CWE-436 - Interpretation conflict](https://cwe.mitre.org/data/definitions/436.html)
