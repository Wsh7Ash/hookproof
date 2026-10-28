---
name: signature-scheme-identification
description: "Determine how the sender signs a delivery and which header carries the result, because every later test depends on knowing exactly what the verifier is supposed to check. Use when an inbound endpoint receives deliveries and the signing scheme or signature header has not been confirmed from a real delivery"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [identify, signature, scheme]
---

# Signature Scheme Identification

> Determine how the sender signs a delivery and which header carries the result, because every later test depends on knowing exactly what the verifier is supposed to check

**Use when:** an inbound endpoint receives deliveries and the signing scheme or signature header has not been confirmed from a real delivery

**Avoid when:** the provider documents the scheme and a captured delivery confirms the header and format match

## Procedure

1. Capture one delivery from the provider's own testing facility and record the complete header set verbatim, without altering the body.
2. Identify the header carrying the signature and its format: bare hex, base64, a prefixed value, or a list of attributes.
3. Read the provider documentation for what bytes are signed: body only, timestamp plus body, method and path plus body, or a subset of fields.
4. Determine whether the scheme is symmetric (shared secret) or asymmetric (provider key pair), since the failure modes differ completely.
5. Note whether the signature is versioned or carries an algorithm field, because versioned schemes change what the canonical string contains.
6. Write a one-paragraph scheme statement naming header, format, signed bytes and key type, and keep it beside the evidence.

## Signals

- The signature header name is not mentioned anywhere in the receiver code
- A captured delivery carries several candidate headers and only one is checked
- The signed byte set described in documentation differs from what the handler computes
- The signature value carries a version or algorithm segment the handler ignores

## Patterns

**1. Scheme statement**

```text
header: stripe-signature
format: t=<timestamp>,v1=<hex hmac>
signed bytes: <timestamp>.<raw body>
key: shared secret (symmetric)
```

**2. Header candidates**

```text
common names: stripe-signature, x-hub-signature-256, x-signature, x-webhook-signature, authorization bearer when no dedicated header exists
```

**3. Signed-byte question**

```text
ask three things: does it include the timestamp, does it include method and path, does it cover the raw bytes or a re-encoded form of them
```

## Pitfalls

- Reading a scheme from a blog post instead of from a delivery your own environment received
- Assuming the body alone is signed when the timestamp is part of the signed string
- Ignoring an algorithm or version field, which is exactly where scheme confusion lives

## Done when

- A scheme statement names the header, value format, signed bytes and key type
- The statement is backed by a captured delivery from the provider's own testing facility

## References

- [Stripe - Signature verification](https://docs.stripe.com/webhooks/signature)
- [GitHub - Validating webhook deliveries](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)
