"""hookproof skills 34-50: confirm, harden and document phases."""

from __future__ import annotations

SKILLS: list[dict] = [
    {
        "slug": "clean-session-reproduction-recipe",
        "title": "Clean Session Reproduction Recipe",
        "summary": "Write a reproduction that starts cold every time, so a reviewer or the sending partner can replay your observation without inheriting your dedup state or stored identifiers",
        "use_when": "a webhook observation must be handed to an owner or partner who will replay it in a different environment",
        "avoid_when": "the behaviour is deterministic and cannot depend on stored state, which a repeat delivery already proved",
        "tags": ["confirm", "reproduction", "evidence"],
        "steps": [
            "Identify every store that could remember your earlier deliveries: deduplication, queues, caches and any rate limiter.",
            "State which of those must be empty before step one and how a reader clears or avoids each one.",
            "Use a fresh synthetic event identifier for each run so prior runs cannot pre-seed the dedup store.",
            "Write the request sequence in order, including waits, so it can be replayed without interpretation.",
            "Record the status and response marker for each step so a reader can tell a pass from a divergence.",
            "Package the recipe with the observation it produced and mark any step a partner cannot reproduce outside your session.",
        ],
        "signals": [
            "The reproduction succeeds on your machine but fails for a reviewer with a warm dedup store",
            "The first delivery of a session behaves differently from every later one",
            "A step has no recorded status, leaving the state at that point ambiguous",
            "The recipe depends on an identifier that was already seen by an earlier probe",
        ],
        "patterns": [
            (
                "Recipe block",
                "precondition: dedup store empty for this identifier\n1. POST /hooks/demo (no signature) -> expect 401\n2. POST /hooks/demo (valid signature, id test_evt_r1) -> record status\n3. repeat step 2 -> record status and marker\nrecord every status",
            ),
            (
                "Fresh-id rule",
                "each run uses a new identifier, e.g. suffixed with the run number, so no run inherits another's dedup entry",
            ),
            (
                "Assumption list",
                "if a step cannot be replayed outside your session, write it as an environment assumption rather than presenting it as deterministic",
            ),
        ],
        "pitfalls": [
            "Writing a reproduction that silently relies on a dedup entry your earlier probe created",
            "Omitting the empty-store precondition, so the reviewer sees a different result and reports a false negative",
            "Presenting an environment-dependent sequence as though it were deterministic",
        ],
        "done_when": [
            "A numbered recipe lists every delivery with its status and the stores that must be empty first",
            "The recipe reproduces in a fresh context without relying on state from earlier runs",
        ],
        "refs": [
            "[PortSwigger - Writing reproducible reports](https://portswigger.net/web-security)",
            "[NIST - Evidence handling guidance](https://csrc.nist.gov/publications/detail/sp/800-86/final)",
        ],
        "meta": {"phase": "confirm"},
    },
    {
        "slug": "sandbox-reproduction-with-provider-tool",
        "title": "Sandbox Reproduction With Provider Tool",
        "summary": "Reproduce the observation using the provider's own simulator or sandbox so the evidence comes from the delivery path partners actually use rather than from a hand-crafted request",
        "use_when": "the sending provider offers a testing facility and the observation should be confirmed through it",
        "avoid_when": "the provider has no such facility, in which case the gap is recorded rather than worked around silently",
        "tags": ["confirm", "provider", "sandbox"],
        "steps": [
            "Select the provider testing method identified in the scope phase and confirm it produces a real signature.",
            "Trigger one delivery through that method and capture the receiver's status, body and timing.",
            "Compare the response with your own crafted delivery for the same case; a difference means the simulator and real path differ.",
            "If the simulator cannot produce the failing case, record which case remains craft-only and why.",
            "Check that the simulator targeted the intended environment rather than a live receiver.",
            "Record the reproduction as provider-reproduced, craft-only or not-reproducible with the reason.",
        ],
        "signals": [
            "The provider tool produces a delivery that behaves differently from your crafted one",
            "The simulator omits the signature header entirely, so it cannot exercise verification",
            "The tool sent to a live receiver rather than the sandbox you intended",
            "A failing case cannot be constructed through the provider's facility at all",
        ],
        "patterns": [
            (
                "Reproduction label",
                "provider-reproduced | craft-only | not-reproducible, each with the method used and the response captured",
            ),
            (
                "Compare line",
                "crafted: 401 marker X | provider tool: 200 marker Y -> simulator and real path differ, record both",
            ),
            (
                "Gap note",
                "simulator cannot emit case C -> C marked craft-only with this reason so a reader knows its evidence is thinner",
            ),
        ],
        "pitfalls": [
            "Presenting a crafted delivery as though a partner could reproduce it through their own dashboard",
            "Trusting a simulator that never signs and concluding verification works",
            "Triggering a delivery to a live receiver while testing the facility",
        ],
        "done_when": [
            "Each key observation carries a reproduction label and the method used",
            "Cases the provider facility cannot produce are listed as craft-only with reasons",
        ],
        "refs": [
            "[Stripe - Testing webhooks locally](https://docs.stripe.com/webhooks/test)",
            "[GitHub - Webhook testing with a local server](https://docs.github.com/en/webhooks/using-webhooks/webhook-events-and-payloads)",
        ],
        "meta": {"phase": "confirm"},
    },
    {
        "slug": "rejection-evidence-capture",
        "title": "Rejection Evidence Capture",
        "summary": "Record every rejection as status, body marker, timing and header set, so a claim that verification works or fails rests on captured responses rather than on memory",
        "use_when": "a probe has produced a rejection or acceptance and the result is going into a report",
        "avoid_when": "the observation is a configuration reading that needs no request evidence",
        "tags": ["confirm", "evidence", "rejection"],
        "steps": [
            "Capture the full response for each case: status line, every header, the body and the measured duration.",
            "Label each capture with the case that produced it, such as missing, malformed, stale or wrong key.",
            "Include the control capture with a valid signature, since a comparison needs both sides.",
            "Record your request shape beside each response, including which header you manipulated.",
            "Keep only markers and hashes for bodies containing anything sensitive; never archive a real event body.",
            "Index each capture with a number and a timestamp so a reader can trace a claim to its evidence line.",
        ],
        "signals": [
            "A report claims a rejection without the response that shows it",
            "Captures lack timestamps, so the order of events cannot be established",
            "A control with a valid signature is missing from the evidence set",
            "A body containing sensitive content was archived in full",
        ],
        "patterns": [
            (
                "Capture block",
                "E-007 | 2026-10-28T10:14Z | case=wrong-key | req: sig header replaced | resp: 401, marker invalid signature, 10ms",
            ),
            (
                "Control rule",
                "every rejection set includes the valid-signature control captured in the same session, so both sides share conditions",
            ),
            (
                "Body rule",
                "store status, headers and a body marker; hash the body if sameness must be proven, never archive the body itself",
            ),
        ],
        "pitfalls": [
            "Reporting a rejection from memory when the capture was never saved",
            "Comparing captures from different sessions or environments and treating them as one experiment",
            "Archiving a delivery body that contained anything beyond your synthetic fixture",
        ],
        "done_when": [
            "Every claim in the report maps to a numbered capture with status, marker, timing and request shape",
            "A valid-signature control capture exists for each rejection set",
        ],
        "refs": [
            "[NIST SP 800-61 - Incident documentation](https://csrc.nist.gov/pubs/sp/800/61/r2/final)",
            "[OWASP - Reporting security findings](https://owasp.org/www-project-web-security-testing-guide/)",
        ],
        "meta": {"phase": "confirm"},
    },
    {
        "slug": "timing-sample-collection-rigor",
        "title": "Timing Sample Collection Rigor",
        "summary": "Gather timing evidence the way a claim will be judged: interleaved groups, enough samples and an honest statement of spread, so a timing difference is separable from network noise",
        "use_when": "a report will include any statement about how long the endpoint takes to respond in different cases",
        "avoid_when": "the report makes no timing claim at all and only the code path is cited",
        "tags": ["confirm", "timing", "method"],
        "steps": [
            "Define the two or more groups you will compare and the single variable that differs between them.",
            "Interleave the groups round-robin rather than running one group then the other, so drift does not masquerade as a difference.",
            "Collect a sample count large enough to characterize spread, and record the exact number you used.",
            "Compute and record a simple distribution for each group: median and range are sufficient for a report.",
            "Separate your own client's latency from the endpoint's by measuring a baseline against an endpoint you know is simple.",
            "Write what the data supports and nothing more, including a statement that the difference was not separable when that is the result.",
        ],
        "signals": [
            "Groups were run in blocks, so time drift is confounded with the difference being measured",
            "A conclusion rests on two or three samples per group",
            "The report states a difference without publishing the sample count or spread",
            "Client-side latency was never separated from endpoint latency",
        ],
        "patterns": [
            (
                "Method line",
                "groups A/B, interleaved round-robin, N=40 per group, median 9ms vs 11ms, range 7-14ms vs 7-16ms",
            ),
            (
                "Baseline",
                "measure a trivial endpoint under the same conditions to establish your own transport noise floor before comparing groups",
            ),
            (
                "Honest result",
                "when ranges overlap heavily, write that the difference was not separable at N samples on this network and rely on the code observation instead",
            ),
        ],
        "pitfalls": [
            "Reporting a timing vulnerability from a handful of measurements taken in blocks",
            "Claiming a separation the data does not support because the ranges overlap",
            "Forgetting that the code path reading already settles the question without any timing data",
        ],
        "done_when": [
            "Sample count, grouping method and median with range are recorded for each group",
            "The written claim matches what the data supports, including a negative result where that is what occurred",
        ],
        "refs": [
            "[CWE-208 - Observable timing discrepancy](https://cwe.mitre.org/data/definitions/208.html)",
            "[PortSwigger - Timing attacks in practice](https://portswigger.net/web-security/authentication)",
        ],
        "meta": {"phase": "confirm"},
    },
    {
        "slug": "retry-amplification-confirmation",
        "title": "Retry Amplification Confirmation",
        "summary": "Confirm from the receiver's own telemetry how many deliveries your rejection actually produced, so the report states measured amplification rather than an estimate from documentation",
        "use_when": "probes have produced rejections and the provider's documented retry behaviour needs checking against reality",
        "avoid_when": "every probe returned a status the provider never retries",
        "tags": ["confirm", "retries", "operations"],
        "steps": [
            "Note the delivery count immediately before and after a probe family that produces a chosen rejection status.",
            "Query the receiver's logs for repeated deliveries carrying the same event identifier.",
            "Record the number of arrivals, their timestamps and the status the receiver returned each time.",
            "Compare the measured count with the provider's documented retry expectation for that status.",
            "Check whether retries continued past the end of the probe, since queued redelivery extends your footprint.",
            "Report the measured multiplier beside the plan, and tell the owner if retries are still draining.",
        ],
        "signals": [
            "One crafted delivery produced several arrivals with the same event identifier",
            "Retries continued after the assessment session had ended",
            "The measured count differs noticeably from the documented expectation",
            "The receiver's response status sits in a class the provider treats as retryable",
        ],
        "patterns": [
            (
                "Measurement line",
                "probe at 10:14Z produced 1 delivery; arrivals with id test_evt_r1: 5 total over 90s -> measured multiplier 5x",
            ),
            (
                "Comparison",
                "documented expectation for 500: up to N retries over T; observed: M over T2 -> record both, state whether they agree",
            ),
            (
                "Footprint note",
                "if retries were still arriving when the session ended, record the drain time and tell the owner, since that is a side effect you caused",
            ),
        ],
        "pitfalls": [
            "Quoting the documented retry count instead of measuring what your own test produced",
            "Counting arrivals across two probe families that reused one identifier",
            "Ending the session without checking whether retries were still draining",
        ],
        "done_when": [
            "A measured multiplier with arrival timestamps is recorded for at least one rejection status",
            "Whether retries outlived the session is stated, with a drain note if they did",
        ],
        "refs": [
            "[Stripe - Webhook retries and recovery](https://docs.stripe.com/webhooks#handle-retry-events)",
            "[GitHub - Redelivery of webhooks](https://docs.github.com/en/webhooks/using-webhooks/redelivering-webhooks)",
        ],
        "meta": {"phase": "confirm"},
    },
    {
        "slug": "impact-boundary-statement",
        "title": "Impact Boundary Statement",
        "summary": "State precisely what an attacker could and could not do with the observed behaviour, including the precondition of already holding a valid signature, so severity is argued rather than assumed",
        "use_when": "a webhook observation is confirmed and the report needs an impact statement that will survive review",
        "avoid_when": "the observation is a configuration note with no behavioural consequence",
        "tags": ["confirm", "impact", "severity"],
        "steps": [
            "List the precondition required to reach the behaviour, such as possessing a valid signature or controlling a target URL.",
            "State the effect once that precondition holds, in terms of what changes in the system rather than in adjectives.",
            "State what remains impossible even with the behaviour, so the reader sees the boundary of the claim.",
            "Separate the inbound signature finding from any outbound target finding, since their preconditions differ entirely.",
            "Rank the finding against a recognised class such as replay, unsigned input or server-side request, with a reason.",
            "Write the paragraph a reviewer would accept: precondition, effect, boundary, class, and nothing beyond it.",
        ],
        "signals": [
            "An impact statement reads as an adjective list with no precondition named",
            "Severity is stated without saying what an attacker must already possess",
            "The statement does not say what the behaviour cannot achieve",
            "Inbound and outbound consequences are merged into one undifferentiated claim",
        ],
        "patterns": [
            (
                "Impact skeleton",
                "precondition: <what the caller must already have>\neffect: <what changes in the system>\nboundary: <what remains impossible>\nclass: <replay | unsigned input | ssrf | disclosure>",
            ),
            (
                "Worked example",
                "precondition: possession of one valid signed delivery; effect: the same event can be re-delivered within the window despite dedup absent; boundary: no new event content can be introduced; class: replay",
            ),
            (
                "Dual-finding rule",
                "if both an inbound and an outbound issue exist, write two separate paragraphs; merging them hides the differing preconditions",
            ),
        ],
        "pitfalls": [
            "Claiming critical severity for behaviour that already requires a valid signature to reach",
            "Omitting the boundary, which makes a reviewer trust the claim less rather than more",
            "Blending an outbound target issue into an inbound signature finding so neither can be triaged",
        ],
        "done_when": [
            "The statement names precondition, effect, boundary and class in that order",
            "Inbound and outbound consequences appear as separate claims when both exist",
        ],
        "refs": [
            "[OWASP - Risk rating methodology](https://owasp.org/www-community/OWASP_Risk_Rating_Methodology)",
            "[CVSS - Qualitative severity mapping](https://www.first.org/cvss/)",
        ],
        "meta": {"phase": "confirm"},
    },
    {
        "slug": "raw-buffer-verification-ordering",
        "title": "Raw Buffer Verification Ordering",
        "summary": "Move signature verification to the exact bytes received, before any parsing or decoding, so what is checked and what is processed cannot drift apart",
        "use_when": "the receiver parses or decodes the body before verification, or the verification point cannot be located before the parse",
        "avoid_when": "verification already runs on a captured buffer and a formatting-variant test confirms it",
        "tags": ["harden", "parsing", "signature"],
        "steps": [
            "Locate the first place in the request pipeline where the body is read and record everything that touches it before verification.",
            "Capture the raw request body into a buffer before any framework body parser runs, and verify against that buffer.",
            "Confirm that only after a successful verification does the handler parse or decode the content.",
            "Handle content encoding explicitly: either verify the received bytes or decode first and document which one you chose.",
            "Re-run the formatting-variant and encoding tests from the probe phase and confirm both now behave as expected.",
            "Record the pipeline order with the code location so a later refactor cannot silently move verification after parsing.",
        ],
        "signals": [
            "A framework body parser runs before the verification middleware",
            "Verification reads a parsed object rather than a buffer",
            "A formatting change in the delivered body alters the bytes that get hashed",
            "Content decoding happens implicitly with no recorded decision about it",
        ],
        "patterns": [
            (
                "Target order",
                "receive -> buffer raw bytes -> verify over buffer -> parse -> handle; record the file and function that owns each stage",
            ),
            (
                "Reorder test",
                "after the change, send identical logical content with different formatting: it must fail verification, because raw bytes now govern",
            ),
            (
                "Decision note",
                "document whether you verify received bytes or decoded bytes; either can be correct, silently choosing is what causes defects",
            ),
        ],
        "pitfalls": [
            "Moving verification earlier and breaking legitimate senders who compress their payloads",
            "Fixing the handler while a global middleware still parses the body first",
            "Assuming the new ordering holds without re-running the formatting-variant test",
        ],
        "done_when": [
            "The pipeline order is recorded with code locations for each stage",
            "The formatting-variant retest fails verification and the result is captured",
        ],
        "refs": [
            "[PortSwigger - HTTP request smuggling fundamentals](https://portswigger.net/web-security/request-smuggling)",
            "[Stripe - Verify the raw request body](https://docs.stripe.com/webhooks/signature)",
        ],
        "meta": {"phase": "harden"},
    },
    {
        "slug": "constant-time-comparison-enforcement",
        "title": "Constant-Time Comparison Enforcement",
        "summary": "Replace generic equality on signature bytes with a constant-time comparison, closing the timing signal before anyone tries to measure it",
        "use_when": "the verifier compares signatures or secrets with a language-level equality operator",
        "avoid_when": "a constant-time helper is already used and a reading of the call confirms it",
        "tags": ["harden", "cryptography", "timing"],
        "steps": [
            "Find every comparison of a signature, secret or derived value against attacker-controlled input and record its call site.",
            "Replace generic equality with the standard library's constant-time comparison helper for each of those sites.",
            "Check the comparison runs on decoded bytes of equal expected length, not on a raw string of attacker-chosen length.",
            "Add a length check before the comparison so a mismatched length fails fast without leaking prefix information.",
            "Re-run the timing probe groups and record that the code path now uses the helper, with the measurement as support.",
            "Record the changed call sites so a later refactor cannot quietly reintroduce an equality operator.",
        ],
        "signals": [
            "A signature is compared with a generic equality operator",
            "Comparison runs before a length check, on bytes of attacker-chosen length",
            "A hand-rolled comparison loop compares and returns early on the first differing byte",
            "Only one of several verification paths was converted",
        ],
        "patterns": [
            (
                "Call-site list",
                "file/function | current comparison | replacement\nhooks/verify.py:signature_eq | == | constant_time_compare\nhooks/jwt.py:claim_eq | == | constant_time_compare",
            ),
            (
                "Length rule",
                "check decoded length first, then compare in constant time; both steps recorded as separate code positions",
            ),
            (
                "Retest instruction",
                "re-run the interleaved timing groups from the probe phase and note the code change alongside whatever the measurements now show",
            ),
        ],
        "pitfalls": [
            "Converting one comparison while a second path in the same handler still uses equality",
            "Comparing hex strings of different lengths without a length check in front",
            "Claiming the timing signal is gone without re-running the measurement you took before",
        ],
        "done_when": [
            "Every comparison against attacker-controlled input uses a constant-time helper with a preceding length check",
            "The retest result is recorded next to the call-site list",
        ],
        "refs": [
            "[CWE-208 - Observable timing discrepancy](https://cwe.mitre.org/data/definitions/208.html)",
            "[PortSwigger - Timing attacks](https://portswigger.net/web-security/authentication)",
        ],
        "meta": {"phase": "harden"},
    },
    {
        "slug": "tolerance-window-bounding",
        "title": "Tolerance Window Bounding",
        "summary": "Set the acceptance window to the smallest value that still covers the sender's clock skew, and make it two-sided, so the replay window stops being an unbounded convenience",
        "use_when": "the timestamp tolerance is wide, one-sided, or taken from a default no one has reviewed",
        "avoid_when": "the window is already two-sided, deliberately chosen and smaller than the sender's retry horizon",
        "tags": ["harden", "timestamp", "replay"],
        "steps": [
            "Record the current tolerance, its directionality and where the value comes from in configuration.",
            "Measure the actual clock skew between sender and receiver so the replacement value has evidence behind it.",
            "Choose a window comfortably larger than measured skew but smaller than the sender's own retry horizon.",
            "Enforce the window symmetrically, rejecting both stale and far-future timestamps.",
            "Confirm the timestamp is inside the signed bytes so it cannot simply be rewritten.",
            "Re-run the stale and future probes and record the enforced boundaries as they now behave.",
        ],
        "signals": [
            "The tolerance is larger than the provider's own retry horizon, so a retry can never fail the window",
            "Only stale values are rejected while future values are unbounded",
            "The timestamp sits outside the signed byte set",
            "The value is a framework default nobody has reviewed since integration",
        ],
        "patterns": [
            (
                "Window record",
                "before: 3600s, past-only, unsigned timestamp\nafter: 300s, two-sided, signed timestamp\nmeasured skew: 2s; sender retry horizon: 7200s",
            ),
            (
                "Constraint order",
                "window <= sender retry horizon, and window >> measured skew; write both inequalities with the numbers you used",
            ),
            (
                "Retest expectation",
                "stale at -3600s -> reject, future at +3600s -> reject, control at 0s -> accept; all three recorded",
            ),
        ],
        "pitfalls": [
            "Tightening the window until legitimate deliveries start failing because skew was never measured",
            "Enforcing a symmetric window while the timestamp remains unsigned and replaceable",
            "Leaving the old value in one environment while changing another",
        ],
        "done_when": [
            "The new window, its directionality and its signing status are recorded with measured skew",
            "Stale, future and control probes each show the expected verdict after the change",
        ],
        "refs": [
            "[Stripe - Signature tolerance](https://docs.stripe.com/webhooks/signature)",
            "[CWE-294 - Authentication bypass by capture-replay](https://cwe.mitre.org/data/definitions/294.html)",
        ],
        "meta": {"phase": "harden"},
    },
    {
        "slug": "replay-store-and-dedup-implementation",
        "title": "Replay Store and Dedup Implementation",
        "summary": "Give the receiver a real memory of deliveries it has already processed, keyed on a signed identifier and bounded by a window that outlasts the sender's retries",
        "use_when": "duplicates are processed twice because no dedup store exists or its key comes from an unsigned source",
        "avoid_when": "a dedup store keyed on a signed field already suppresses duplicates with a reviewed window",
        "tags": ["harden", "idempotency", "replay"],
        "steps": [
            "Choose the deduplication key from inside the signed payload, such as an event identifier the sender signs.",
            "Write the key to the store only after the side effect commits, so a failure between the two cannot lose the record.",
            "Set the retention window longer than the sender's full retry schedule plus the tolerance window.",
            "Make the write atomic with the check, so two concurrent deliveries of one event cannot both pass.",
            "Confirm a second delivery returns a suppression response rather than a fresh success that hides the duplicate.",
            "Re-run the duplicate probe and record the suppression behaviour and the window you configured.",
        ],
        "signals": [
            "The deduplication key comes from an unsigned header rather than the signed body",
            "The retention window is shorter than the sender's retry schedule",
            "Two concurrent duplicates both reach the side effect",
            "A suppressed duplicate is reported to the sender as a fresh success",
        ],
        "patterns": [
            (
                "Key and window",
                "key: signed event_id | written: post-commit | retention: 86400s | sender horizon: 7200s | atomic: yes",
            ),
            (
                "Concurrency rule",
                "check and write must be one atomic operation; separate read-then-write lets two duplicates through on a busy receiver",
            ),
            (
                "Retest expectation",
                "three deliveries of one identifier: first processed, second suppressed, third suppressed; record the three statuses",
            ),
        ],
        "pitfalls": [
            "Keying dedup on a timestamp, which resets the store's memory on every retry",
            "Recording the key before the side effect commits and losing events when processing fails",
            "Reporting success to the sender on a suppression, which hides a real duplicate from their dashboard",
        ],
        "done_when": [
            "The key source, write ordering, retention window and concurrency approach are recorded",
            "A three-delivery retest shows processing followed by suppression each time",
        ],
        "refs": [
            "[Stripe - Idempotency keys](https://docs.stripe.com/api/idempotent_requests)",
            "[CWE-294 - Authentication bypass by capture-replay](https://cwe.mitre.org/data/definitions/294.html)",
        ],
        "meta": {"phase": "harden"},
    },
    {
        "slug": "uniform-rejection-response",
        "title": "Uniform Rejection Response",
        "summary": "Return one status and one body for every verification failure, so a caller cannot map your verifier's internal structure by trying different malformed inputs",
        "use_when": "rejection bodies or statuses differ between failure cases as the leakage probe showed",
        "avoid_when": "every verification failure already returns one fixed response with only a correlation id for operators",
        "tags": ["harden", "errors", "disclosure"],
        "steps": [
            "List the distinct failure cases your probe produced and the marker each response carried.",
            "Replace them with a single status and a single body covering all verification failures.",
            "Keep a correlation id in the response and the specific reason in the server log only.",
            "Confirm the response status is one the sender treats as terminal, so a rejection never becomes a retry loop.",
            "Re-run every rejection case from the probe phase and confirm each now returns the identical response.",
            "Record the before and after markers so the reduction in disclosed detail is provable.",
        ],
        "signals": [
            "Different failure cases return different messages or statuses",
            "A response body contains a reason string, a stack trace or a configuration key",
            "A verification failure returns a status the sender retries",
            "The specific reason is only reachable through an externally visible response",
        ],
        "patterns": [
            (
                "Before and after",
                "before: 401 missing / 401 stale / 401 wrong-key with three markers\nafter: 401 with one marker and correlation id, reason only in server log",
            ),
            (
                "Status choice",
                "pick a status the provider documents as terminal for this class; record the provider policy line you are relying on",
            ),
            (
                "Retest sweep",
                "re-run missing, malformed, stale and wrong-key cases; all four must return byte-identical responses",
            ),
        ],
        "pitfalls": [
            "Unifying the body while leaving statuses different, so detail still leaks through the code",
            "Choosing a status the sender retries and creating an amplification problem while fixing a disclosure one",
            "Removing the correlation id, which leaves operators unable to diagnose a real failure",
        ],
        "done_when": [
            "All tested failure cases return an identical status and body with a correlation id",
            "The chosen status is confirmed terminal against the provider's documented retry classes",
        ],
        "refs": [
            "[CWE-209 - Generation of error message containing sensitive information](https://cwe.mitre.org/data/definitions/209.html)",
            "[OWASP - Error handling guidance](https://owasp.org/www-project-web-security-testing-guide/)",
        ],
        "meta": {"phase": "harden"},
    },
    {
        "slug": "outbound-target-allowlist-and-egress-control",
        "title": "Outbound Target Allowlist and Egress Control",
        "summary": "Constrain where outbound callbacks may go, at validation time and again at the network layer, so a target field can never become a request into your own infrastructure",
        "use_when": "the application stores or accepts callback destination URLs that it later requests",
        "avoid_when": "destinations are fixed in configuration and no user- or partner-supplied URL can reach the fetcher",
        "tags": ["harden", "ssrf", "outbound"],
        "steps": [
            "Classify which destinations are legitimate: partner hosts, internal services and any address ranges that must never be reached.",
            "Validate the destination at write time and again immediately before the request, since the stored value can change between the two.",
            "Resolve the hostname and reject addresses in private, loopback and link-local ranges rather than checking the string alone.",
            "Disable or strictly bound redirect-following, and re-run the same validation on any redirect target.",
            "Attach no credentials to a destination the validator did not allow, and strip authorization on any cross-host redirect.",
            "Enforce egress restrictions at the network layer as a second control, and record what the layer would block.",
        ],
        "signals": [
            "Validation checks a hostname string but never resolves it before the request",
            "The destination is validated once at write time and never again before the fetch",
            "Redirects are followed without re-running validation on the new target",
            "Fixed credentials are attached to destinations supplied at runtime",
        ],
        "patterns": [
            (
                "Two-stage rule",
                "validate on write, validate again immediately before request, after resolution; a single check at either point is not enough",
            ),
            (
                "Address classes",
                "reject: loopback, private ranges, link-local, and any range the owner lists as internal; record which classes you enforced",
            ),
            (
                "Egress note",
                "network-layer rule as second control: state the destination classes it blocks so the defence in depth is documented",
            ),
        ],
        "pitfalls": [
            "Validating the hostname but resolving it only inside the HTTP client, after the check has already passed",
            "Fixing the initial validation while leaving redirect targets unchecked",
            "Removing credentials from requests and breaking a legitimate partner integration in the process",
        ],
        "done_when": [
            "Validation runs at write time and again after resolution immediately before the request",
            "Redirect handling and credential attachment behaviour are recorded with the network-layer control",
        ],
        "refs": [
            "[OWASP - SSRF prevention cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)",
            "[CWE-918 - Server-side request forgery](https://cwe.mitre.org/data/definitions/918.html)",
        ],
        "meta": {"phase": "harden"},
    },
    {
        "slug": "dual-secret-rotation-with-overlap",
        "title": "Dual Secret Rotation With Overlap",
        "summary": "Rotate signing secrets through a period where two are accepted, so a key change becomes a scheduled operation instead of a coordinated outage with every partner",
        "use_when": "a secret needs changing, or rotation currently requires every sender to switch at the same instant",
        "avoid_when": "the verifier already accepts multiple secrets per provider with a documented overlap",
        "tags": ["harden", "secrets", "rotation"],
        "steps": [
            "Add a second accepted secret for the provider while keeping the current one active, and verify both compute identical results.",
            "Publish the new secret to the sender through the agreed channel and record when it was acknowledged.",
            "Switch verification to prefer the new secret while still accepting the old one for the overlap period.",
            "Monitor verification failures during the overlap, since a sender that missed the message will surface there.",
            "Retire the old secret once the overlap ends, and confirm deliveries with it are now rejected.",
            "Record the rotation with both secret identifiers, the overlap window and the confirmation of retirement.",
        ],
        "signals": [
            "Only one secret can be accepted at a time, so rotation is a synchronised event",
            "Verification failures spike whenever a secret is changed",
            "No monitoring exists that would reveal a sender still using a retired secret",
            "The overlap period has never been exercised or measured",
        ],
        "patterns": [
            (
                "Rotation timeline",
                "T0: add new secret, both accepted | T1: sender acknowledges | T2: prefer new | T3: retire old, confirm rejection",
            ),
            (
                "Failure watch",
                "monitor verification failure rate across T0..T3; a spike at T3 means a sender never moved and the retirement is premature",
            ),
            (
                "Inventory update",
                "update the secret inventory row for both identifiers and the dates, so the next rotation starts from an accurate list",
            ),
        ],
        "pitfalls": [
            "Retiring the old secret before every sender has acknowledged the new one",
            "Adding a second secret without monitoring, so a straggler is discovered as an outage",
            "Leaving both secrets accepted indefinitely because the retirement step never happened",
        ],
        "done_when": [
            "Both secrets were accepted during a measured overlap window with dates recorded",
            "Retirement is confirmed by an observed rejection of a delivery signed with the old secret",
        ],
        "refs": [
            "[NIST SP 800-57 - Key rotation recommendations](https://csrc.nist.gov/pubs/sp/800/57/r5/final)",
            "[Stripe - Rotating endpoint secrets](https://docs.stripe.com/webhooks#rotate-endpoint-secret)",
        ],
        "meta": {"phase": "harden"},
    },
    {
        "slug": "webhook-finding-evidence-pack",
        "title": "Webhook Finding Evidence Pack",
        "summary": "Assemble a report where every webhook claim carries the delivery pair, the responses and the scheme statement that make it checkable by someone who was not present",
        "use_when": "a webhook observation is ready to be written up for the owner or the sending partner",
        "avoid_when": "the finding has already been reported and only a closing note remains",
        "tags": ["document", "evidence", "reporting"],
        "steps": [
            "State the defect in one sentence naming the endpoint, the check and the outcome, without adjectives.",
            "Attach the scheme statement, so the reader knows what the verifier was supposed to check.",
            "Include the delivery pair: the case that failed or passed and the control, each with status, marker and timing.",
            "Record your request shape for every delivery, including which header or field you manipulated.",
            "Give the reproduction recipe and the boundary document version that permitted each request.",
            "State the impact in the precondition, effect, boundary form and stop there.",
        ],
        "signals": [
            "A report claims a verification defect without the delivery pair that revealed it",
            "The scheme statement is missing, so the reader cannot tell what was supposed to be checked",
            "Statuses are given without the response markers that distinguish the cases",
            "Impact is stated without naming the precondition an attacker would already need",
        ],
        "patterns": [
            (
                "Claim skeleton",
                "claim: <endpoint> accepts <case> because <check> is <missing/weak>\nscheme: <what is supposed to be verified>\npair: <case> vs <control>, each with status and marker\nimpact: precondition / effect / boundary / class",
            ),
            (
                "Evidence block",
                "E-011 | case=missing-signature | req: header absent | resp: 401, marker, 9ms\nE-012 | case=valid control | resp: 200, marker, 34ms",
            ),
            (
                "Boundary note",
                "attach the boundary version and mark each delivery as permitted by it, so the test itself can be audited",
            ),
        ],
        "pitfalls": [
            "Presenting a narrative claim when the reader needs the raw delivery pair to judge it",
            "Leaving out the scheme statement, so a reader cannot tell a real gap from an unusual scheme",
            "Inflating impact beyond what the recorded deliveries demonstrate",
        ],
        "done_when": [
            "Every claim is followed by a delivery pair with status, marker, timing and request shape",
            "The scheme statement, reproduction recipe and boundary version are attached to the pack",
        ],
        "refs": [
            "[OWASP - Reporting security findings](https://owasp.org/www-project-web-security-testing-guide/)",
            "[NIST SP 800-61 - Incident handling guidance](https://csrc.nist.gov/pubs/sp/800/61/r2/final)",
        ],
        "meta": {"phase": "document"},
    },
    {
        "slug": "scheme-aware-remediation-wording",
        "title": "Scheme-Aware Remediation Wording",
        "summary": "Describe each fix in the language of the signing scheme and the sender's contract, so the receiving team can implement it without first reverse-engineering your finding",
        "use_when": "a webhook finding is ready to include remediation and the fix spans verifier code, configuration and provider settings",
        "avoid_when": "the fix is a single configuration value with an obvious verification step",
        "tags": ["document", "remediation", "communication"],
        "steps": [
            "Name the layer for each step: verifier code, receiver configuration, sender configuration or network rule.",
            "Write the step in scheme terms: which bytes are signed, which header is read, which window is enforced.",
            "State the expected effect of each step so a reader can verify the change rather than assume it.",
            "Include a retest instruction using the exact delivery from the probe that revealed the defect.",
            "Mark steps needing a partner action or a scheduled window, since those require coordination rather than a merge request.",
            "List what you deliberately did not change and why, so nothing appears silently out of scope.",
        ],
        "signals": [
            "A remediation step says fix the verification without naming which bytes or header it concerns",
            "A step requiring partner action appears with no owner or date attached",
            "No retest instruction is given, so closure cannot be verified",
            "The report does not say which related items were left unchanged",
        ],
        "patterns": [
            (
                "Step line",
                "layer: receiver code | change: verify over raw buffer before parse | effect: formatting variants now fail | retest: replay delivery E-011",
            ),
            (
                "Scheme terms",
                "reference the canonical string, the header name and the tolerance value explicitly, because that is the vocabulary the implementer works in",
            ),
            (
                "Not-changed list",
                "unchanged: sender retry policy, because it belongs to the partner; recorded so it is not reported as an outstanding item on our side",
            ),
        ],
        "pitfalls": [
            "Writing generic advice the implementer already knows while omitting the specifics of this scheme",
            "Hiding a partner-dependent step inside our own task list so it never gets scheduled",
            "Omitting retest instructions, which makes an owner's closure claim unverifiable",
        ],
        "done_when": [
            "Every step names its layer, its effect in scheme terms and a retest instruction",
            "Partner-dependent steps carry an owner and a date, and unchanged items are listed with reasons",
        ],
        "refs": [
            "[OWASP - Defect remediation guidance](https://owasp.org/www-project-web-security-testing-guide/)",
            "[NIST SP 800-40 - Patch and configuration management](https://csrc.nist.gov/pubs/sp/800/40/r4/final)",
        ],
        "meta": {"phase": "document"},
    },
    {
        "slug": "provider-coordinated-disclosure",
        "title": "Provider Coordinated Disclosure",
        "summary": "Route a webhook defect to the party that can fix it, receiver team or sending provider, agree a timeline in writing, and re-test before announcing closure",
        "use_when": "a finding involves the sending provider's own scheme, SDK or platform behaviour rather than only your receiver",
        "avoid_when": "the defect is entirely in receiver code and needs no partner involvement",
        "tags": ["document", "disclosure", "coordination"],
        "steps": [
            "Decide the fixing party from the evidence: receiver code, receiver configuration, or provider platform.",
            "Prepare the report with the evidence pack and reproduction recipe, using synthetic data only.",
            "Send it to the property owner first, since they hold the relationship and the contractual path to the provider.",
            "Agree an acknowledgement date, a target fix date and a disclosure date, recorded in writing.",
            "Re-test after the fix lands using the same recipe and record the before and after response markers.",
            "Close with a note on anything still open, including items that depend on a provider release you do not control.",
        ],
        "signals": [
            "The defect requires a change only the sending provider can make to its scheme or SDK",
            "The report reaches the provider before the owner has seen it, breaking the agreed channel",
            "Closure was announced without a re-test showing the behaviour changed",
            "Items remain open with no owner and no date attached",
        ],
        "patterns": [
            (
                "Routing line",
                "defect: provider SDK re-encodes the body before signing | fixing party: provider | channel: owner to provider | receiver mitigation: none available",
            ),
            (
                "Timeline block",
                "ack by <date> | fix target <date> | re-test <date> | disclosure <date> -> confirmed in writing by both sides",
            ),
            (
                "Closure note",
                "re-tested with the published recipe at <timestamp>: response moved from <before marker> to <after marker> -> item closed",
            ),
        ],
        "pitfalls": [
            "Contacting a provider directly about a defect that is really the receiver's configuration choice",
            "Publishing a delivery body in a report a partner portal will retain indefinitely",
            "Announcing closure without a re-test that shows the behaviour actually changed",
        ],
        "done_when": [
            "The fixing party and channel are named with a timeline confirmed in writing",
            "A post-fix re-test records before and after response markers for each closed item",
        ],
        "refs": [
            "[ISO 29147 - Vulnerability disclosure guidance](https://www.iso.org/standard/72311.html)",
            "[OWASP - Coordinated disclosure](https://owasp.org/www-project-vulnerability-disclosure/)",
        ],
        "meta": {"phase": "document"},
    },
    {
        "slug": "coverage-gap-and-skip-register",
        "title": "Coverage Gap and Skip Register",
        "summary": "Publish the list of tests you did not run and why, so an untested path reads as a declared gap rather than as an unremarked pass",
        "use_when": "a webhook assessment ends with cases that were forbidden, unsupported or impossible to exercise",
        "avoid_when": "every planned case ran and each produced a recorded response",
        "tags": ["document", "coverage", "reporting"],
        "steps": [
            "List every planned case that did not run, using the skip notes recorded during the scope and probe phases.",
            "For each gap record the reason class: forbidden by boundary, unsupported by provider, needs an environment you lack, or not safe to trigger.",
            "State what a reader may and may not conclude from the gap, since an untested case is neither a pass nor a confirmed defect.",
            "Rank the gaps by how much they weaken the overall claim, so a reviewer can judge the assessment rather than trust it blindly.",
            "Name what would close each gap: a permission, a provider capability or an environment, with an owner where one exists.",
            "Place the register next to the findings, not in an appendix, because a reader who never sees it will over-read the results.",
        ],
        "signals": [
            "The report lists only tests that ran, implying coverage that was never achieved",
            "A replay case was forbidden by the boundary but the report says replay resistance works",
            "No provider capability exists for a case and nothing in the report says so",
            "Gaps appear only in a section most readers skip",
        ],
        "patterns": [
            (
                "Register row",
                "case: replay of signed delivery | reason: forbidden by boundary v2 | conclusion: not assessed | closes with: written permission",
            ),
            (
                "Reason classes",
                "forbidden (scope), unsupported (provider capability), unavailable (environment), unsafe (side effects); pick one and say which",
            ),
            (
                "Placement rule",
                "the register sits directly after the summary so a reader meets it before the findings, never in an appendix",
            ),
        ],
        "pitfalls": [
            "Letting an untested case read as a pass because the report describes only what succeeded",
            "Filing the register where a reviewer will not reach it and overstating coverage by omission",
            "Listing a gap without saying what would close it, which leaves it permanently open",
        ],
        "done_when": [
            "Every case that did not run appears in the register with a reason class and a stated conclusion",
            "Each gap names what would close it and sits beside the findings rather than in an appendix",
        ],
        "refs": [
            "[NIST SP 800-53 - Assessment coverage documentation](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)",
            "[OWASP - Reporting security findings](https://owasp.org/www-project-web-security-testing-guide/)",
        ],
        "meta": {"phase": "document"},
    },
]