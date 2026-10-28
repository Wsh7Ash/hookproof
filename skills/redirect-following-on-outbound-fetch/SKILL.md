---
name: redirect-following-on-outbound-fetch
description: "Determine whether an outbound callback follows redirects to a second destination, since a target you are allowed to name can otherwise reach one you are not. Use when the application fetches a stored or supplied URL and outbound testing is permitted by the boundary"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, ssrf, redirects]
---

# Redirect Following on Outbound Fetch

> Determine whether an outbound callback follows redirects to a second destination, since a target you are allowed to name can otherwise reach one you are not

**Use when:** the application fetches a stored or supplied URL and outbound testing is permitted by the boundary

**Avoid when:** the boundary forbids outbound requests or the fetcher explicitly does not follow redirects

## Procedure

1. Re-read the boundary and record whether outbound requests and redirect-following tests are permitted.
2. Set up a redirect on a host you own that points to a second host you also own.
3. Issue one outbound fetch against the first host and record whether a second request arrives at the second host.
4. Check whether credentials, authorization headers or cookies survive the redirect to the second destination.
5. Note the maximum redirect depth the client enforces, if any, and whether a loop is detected.
6. Record the chain with hop count, surviving headers and the destination ultimately reached.

## Signals

- A redirect from an allowed host is followed to a destination the validator would have rejected
- An authorization header is forwarded across the redirect to a different host
- The client has no redirect depth limit and accepts a loop
- The validator runs on the first URL only and never re-checks the redirect target

## Patterns

**1. Chain record**

```text
hop 1: your host -> 302 -> hop 2: your second host; headers carried: authorization yes, cookie no
```

**2. Re-validation question**

```text
does the validator run again on the redirect target? no -> the allow-list applies to the first URL only
```

**3. Header rule**

```text
the safe behaviour is to strip credentials on any cross-host redirect; record whether yours does
```

## Pitfalls

- Running an outbound test the boundary forbids and reporting it as a pass
- Using a client that strips credentials by default and assuming the application's client behaves the same
- Reporting a redirect finding without stating whether credentials survived the hop

## Done when

- A redirect chain is recorded with hop count, surviving headers and final destination
- Whether re-validation occurs on the redirect target is stated explicitly

## References

- [OWASP - SSRF prevention cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [CWE-601 - Open redirect](https://cwe.mitre.org/data/definitions/601.html)
