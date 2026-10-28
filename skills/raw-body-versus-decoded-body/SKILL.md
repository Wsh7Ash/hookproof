---
name: raw-body-versus-decoded-body
description: "Determine whether the signature is verified over the exact bytes received or over a re-encoded parse of them, because the difference decides whether legitimate deliveries fail and which bypasses exist. Use when the receiver parses a body before verifying it, or a framework middleware decodes content before your handler runs"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [identify, parsing, signature]
---

# Raw Body Versus Decoded Body

> Determine whether the signature is verified over the exact bytes received or over a re-encoded parse of them, because the difference decides whether legitimate deliveries fail and which bypasses exist

**Use when:** the receiver parses a body before verifying it, or a framework middleware decodes content before your handler runs

**Avoid when:** verification demonstrably runs on a buffer captured before any parsing or decoding step

## Procedure

1. Read the receiver path and identify the exact point where the body is first parsed or decoded relative to verification.
2. Capture the raw bytes of a delivery and the parsed object the handler sees, and compare their serializations.
3. Check how the framework handles content encoding and charset, since either can change bytes between receipt and verification.
4. Send a delivery whose JSON formatting differs but whose parsed content is identical, and observe whether verification still passes.
5. Note whether re-serializing the parsed body can produce different bytes from the original, which is the classic failure mode.
6. Record the verification point as raw-buffer or re-encoded, with the code location that proves it.

## Signals

- Verification reads a parsed object rather than a request buffer
- A delivery with reordered JSON keys fails signature verification
- A compressed delivery is rejected while an uncompressed one with the same content passes
- The handler parses the body in middleware before the verification code runs

## Patterns

**1. Order record**

```text
receive -> buffer raw bytes -> verify signature over buffer -> parse -> handle
any other order is a finding to explain, not an assumption to make
```

**2. Re-encode probe**

```text
same logical content, different whitespace or key order: pass means raw bytes are used, fail means a re-encoded form is being verified
```

**3. Encoding note**

```text
record content-encoding and charset handling; if either is applied before verification, the signed bytes and the hashed bytes differ
```

## Pitfalls

- Concluding verification is broken when a framework's default body parser simply ran first
- Testing only well-formed UTF-8 bodies and missing the encoding path entirely
- Reporting a false failure because your own client re-encoded the body before sending

## Done when

- The verification point is identified with a code location and labelled raw-buffer or re-encoded
- A formatting-variant delivery demonstrates which behaviour actually occurs

## References

- [PortSwigger - HTTP request smuggling basics](https://portswigger.net/web-security/request-smuggling)
- [MDN - Content-Encoding header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Encoding)
