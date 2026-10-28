---
name: synthetic-event-only-policy
description: "Keep every delivery you send and every payload you store synthetic, so a webhook assessment never moves real customer data through a test harness. Use when testing requires constructing deliveries or replaying bodies and real events are present in the environment"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [scope, data-handling, privacy]
---

# Synthetic Event Only Policy

> Keep every delivery you send and every payload you store synthetic, so a webhook assessment never moves real customer data through a test harness

**Use when:** testing requires constructing deliveries or replaying bodies and real events are present in the environment

**Avoid when:** the whole test surface already runs on fixture data that no customer record can reach

## Procedure

1. Identify which data classes the receiver handles: payment, identity, message or internal-only, since each raises the cost of a leak.
2. Construct synthetic events with invented identifiers and amounts that cannot collide with a real record.
3. If a real delivery must be examined, record only its headers and a hash of its body, never the body itself.
4. Store test deliveries in a directory that is excluded from version control and delete them once the report is filed.
5. Mark any step that would require a real customer record as skipped, with the reason, so the gap is visible in the report.
6. Confirm before starting that the environment you are pointed at is not receiving live customer traffic.

## Signals

- The endpoint you are about to test is the production receiver rather than a sandbox
- A captured delivery body contains a real email address, card fragment or account id
- A test payload was copied from a support ticket rather than constructed
- Test deliveries are being written into a tracked directory

## Patterns

**1. Synthetic marker**

```text
id: test_evt_0001, email: tester@example.test, amount: 100, note: synthetic fixture for authorized assessment
```

**2. Redaction rule**

```text
real delivery -> headers verbatim + sha256 of body only; if no non-sensitive region exists, record the header evidence alone
```

**3. Skip note**

```text
when a step is skipped for data reasons, write one line naming the step and the reason so the gap appears in the report
```

## Pitfalls

- Copying a live event into a test fixture and committing someone else's data to a repository
- Running synthetic tests against the production receiver where they will be processed as real
- Retaining captured deliveries after the report is filed because they were never cleaned up

## Done when

- Every payload used in the assessment carries an explicit synthetic marker
- No stored artifact contains a real customer identifier, and skipped steps are listed with reasons

## References

- [OWASP - Sensitive data protection](https://owasp.org/www-project-top-ten/)
- [NIST SP 800-53 - PII handling controls](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)
