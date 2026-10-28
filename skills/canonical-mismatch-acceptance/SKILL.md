---
name: canonical-mismatch-acceptance
description: "Deliver a body whose bytes differ from the ones the signature covers, so the report can say whether verification protects content or only a snapshot of it. Use when the canonical string is understood and you need to know what happens when delivered bytes differ from signed bytes"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, canonicalization, integrity]
---

# Canonical Mismatch Acceptance

> Deliver a body whose bytes differ from the ones the signature covers, so the report can say whether verification protects content or only a snapshot of it

**Use when:** the canonical string is understood and you need to know what happens when delivered bytes differ from signed bytes

**Avoid when:** verification demonstrably hashes the exact received buffer and a formatting-variant test already confirms it

## Procedure

1. Reconstruct the canonical string from your earlier audit and sign a synthetic body with it.
2. Send a delivery whose bytes differ from the signed ones while parsing to the same logical content, changing only formatting.
3. Send a second delivery where the content itself differs, to separate a formatting tolerance from a content bypass.
4. Capture status, body and timing for each and compare against the control with an identical body.
5. Check whether the receiver re-serializes the parsed body before hashing, which explains a formatting pass.
6. Record three rows: identical bytes, different formatting, different content, each with its verdict.

## Signals

- Reordered JSON keys or added whitespace still verify successfully
- Content that differs from the signed bytes is processed after a pass
- The handler hashes a re-serialization of the parsed object rather than the buffer
- A control delivery with identical bytes behaves differently from a formatting variant

## Patterns

**1. Three-row table**

```text
variant | bytes vs signed | parsed content | status
identical | equal | equal | 200
reformatted | differ | equal | 200  <- re-encode in play
different content | differ | differ | 401
```

**2. Control rule**

```text
always include the identical-bytes control; without it a failure could be a bad secret rather than a canonicalization effect
```

**3. Re-encode diagnosis**

```text
a formatting pass plus a content rejection means the handler verifies a re-serialized form, which is still worth reporting as a brittle scheme
```

## Pitfalls

- Reporting a content bypass when only a formatting variant was tested
- Signing with a reconstructed canonical string that was never validated against a real delivery
- Omitting the control row and misattributing the failure

## Done when

- Three variants, identical, reformatted and different content, each have a recorded verdict
- The result is attributed to raw bytes or re-serialized form with the evidence shown

## References

- [RFC 8785 - Canonicalization](https://www.rfc-editor.org/rfc/rfc8785)
- [CWE-345 - Insufficient verification of data authenticity](https://cwe.mitre.org/data/definitions/345.html)
