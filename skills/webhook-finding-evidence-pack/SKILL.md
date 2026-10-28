---
name: webhook-finding-evidence-pack
description: "Assemble a report where every webhook claim carries the delivery pair, the responses and the scheme statement that make it checkable by someone who was not present. Use when a webhook observation is ready to be written up for the owner or the sending partner"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [document, evidence, reporting]
---

# Webhook Finding Evidence Pack

> Assemble a report where every webhook claim carries the delivery pair, the responses and the scheme statement that make it checkable by someone who was not present

**Use when:** a webhook observation is ready to be written up for the owner or the sending partner

**Avoid when:** the finding has already been reported and only a closing note remains

## Procedure

1. State the defect in one sentence naming the endpoint, the check and the outcome, without adjectives.
2. Attach the scheme statement, so the reader knows what the verifier was supposed to check.
3. Include the delivery pair: the case that failed or passed and the control, each with status, marker and timing.
4. Record your request shape for every delivery, including which header or field you manipulated.
5. Give the reproduction recipe and the boundary document version that permitted each request.
6. State the impact in the precondition, effect, boundary form and stop there.

## Signals

- A report claims a verification defect without the delivery pair that revealed it
- The scheme statement is missing, so the reader cannot tell what was supposed to be checked
- Statuses are given without the response markers that distinguish the cases
- Impact is stated without naming the precondition an attacker would already need

## Patterns

**1. Claim skeleton**

```text
claim: <endpoint> accepts <case> because <check> is <missing/weak>
scheme: <what is supposed to be verified>
pair: <case> vs <control>, each with status and marker
impact: precondition / effect / boundary / class
```

**2. Evidence block**

```text
E-011 | case=missing-signature | req: header absent | resp: 401, marker, 9ms
E-012 | case=valid control | resp: 200, marker, 34ms
```

**3. Boundary note**

```text
attach the boundary version and mark each delivery as permitted by it, so the test itself can be audited
```

## Pitfalls

- Presenting a narrative claim when the reader needs the raw delivery pair to judge it
- Leaving out the scheme statement, so a reader cannot tell a real gap from an unusual scheme
- Inflating impact beyond what the recorded deliveries demonstrate

## Done when

- Every claim is followed by a delivery pair with status, marker, timing and request shape
- The scheme statement, reproduction recipe and boundary version are attached to the pack

## References

- [OWASP - Reporting security findings](https://owasp.org/www-project-web-security-testing-guide/)
- [NIST SP 800-61 - Incident handling guidance](https://csrc.nist.gov/pubs/sp/800/61/r2/final)
