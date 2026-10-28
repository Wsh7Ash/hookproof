---
name: sandbox-reproduction-with-provider-tool
description: "Reproduce the observation using the provider's own simulator or sandbox so the evidence comes from the delivery path partners actually use rather than from a hand-crafted request. Use when the sending provider offers a testing facility and the observation should be confirmed through it"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [confirm, provider, sandbox]
---

# Sandbox Reproduction With Provider Tool

> Reproduce the observation using the provider's own simulator or sandbox so the evidence comes from the delivery path partners actually use rather than from a hand-crafted request

**Use when:** the sending provider offers a testing facility and the observation should be confirmed through it

**Avoid when:** the provider has no such facility, in which case the gap is recorded rather than worked around silently

## Procedure

1. Select the provider testing method identified in the scope phase and confirm it produces a real signature.
2. Trigger one delivery through that method and capture the receiver's status, body and timing.
3. Compare the response with your own crafted delivery for the same case; a difference means the simulator and real path differ.
4. If the simulator cannot produce the failing case, record which case remains craft-only and why.
5. Check that the simulator targeted the intended environment rather than a live receiver.
6. Record the reproduction as provider-reproduced, craft-only or not-reproducible with the reason.

## Signals

- The provider tool produces a delivery that behaves differently from your crafted one
- The simulator omits the signature header entirely, so it cannot exercise verification
- The tool sent to a live receiver rather than the sandbox you intended
- A failing case cannot be constructed through the provider's facility at all

## Patterns

**1. Reproduction label**

```text
provider-reproduced | craft-only | not-reproducible, each with the method used and the response captured
```

**2. Compare line**

```text
crafted: 401 marker X | provider tool: 200 marker Y -> simulator and real path differ, record both
```

**3. Gap note**

```text
simulator cannot emit case C -> C marked craft-only with this reason so a reader knows its evidence is thinner
```

## Pitfalls

- Presenting a crafted delivery as though a partner could reproduce it through their own dashboard
- Trusting a simulator that never signs and concluding verification works
- Triggering a delivery to a live receiver while testing the facility

## Done when

- Each key observation carries a reproduction label and the method used
- Cases the provider facility cannot produce are listed as craft-only with reasons

## References

- [Stripe - Testing webhooks locally](https://docs.stripe.com/webhooks/test)
- [GitHub - Webhook testing with a local server](https://docs.github.com/en/webhooks/using-webhooks/webhook-events-and-payloads)
