---
name: signature-header-removal-and-blanking
description: "Test each signature-carrying header in three states, because a handler that accepts an empty or whitespace value accepts no verification at all. Use when the signature header is known and its behaviour when present but empty has not been observed"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [probe, headers, signature]
---

# Signature Header Removal and Blanking

> Test each signature-carrying header in three states, because a handler that accepts an empty or whitespace value accepts no verification at all

**Use when:** the signature header is known and its behaviour when present but empty has not been observed

**Avoid when:** the handler already rejects an empty value and a test confirms it in the current build

## Procedure

1. For each candidate signature header, prepare three synthetic deliveries: header absent, header empty, header of whitespace only.
2. Send each one at the agreed rate and capture status, body and timing for every case.
3. Add a fourth case with an obviously invalid non-empty value to separate an emptiness bug from a general rejection.
4. Check whether the header name comparison itself is case-insensitive, since some handlers read only one casing.
5. Record all four outcomes per header in a small table so the reader can see which states pass.
6. Note whether any accepted case reached downstream processing, which changes the finding from theoretical to consequential.

## Signals

- An empty signature value is treated as valid
- A whitespace-only value passes while an invalid non-empty value fails
- The handler reads only one casing of the header name and misses the other
- Acceptance of an empty value is followed by downstream processing of the event

## Patterns

**1. State table**

```text
header state | status | downstream reached
absent | 401 | no
empty | 200 | yes  <- finding
whitespace | 200 | yes  <- finding
invalid value | 401 | no
```

**2. Casing check**

```text
send the correct value under a differently cased header name; a rejection means the handler is case-sensitive about the name
```

**3. Order note**

```text
run these before any valid-signature test so the baseline is established while the store is cold
```

## Pitfalls

- Testing only the absent case, which every handler rejects, and missing the empty-value case entirely
- Assuming a gateway strips an empty header without observing the origin's response
- Concluding no downstream effect without checking what the handler did after accepting

## Done when

- Four header states per candidate header have recorded status, body and timing
- Any accepted case records whether downstream processing occurred

## References

- [MDN - Request header fields](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers)
- [OWASP - Input validation cheat sheet](https://cheatsheetseries.owasp.org/)
