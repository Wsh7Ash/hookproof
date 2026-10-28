---
name: outbound-target-scheme-validation
description: "When you may exercise outbound targets, check which URL schemes and hosts the application accepts before it makes a request on your behalf. Use when the boundary permits outbound target testing and the application stores or accepts destination URLs"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, ssrf, outbound]
---

# Outbound Target Scheme Validation

> When you may exercise outbound targets, check which URL schemes and hosts the application accepts before it makes a request on your behalf

**Use when:** the boundary permits outbound target testing and the application stores or accepts destination URLs

**Avoid when:** the boundary forbids outbound requests, in which case this test is recorded as skipped with the reason

## Procedure

1. Re-read the boundary: if outbound requests are forbidden, record this as skipped and do not send anything.
2. Enumerate the schemes the validator accepts, testing each against a target you own rather than against an internal address.
3. Check whether the validator resolves a hostname before deciding, since that is where allow-lists are usually bypassed.
4. Look for redirect-following on a target you control, because a redirect you set is still a request you chose.
5. Note whether the request carries credentials or fixed headers that would leak to the destination you name.
6. Record accepted schemes, host handling, redirect behaviour and header leakage, each with the request that proved it.

## Signals

- A scheme outside http and https is accepted by the validator
- The validator checks a hostname string but never resolves it before the request
- A redirect from your owned target is followed to a second destination
- Fixed credentials or tokens are attached to a destination you supplied

## Patterns

**1. Scheme table**

```text
scheme | accepted | request issued
http | yes | yes
https | yes | yes
file | yes | no  <- rejected later, record where
data | no | no
```

**2. Owned-target rule**

```text
every request you issue goes to a host you control; the observation is what the application did, not what an internal host would have returned
```

**3. Redirect note**

```text
if redirects are followed, record the maximum hop count and whether headers survive the hop
```

## Pitfalls

- Requesting an internal address to prove a point the boundary never allowed
- Failing to notice that your own client followed a redirect the application would not have
- Reporting a scheme acceptance without confirming whether a request is ever issued for it

## Done when

- A scheme table records acceptance and whether a request was issued, for each scheme tested
- Redirect and header-leakage behaviour are recorded with the owned-target request that showed them

## References

- [OWASP - SSRF prevention cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [CWE-918 - Server-side request forgery](https://cwe.mitre.org/data/definitions/918.html)
