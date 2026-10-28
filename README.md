# hookproof

**50 validated webhook and callback security skills**, plus a `hookplan` CLI that turns an endpoint configuration into a phase-ordered verification plan.

Authorized testing only: every skill describes how to *identify, probe, confirm, harden and report* webhook verification behaviour on systems you own or have written permission to test. The corpus contains no weaponized payload and no live target data.

```shell
python -m pip install -e ".[dev]"
hookproof validate          # -> hookproof: 50/50 skills valid
hookproof build             # -> skills/, pack.json, results/
python -m pytest -q         # -> 22 passed
```

## Why this pack exists

Webhook verification is the kind of check that is written once, under schedule pressure, and then never re-read: someone hashes a body, compares a header, and moves on. The questions that decide whether it actually works — is the signature computed over the raw bytes or a re-encoded parse, is the timestamp inside the signed string, is the tolerance two-sided, does an empty header count as missing, does a duplicate reach the side effect twice — are never written down, and every incident report re-derives them.

`hookproof` makes that knowledge checkable. Each of the 50 skills is one self-contained procedure with a stated **use when** and **avoid when**, a numbered procedure, observable **signals**, concrete **patterns**, known **pitfalls** and **done when** criteria. A validator enforces the floor on all of them and the CLI will not report success below 50/50.

## The arc

| Phase | Count | What it covers |
|---|---|---|
| `scope` | 7 | authorization boundary, endpoint and secret inventory, outbound target scope, synthetic-only policy, rate budget, provider testing mode |
| `identify` | 8 | scheme identification, canonical string, header vocabulary, timestamp format, raw vs decoded body, envelope taxonomy, metadata trust, rejection shape |
| `probe` | 18 | unsigned acceptance, header blanking, malformed and truncated signatures, stale/future timestamps, algorithm confusion, canonical mismatch, encoding, query coverage, timing, idempotency, leakage, content type, batch, outbound scheme and redirects, retry amplification |
| `confirm` | 6 | clean-session recipe, provider-sandbox reproduction, evidence capture, timing rigor, measured amplification, impact boundary |
| `harden` | 7 | raw-buffer ordering, constant-time comparison, window bounding, dedup store, uniform rejection, egress allowlist, dual-secret rotation |
| `document` | 4 | evidence pack, scheme-aware remediation wording, coordinated disclosure, coverage-gap register |

## CLI

```shell
hookproof validate --json                # the 50/50 gate, machine-readable
hookproof list --phase probe             # 18 skills
hookproof show unsigned-delivery-acceptance
hookproof search signature replay
hookproof build                          # regenerate skills/, pack.json, results/
hookproof hookplan --config-file examples/demo-endpoint.json
```

### `hookplan`

`hookplan` is this pack's domain command. It reads a small JSON configuration describing the receiver you actually have —

```json
{
  "target": "payments receiver",
  "scheme": "hmac-sha256 over <timestamp>.<raw body>",
  "endpoints": ["/hooks/stripe", "/hooks/github"],
  "signature_headers": ["stripe-signature", "x-hub-signature-256"],
  "providers": ["stripe", "github"],
  "observed": { "tolerance_seconds": 300, "rejection_status": 500 },
  "concerns": ["does the handler verify the raw buffer before parsing"]
}
```

— flattens it into vocabulary, scores every skill against that vocabulary, and emits a verification plan in phase order. Selection is **phase-stratified**: the first pass takes the best match in each matched phase before any phase gets a second slot, so a small `--top` can never crowd out the later phases of the arc. *Thin coverage* lists phases the configuration matched nothing in, computed from matches rather than from the truncated plan.

## Loading the skills into an agent runtime

Each skill is a standalone `skills/<slug>/SKILL.md` with YAML front-matter, so any runtime that loads `SKILL.md` files can use them directly. See [docs/USAGE.md](docs/USAGE.md) for the exact Claude Code and opencode configuration.

## Layout

```text
src/hookproof/
├─ corpus/        authored skill data — the single source of truth
│  ├─ part1.py    skills 1-15   (scope, identify)
│  ├─ part2.py    skills 16-33  (probe)
│  └─ part3.py    skills 34-50  (confirm, harden, document)
├─ model.py       Skill dataclass + strict dict loading
├─ render.py      deterministic SKILL.md / pack.json / results writer
├─ validate.py    every rule, one place
└─ cli.py         validate / list / show / search / build / hookplan
```

Markdown under `skills/` is **generated**. Edit the corpus, run `hookproof build`, and a test asserts the committed files match a fresh render — the two can never silently disagree.

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — components, data flow, design decisions
- [docs/USAGE.md](docs/USAGE.md) — commands, agent integration, regeneration discipline
- [docs/PROJECT_SPEC.md](docs/PROJECT_SPEC.md) — problem, solution, acceptance tests
- [RESULTS.md](RESULTS.md) — reproducible evidence for every claim above
- [SECURITY.md](SECURITY.md) — authorized-use scope and the reporting path
- [CONTRIBUTING.md](CONTRIBUTING.md) — the quality floor CI enforces

## License

MIT. References link to public specifications and provider documentation; see each skill's **References** section.