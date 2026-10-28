---
name: algorithm-and-version-confusion
description: "Examine whether the signature value carries an algorithm or version field the verifier trusts, because a self-declared algorithm is a comparison the caller gets to choose. Use when the signature format includes a version, algorithm or key-identifier segment parsed from the value"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, signature, algorithm]
---

# Algorithm and Version Confusion

> Examine whether the signature value carries an algorithm or version field the verifier trusts, because a self-declared algorithm is a comparison the caller gets to choose

**Use when:** the signature format includes a version, algorithm or key-identifier segment parsed from the value

**Avoid when:** the algorithm is fixed in configuration and the value carries no field the handler reads

## Procedure

1. Parse the signature value and list every field the handler reads out of it before comparing.
2. Determine whether any field influences which algorithm or which key is used for the comparison.
3. Construct a value declaring an unsupported or weaker algorithm and record whether it is rejected outright.
4. Try a value with the algorithm segment absent, which is the classic default-branch case.
5. Check whether the key identifier selects from multiple accepted keys without authenticating the selection.
6. Record which fields the handler trusts, with a verdict per field: ignored, validated or acted upon.

## Signals

- An algorithm field is read from the value and dispatched on without an allow-list
- A missing algorithm segment falls through to an unchecked default branch
- The key identifier chooses among accepted secrets without being signed itself
- A version field is present in the format but never validated by the handler

## Patterns

**1. Field verdicts**

```text
field | read | validated | acted upon
alg | yes | no | yes  <- dispatches
kid | yes | no | selects key
v1 | yes | format only | no
```

**2. Reject rule**

```text
the safe behaviour is an allow-list of algorithms in configuration; anything read from the value and dispatched on is the finding
```

**3. Absent-field probe**

```text
send a value with the field omitted: a default branch that still compares is where confusion enters
```

## Pitfalls

- Assuming a field is informational because the provider documents it as such while the handler reads it
- Testing only a well-formed value and never the absent or unsupported variant
- Reporting a generic algorithm-confusion claim without naming the field the handler dispatches on

## Done when

- Every field parsed from the signature value has a verdict: ignored, validated or acted upon
- An unsupported or absent algorithm case has a recorded response

## References

- [CWE-347 - Improper verification of cryptographic signature](https://cwe.mitre.org/data/definitions/347.html)
- [OWASP - Cryptographic failures](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)
