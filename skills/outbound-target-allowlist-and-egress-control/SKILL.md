---
name: outbound-target-allowlist-and-egress-control
description: "Constrain where outbound callbacks may go, at validation time and again at the network layer, so a target field can never become a request into your own infrastructure. Use when the application stores or accepts callback destination URLs that it later requests"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [harden, ssrf, outbound]
---

# Outbound Target Allowlist and Egress Control

> Constrain where outbound callbacks may go, at validation time and again at the network layer, so a target field can never become a request into your own infrastructure

**Use when:** the application stores or accepts callback destination URLs that it later requests

**Avoid when:** destinations are fixed in configuration and no user- or partner-supplied URL can reach the fetcher

## Procedure

1. Classify which destinations are legitimate: partner hosts, internal services and any address ranges that must never be reached.
2. Validate the destination at write time and again immediately before the request, since the stored value can change between the two.
3. Resolve the hostname and reject addresses in private, loopback and link-local ranges rather than checking the string alone.
4. Disable or strictly bound redirect-following, and re-run the same validation on any redirect target.
5. Attach no credentials to a destination the validator did not allow, and strip authorization on any cross-host redirect.
6. Enforce egress restrictions at the network layer as a second control, and record what the layer would block.

## Signals

- Validation checks a hostname string but never resolves it before the request
- The destination is validated once at write time and never again before the fetch
- Redirects are followed without re-running validation on the new target
- Fixed credentials are attached to destinations supplied at runtime

## Patterns

**1. Two-stage rule**

```text
validate on write, validate again immediately before request, after resolution; a single check at either point is not enough
```

**2. Address classes**

```text
reject: loopback, private ranges, link-local, and any range the owner lists as internal; record which classes you enforced
```

**3. Egress note**

```text
network-layer rule as second control: state the destination classes it blocks so the defence in depth is documented
```

## Pitfalls

- Validating the hostname but resolving it only inside the HTTP client, after the check has already passed
- Fixing the initial validation while leaving redirect targets unchecked
- Removing credentials from requests and breaking a legitimate partner integration in the process

## Done when

- Validation runs at write time and again after resolution immediately before the request
- Redirect handling and credential attachment behaviour are recorded with the network-layer control

## References

- [OWASP - SSRF prevention cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [CWE-918 - Server-side request forgery](https://cwe.mitre.org/data/definitions/918.html)
