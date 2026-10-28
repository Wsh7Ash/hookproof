---
name: impact-boundary-statement
description: "State precisely what an attacker could and could not do with the observed behaviour, including the precondition of already holding a valid signature, so severity is argued rather than assumed. Use when a webhook observation is confirmed and the report needs an impact statement that will survive review"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [confirm, impact, severity]
---

# Impact Boundary Statement

> State precisely what an attacker could and could not do with the observed behaviour, including the precondition of already holding a valid signature, so severity is argued rather than assumed

**Use when:** a webhook observation is confirmed and the report needs an impact statement that will survive review

**Avoid when:** the observation is a configuration note with no behavioural consequence

## Procedure

1. List the precondition required to reach the behaviour, such as possessing a valid signature or controlling a target URL.
2. State the effect once that precondition holds, in terms of what changes in the system rather than in adjectives.
3. State what remains impossible even with the behaviour, so the reader sees the boundary of the claim.
4. Separate the inbound signature finding from any outbound target finding, since their preconditions differ entirely.
5. Rank the finding against a recognised class such as replay, unsigned input or server-side request, with a reason.
6. Write the paragraph a reviewer would accept: precondition, effect, boundary, class, and nothing beyond it.

## Signals

- An impact statement reads as an adjective list with no precondition named
- Severity is stated without saying what an attacker must already possess
- The statement does not say what the behaviour cannot achieve
- Inbound and outbound consequences are merged into one undifferentiated claim

## Patterns

**1. Impact skeleton**

```text
precondition: <what the caller must already have>
effect: <what changes in the system>
boundary: <what remains impossible>
class: <replay | unsigned input | ssrf | disclosure>
```

**2. Worked example**

```text
precondition: possession of one valid signed delivery; effect: the same event can be re-delivered within the window despite dedup absent; boundary: no new event content can be introduced; class: replay
```

**3. Dual-finding rule**

```text
if both an inbound and an outbound issue exist, write two separate paragraphs; merging them hides the differing preconditions
```

## Pitfalls

- Claiming critical severity for behaviour that already requires a valid signature to reach
- Omitting the boundary, which makes a reviewer trust the claim less rather than more
- Blending an outbound target issue into an inbound signature finding so neither can be triaged

## Done when

- The statement names precondition, effect, boundary and class in that order
- Inbound and outbound consequences appear as separate claims when both exist

## References

- [OWASP - Risk rating methodology](https://owasp.org/www-community/OWASP_Risk_Rating_Methodology)
- [CVSS - Qualitative severity mapping](https://www.first.org/cvss/)
