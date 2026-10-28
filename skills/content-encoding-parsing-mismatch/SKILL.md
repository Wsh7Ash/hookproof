---
name: content-encoding-parsing-mismatch
description: "Test deliveries whose transfer encoding differs from what the verifier expects, because bytes that change between receipt and hashing break verification in both directions. Use when the receiver accepts compressed or charset-varied bodies and verification runs after any decoding step"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, encoding, parsing]
---

# Content-Encoding Parsing Mismatch

> Test deliveries whose transfer encoding differs from what the verifier expects, because bytes that change between receipt and hashing break verification in both directions

**Use when:** the receiver accepts compressed or charset-varied bodies and verification runs after any decoding step

**Avoid when:** the handler verifies a raw buffer captured before decoding and a compressed test confirms it

## Procedure

1. Confirm the boundary permits sending a delivery with a non-default content encoding to this endpoint.
2. Send an identical synthetic event twice: once plain, once compressed, with the signature computed over the logical body in both cases.
3. Capture status, body and timing for each and note whether the difference is in the encoding layer or the signature check.
4. Add a charset variant if the receiver declares one, since a charset rewrite also changes bytes.
5. Check where in the code the decoding happens relative to verification.
6. Record which layers transform bytes before verification and what that means for legitimate senders.

## Signals

- A compressed delivery is rejected while the uncompressed equivalent passes
- Decoding happens in middleware that runs before the verification code
- A declared charset causes re-encoding that invalidates the signature
- Legitimate senders would fail if they ever compressed their payloads

## Patterns

**1. Encoding pair**

```text
plain body, correct signature -> 200
same logical body, gzip, correct signature -> 401  <- decode order matters
```

**2. Order record**

```text
receive -> decode? -> verify? -> parse?; write the actual order from the code rather than the expected one
```

**3. Sender impact**

```text
state which legitimate senders would break: any partner that compresses, or any client that sets a charset
```

## Pitfalls

- Sending a compressed body your own client encoded incorrectly and blaming the endpoint
- Reporting an availability defect for senders who cannot exist, such as one the provider never uses
- Testing only the default encoding path where no transformation occurs

## Done when

- Plain and transformed deliveries each have a recorded status and timing
- The decode-versus-verify order is identified from the code path

## References

- [MDN - Content-Encoding header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Encoding)
- [CWE-436 - Interpretation conflict](https://cwe.mitre.org/data/definitions/436.html)
