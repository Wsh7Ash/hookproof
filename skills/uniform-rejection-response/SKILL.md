---
name: uniform-rejection-response
description: "Return one status and one body for every verification failure, so a caller cannot map your verifier's internal structure by trying different malformed inputs. Use when rejection bodies or statuses differ between failure cases as the leakage probe showed"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [harden, errors, disclosure]
---

# Uniform Rejection Response

> Return one status and one body for every verification failure, so a caller cannot map your verifier's internal structure by trying different malformed inputs

**Use when:** rejection bodies or statuses differ between failure cases as the leakage probe showed

**Avoid when:** every verification failure already returns one fixed response with only a correlation id for operators

## Procedure

1. List the distinct failure cases your probe produced and the marker each response carried.
2. Replace them with a single status and a single body covering all verification failures.
3. Keep a correlation id in the response and the specific reason in the server log only.
4. Confirm the response status is one the sender treats as terminal, so a rejection never becomes a retry loop.
5. Re-run every rejection case from the probe phase and confirm each now returns the identical response.
6. Record the before and after markers so the reduction in disclosed detail is provable.

## Signals

- Different failure cases return different messages or statuses
- A response body contains a reason string, a stack trace or a configuration key
- A verification failure returns a status the sender retries
- The specific reason is only reachable through an externally visible response

## Patterns

**1. Before and after**

```text
before: 401 missing / 401 stale / 401 wrong-key with three markers
after: 401 with one marker and correlation id, reason only in server log
```

**2. Status choice**

```text
pick a status the provider documents as terminal for this class; record the provider policy line you are relying on
```

**3. Retest sweep**

```text
re-run missing, malformed, stale and wrong-key cases; all four must return byte-identical responses
```

## Pitfalls

- Unifying the body while leaving statuses different, so detail still leaks through the code
- Choosing a status the sender retries and creating an amplification problem while fixing a disclosure one
- Removing the correlation id, which leaves operators unable to diagnose a real failure

## Done when

- All tested failure cases return an identical status and body with a correlation id
- The chosen status is confirmed terminal against the provider's documented retry classes

## References

- [CWE-209 - Generation of error message containing sensitive information](https://cwe.mitre.org/data/definitions/209.html)
- [OWASP - Error handling guidance](https://owasp.org/www-project-web-security-testing-guide/)
