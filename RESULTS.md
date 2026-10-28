# Results

Reproducible evidence for the claims in `README.md`.

## Environment

- OS: Windows (MSYS2 shell)
- Python: 3.14.3 (`requires-python >= 3.10`)
- Runtime dependencies: none (standard library only)
- Dev dependency: `pytest`
- Network: none required at any point — the package performs no network requests

## Validation performed

### 1. Corpus gate — PASS

```shell
$ PYTHONPATH=src python -m hookproof validate
hookproof: 50/50 skills valid
  ok  steps>=6 signals>=4 patterns>=3 pitfalls>=3 words>=180 refs canonical https
```

```shell
$ PYTHONPATH=src python -m hookproof validate --json
{ "pack": "hookproof", "checked": 50, "valid": 50, "passed": true, "issues": [] }
```

Exit code 0. With generated files included (the default), this also byte-compares every `skills/**/SKILL.md` against a fresh render.

### 2. Test suite — PASS (22 tests)

```shell
$ PYTHONPATH=src python -m pytest -q
......................                                                   [100%]
22 passed
```

Covered: pack declares and delivers 50; slugs and titles unique; every skill passes every rule; all six phases populated and balanced; word floor holds on the weakest skill; no placeholder or machine-local path tokens; no private address literals or plaintext URLs anywhere in the corpus; committed `SKILL.md` files match the render; `pack.json` hashes match file bytes; build is byte-idempotent in a temp directory; drift is detected; `validate --json` reports 50/50; `list`/`show`/`search` behave as documented; `hookplan` orders phases, covers all six with `--top 12` and with `--top 6`, rejects a missing configuration, reports every phase as thin coverage for a configuration that matches nothing, and aggregates vocabulary across configuration keys; `results/validation.json` and `results/catalog.md` are consistent with the corpus.

### 3. Build and artifact sync — PASS

```shell
$ PYTHONPATH=src python -m hookproof build
built 50 skills -> .../hookproof/skills
$ PYTHONPATH=src python -m hookproof validate
hookproof: 50/50 skills valid
```

Regenerating twice produces byte-identical output; `test_build_is_idempotent` asserts this against a clean temp directory.

### 4. Phase distribution — as specified

| Phase | Skills |
|---|---|
| scope | 7 |
| identify | 8 |
| probe | 18 |
| confirm | 6 |
| harden | 7 |
| document | 4 |
| **total** | **50** |

`hookproof list --phase probe` returns 18; every other phase filter returns its count above.

### 5. `hookplan` on the checked-in example — PASS

```shell
$ PYTHONPATH=src python -m hookproof hookplan --config-file examples/demo-endpoint.json
# Verification plan - payments receiver
Scheme: hmac-sha256 over <timestamp>.<raw body>   Endpoints: 2   Signature headers: 2   Skills matched: 50 of 50   Plan steps: 12   Phases covered: 6/6

Endpoints: /hooks/stripe, /hooks/github
Signature headers: stripe-signature, x-hub-signature-256

## scope
...
```

Observed behaviour: 50 of 50 skills matched the configuration vocabulary; the plan contains 12 steps spread across **all 6 phases** despite `--top 12`; `missing_phases` is empty because every phase matched. With `--top 6` the plan still covers 6/6 phases.

For a configuration whose vocabulary matches nothing (`{"keywords": ["qqqqqq", "zzzzzz"]}`), `skills_matched` is 0, `plan_steps` is 0 and `missing_phases` lists all six phases — confirming thin coverage is derived from matches rather than from the truncated plan.

### 6. Cross-pack uniqueness — PASS

Against the sibling pack `edgescout` (50 skills): **0 slug overlap, 0 title overlap.**

## Commands executed

```shell
python -m hookproof validate --json
python -m hookproof validate
python -m hookproof build
python -m hookproof list --phase probe
python -m hookproof search signature replay
python -m hookproof hookplan --config-file examples/demo-endpoint.json
python -m pytest -q
```

## Known limitations

- **`hookplan` is vocabulary matching, not a verification engine.** It scores observed tokens against skill text. It will not tell you which check matters most, only which skills relate to the receiver you described and which phases you matched nothing in.
- **Thin coverage is only as good as the configuration.** A receiver with an undocumented second content type or an unnoticed outbound target will not surface those dimensions.
- **No deliveries are sent.** Nothing in this pack contacts a provider, replays an event or fetches an outbound target. Every probe still has to be executed by the tester under the boundary they established.
- **Replay tests may be forbidden.** Where the boundary forbids replaying signed deliveries, those skills record themselves as skipped rather than as passing — the register in `coverage-gap-and-skip-register` is how that stays visible.
- Tests were run on Python 3.14 locally. CI additionally covers 3.10, 3.12 and 3.13.

## Generated artifacts

| Path | What it is |
|---|---|
| `skills/**/SKILL.md` | 50 rendered skills, byte-identical to the corpus |
| `pack.json` | manifest with SHA-256 per skill file |
| `results/catalog.md` | generated skill catalog table |
| `results/validation.json` | machine-readable gate report (`passed: true`) |
| `examples/demo-endpoint.json` | the example configuration used above |