---
name: rejection-evidence-capture
description: "Record every rejection as status, body marker, timing and header set, so a claim that verification works or fails rests on captured responses rather than on memory. Use when a probe has produced a rejection or acceptance and the result is going into a report"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [confirm, evidence, rejection]
---

# Rejection Evidence Capture

> Record every rejection as status, body marker, timing and header set, so a claim that verification works or fails rests on captured responses rather than on memory

**Use when:** a probe has produced a rejection or acceptance and the result is going into a report

**Avoid when:** the observation is a configuration reading that needs no request evidence

## Procedure

1. Capture the full response for each case: status line, every header, the body and the measured duration.
2. Label each capture with the case that produced it, such as missing, malformed, stale or wrong key.
3. Include the control capture with a valid signature, since a comparison needs both sides.
4. Record your request shape beside each response, including which header you manipulated.
5. Keep only markers and hashes for bodies containing anything sensitive; never archive a real event body.
6. Index each capture with a number and a timestamp so a reader can trace a claim to its evidence line.

## Signals

- A report claims a rejection without the response that shows it
- Captures lack timestamps, so the order of events cannot be established
- A control with a valid signature is missing from the evidence set
- A body containing sensitive content was archived in full

## Patterns

**1. Capture block**

```text
E-007 | 2026-10-28T10:14Z | case=wrong-key | req: sig header replaced | resp: 401, marker invalid signature, 10ms
```

**2. Control rule**

```text
every rejection set includes the valid-signature control captured in the same session, so both sides share conditions
```

**3. Body rule**

```text
store status, headers and a body marker; hash the body if sameness must be proven, never archive the body itself
```

## Pitfalls

- Reporting a rejection from memory when the capture was never saved
- Comparing captures from different sessions or environments and treating them as one experiment
- Archiving a delivery body that contained anything beyond your synthetic fixture

## Done when

- Every claim in the report maps to a numbered capture with status, marker, timing and request shape
- A valid-signature control capture exists for each rejection set

## References

- [NIST SP 800-61 - Incident documentation](https://csrc.nist.gov/pubs/sp/800/61/r2/final)
- [OWASP - Reporting security findings](https://owasp.org/www-project-web-security-testing-guide/)
