---
name: timestamp-and-tolerance-format-audit
description: "Establish how the timestamp is encoded and how wide the acceptance window is, since the replay window is defined entirely by those two facts. Use when the signed string includes a timestamp and the tolerance the verifier enforces has not been confirmed"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [identify, timestamp, replay]
---

# Timestamp and Tolerance Format Audit

> Establish how the timestamp is encoded and how wide the acceptance window is, since the replay window is defined entirely by those two facts

**Use when:** the signed string includes a timestamp and the tolerance the verifier enforces has not been confirmed

**Avoid when:** the scheme carries no timestamp and replay defence rests on something other than a time window

## Procedure

1. Capture the timestamp element from a real delivery and record its unit: seconds, milliseconds or a formatted date string.
2. Locate the tolerance value in configuration or code and record it in seconds, noting whether it is configurable per environment.
3. Check which clock the verifier compares against, because a receiver with drifting clock rejects valid deliveries silently.
4. Determine whether the timestamp is inside the signed string, because an unsigned timestamp can simply be replaced.
5. Note whether the window is applied symmetrically (past and future) or only to stale values.
6. Write both numbers next to each other: the encoded unit and the tolerance, plus the maximum replay window they imply.

## Signals

- The tolerance lives in a constant nobody has reviewed since the integration shipped
- The timestamp sits outside the signed bytes and can be rewritten independently
- Seconds and milliseconds are mixed between the sender and the receiver
- Future timestamps are accepted without limit while only stale ones are rejected

## Patterns

**1. Window record**

```text
unit: unix seconds | tolerance: 300s | signed: yes | clock: receiver system clock | symmetric: past only
-> replay window = 300s
```

**2. Unit check**

```text
1778900000 is seconds; 1778900000000 is milliseconds; if one side treats the other as its own unit the window becomes effectively infinite
```

**3. Signed-or-not**

```text
timestamp outside the signature -> replaceable; record that as a scheme weakness separate from the tolerance value
```

## Pitfalls

- Assuming the documented default is the deployed value without reading the configuration
- Testing replay against a receiver whose clock differs from the sender's, which distorts every result
- Ignoring that an unsigned timestamp reduces the replay defence to a value the sender's opponent controls

## Done when

- The timestamp unit, tolerance value, signing status and clock source are all recorded
- The resulting maximum replay window is stated as a number in seconds

## References

- [Stripe - Tolerance and replay](https://docs.stripe.com/webhooks/signature)
- [IETF RFC 9110 - Date and time semantics](https://www.rfc-editor.org/rfc/rfc9110)
