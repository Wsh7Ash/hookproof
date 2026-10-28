# Usage

## Setup

```shell
python -m pip install -e ".[dev]"
hookproof validate      # must print: hookproof: 50/50 skills valid
python -m pytest -q     # 22 passed
```

Python 3.10+, no runtime dependencies.

## Day-to-day commands

| Command | What it does |
|---|---|
| `hookproof validate` | Runs every corpus rule **and** checks `skills/**/SKILL.md` on disk against a fresh render. Exit 0 only at 50/50. |
| `hookproof validate --skip-files` | Validates the authored corpus without touching generated files (useful mid-edit). |
| `hookproof validate --json` | Machine-readable report: checked, valid, passed, floors, issues. |
| `hookproof list` | All 50 skills with their phase. |
| `hookproof list --phase probe` | Narrow to one phase (18 skills). |
| `hookproof list --tag signature` | Narrow to one tag. |
| `hookproof show <slug>` | Print one rendered `SKILL.md`. |
| `hookproof search <terms...>` | Rank skills by keyword across slug, title, summary, tags and steps. |
| `hookproof build` | Regenerate `skills/`, `pack.json`, `results/catalog.md` and `results/validation.json`. |

## Turning an endpoint configuration into a verification plan

```shell
hookproof hookplan --config-file examples/demo-endpoint.json
hookproof hookplan --config-file examples/demo-endpoint.json --top 6 --json
```

```text
# Verification plan - payments receiver
Scheme: hmac-sha256 over <timestamp>.<raw body>   Endpoints: 2   Signature headers: 2   Skills matched: 50 of 50   Plan steps: 12   Phases covered: 6/6

Endpoints: /hooks/stripe, /hooks/github
Signature headers: stripe-signature, x-hub-signature-256

## scope
...
```

Configuration keys consumed as vocabulary: `endpoints`, `scheme`, `signature_headers`, `providers`, `content_types`, `observed`, `concerns`, `keywords`. Anything else in the file is ignored rather than guessed at.

- **`--top N`** caps plan length; selection is round-robin across phases, so every matched phase gets a slot before any phase gets a second.
- **Thin coverage** lists phases where the configuration matched *no* skill at all. It is computed from matches, never from the truncated plan.

## Loading skills into agents

Every skill is a standalone file with YAML front-matter:

```text
skills/unsigned-delivery-acceptance/SKILL.md
```

**Claude Code** — point `skills` at this repository in `.claude/settings.json`, or copy the directory you want into the project's skills folder:

```json
{ "skills": { "paths": ["../hookproof/skills"] } }
```

**opencode** — add the directory to `opencode.json`:

```json
{ "skill": [{ "path": "../hookproof/skills" }] }
```

Any runtime that loads `SKILL.md` files works the same way; front-matter carries `name`, `description`, `pack`, `version`, `category` and `tags`.

## Regeneration discipline

`skills/**` and `pack.json` are **generated**. Never hand-edit them — a drift test will fail.

```shell
# 1. edit the corpus in src/hookproof/corpus/part1..3.py
# 2. regenerate and check the gate
hookproof build
hookproof validate      # must print 50/50
python -m pytest -q
```

CI runs the same sequence and then `git diff --exit-code -- skills pack.json results`, so a corpus edit committed without a rebuild fails the build.