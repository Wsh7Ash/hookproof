---
name: provider-terms-and-testing-mode
description: "Confirm which testing facility the sending provider intends you to use, so verification work happens in a simulator or sandbox instead of against a live partner account. Use when a third-party provider signs deliveries into the application and its testing method has not been confirmed"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [scope, provider, sandbox]
---

# Provider Terms and Testing Mode

> Confirm which testing facility the sending provider intends you to use, so verification work happens in a simulator or sandbox instead of against a live partner account

**Use when:** a third-party provider signs deliveries into the application and its testing method has not been confirmed

**Avoid when:** the provider documents a sandbox or CLI simulator and the assessment already uses it exclusively

## Procedure

1. Read the provider's testing documentation and record the supported method: CLI simulator, dashboard trigger, sandbox account or test event.
2. Confirm whether that method reproduces the real signature scheme, since a simulator that omits signing tests nothing that matters.
3. Record whether the sandbox uses separate credentials and endpoints from production, and which one your endpoint currently points at.
4. Check whether the provider's testing method respects your rate budget, and note any method that could trigger live deliveries.
5. Decide the single method you will use for the session and write it into the boundary document.
6. Note any provider capability the assessment cannot use, such as replay of a signed event, and record the resulting coverage gap.

## Signals

- The only documented way to trigger a delivery sends it to a live customer flow
- The simulator does not produce a signature header at all
- Sandbox and production share a receiver path with no distinguishing marker
- No documented method exists for replaying a previously signed event

## Patterns

**1. Method record**

```text
provider: stripe | method: CLI trigger | signature produced: yes | sandbox separate: yes | rate safe: yes
```

**2. Gap note**

```text
provider X has no replay capability -> replay tests marked untestable with this reason rather than reported as passing
```

**3. Environment marker**

```text
request the receiver with the provider's own test flag and confirm the handler treats it as sandbox before any signature test runs
```

## Pitfalls

- Triggering a live delivery through a provider tool intended for demos
- Accepting a simulator as proof of verification when it never attaches a signature
- Recording a passing replay test that was never actually executed because no facility exists

## Done when

- One provider testing method is chosen, documented and written into the boundary
- Untestable capabilities are listed as coverage gaps with the reason

## References

- [Stripe - Webhook testing documentation](https://docs.stripe.com/webhooks/test)
- [GitHub - Webhook deliveries and testing](https://docs.github.com/en/webhooks/using-webhooks/creating-webhooks)
