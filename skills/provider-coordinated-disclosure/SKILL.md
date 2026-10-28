---
name: provider-coordinated-disclosure
description: "Route a webhook defect to the party that can fix it, receiver team or sending provider, agree a timeline in writing, and re-test before announcing closure. Use when a finding involves the sending provider's own scheme, SDK or platform behaviour rather than only your receiver"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [document, disclosure, coordination]
---

# Provider Coordinated Disclosure

> Route a webhook defect to the party that can fix it, receiver team or sending provider, agree a timeline in writing, and re-test before announcing closure

**Use when:** a finding involves the sending provider's own scheme, SDK or platform behaviour rather than only your receiver

**Avoid when:** the defect is entirely in receiver code and needs no partner involvement

## Procedure

1. Decide the fixing party from the evidence: receiver code, receiver configuration, or provider platform.
2. Prepare the report with the evidence pack and reproduction recipe, using synthetic data only.
3. Send it to the property owner first, since they hold the relationship and the contractual path to the provider.
4. Agree an acknowledgement date, a target fix date and a disclosure date, recorded in writing.
5. Re-test after the fix lands using the same recipe and record the before and after response markers.
6. Close with a note on anything still open, including items that depend on a provider release you do not control.

## Signals

- The defect requires a change only the sending provider can make to its scheme or SDK
- The report reaches the provider before the owner has seen it, breaking the agreed channel
- Closure was announced without a re-test showing the behaviour changed
- Items remain open with no owner and no date attached

## Patterns

**1. Routing line**

```text
defect: provider SDK re-encodes the body before signing | fixing party: provider | channel: owner to provider | receiver mitigation: none available
```

**2. Timeline block**

```text
ack by <date> | fix target <date> | re-test <date> | disclosure <date> -> confirmed in writing by both sides
```

**3. Closure note**

```text
re-tested with the published recipe at <timestamp>: response moved from <before marker> to <after marker> -> item closed
```

## Pitfalls

- Contacting a provider directly about a defect that is really the receiver's configuration choice
- Publishing a delivery body in a report a partner portal will retain indefinitely
- Announcing closure without a re-test that shows the behaviour actually changed

## Done when

- The fixing party and channel are named with a timeline confirmed in writing
- A post-fix re-test records before and after response markers for each closed item

## References

- [ISO 29147 - Vulnerability disclosure guidance](https://www.iso.org/standard/72311.html)
- [OWASP - Coordinated disclosure](https://owasp.org/www-project-vulnerability-disclosure/)
