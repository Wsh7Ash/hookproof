"""hookproof command line interface.

Shared subcommands (validate / list / show / search / build) exist in every
skill pack built on this harness; ``hookplan`` is hookproof's domain command:
it turns an endpoint configuration into a phase-ordered verification plan drawn
from the corpus, and reports the phases the configuration matches nothing in.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .corpus import PACK, PHASE_ORDER, SKILLS
from .render import build_pack, render_skill, word_count
from .validate import (
    MAX_DESCRIPTION,
    MIN_DONE,
    MIN_PATTERNS,
    MIN_PITFALLS,
    MIN_SIGNALS,
    MIN_STEPS,
    MIN_SUMMARY,
    MIN_WORDS,
    Issue,
    validate_pack,
)

FLOORS = {
    "min_steps": MIN_STEPS,
    "min_signals": MIN_SIGNALS,
    "min_patterns": MIN_PATTERNS,
    "min_pitfalls": MIN_PITFALLS,
    "min_done_when": MIN_DONE,
    "min_summary_chars": MIN_SUMMARY,
    "min_words": MIN_WORDS,
    "max_description_chars": MAX_DESCRIPTION,
}


def repo_root() -> Path:
    """Repository root: src/<package>/cli.py -> repo root."""
    return Path(__file__).resolve().parents[2]


def _report(issues: list[Issue], total: int, as_json: bool, title: str) -> int:
    bad = {issue.slug for issue in issues if issue.slug}
    valid = total - len(bad)
    if as_json:
        print(
            json.dumps(
                {
                    "pack": title,
                    "checked": total,
                    "valid": valid,
                    "passed": not issues,
                    "floors": FLOORS,
                    "issues": [
                        {"slug": i.slug, "rule": i.rule, "message": i.message}
                        for i in issues
                    ],
                },
                indent=2,
            )
        )
    else:
        print(f"{title}: {valid}/{total} skills valid")
        for issue in issues:
            print(f"  FAIL {issue}")
        if not issues:
            print(
                f"  ok  steps>={MIN_STEPS} signals>={MIN_SIGNALS} patterns>={MIN_PATTERNS} "
                f"pitfalls>={MIN_PITFALLS} words>={MIN_WORDS} refs canonical https"
            )
    return 0 if not issues else 1


def cmd_validate(args: argparse.Namespace) -> int:
    issues = validate_pack(PACK, SKILLS)
    root = Path(args.root) if args.root else repo_root()
    if not args.skip_files:
        for skill in SKILLS:
            path = root / "skills" / skill.slug / "SKILL.md"
            if not path.exists():
                issues.append(Issue(skill.slug, "file-missing", f"{path.relative_to(root)} missing"))
                continue
            if path.read_text(encoding="utf-8") != render_skill(PACK, skill):
                issues.append(
                    Issue(skill.slug, "file-drift", "SKILL.md on disk differs from the corpus render")
                )
    return _report(issues, len(SKILLS), args.json, PACK["name"])


def cmd_list(args: argparse.Namespace) -> int:
    skills = [
        skill
        for skill in SKILLS
        if (not args.tag or args.tag in skill.tags)
        and (not args.phase or skill.meta_get("phase") == args.phase)
    ]
    if args.json:
        print(
            json.dumps(
                [
                    {
                        "slug": s.slug,
                        "title": s.title,
                        "tags": list(s.tags),
                        "meta": s.meta,
                        "words": word_count(render_skill(PACK, s)),
                    }
                    for s in skills
                ],
                indent=2,
            )
        )
        return 0
    for skill in skills:
        phase = skill.meta_get("phase", "-")
        print(f"{skill.slug:46s} {phase:12s} {skill.title}")
    print(f"-- {len(skills)} skills")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    for skill in SKILLS:
        if skill.slug == args.slug:
            print(render_skill(PACK, skill), end="")
            return 0
    print(f"unknown skill: {args.slug}", file=sys.stderr)
    return 1


def cmd_search(args: argparse.Namespace) -> int:
    terms = [t.lower() for t in args.terms]
    scored: list[tuple[int, Any]] = []
    for skill in SKILLS:
        haystack = " ".join(
            [skill.slug, skill.title, skill.summary, " ".join(skill.tags), " ".join(skill.steps)]
        ).lower()
        score = sum(haystack.count(term) for term in terms)
        if score:
            scored.append((score, skill))
    scored.sort(key=lambda pair: (-pair[0], pair[1].slug))
    for score, skill in scored[: args.limit]:
        print(f"{score:3d}  {skill.slug:46s} {skill.title}")
    if not scored:
        print("no matches")
        return 1
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else repo_root()
    build_pack(root, PACK, SKILLS)
    issues = validate_pack(PACK, SKILLS)
    for skill in SKILLS:
        path = root / "skills" / skill.slug / "SKILL.md"
        if path.read_text(encoding="utf-8") != render_skill(PACK, skill):
            issues.append(Issue(skill.slug, "file-drift", "render mismatch"))
    bad = {i.slug for i in issues if i.slug}
    report = {
        "pack": PACK["name"],
        "version": PACK["version"],
        "expected_skills": PACK.get("expected_skills", len(SKILLS)),
        "checked": len(SKILLS),
        "valid": len(SKILLS) - len(bad),
        "passed": not issues,
        "floors": FLOORS,
        "issues": [
            {"slug": i.slug, "rule": i.rule, "message": i.message} for i in issues
        ],
    }
    results = root / "results"
    results.mkdir(parents=True, exist_ok=True)
    (results / "validation.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"built {len(SKILLS)} skills -> {root / 'skills'}")
    return 0 if not issues else 1


# ---------------------------------------------------------------- hookplan


def config_vocabulary(config: dict[str, Any]) -> list[str]:
    """Flatten an endpoint configuration into the keywords used to score it.

    Everything in the configuration is a real observation: endpoints, the
    signing scheme, headers actually read, providers, content types and any
    concerns the tester recorded.
    """
    keywords: list[str] = []

    def add(value: Any) -> None:
        if isinstance(value, str):
            for token in value.replace("-", " ").replace("_", " ").replace("/", " ").split():
                keywords.append(token.lower())
        elif isinstance(value, (list, tuple)):
            for item in value:
                add(item)
        elif isinstance(value, dict):
            for item in value.values():
                add(item)

    for key in (
        "endpoints",
        "scheme",
        "signature_headers",
        "providers",
        "content_types",
        "observed",
        "concerns",
        "keywords",
    ):
        add(config.get(key, []))
    return sorted({k for k in keywords if len(k) > 2})


def build_hookplan(config: dict[str, Any], top: int = 12) -> dict[str, Any]:
    """Turn an endpoint configuration into a phase-ordered verification plan.

    Vocabulary comes from the configuration's observations, so the plan
    reflects the scheme and endpoints that actually exist rather than a
    generic webhook checklist.
    """
    label = str(config.get("target", "unnamed receiver"))
    keywords = config_vocabulary(config)
    endpoints = [str(x) for x in config.get("endpoints", []) or []]
    headers = [str(x) for x in config.get("signature_headers", []) or []]
    scheme = config.get("scheme", "unidentified")

    scored: list[tuple[int, int, Any]] = []
    for skill in SKILLS:
        haystack = " ".join(
            [skill.slug, skill.title, skill.summary, " ".join(skill.tags), " ".join(skill.steps)]
        )
        haystack = haystack.replace("-", " ").lower()
        score = sum(1 for k in keywords if k and k in haystack)
        if score:
            phase = skill.meta_get("phase", "probe")
            scored.append((PHASE_ORDER.index(phase), score, skill))
    scored.sort(key=lambda t: (t[0], -t[1], t[2].slug))

    # Phase-stratified selection: the first pass takes the best match in every
    # matched phase, later passes fill the remaining slots in phase order, so
    # a small --top can never crowd out the later phases of the arc.
    by_phase: dict[int, list[tuple[int, Any]]] = {}
    for phase_index, score, skill in scored:
        by_phase.setdefault(phase_index, []).append((score, skill))
    for bucket in by_phase.values():
        bucket.sort(key=lambda t: (-t[0], t[1].slug))

    ordered: list[tuple[int, int, Any]] = []
    round_index = 0
    while any(len(by_phase[phase_index]) > round_index for phase_index in by_phase):
        for phase_index in sorted(by_phase):
            bucket = by_phase[phase_index]
            if round_index < len(bucket) and len(ordered) < top:
                score, skill = bucket[round_index]
                ordered.append((phase_index, score, skill))
        round_index += 1

    plan: list[dict[str, Any]] = []
    for phase_index, score, skill in ordered:
        plan.append(
            {
                "phase": skill.meta_get("phase", "probe"),
                "slug": skill.slug,
                "title": skill.title,
                "match_score": score,
                "why": skill.summary,
                "steps": skill.steps,
            }
        )
    covered = {entry["phase"] for entry in plan}
    matched_phases = {skill.meta_get("phase", "probe") for _, _, skill in scored}
    missing_phases = [p for p in PHASE_ORDER if p not in matched_phases]
    return {
        "target": label,
        "scheme": scheme,
        "endpoints": endpoints,
        "signature_headers": headers,
        "vocabulary": keywords,
        "skills_total": len(SKILLS),
        "skills_matched": len(scored),
        "plan_steps": len(plan),
        "phases_covered": [p for p in PHASE_ORDER if p in covered],
        "missing_phases": missing_phases,
        "plan": plan,
    }


def cmd_hookplan(args: argparse.Namespace) -> int:
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    payload = build_hookplan(config, top=args.top)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0
    print(f"# Verification plan - {payload['target']}")
    print(
        f"Scheme: {payload['scheme']}   Endpoints: {len(payload['endpoints'])}   "
        f"Signature headers: {len(payload['signature_headers'])}   "
        f"Skills matched: {payload['skills_matched']} of {payload['skills_total']}   "
        f"Plan steps: {payload['plan_steps']}   Phases covered: {len(payload['phases_covered'])}/{len(PHASE_ORDER)}"
    )
    if payload["endpoints"]:
        print()
        print("Endpoints: " + ", ".join(payload["endpoints"]))
    if payload["signature_headers"]:
        print("Signature headers: " + ", ".join(payload["signature_headers"]))
    if payload["missing_phases"]:
        print()
        print("Thin coverage (configuration matches no skill in these phases): " + ", ".join(payload["missing_phases"]))
    current = None
    for entry in payload["plan"]:
        if entry["phase"] != current:
            current = entry["phase"]
            print()
            print(f"## {current}")
        print()
        print(f"{entry['slug']}  (match {entry['match_score']})")
        print(f"  {entry['why']}")
        for idx, step in enumerate(entry["steps"], start=1):
            print(f"   {idx}. {step}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PACK["name"],
        description=PACK["description"],
    )
    parser.add_argument("--version", action="version", version=f"{PACK['name']} {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="run every corpus rule and check disk sync")
    p.add_argument("--json", action="store_true")
    p.add_argument("--root", default=None)
    p.add_argument("--skip-files", action="store_true", help="validate the corpus only")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("list", help="list skills")
    p.add_argument("--tag", default=None)
    p.add_argument("--phase", default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show", help="print one SKILL.md")
    p.add_argument("slug")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("search", help="rank skills by keyword")
    p.add_argument("terms", nargs="+")
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("build", help="regenerate skills/, pack.json and results/")
    p.add_argument("--root", default=None)
    p.set_defaults(func=cmd_build)

    p = sub.add_parser(
        "hookplan",
        help="turn a webhook endpoint configuration into a phase-ordered verification plan",
    )
    p.add_argument(
        "--config-file",
        required=True,
        dest="config",
        help="JSON file describing the receiver: endpoints, scheme, signature headers, providers, concerns",
    )
    p.add_argument("--top", type=int, default=12, help="maximum skills in the plan")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_hookplan)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())