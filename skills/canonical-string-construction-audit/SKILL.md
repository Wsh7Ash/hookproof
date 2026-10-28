---
name: canonical-string-construction-audit
description: "Reconstruct precisely which bytes the verifier hashes, including separators and ordering, so a signature mismatch is explained by the canonical form rather than by guesswork. Use when the scheme statement names signed bytes but the exact concatenation, separators and field order are unconfirmed"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [identify, canonicalization, signature]
---

# Canonical String Construction Audit

> Reconstruct precisely which bytes the verifier hashes, including separators and ordering, so a signature mismatch is explained by the canonical form rather than by guesswork

**Use when:** the scheme statement names signed bytes but the exact concatenation, separators and field order are unconfirmed

**Avoid when:** the provider specifies an explicit canonical form and your reconstruction reproduces a valid signature from a captured delivery

## Procedure

1. Write the canonical string as a template with named placeholders for every element the scheme includes.
2. List the separators explicitly, including whether an empty element contributes an empty field rather than disappearing.
3. Reproduce one captured signature yourself using the known secret and compare byte for byte with the header value.
4. If reproduction fails, vary one element at a time: separator, order, encoding of the body, presence of the timestamp.
5. Record the encoding used for each element, such as lowercase hex versus base64, because a mismatch here looks like a bad secret.
6. Store the working template as the reference against which later canonicalization tests are compared.

## Signals

- Your reconstruction of a valid signature does not match the header value
- An empty or optional element disappears from the string rather than leaving an empty field
- The handler joins fields in a different order from the one the provider documents
- The body is hashed after re-encoding rather than as the raw received bytes

## Patterns

**1. Template**

```text
canonical = timestamp + "." + raw_body_bytes
empty element -> contributes "" between separators, it does not vanish
encode -> lowercase hex for HMAC-SHA256 output
```

**2. Reproduction check**

```text
recompute from a captured delivery with the known secret; a byte match proves you understand the scheme, a mismatch means one element is wrong
```

**3. One-at-a-time rule**

```text
when reproduction fails, change exactly one thing per attempt and record which change produced the match
```

## Pitfalls

- Concluding the secret is wrong when the real defect is an ordering or encoding difference
- Ignoring optional fields that the provider includes only when present
- Trusting a re-encoded body when the scheme signs the raw bytes you received

## Done when

- A canonical template with named placeholders and explicit separators is written down
- At least one captured signature is reproduced byte for byte from the known secret

## References

- [RFC 8785 - Canonical JSON](https://www.rfc-editor.org/rfc/rfc8785)
- [Stripe - Computing a signature](https://docs.stripe.com/webhooks/signature)
