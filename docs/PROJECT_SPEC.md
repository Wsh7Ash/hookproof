# Project Spec — hookproof

## Name

`hookproof`

## Category

`webhook-tooling`

## Target user

Engineers and authorized testers responsible for receivers that accept third-party deliveries, and for the outbound callback targets an application fetches on a partner's behalf.

## Problem

Webhook verification is written once, under schedule pressure, and never re-read. The questions that decide whether it actually works are never written down anywhere the next person can find them: whether the signature covers the raw bytes or a re-encoded parse, whether the timestamp is inside the signed string, whether the acceptance window is two-sided, whether an empty header counts as missing, whether a duplicate reaches the side effect twice, and whether an outbound callback target is validated again after resolution. Each of these is re-derived from scratch during every incident, and agents have no structured skill files to load — so verification keeps being re-implemented by people who have never seen the failure modes.

## Solution

A corpus of 50 unique, validated webhook security skills organised into six phases (`scope`, `identify`, `probe`, `confirm`, `harden`, `document`), a validator that enforces quality floors, and a `hookplan` CLI that turns an endpoint configuration into a phase-ordered verification plan with honest thin-coverage reporting.

## Core workflow

```text
author/edit corpus  ->  build  ->  skills/ + pack.json + results/
                                    |
                                    v
                          validate (50/50 gate)  ->  pytest  ->  CI
                                    |
                                    v
                       hookplan --config-file endpoint.json -> ordered plan
```

## Must-have features

- 50 unique skills with unique slugs and titles across the six phases.
- Validator with structural, strength and hygiene rules; exit `0` only at 50/50.
- Deterministic renderer; committed files proven in sync by tests.
- `hookplan` producing a phase-ordered plan from a JSON configuration, with thin coverage derived from matches rather than from the truncated plan.

## Nice-to-have (explicitly out of scope for v1)

- Sending real deliveries. The pack makes **no** network requests.
- Implementing a verification scheme on the reader's behalf.
- Provider-specific SDK integration or secret distribution.

## Acceptance tests

1. `validate` exits 0 and reports 50/50.
2. `pytest -q` passes 22 tests, including regeneration equality, drift detection and the evidence-hygiene rules.
3. `hookplan` — round-trips the checked-in example configuration, covers all 6 phases with `--top 6`, and reports every phase as thin coverage for a configuration that matches nothing.
4. A generated build lands byte-identically in a clean temp directory.

## Authorized-use constraint

This is a defensive and methodology pack. Skills describe identification, probing you are cleared to perform, confirmation, hardening and disclosure. The corpus contains no weaponized payload, no exploit chain and no live target data; `SECURITY.md` states the boundary and the reporting path.