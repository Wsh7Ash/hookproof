---
name: secret-inventory-and-ownership
description: "Establish which signing secrets exist, where each one lives and who may rotate it, so a rotation test never breaks a partner you did not intend to touch. Use when several providers sign deliveries into the application and no single list states secret location, owner and rotation rights"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [scope, secrets, rotation]
---

# Secret Inventory and Ownership

> Establish which signing secrets exist, where each one lives and who may rotate it, so a rotation test never breaks a partner you did not intend to touch

**Use when:** several providers sign deliveries into the application and no single list states secret location, owner and rotation rights

**Avoid when:** one provider signs with one secret held in a managed secret store with a documented rotation owner

## Procedure

1. List one row per provider and environment: secret identifier, storage location, retrieval code path and the role allowed to rotate it.
2. Confirm whether older secrets are still accepted, since overlapping acceptance is what makes a safe rotation possible.
3. Check whether the secret is reachable from logs, error messages, debug endpoints or client-visible configuration.
4. Note whether the sandbox uses a different secret from production, so a test never crosses the two.
5. Record the partner notification path for a rotation, including who contacts whom and how long the overlap must last.
6. Carry the inventory into the probe phase as the set of secrets you are and are not permitted to exercise.

## Signals

- Two environments share one secret with no documented reason
- A signing secret appears in a log line or a debug response
- No one can name the role allowed to rotate a secret
- Rotation would have an immediate effect because no overlap window exists

## Patterns

**1. Secret row**

```text
provider | env | location | retrieval path | rotator role | overlap
stripe | prod | secret manager | settings.stripe_signing | payments-oncall | 24h
stripe | sandbox | env var | settings.stripe_signing | payments-oncall | n/a
```

**2. Acceptance check**

```text
does the verifier accept more than one secret per provider? yes -> rotation is safe; no -> any rotation is an outage, record it before testing
```

**3. Leak sweep**

```text
search logs, error bodies and config responses for the secret prefix you know exists; a hit is a finding independent of the webhook tests
```

## Pitfalls

- Rotating a secret during an assessment and breaking a live partner integration
- Testing the production secret against a sandbox receiver or the reverse
- Finding a secret in a log and continuing with the rest of the plan without escalating it

## Done when

- Every provider and environment has a secret row with location, rotator and overlap status
- A leak sweep of logs, errors and config responses is recorded as pass or finding

## References

- [OWASP - Secrets management guidance](https://owasp.org/www-project-secretshub/)
- [NIST SP 800-57 - Key management recommendations](https://csrc.nist.gov/pubs/sp/800/57/r5/final)
