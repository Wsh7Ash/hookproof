---
name: outbound-target-scope-classification
description: "Decide whether you may exercise the application's outbound callback targets at all, because a target URL you control is a server-side request primitive the rules must cover explicitly. Use when the application makes requests to URLs it stores or receives, and the rules of engagement are silent on outbound testing"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [scope, ssrf, outbound]
---

# Outbound Target Scope Classification

> Decide whether you may exercise the application's outbound callback targets at all, because a target URL you control is a server-side request primitive the rules must cover explicitly

**Use when:** the application makes requests to URLs it stores or receives, and the rules of engagement are silent on outbound testing

**Avoid when:** the program states plainly that outbound target requests are out of scope and only inbound delivery verification may be tested

## Procedure

1. Search the rules of engagement for outbound, callback, redirect, target and URL, and quote the surrounding sentences verbatim in your notes.
2. Ask a direct yes-or-no question about outbound target requests when the document is silent, and wait for the answer before proceeding.
3. If outbound testing is out of scope, restrict yourself to reading how the target is stored and validated, without issuing the request.
4. When permitted, plan a request to a target you own that returns an observable difference, with a rate ceiling and a stop condition.
5. Record which findings depend on outbound access, so a reader can separate a target-validation defect from an inbound signature defect.
6. Re-confirm the decision at any change of engagement, since a scope update often reverses this item without changing endpoint lists.

## Signals

- Rules list receiver endpoints but never mention outbound target requests
- A target URL field is editable through an API the program exposes
- The application follows redirects when fetching a stored target
- No written answer exists to a direct outbound-request question

## Patterns

**1. Decision record**

```text
outbound_target: unknown | permitted | forbidden
source: <document section or program reply>
date: <ISO date>
consequence: read validation only | one request to owned target allowed
```

**2. Passive fallback**

```text
if outbound contact is forbidden, describe the validation you observed in code or configuration and mark the claim as untested rather than as a finding
```

**3. Owned-target rule**

```text
when permitted, the only target you request is one you control; a response difference from that target is the entire evidence, nothing more
```

## Pitfalls

- Requesting an internal address because a target field accepted it, when outbound testing was never cleared
- Reporting an untested outbound claim as though a request had been made
- Forgetting that redirect-following turns your owned target into a chain you did not choose

## Done when

- Outbound target testing is recorded as permitted or forbidden with a quoted source
- Every later finding carries an inbound-observed or outbound-observed label

## References

- [OWASP - SSRF prevention cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [PortSwigger - SSRF](https://portswigger.net/web-security/ssrf)
