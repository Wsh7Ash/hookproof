---
name: delivery-volume-and-rate-budget
description: "Agree a numeric delivery budget before testing, so a retry storm caused by a rejection behaviour never becomes an incident for you or the sending partner. Use when the assessment will send or trigger deliveries and no numeric ceiling has been agreed with the owner"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [scope, rate-limit, operations]
---

# Delivery Volume and Rate Budget

> Agree a numeric delivery budget before testing, so a retry storm caused by a rejection behaviour never becomes an incident for you or the sending partner

**Use when:** the assessment will send or trigger deliveries and no numeric ceiling has been agreed with the owner

**Avoid when:** the rules of engagement already state a per-minute ceiling and a maximum total delivery count

## Procedure

1. Record a numeric ceiling: deliveries per minute, total deliveries for the session and the pause used between probe families.
2. Ask whether the sender retries rejected deliveries and how aggressively, because that multiplies your effective volume.
3. Set a stop condition tied to observed behaviour, such as five consecutive retries, rather than to a fixed plan step count.
4. Check what your own receiver logs and queues will hold, since a test that fills a queue creates work for someone else.
5. Re-read the ceiling before starting a new probe family, not only once at the start of the session.
6. Log your actual delivery count beside the plan so the owner can see the session stayed inside the budget.

## Signals

- The sender retries on 4xx as well as 5xx and nobody knows the backoff schedule
- Your test queue is growing while the plan still has steps remaining
- The ceiling exists in prose with no number attached to it
- A single rejected delivery produced several more deliveries within seconds

## Patterns

**1. Budget record**

```text
per_minute: 3
session_total: 40
pause_between_families: 10s
stop_condition: 5 consecutive sender retries
actual_this_session: 17
```

**2. Multiplier check**

```text
one request x sender retries N times = actual volume; write N next to the ceiling before the first request
```

**3. Queue note**

```text
record queue depth before and after each probe family; growth that outlives the test is a side effect you caused and must report
```

## Pitfalls

- Sending a delivery that the sender retries aggressively and unintentionally amplifying your own volume
- Setting a ceiling without knowing the retry schedule, so the real volume is a multiple of what you planned
- Filling a shared queue and leaving someone else to drain it after you finish

## Done when

- A numeric ceiling, multiplier and stop condition are written down before the first delivery
- The session's actual delivery count is recorded beside the plan and stayed inside the budget

## References

- [PortSwigger - Burp Suite rate limiting guidance](https://portswigger.net/burp/documentation/desktop)
- [NIST - Availability control considerations](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)
