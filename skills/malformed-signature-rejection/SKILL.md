---
name: malformed-signature-rejection
description: "Feed the verifier signatures that are structurally wrong before feeding it wrong-key signatures, since a parser that mishandles malformed input often never reaches the comparison step. Use when the signature value format is known and its parser has not been exercised with structurally invalid input"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, parsing, signature]
---

# Malformed Signature Rejection

> Feed the verifier signatures that are structurally wrong before feeding it wrong-key signatures, since a parser that mishandles malformed input often never reaches the comparison step

**Use when:** the signature value format is known and its parser has not been exercised with structurally invalid input

**Avoid when:** the handler validates format explicitly and a test confirms malformed values are rejected early

## Procedure

1. Build a small set of malformed values: wrong length, invalid alphabet, missing prefix, an extra separator, a truncated pair.
2. Send each in its own request at the agreed rate and capture status, body and timing for every one.
3. Watch for cases that return 500 rather than 401, which marks an unhandled parse error on attacker-controlled input.
4. Note whether any malformed value is silently coerced into something the comparison accepts.
5. Check whether the error body differs per malformed shape, which tells a caller how the parser is structured.
6. Record a table of shape, status and whether the request reached the comparison step.

## Signals

- A truncated signature value returns 500 with a stack trace in the body
- An invalid alphabet character is stripped rather than rejected
- Different malformed shapes produce different error messages
- The handler logs an exception and continues as though verification succeeded

## Patterns

**1. Shape table**

```text
shape | example | status | reached comparison
wrong length | 10 hex chars | 401 | no
invalid alphabet | value with ! | 401 | no
missing prefix | bare hex | 401 | no
truncated pair | t=,v1= | 500 | no  <- parse error
```

**2. Silent-coercion check**

```text
if a character is stripped or a length is padded before comparison, the effective search space shrinks; record exactly what the parser normalizes
```

**3. Uniform-error rule**

```text
the target behaviour is one status and one body for every malformed shape; any variation is what the fix should remove
```

## Pitfalls

- Sending only wrong-key signatures and never exercising the parser that runs first
- Reporting a 500 without recording whether the event was processed anyway
- Overstating a timing gap measured over two requests instead of a sample

## Done when

- At least four malformed shapes each have a recorded status and a reached-comparison verdict
- Any 500 response records whether processing continued after the error

## References

- [OWASP - Input validation cheat sheet](https://cheatsheetseries.owasp.org/)
- [CWE-20 - Improper input validation](https://cwe.mitre.org/data/definitions/20.html)
