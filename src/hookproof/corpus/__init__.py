"""hookproof corpus: pack metadata plus 50 authored webhook security skills.

Skills are authored as plain dicts in ``part1``..``part3`` and loaded once
into the validated :class:`~hookproof.model.Skill` shape.
"""

from __future__ import annotations

from typing import Any

from ..model import skill_from_dict
from .part1 import SKILLS as PART1
from .part2 import SKILLS as PART2
from .part3 import SKILLS as PART3

PACK: dict[str, Any] = {
    "name": "hookproof",
    "version": "1.0.0",
    "category": "webhook-tooling",
    "license": "MIT",
    "runtime": "Claude Code, opencode, or any agent runtime that loads SKILL.md files",
    "description": (
        "50 validated webhook and callback security skills: signature scheme "
        "identification, replay and tolerance auditing, delivery-rejection "
        "verification, outbound target safety and secret rotation, with a "
        "endpoint-config-to-verification-plan CLI."
    ),
    "expected_skills": 50,
    "meta_keys": ("phase",),
    "requires_verification": False,
}

PHASE_ORDER = (
    "scope",
    "identify",
    "probe",
    "confirm",
    "harden",
    "document",
)

SKILLS: list[Any] = [skill_from_dict(raw) for raw in (*PART1, *PART2, *PART3)]
