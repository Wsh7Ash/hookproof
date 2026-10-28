---
name: webhook-endpoint-inventory
description: "Enumerate every inbound webhook receiver and outbound callback target the application exposes, because an unlisted endpoint is where an unsigned delivery usually lands. Use when the application is known to receive or send webhooks and no maintained list of those endpoints exists"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [scope, inventory, webhooks]
---

# Webhook Endpoint Inventory

> Enumerate every inbound webhook receiver and outbound callback target the application exposes, because an unlisted endpoint is where an unsigned delivery usually lands

**Use when:** the application is known to receive or send webhooks and no maintained list of those endpoints exists

**Avoid when:** a current inventory already lists each receiver route, sender provider and outbound target with its owner

## Procedure

1. Walk the routing table and middleware chain to find every path that accepts an external delivery, including ones registered dynamically.
2. Separate receivers from senders: inbound deliveries you verify, and outbound target URLs you request on someone else's behalf.
3. Record for each receiver its provider, expected signature header, environment and owning team.
4. Record for each sender its target URL source (config, database, request field) and whether the target can be changed at runtime.
5. Note endpoints that exist only in one environment, since a sandbox-only receiver often skips verification entirely.
6. Mark each entry verified or unconfirmed, and carry every unconfirmed entry into the identify phase as a question.

## Signals

- A route accepts deliveries but no one can name the provider that sends to it
- A receiver exists in the sandbox only and no one remembers why
- An outbound target URL is stored in a field a user or API client can edit
- A legacy receiver path still returns 200 to any body

## Patterns

**1. Inventory row**

```text
path | direction | provider | signature header | env | owner
/hooks/stripe | inbound | stripe | stripe-signature | prod | payments
/hooks/legacy | inbound | unknown | none observed | prod | unowned
/api/notify | outbound | self | n/a | prod | integrations
```

**2. Direction split**

```text
inbound -> you must verify a signature; outbound -> you must constrain the target. Writing the direction beside each row decides which half of the pack applies.
```

**3. Unconfirmed rule**

```text
any row with owner unknown or provider unknown is carried into identify as an open question rather than dropped from the list
```

## Pitfalls

- Inventorying only inbound receivers and missing the outbound targets that make requests for you
- Finding routes by URL pattern alone while another set is registered through a framework hook
- Assuming an unowned legacy receiver is harmless because no one sends to it today

## Done when

- Every receiver and outbound target appears as a row with provider, header, environment and owner
- Unconfirmed rows are listed explicitly and assigned to an identify question

## References

- [OWASP - Server-side request forgery](https://owasp.org/SSRF_Sheet/)
- [MDN - HTTP request handling](https://developer.mozilla.org/en-US/docs/Web/HTTP)
