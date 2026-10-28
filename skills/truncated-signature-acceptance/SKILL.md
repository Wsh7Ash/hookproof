---
name: truncated-signature-acceptance
description: "Check whether a shortened but correctly formatted signature is accepted, because a comparison that stops early accepts a prefix instead of a whole value. Use when the signature is compared with a function that may not enforce full length equality"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, signature, comparison]
---

# Truncated Signature Acceptance

> Check whether a shortened but correctly formatted signature is accepted, because a comparison that stops early accepts a prefix instead of a whole value

**Use when:** the signature is compared with a function that may not enforce full length equality

**Avoid when:** the verifier checks decoded length before comparing, and a test confirms a truncated value fails

## Procedure

1. Produce a correctly formed signature and then versions truncated to roughly half and three-quarter length, keeping valid alphabet and encoding.
2. Send each version in its own request and capture status, body and timing.
3. Confirm that the same value with its full length is accepted, so a failure is attributable to truncation rather than to a bad secret.
4. Check whether comparison happens in constant time with an explicit length check, from the code path if it is readable.
5. Record each length tried with the verdict, so a reader can see whether acceptance shrinks with length.
6. Note any case where a truncated value is accepted, since that reduces the effective secret space materially.

## Signals

- A half-length signature is accepted while the full length is also accepted
- The verifier compares with a substring or startsWith style operation
- No explicit length check appears before the comparison
- Acceptance depends only on the first few bytes matching

## Patterns

**1. Length table**

```text
length | value shape | status
full (64 hex) | correct | 200
three-quarter | correct prefix | 401
half | correct prefix | 401
full but wrong | incorrect | 401
```

**2. Code check**

```text
look for an explicit length check before compare; absence of one is worth recording even when the language's comparison is length-aware
```

**3. Control case**

```text
always send a full-length wrong-key signature alongside, so a truncation failure cannot be confused with a bad secret
```

## Pitfalls

- Reporting truncation acceptance without the full-length control that proves the secret was right
- Truncating to a length that is invalid by encoding, which only re-tests malformed input
- Assuming the runtime's comparison is unsafe without reading the actual comparison call

## Done when

- A length table records status for full, three-quarter and half-length signatures plus a wrong-key control
- The code path shows an explicit length check or the absence of one is recorded

## References

- [CWE-187 - Partial string comparison](https://cwe.mitre.org/data/definitions/187.html)
- [PortSwigger - Authentication test techniques](https://portswigger.net/web-security/authentication)
