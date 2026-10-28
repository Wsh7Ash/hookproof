---
name: raw-buffer-verification-ordering
description: "Move signature verification to the exact bytes received, before any parsing or decoding, so what is checked and what is processed cannot drift apart. Use when the receiver parses or decodes the body before verification, or the verification point cannot be located before the parse"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [harden, parsing, signature]
---

# Raw Buffer Verification Ordering

> Move signature verification to the exact bytes received, before any parsing or decoding, so what is checked and what is processed cannot drift apart

**Use when:** the receiver parses or decodes the body before verification, or the verification point cannot be located before the parse

**Avoid when:** verification already runs on a captured buffer and a formatting-variant test confirms it

## Procedure

1. Locate the first place in the request pipeline where the body is read and record everything that touches it before verification.
2. Capture the raw request body into a buffer before any framework body parser runs, and verify against that buffer.
3. Confirm that only after a successful verification does the handler parse or decode the content.
4. Handle content encoding explicitly: either verify the received bytes or decode first and document which one you chose.
5. Re-run the formatting-variant and encoding tests from the probe phase and confirm both now behave as expected.
6. Record the pipeline order with the code location so a later refactor cannot silently move verification after parsing.

## Signals

- A framework body parser runs before the verification middleware
- Verification reads a parsed object rather than a buffer
- A formatting change in the delivered body alters the bytes that get hashed
- Content decoding happens implicitly with no recorded decision about it

## Patterns

**1. Target order**

```text
receive -> buffer raw bytes -> verify over buffer -> parse -> handle; record the file and function that owns each stage
```

**2. Reorder test**

```text
after the change, send identical logical content with different formatting: it must fail verification, because raw bytes now govern
```

**3. Decision note**

```text
document whether you verify received bytes or decoded bytes; either can be correct, silently choosing is what causes defects
```

## Pitfalls

- Moving verification earlier and breaking legitimate senders who compress their payloads
- Fixing the handler while a global middleware still parses the body first
- Assuming the new ordering holds without re-running the formatting-variant test

## Done when

- The pipeline order is recorded with code locations for each stage
- The formatting-variant retest fails verification and the result is captured

## References

- [PortSwigger - HTTP request smuggling fundamentals](https://portswigger.net/web-security/request-smuggling)
- [Stripe - Verify the raw request body](https://docs.stripe.com/webhooks/signature)
