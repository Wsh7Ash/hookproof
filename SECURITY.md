# Security Policy

## Authorized use only

`hookproof` is a knowledge corpus and planning tool for **authorized** security work: assessing receivers you own, or programs whose rules explicitly permit the testing you perform. The software itself performs **no network requests** — it renders, validates and plans locally from a JSON configuration you supply.

The skills describe webhook and callback **assessment** methodology: how to identify what a verifier is supposed to check, which probes are in scope, how to confirm a result without touching real customer data, and how to harden and disclose what you found. They contain no weaponized exploit material.

## What this corpus deliberately does not contain

- No exploit payloads, proof-of-concept attack code or automation against third parties.
- No instructions for signing deliveries on someone else's behalf or forging a partner's signature.
- No credential harvesting, session theft, phishing or evasion guidance.
- No live target data, credentials or personal data. The example configuration uses `/hooks/stripe`, `/hooks/github` and synthetic event identifiers only.

## Scope discipline is built into the corpus

The opening skills exist to keep an assessment bounded and honest:

1. `callback-authorization-boundary` — the written boundary is re-read before the first delivery of every session, including whether replay is permitted at all.
2. `synthetic-event-only-policy` — payloads carry invented identifiers; a real delivery is recorded as headers plus a body hash, never as the body.
3. `delivery-volume-and-rate-budget` — a numeric ceiling and a stop condition are agreed first, because a rejection the sender retries multiplies your own volume.
4. `outbound-target-scope-classification` — outbound target requests require their own explicit permission; when forbidden, claims are marked untested rather than reported as findings.

`hookplan` always emits `scope` first for this reason: a plan that begins with a probe rather than a permission is a plan that has already skipped its most important step.

## Reporting a vulnerability in this project

If you find a defect in `hookproof` itself — for example, a validation bypass that lets a malformed skill pass the 50/50 gate — please open a private security advisory on the repository or contact the maintainer through GitHub. Do not publish exploit details before a fix is available.

## Scope of this project's own testing

All tests run locally against the checked-in corpus and the checked-in example configuration. No test sends traffic anywhere; `hookplan` reads one JSON file and scores text. Continuous integration runs the same local gates: validation, unit tests and an artifact-sync check.