---
name: rejection-response-detail-leakage
description: "Read what a rejected delivery tells the caller, since a response that names the failing check or dumps a stack trace hands an attacker a map of the verifier. Use when rejection responses have been captured and it is unclear how much verifier detail they expose"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, errors, information-disclosure]
---

# Rejection Response Detail Leakage

> Read what a rejected delivery tells the caller, since a response that names the failing check or dumps a stack trace hands an attacker a map of the verifier

**Use when:** rejection responses have been captured and it is unclear how much verifier detail they expose

**Avoid when:** every rejection returns one fixed status and body with no diagnostic detail

## Procedure

1. Collect rejection bodies from several distinct failure cases: missing, malformed, stale and wrong key.
2. Compare them line by line and record every marker that differs between cases.
3. Look for stack traces, file paths, library versions, configuration keys or fragments of the secret itself.
4. Check whether the response includes a request identifier that maps to a detailed server-side log an attacker cannot see.
5. Distinguish detail visible to an external caller from detail only present in your own logs, since they have different risk.
6. Write a leakage table with one row per failure case and the markers it exposes.

## Signals

- Each failure reason produces a distinct human-readable message
- A body contains a stack trace or a filesystem path
- The response echoes a fragment of the signature or the expected value
- Diagnostic detail intended for operators is returned to the external caller

## Patterns

**1. Leakage table**

```text
case | status | body marker | leaks
missing | 401 | signature absent | which check exists
stale | 401 | timestamp expired | tolerance enforcement
wrong key | 401 | key mismatch | key selection logic
```

**2. Uniform target**

```text
target behaviour: one status and one body for all verification failures, with a correlation id for operators only
```

**3. Severity line**

```text
detail in your own logs is fine; the same detail in the external response is the finding, and the report should say which one you observed
```

## Pitfalls

- Reporting operator-facing log detail as an external leak without checking where it appeared
- Comparing bodies from different endpoints and attributing the difference to the verifier
- Omitting the correlation id, which is often the acceptable answer rather than a defect

## Done when

- A leakage table records status and markers for at least four distinct failure cases
- The report states which detail is externally visible and which stays in server logs

## References

- [OWASP - Error handling guidance](https://owasp.org/www-project-web-security-testing-guide/)
- [CWE-209 - Generation of error message containing sensitive information](https://cwe.mitre.org/data/definitions/209.html)
