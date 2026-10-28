---
name: callback-authorization-boundary
description: "Write down exactly which endpoints, secrets, providers and payload shapes the webhook assessment may touch before any delivery request leaves the workstation. Use when a webhook or callback assessment is about to start and the rules of engagement name no endpoint list, secret set or permitted delivery method"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [scope, authorization, rules-of-engagement]
---

# Callback Authorization Boundary

> Write down exactly which endpoints, secrets, providers and payload shapes the webhook assessment may touch before any delivery request leaves the workstation

**Use when:** a webhook or callback assessment is about to start and the rules of engagement name no endpoint list, secret set or permitted delivery method

**Avoid when:** the program already publishes a machine-readable scope listing endpoints, providers and the permitted test method

## Procedure

1. Collect the signed rules of engagement, the provider's testing documentation and any internal endpoint list into one place and note the versions used.
2. List every in-scope receiver path, sender provider, callback URL class and environment exactly as written, without normalizing or guessing wildcards.
3. Record the permitted delivery method (sandbox simulator, replay tool, own account), the request-rate ceiling and the explicit ban list in one table.
4. Confirm whether replaying a previously signed delivery is allowed, since that single permission decides whether the replay tests exist at all.
5. Write the boundary as a short pre-flight checklist you re-read before the first request of every session, not as a note you recall from memory.
6. Save the boundary text beside the evidence you collect so a reviewer can prove every recorded delivery fell inside the permitted set.

## Signals

- Rules of engagement list endpoints but say nothing about replay or rate
- The provider page describes live delivery while the assessment only permits a sandbox
- A previous session recorded deliveries against an endpoint you cannot find in writing
- Rate limits are described in prose rather than as a number you can enforce

## Patterns

**1. Boundary record**

```text
scope:
  endpoints: [/hooks/stripe, /hooks/github]
  senders: [stripe, github]
  methods: [sandbox-simulator, replay-tool]
  replay_signed: forbidden
  rate_rps: 1
  live_delivery: forbidden
```

**2. Pre-flight echo**

```text
Before session start, restate: endpoints, senders, permitted methods, rate ceiling and the two explicit bans. Any element you cannot quote from the document is a gap to resolve, not a permission to assume.
```

**3. Evidence binding**

```text
Store boundary.md beside evidence/ so each recorded delivery line can be checked against a document version during review.
```

## Pitfalls

- Reading a wildcard host as permission for every path the application exposes
- Assuming staging and production share scope because they share a provider configuration
- Treating an old thread as current authorization after the provider or program changed its rules

## Done when

- A written boundary table names endpoints, senders, methods, rate ceiling and explicit bans
- Every later evidence file carries the document version used to justify it

## References

- [PortSwigger - Webhook security testing](https://portswigger.net/web-security)
- [OWASP - Testing for improper access control](https://owasp.org/www-project-web-security-testing-guide/)
