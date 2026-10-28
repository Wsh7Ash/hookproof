---
name: timing-sample-collection-rigor
description: "Gather timing evidence the way a claim will be judged: interleaved groups, enough samples and an honest statement of spread, so a timing difference is separable from network noise. Use when a report will include any statement about how long the endpoint takes to respond in different cases"
pack: hookproof
version: 1.0.0
category: webhook-tooling
tags: [confirm, timing, method]
---

# Timing Sample Collection Rigor

> Gather timing evidence the way a claim will be judged: interleaved groups, enough samples and an honest statement of spread, so a timing difference is separable from network noise

**Use when:** a report will include any statement about how long the endpoint takes to respond in different cases

**Avoid when:** the report makes no timing claim at all and only the code path is cited

## Procedure

1. Define the two or more groups you will compare and the single variable that differs between them.
2. Interleave the groups round-robin rather than running one group then the other, so drift does not masquerade as a difference.
3. Collect a sample count large enough to characterize spread, and record the exact number you used.
4. Compute and record a simple distribution for each group: median and range are sufficient for a report.
5. Separate your own client's latency from the endpoint's by measuring a baseline against an endpoint you know is simple.
6. Write what the data supports and nothing more, including a statement that the difference was not separable when that is the result.

## Signals

- Groups were run in blocks, so time drift is confounded with the difference being measured
- A conclusion rests on two or three samples per group
- The report states a difference without publishing the sample count or spread
- Client-side latency was never separated from endpoint latency

## Patterns

**1. Method line**

```text
groups A/B, interleaved round-robin, N=40 per group, median 9ms vs 11ms, range 7-14ms vs 7-16ms
```

**2. Baseline**

```text
measure a trivial endpoint under the same conditions to establish your own transport noise floor before comparing groups
```

**3. Honest result**

```text
when ranges overlap heavily, write that the difference was not separable at N samples on this network and rely on the code observation instead
```

## Pitfalls

- Reporting a timing vulnerability from a handful of measurements taken in blocks
- Claiming a separation the data does not support because the ranges overlap
- Forgetting that the code path reading already settles the question without any timing data

## Done when

- Sample count, grouping method and median with range are recorded for each group
- The written claim matches what the data supports, including a negative result where that is what occurred

## References

- [CWE-208 - Observable timing discrepancy](https://cwe.mitre.org/data/definitions/208.html)
- [PortSwigger - Timing attacks in practice](https://portswigger.net/web-security/authentication)
