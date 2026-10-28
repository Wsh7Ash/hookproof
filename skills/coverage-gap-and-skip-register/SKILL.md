---
name: coverage-gap-and-skip-register
description: "Publish the list of tests you did not run and why, so an untested path reads as a declared gap rather than as an unremarked pass. Use when a webhook assessment ends with cases that were forbidden, unsupported or impossible to exercise"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [document, coverage, reporting]
---

# Coverage Gap and Skip Register

> Publish the list of tests you did not run and why, so an untested path reads as a declared gap rather than as an unremarked pass

**Use when:** a webhook assessment ends with cases that were forbidden, unsupported or impossible to exercise

**Avoid when:** every planned case ran and each produced a recorded response

## Procedure

1. List every planned case that did not run, using the skip notes recorded during the scope and probe phases.
2. For each gap record the reason class: forbidden by boundary, unsupported by provider, needs an environment you lack, or not safe to trigger.
3. State what a reader may and may not conclude from the gap, since an untested case is neither a pass nor a confirmed defect.
4. Rank the gaps by how much they weaken the overall claim, so a reviewer can judge the assessment rather than trust it blindly.
5. Name what would close each gap: a permission, a provider capability or an environment, with an owner where one exists.
6. Place the register next to the findings, not in an appendix, because a reader who never sees it will over-read the results.

## Signals

- The report lists only tests that ran, implying coverage that was never achieved
- A replay case was forbidden by the boundary but the report says replay resistance works
- No provider capability exists for a case and nothing in the report says so
- Gaps appear only in a section most readers skip

## Patterns

**1. Register row**

```text
case: replay of signed delivery | reason: forbidden by boundary v2 | conclusion: not assessed | closes with: written permission
```

**2. Reason classes**

```text
forbidden (scope), unsupported (provider capability), unavailable (environment), unsafe (side effects); pick one and say which
```

**3. Placement rule**

```text
the register sits directly after the summary so a reader meets it before the findings, never in an appendix
```

## Pitfalls

- Letting an untested case read as a pass because the report describes only what succeeded
- Filing the register where a reviewer will not reach it and overstating coverage by omission
- Listing a gap without saying what would close it, which leaves it permanently open

## Done when

- Every case that did not run appears in the register with a reason class and a stated conclusion
- Each gap names what would close it and sits beside the findings rather than in an appendix

## References

- [NIST SP 800-53 - Assessment coverage documentation](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)
- [OWASP - Reporting security findings](https://owasp.org/www-project-web-security-testing-guide/)
