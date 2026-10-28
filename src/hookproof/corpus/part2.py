"""hookproof skills 16-30: probe phase."""

from __future__ import annotations

SKILLS: list[dict] = [
    {
        "slug": "unsigned-delivery-acceptance",
        "title": "Unsigned Delivery Acceptance",
        "summary": "Send one synthetic delivery with no signature at all and record whether the endpoint accepts it, which is the single highest-value check a receiver can fail",
        "use_when": "an inbound endpoint has not yet been observed rejecting a delivery that carries no signature header",
        "avoid_when": "the endpoint has already returned a rejection for an unsigned delivery in the current build",
        "tags": ["probe", "signature", "baseline"],
        "steps": [
            "Confirm the boundary permits sending a delivery to this endpoint and record the rate budget you will stay inside.",
            "Construct one synthetic event with an invented identifier and no signature header of any kind.",
            "Send it once and capture status, body, timing and every response header verbatim.",
            "Repeat a second time to confirm the answer is stable rather than a race with a cold handler.",
            "Check the receiver's own log or handler code to see which branch produced the observed response.",
            "Record the result as accepted or rejected with both response captures, because this is the baseline every later probe reads against.",
        ],
        "signals": [
            "The endpoint returns 200 for a body that carries no signature header",
            "The handler processes the event and only logs that a signature was absent",
            "A rejection is produced by a downstream validator while the receiver already acted",
            "The first request behaves differently from the second on an unsigned delivery",
        ],
        "patterns": [
            (
                "Baseline pair",
                "POST /hooks/demo  (no signature header) -> 401 missing signature, 9ms\nPOST /hooks/demo  (no signature header) -> 401 missing signature, 8ms  <- stable",
            ),
            (
                "Decision record",
                "accepted | rejected | rejected-after-processing; the third case is a finding because the effect already happened",
            ),
            (
                "Branch note",
                "record which handler branch produced the response: verify middleware, controller check, or downstream worker",
            ),
        ],
        "pitfalls": [
            "Recording a 200 that came from an error page or a gateway rather than from the receiver",
            "Testing against a staging receiver and reporting it as the production behaviour",
            "Sending one request and calling it stable without the confirming repeat",
        ],
        "done_when": [
            "Two unsigned deliveries return recorded status, body and timing with a stable verdict",
            "The handler branch responsible for the verdict is identified",
        ],
        "refs": [
            "[PortSwigger - Authentication vulnerabilities](https://portswigger.net/web-security/authentication)",
            "[OWASP - Broken authentication guidance](https://owasp.org/www-project-top-ten/)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "signature-header-removal-and-blanking",
        "title": "Signature Header Removal and Blanking",
        "summary": "Test each signature-carrying header in three states, because a handler that accepts an empty or whitespace value accepts no verification at all",
        "use_when": "the signature header is known and its behaviour when present but empty has not been observed",
        "avoid_when": "the handler already rejects an empty value and a test confirms it in the current build",
        "tags": ["probe", "headers", "signature"],
        "steps": [
            "For each candidate signature header, prepare three synthetic deliveries: header absent, header empty, header of whitespace only.",
            "Send each one at the agreed rate and capture status, body and timing for every case.",
            "Add a fourth case with an obviously invalid non-empty value to separate an emptiness bug from a general rejection.",
            "Check whether the header name comparison itself is case-insensitive, since some handlers read only one casing.",
            "Record all four outcomes per header in a small table so the reader can see which states pass.",
            "Note whether any accepted case reached downstream processing, which changes the finding from theoretical to consequential.",
        ],
        "signals": [
            "An empty signature value is treated as valid",
            "A whitespace-only value passes while an invalid non-empty value fails",
            "The handler reads only one casing of the header name and misses the other",
            "Acceptance of an empty value is followed by downstream processing of the event",
        ],
        "patterns": [
            (
                "State table",
                "header state | status | downstream reached\nabsent | 401 | no\nempty | 200 | yes  <- finding\nwhitespace | 200 | yes  <- finding\ninvalid value | 401 | no",
            ),
            (
                "Casing check",
                "send the correct value under a differently cased header name; a rejection means the handler is case-sensitive about the name",
            ),
            (
                "Order note",
                "run these before any valid-signature test so the baseline is established while the store is cold",
            ),
        ],
        "pitfalls": [
            "Testing only the absent case, which every handler rejects, and missing the empty-value case entirely",
            "Assuming a gateway strips an empty header without observing the origin's response",
            "Concluding no downstream effect without checking what the handler did after accepting",
        ],
        "done_when": [
            "Four header states per candidate header have recorded status, body and timing",
            "Any accepted case records whether downstream processing occurred",
        ],
        "refs": [
            "[MDN - Request header fields](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers)",
            "[OWASP - Input validation cheat sheet](https://cheatsheetseries.owasp.org/)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "malformed-signature-rejection",
        "title": "Malformed Signature Rejection",
        "summary": "Feed the verifier signatures that are structurally wrong before feeding it wrong-key signatures, since a parser that mishandles malformed input often never reaches the comparison step",
        "use_when": "the signature value format is known and its parser has not been exercised with structurally invalid input",
        "avoid_when": "the handler validates format explicitly and a test confirms malformed values are rejected early",
        "tags": ["probe", "parsing", "signature"],
        "steps": [
            "Build a small set of malformed values: wrong length, invalid alphabet, missing prefix, an extra separator, a truncated pair.",
            "Send each in its own request at the agreed rate and capture status, body and timing for every one.",
            "Watch for cases that return 500 rather than 401, which marks an unhandled parse error on attacker-controlled input.",
            "Note whether any malformed value is silently coerced into something the comparison accepts.",
            "Check whether the error body differs per malformed shape, which tells a caller how the parser is structured.",
            "Record a table of shape, status and whether the request reached the comparison step.",
        ],
        "signals": [
            "A truncated signature value returns 500 with a stack trace in the body",
            "An invalid alphabet character is stripped rather than rejected",
            "Different malformed shapes produce different error messages",
            "The handler logs an exception and continues as though verification succeeded",
        ],
        "patterns": [
            (
                "Shape table",
                "shape | example | status | reached comparison\nwrong length | 10 hex chars | 401 | no\ninvalid alphabet | value with ! | 401 | no\nmissing prefix | bare hex | 401 | no\ntruncated pair | t=,v1= | 500 | no  <- parse error",
            ),
            (
                "Silent-coercion check",
                "if a character is stripped or a length is padded before comparison, the effective search space shrinks; record exactly what the parser normalizes",
            ),
            (
                "Uniform-error rule",
                "the target behaviour is one status and one body for every malformed shape; any variation is what the fix should remove",
            ),
        ],
        "pitfalls": [
            "Sending only wrong-key signatures and never exercising the parser that runs first",
            "Reporting a 500 without recording whether the event was processed anyway",
            "Overstating a timing gap measured over two requests instead of a sample",
        ],
        "done_when": [
            "At least four malformed shapes each have a recorded status and a reached-comparison verdict",
            "Any 500 response records whether processing continued after the error",
        ],
        "refs": [
            "[OWASP - Input validation cheat sheet](https://cheatsheetseries.owasp.org/)",
            "[CWE-20 - Improper input validation](https://cwe.mitre.org/data/definitions/20.html)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "truncated-signature-acceptance",
        "title": "Truncated Signature Acceptance",
        "summary": "Check whether a shortened but correctly formatted signature is accepted, because a comparison that stops early accepts a prefix instead of a whole value",
        "use_when": "the signature is compared with a function that may not enforce full length equality",
        "avoid_when": "the verifier checks decoded length before comparing, and a test confirms a truncated value fails",
        "tags": ["probe", "signature", "comparison"],
        "steps": [
            "Produce a correctly formed signature and then versions truncated to roughly half and three-quarter length, keeping valid alphabet and encoding.",
            "Send each version in its own request and capture status, body and timing.",
            "Confirm that the same value with its full length is accepted, so a failure is attributable to truncation rather than to a bad secret.",
            "Check whether comparison happens in constant time with an explicit length check, from the code path if it is readable.",
            "Record each length tried with the verdict, so a reader can see whether acceptance shrinks with length.",
            "Note any case where a truncated value is accepted, since that reduces the effective secret space materially.",
        ],
        "signals": [
            "A half-length signature is accepted while the full length is also accepted",
            "The verifier compares with a substring or startsWith style operation",
            "No explicit length check appears before the comparison",
            "Acceptance depends only on the first few bytes matching",
        ],
        "patterns": [
            (
                "Length table",
                "length | value shape | status\nfull (64 hex) | correct | 200\nthree-quarter | correct prefix | 401\nhalf | correct prefix | 401\nfull but wrong | incorrect | 401",
            ),
            (
                "Code check",
                "look for an explicit length check before compare; absence of one is worth recording even when the language's comparison is length-aware",
            ),
            (
                "Control case",
                "always send a full-length wrong-key signature alongside, so a truncation failure cannot be confused with a bad secret",
            ),
        ],
        "pitfalls": [
            "Reporting truncation acceptance without the full-length control that proves the secret was right",
            "Truncating to a length that is invalid by encoding, which only re-tests malformed input",
            "Assuming the runtime's comparison is unsafe without reading the actual comparison call",
        ],
        "done_when": [
            "A length table records status for full, three-quarter and half-length signatures plus a wrong-key control",
            "The code path shows an explicit length check or the absence of one is recorded",
        ],
        "refs": [
            "[CWE-187 - Partial string comparison](https://cwe.mitre.org/data/definitions/187.html)",
            "[PortSwigger - Authentication test techniques](https://portswigger.net/web-security/authentication)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "stale-timestamp-rejection",
        "title": "Stale Timestamp Rejection",
        "summary": "Send a signature built over an old timestamp to see whether the tolerance is enforced, since an unenforced window turns every captured delivery into a reusable one",
        "use_when": "the scheme signs a timestamp and the tolerance has been identified but not exercised",
        "avoid_when": "the boundary forbids replaying signed deliveries, in which case this test is recorded as skipped",
        "tags": ["probe", "timestamp", "replay"],
        "steps": [
            "Re-read the boundary: if replaying a signed delivery is forbidden, record this test as skipped with the reason and stop.",
            "Otherwise compute a signature over a timestamp older than the documented tolerance using a synthetic body you own.",
            "Send it once and capture status, body and timing, then repeat to confirm stability.",
            "Send a second value just inside the tolerance and a third just outside it to find the boundary the handler actually enforces.",
            "Compare the enforced boundary with the documented tolerance, since deployments often differ from documentation.",
            "Record three rows: inside, at the boundary and outside, each with its verdict.",
        ],
        "signals": [
            "A timestamp well beyond the documented tolerance is accepted",
            "The enforced boundary differs noticeably from the configured value",
            "Stale deliveries are accepted while future ones are rejected without limit",
            "The tolerance is never checked because the handler only compares the signature",
        ],
        "patterns": [
            (
                "Boundary rows",
                "offset | expected | observed\n-120s (inside 300s) | accept | accept\n-301s (outside) | reject | reject\n-3600s | reject | accept  <- tolerance not enforced",
            ),
            (
                "Skip record",
                "replay of signed deliveries forbidden by boundary -> skipped, reason recorded, no request sent",
            ),
            (
                "Symmetry note",
                "record whether the same bound applies to future timestamps; an asymmetric check leaves a different hole",
            ),
        ],
        "pitfalls": [
            "Running a replay test the boundary explicitly forbids and turning a pass into a scope breach",
            "Testing only one stale offset and never locating the actual enforced boundary",
            "Concluding the tolerance is enforced when a signature over an unsigned timestamp was simply replaced",
        ],
        "done_when": [
            "Inside, boundary and outside offsets each have a recorded verdict, or the test is recorded as skipped with a reason",
            "The enforced boundary is compared against the documented tolerance in the report",
        ],
        "refs": [
            "[Stripe - Timestamp tolerance](https://docs.stripe.com/webhooks/signature)",
            "[CWE-294 - Authentication bypass by capture-replay](https://cwe.mitre.org/data/definitions/294.html)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "future-timestamp-rejection",
        "title": "Future Timestamp Rejection",
        "summary": "Check whether a timestamp far ahead of the receiver's clock is rejected, since an unbounded future window lets a captured delivery be staged for later use",
        "use_when": "the tolerance is applied to stale values and its behaviour on future values has not been observed",
        "avoid_when": "the handler compares against an explicit two-sided window and a test confirms both sides",
        "tags": ["probe", "timestamp", "replay"],
        "steps": [
            "Confirm from the boundary that constructing a signature over a synthetic future-timestamped body is permitted.",
            "Send a delivery signed with a timestamp moderately ahead of now, then one far ahead, at the agreed rate.",
            "Capture status, body and timing for each and note which side of the clock the handler appears to enforce.",
            "Check the code path for a symmetric window or two separate comparisons, since many implementations only bound the past.",
            "Record whether a future value would let an attacker stage a delivery for later consumption.",
            "Write the result as symmetric, past-only or unbounded, with the two offsets you actually tested.",
        ],
        "signals": [
            "A timestamp hours ahead is accepted while a stale one of the same age is rejected",
            "The code subtracts the received time from now with no absolute bound",
            "Future acceptance means a delivery captured today can be replayed later at will",
            "Only one comparison exists where a two-sided window was assumed",
        ],
        "patterns": [
            (
                "Symmetry table",
                "offset | status\n-3600s (past) | 401\n+3600s (future) | 200  <- past-only enforcement\n+86400s | 200",
            ),
            (
                "Code shape",
                "look for abs(now - ts) <= tolerance; two separate comparisons or a single signed subtraction indicates one-sided enforcement",
            ),
            (
                "Impact sentence",
                "state it plainly: a delivery captured at T can be delivered at T + N without detection, with N measured from your test",
            ),
        ],
        "pitfalls": [
            "Assuming symmetry because the documentation describes a window rather than a direction",
            "Reporting the theoretical risk without the offsets you actually observed",
            "Forgetting that an unsigned timestamp makes this test meaningless, since the value can just be rewritten",
        ],
        "done_when": [
            "Past and future offsets are each tested with recorded status and timing",
            "The result is labelled symmetric, past-only or unbounded with the offsets shown",
        ],
        "refs": [
            "[CWE-294 - Authentication bypass by capture-replay](https://cwe.mitre.org/data/definitions/294.html)",
            "[IETF RFC 9110 - Date header semantics](https://www.rfc-editor.org/rfc/rfc9110)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "algorithm-and-version-confusion",
        "title": "Algorithm and Version Confusion",
        "summary": "Examine whether the signature value carries an algorithm or version field the verifier trusts, because a self-declared algorithm is a comparison the caller gets to choose",
        "use_when": "the signature format includes a version, algorithm or key-identifier segment parsed from the value",
        "avoid_when": "the algorithm is fixed in configuration and the value carries no field the handler reads",
        "tags": ["probe", "signature", "algorithm"],
        "steps": [
            "Parse the signature value and list every field the handler reads out of it before comparing.",
            "Determine whether any field influences which algorithm or which key is used for the comparison.",
            "Construct a value declaring an unsupported or weaker algorithm and record whether it is rejected outright.",
            "Try a value with the algorithm segment absent, which is the classic default-branch case.",
            "Check whether the key identifier selects from multiple accepted keys without authenticating the selection.",
            "Record which fields the handler trusts, with a verdict per field: ignored, validated or acted upon.",
        ],
        "signals": [
            "An algorithm field is read from the value and dispatched on without an allow-list",
            "A missing algorithm segment falls through to an unchecked default branch",
            "The key identifier chooses among accepted secrets without being signed itself",
            "A version field is present in the format but never validated by the handler",
        ],
        "patterns": [
            (
                "Field verdicts",
                "field | read | validated | acted upon\nalg | yes | no | yes  <- dispatches\nkid | yes | no | selects key\nv1 | yes | format only | no",
            ),
            (
                "Reject rule",
                "the safe behaviour is an allow-list of algorithms in configuration; anything read from the value and dispatched on is the finding",
            ),
            (
                "Absent-field probe",
                "send a value with the field omitted: a default branch that still compares is where confusion enters",
            ),
        ],
        "pitfalls": [
            "Assuming a field is informational because the provider documents it as such while the handler reads it",
            "Testing only a well-formed value and never the absent or unsupported variant",
            "Reporting a generic algorithm-confusion claim without naming the field the handler dispatches on",
        ],
        "done_when": [
            "Every field parsed from the signature value has a verdict: ignored, validated or acted upon",
            "An unsupported or absent algorithm case has a recorded response",
        ],
        "refs": [
            "[CWE-347 - Improper verification of cryptographic signature](https://cwe.mitre.org/data/definitions/347.html)",
            "[OWASP - Cryptographic failures](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "canonical-mismatch-acceptance",
        "title": "Canonical Mismatch Acceptance",
        "summary": "Deliver a body whose bytes differ from the ones the signature covers, so the report can say whether verification protects content or only a snapshot of it",
        "use_when": "the canonical string is understood and you need to know what happens when delivered bytes differ from signed bytes",
        "avoid_when": "verification demonstrably hashes the exact received buffer and a formatting-variant test already confirms it",
        "tags": ["probe", "canonicalization", "integrity"],
        "steps": [
            "Reconstruct the canonical string from your earlier audit and sign a synthetic body with it.",
            "Send a delivery whose bytes differ from the signed ones while parsing to the same logical content, changing only formatting.",
            "Send a second delivery where the content itself differs, to separate a formatting tolerance from a content bypass.",
            "Capture status, body and timing for each and compare against the control with an identical body.",
            "Check whether the receiver re-serializes the parsed body before hashing, which explains a formatting pass.",
            "Record three rows: identical bytes, different formatting, different content, each with its verdict.",
        ],
        "signals": [
            "Reordered JSON keys or added whitespace still verify successfully",
            "Content that differs from the signed bytes is processed after a pass",
            "The handler hashes a re-serialization of the parsed object rather than the buffer",
            "A control delivery with identical bytes behaves differently from a formatting variant",
        ],
        "patterns": [
            (
                "Three-row table",
                "variant | bytes vs signed | parsed content | status\nidentical | equal | equal | 200\nreformatted | differ | equal | 200  <- re-encode in play\ndifferent content | differ | differ | 401",
            ),
            (
                "Control rule",
                "always include the identical-bytes control; without it a failure could be a bad secret rather than a canonicalization effect",
            ),
            (
                "Re-encode diagnosis",
                "a formatting pass plus a content rejection means the handler verifies a re-serialized form, which is still worth reporting as a brittle scheme",
            ),
        ],
        "pitfalls": [
            "Reporting a content bypass when only a formatting variant was tested",
            "Signing with a reconstructed canonical string that was never validated against a real delivery",
            "Omitting the control row and misattributing the failure",
        ],
        "done_when": [
            "Three variants, identical, reformatted and different content, each have a recorded verdict",
            "The result is attributed to raw bytes or re-serialized form with the evidence shown",
        ],
        "refs": [
            "[RFC 8785 - Canonicalization](https://www.rfc-editor.org/rfc/rfc8785)",
            "[CWE-345 - Insufficient verification of data authenticity](https://cwe.mitre.org/data/definitions/345.html)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "content-encoding-parsing-mismatch",
        "title": "Content-Encoding Parsing Mismatch",
        "summary": "Test deliveries whose transfer encoding differs from what the verifier expects, because bytes that change between receipt and hashing break verification in both directions",
        "use_when": "the receiver accepts compressed or charset-varied bodies and verification runs after any decoding step",
        "avoid_when": "the handler verifies a raw buffer captured before decoding and a compressed test confirms it",
        "tags": ["probe", "encoding", "parsing"],
        "steps": [
            "Confirm the boundary permits sending a delivery with a non-default content encoding to this endpoint.",
            "Send an identical synthetic event twice: once plain, once compressed, with the signature computed over the logical body in both cases.",
            "Capture status, body and timing for each and note whether the difference is in the encoding layer or the signature check.",
            "Add a charset variant if the receiver declares one, since a charset rewrite also changes bytes.",
            "Check where in the code the decoding happens relative to verification.",
            "Record which layers transform bytes before verification and what that means for legitimate senders.",
        ],
        "signals": [
            "A compressed delivery is rejected while the uncompressed equivalent passes",
            "Decoding happens in middleware that runs before the verification code",
            "A declared charset causes re-encoding that invalidates the signature",
            "Legitimate senders would fail if they ever compressed their payloads",
        ],
        "patterns": [
            (
                "Encoding pair",
                "plain body, correct signature -> 200\nsame logical body, gzip, correct signature -> 401  <- decode order matters",
            ),
            (
                "Order record",
                "receive -> decode? -> verify? -> parse?; write the actual order from the code rather than the expected one",
            ),
            (
                "Sender impact",
                "state which legitimate senders would break: any partner that compresses, or any client that sets a charset",
            ),
        ],
        "pitfalls": [
            "Sending a compressed body your own client encoded incorrectly and blaming the endpoint",
            "Reporting an availability defect for senders who cannot exist, such as one the provider never uses",
            "Testing only the default encoding path where no transformation occurs",
        ],
        "done_when": [
            "Plain and transformed deliveries each have a recorded status and timing",
            "The decode-versus-verify order is identified from the code path",
        ],
        "refs": [
            "[MDN - Content-Encoding header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Encoding)",
            "[CWE-436 - Interpretation conflict](https://cwe.mitre.org/data/definitions/436.html)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "signature-over-query-parameters",
        "title": "Signature Over Query Parameters",
        "summary": "Check whether query parameters that influence routing or tenant selection are covered by the signature, since an unsigned parameter redirects a correctly verified delivery",
        "use_when": "the receiver reads tenant, account or mode from the query string on the webhook path",
        "avoid_when": "the canonical string demonstrably includes the full request target and a test confirms it",
        "tags": ["probe", "routing", "signature"],
        "steps": [
            "List every query parameter the receiver reads and mark which of them affect routing or processing.",
            "Send a correctly signed delivery to the canonical path with no query parameters, as the control case.",
            "Send the same signed delivery with one routing parameter added and a second with its value changed.",
            "Capture status, body and timing for each, and note which value the handler acted on.",
            "Check the canonical string from your earlier audit to confirm whether the target path was included at all.",
            "Record each parameter with a covered or uncovered verdict and the observed effect of changing it.",
        ],
        "signals": [
            "A tenant or account parameter lives in the query string while the canonical string covers only the body",
            "Adding a query parameter does not invalidate an otherwise correct signature",
            "Changing a routing parameter redirects processing while verification still passes",
            "The canonical string includes the path but not the query component of the target",
        ],
        "patterns": [
            (
                "Coverage table",
                "parameter | in query | affects routing | signed\nmode | yes | yes | no  <- uncovered\nid | yes | no | no\nn/a | path only | - | yes",
            ),
            (
                "Control-and-variant",
                "control: signed delivery to bare path; variant: same bytes plus ?tenant=other; the difference in behaviour is the entire evidence",
            ),
            (
                "Canonical reminder",
                "the signature covers <timestamp>.<body>; if the target is not in that string, no query parameter can be covered by it",
            ),
        ],
        "pitfalls": [
            "Testing only path parameters when the receiver actually routes on the query string",
            "Reporting an uncovered parameter that has no effect on processing",
            "Forgetting the control case, so a rejection cannot be attributed to the added parameter",
        ],
        "done_when": [
            "Every query parameter the receiver reads has a coverage verdict and an observed effect",
            "A control delivery to the bare path is recorded alongside each variant",
        ],
        "refs": [
            "[RFC 3986 - URI query component](https://www.rfc-editor.org/rfc/rfc3986)",
            "[PortSwigger - Web cache poisoning key confusion](https://portswigger.net/web-security/web-cache-poisoning)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "secret-comparison-timing",
        "title": "Secret Comparison Timing",
        "summary": "Look for a comparison whose duration depends on how many leading bytes match, since a timing signal on a signature comparison is a slow but real path to recovering a secret",
        "use_when": "the verifier compares signatures or secrets with a generic equality operation on attacker-supplied input",
        "avoid_when": "the code uses a constant-time comparison helper and a reading of the call confirms it",
        "tags": ["probe", "timing", "cryptography"],
        "steps": [
            "Read the comparison call and record whether it uses a constant-time helper or a language-level equality operator.",
            "If a live timing test is within scope, gather many samples for a correct prefix and for a wrong first byte at the agreed rate.",
            "Compute a simple distribution for each group rather than relying on a single measurement.",
            "Separate network and scheduling variance by interleaving the two groups rather than running them in blocks.",
            "Record the code observation as the primary evidence, with any timing data as supporting context only.",
            "State the practical reachability honestly: sample count, observed spread and whether it could support a claim.",
        ],
        "signals": [
            "The comparison uses a generic equality operator on attacker-controlled bytes",
            "A correct prefix produces a measurably different distribution from a wrong first byte",
            "The handler compares the secret itself rather than a hash of it",
            "Only a handful of samples were collected before a conclusion was drawn",
        ],
        "patterns": [
            (
                "Code verdict",
                "compare(a, b) using a constant-time helper -> safe by inspection\nequality operator on signature bytes -> record the call site as the finding",
            ),
            (
                "Sampling note",
                "groups: correct-prefix and wrong-first-byte, interleaved, N samples each; record N and the spread so a reader can judge it",
            ),
            (
                "Honest sentence",
                "write what the data supports: a difference was or was not separable at N samples on this network, without claiming more",
            ),
        ],
        "pitfalls": [
            "Reporting a timing vulnerability from two or three measurements on a noisy network",
            "Measuring your own client's latency and calling it endpoint behaviour",
            "Treating a constant-time helper as sufficient when the value is compared before decoding",
        ],
        "done_when": [
            "The comparison call site is recorded with a constant-time or generic verdict",
            "Any timing data states sample count, grouping method and observed spread",
        ],
        "refs": [
            "[CWE-208 - Observable timing discrepancy](https://cwe.mitre.org/data/definitions/208.html)",
            "[PortSwigger - Timing attacks in practice](https://portswigger.net/web-security/authentication)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "duplicate-delivery-idempotency",
        "title": "Duplicate Delivery Idempotency",
        "summary": "Deliver the same signed event twice and observe whether the second is suppressed, because idempotency is the defence that remains when a signature is valid but the event is not new",
        "use_when": "the receiver processes events that carry an identifier and the deduplication behaviour has not been observed",
        "avoid_when": "the handler demonstrably deduplicates on a signed identifier and a test confirms the second delivery is suppressed",
        "tags": ["probe", "idempotency", "replay"],
        "steps": [
            "Confirm from the boundary that sending a duplicate delivery of your own synthetic event is permitted.",
            "Send a correctly signed synthetic event once and record the response and the processing outcome.",
            "Send the identical event again, twice, at the agreed rate, capturing status, body and timing each time.",
            "Check whether the deduplication key comes from the signed body or from an unsigned header or timestamp.",
            "Determine how long the deduplication store retains identifiers, since a short window equals no protection later.",
            "Record the three deliveries with their outcomes and the deduplication key and window you identified.",
        ],
        "signals": [
            "A second identical delivery is processed exactly like the first",
            "The deduplication key is an unsigned header rather than a field inside the signature",
            "The deduplication window is shorter than the sender's own retry schedule",
            "Duplicates are only logged while side effects run again",
        ],
        "patterns": [
            (
                "Delivery triple",
                "1st: 200 processed\nelement: 200 processed  <- no suppression\nelement: 200 processed",
            ),
            (
                "Key question",
                "what identifies a duplicate? record source (signed body, unsigned header, request id) and window length in seconds",
            ),
            (
                "Window compare",
                "dedup window vs sender retry schedule: a window shorter than the retry schedule cannot suppress a retry",
            ),
        ],
        "pitfalls": [
            "Testing duplicates on an endpoint where the boundary forbids replay",
            "Concluding deduplication exists because the second request returned a different status without checking the side effect",
            "Ignoring that a timestamp-keyed dedup window resets whenever the timestamp differs",
        ],
        "done_when": [
            "Three deliveries of one event each have a recorded status and processing outcome",
            "The deduplication key, its source and its window are identified",
        ],
        "refs": [
            "[Stripe - Idempotency in webhooks](https://docs.stripe.com/webhooks#handle-retry-events)",
            "[CWE-294 - Authentication bypass by capture-replay](https://cwe.mitre.org/data/definitions/294.html)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "rejection-response-detail-leakage",
        "title": "Rejection Response Detail Leakage",
        "summary": "Read what a rejected delivery tells the caller, since a response that names the failing check or dumps a stack trace hands an attacker a map of the verifier",
        "use_when": "rejection responses have been captured and it is unclear how much verifier detail they expose",
        "avoid_when": "every rejection returns one fixed status and body with no diagnostic detail",
        "tags": ["probe", "errors", "information-disclosure"],
        "steps": [
            "Collect rejection bodies from several distinct failure cases: missing, malformed, stale and wrong key.",
            "Compare them line by line and record every marker that differs between cases.",
            "Look for stack traces, file paths, library versions, configuration keys or fragments of the secret itself.",
            "Check whether the response includes a request identifier that maps to a detailed server-side log an attacker cannot see.",
            "Distinguish detail visible to an external caller from detail only present in your own logs, since they have different risk.",
            "Write a leakage table with one row per failure case and the markers it exposes.",
        ],
        "signals": [
            "Each failure reason produces a distinct human-readable message",
            "A body contains a stack trace or a filesystem path",
            "The response echoes a fragment of the signature or the expected value",
            "Diagnostic detail intended for operators is returned to the external caller",
        ],
        "patterns": [
            (
                "Leakage table",
                "case | status | body marker | leaks\nmissing | 401 | signature absent | which check exists\nstale | 401 | timestamp expired | tolerance enforcement\nwrong key | 401 | key mismatch | key selection logic",
            ),
            (
                "Uniform target",
                "target behaviour: one status and one body for all verification failures, with a correlation id for operators only",
            ),
            (
                "Severity line",
                "detail in your own logs is fine; the same detail in the external response is the finding, and the report should say which one you observed",
            ),
        ],
        "pitfalls": [
            "Reporting operator-facing log detail as an external leak without checking where it appeared",
            "Comparing bodies from different endpoints and attributing the difference to the verifier",
            "Omitting the correlation id, which is often the acceptable answer rather than a defect",
        ],
        "done_when": [
            "A leakage table records status and markers for at least four distinct failure cases",
            "The report states which detail is externally visible and which stays in server logs",
        ],
        "refs": [
            "[OWASP - Error handling guidance](https://owasp.org/www-project-web-security-testing-guide/)",
            "[CWE-209 - Generation of error message containing sensitive information](https://cwe.mitre.org/data/definitions/209.html)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "content-type-parsing-confusion",
        "title": "Content-Type Parsing Confusion",
        "summary": "Vary the declared content type while keeping bytes identical, because a handler that parses differently per header verifies one representation and acts on another",
        "use_when": "the receiver accepts more than one content type or falls back to a parser when the header is absent",
        "avoid_when": "exactly one content type is accepted and a test confirms others are rejected before parsing",
        "tags": ["probe", "content-type", "parsing"],
        "steps": [
            "Send the identical signed body under each accepted content type and with the header absent entirely.",
            "Capture status, body and timing for each case, plus which parsed structure the handler produced.",
            "Check whether an unexpected content type routes to a different handler with its own verification step.",
            "Note whether any path parses the body before verification, since that reintroduces the decode-order problem.",
            "Confirm which content type the real provider sends, so low-risk cases can be ranked honestly.",
            "Record a table of declared type, status, handler reached and verification treatment.",
        ],
        "signals": [
            "Omitting the content type falls through to a handler that skips verification",
            "Two content types produce different parsed structures from identical bytes",
            "An unexpected type returns 200 while a missing one returns 401",
            "A second parser runs on the same bytes and produces a different field set",
        ],
        "patterns": [
            (
                "Type table",
                "declared type | status | handler | verified\napplication/json | 200 | main | yes\nabsent | 200 | fallback | no  <- finding\nform-encoded | 401 | main | yes\ntext/plain | 500 | unknown | parse error",
            ),
            (
                "Bytes-identical rule",
                "hold the body bytes constant across every case so the only variable is the header the handler reads",
            ),
            (
                "Provider reality check",
                "rank each row by whether the real sender can produce it; a type no provider sends is lower risk, not zero risk",
            ),
        ],
        "pitfalls": [
            "Changing the body along with the header and losing the ability to attribute the difference",
            "Ranking a fallback path as critical when no provider can trigger it, or as harmless when any client can",
            "Missing that a second parser sees different fields from the same bytes",
        ],
        "done_when": [
            "A type table records status, handler and verification for every accepted and absent content type",
            "Each row notes whether a real sender can produce that case",
        ],
        "refs": [
            "[IETF RFC 9110 - Content-Type semantics](https://www.rfc-editor.org/rfc/rfc9110)",
            "[CWE-436 - Interpretation conflict](https://cwe.mitre.org/data/definitions/436.html)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "batch-envelope-partial-signature",
        "title": "Batch Envelope Partial Signature",
        "summary": "Examine whether a batch delivery signs every item it carries or only the envelope, since an unsigned item riding inside a signed array is an unauthenticated event",
        "use_when": "the receiver accepts an array or batch of events under one signature",
        "avoid_when": "each item carries its own signature and the handler verifies each one independently",
        "tags": ["probe", "batch", "integrity"],
        "steps": [
            "Confirm whether the receiver accepts a batch envelope and record the exact shape it parses.",
            "Determine what the signature covers: the whole array, a header field, or only the first item.",
            "Send a batch where one item differs from what the signature covers and observe whether it is rejected or processed.",
            "Send a batch with an extra item appended and note whether the signature still validates.",
            "Check whether items are processed independently, so a single unverified item reaches application logic.",
            "Record coverage as envelope-only, item-level or mixed, with the delivery that demonstrated it.",
        ],
        "signals": [
            "Appending an item to a signed array does not invalidate the signature",
            "Items are processed independently after one envelope-level check",
            "Only the first item's fields appear in the signed bytes",
            "A modified item inside a batch is processed while the envelope signature passes",
        ],
        "patterns": [
            (
                "Coverage verdict",
                "envelope signed over full array -> append test fails signature\nenvelope signed over a header field -> appended item processed unverified\nper-item signature -> each item checked separately",
            ),
            (
                "Append test",
                "add one synthetic item to a correctly signed batch and record status plus how many items were processed",
            ),
            (
                "Process count",
                "the number of items processed is the evidence; record it beside the status code rather than relying on the status alone",
            ),
        ],
        "pitfalls": [
            "Reporting batch risk without confirming the receiver actually accepts a batch shape",
            "Assuming envelope coverage includes items without testing an appended item",
            "Judging by status code when the meaningful evidence is how many items ran",
        ],
        "done_when": [
            "Coverage is labelled envelope-only, item-level or mixed with a demonstrating delivery",
            "An appended-item test records status and the count of items processed",
        ],
        "refs": [
            "[CWE-345 - Insufficient verification of data authenticity](https://cwe.mitre.org/data/definitions/345.html)",
            "[Stripe - Batch and event objects](https://docs.stripe.com/webhooks)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "outbound-target-scheme-validation",
        "title": "Outbound Target Scheme Validation",
        "summary": "When you may exercise outbound targets, check which URL schemes and hosts the application accepts before it makes a request on your behalf",
        "use_when": "the boundary permits outbound target testing and the application stores or accepts destination URLs",
        "avoid_when": "the boundary forbids outbound requests, in which case this test is recorded as skipped with the reason",
        "tags": ["probe", "ssrf", "outbound"],
        "steps": [
            "Re-read the boundary: if outbound requests are forbidden, record this as skipped and do not send anything.",
            "Enumerate the schemes the validator accepts, testing each against a target you own rather than against an internal address.",
            "Check whether the validator resolves a hostname before deciding, since that is where allow-lists are usually bypassed.",
            "Look for redirect-following on a target you control, because a redirect you set is still a request you chose.",
            "Note whether the request carries credentials or fixed headers that would leak to the destination you name.",
            "Record accepted schemes, host handling, redirect behaviour and header leakage, each with the request that proved it.",
        ],
        "signals": [
            "A scheme outside http and https is accepted by the validator",
            "The validator checks a hostname string but never resolves it before the request",
            "A redirect from your owned target is followed to a second destination",
            "Fixed credentials or tokens are attached to a destination you supplied",
        ],
        "patterns": [
            (
                "Scheme table",
                "scheme | accepted | request issued\nhttp | yes | yes\nhttps | yes | yes\nfile | yes | no  <- rejected later, record where\ndata | no | no",
            ),
            (
                "Owned-target rule",
                "every request you issue goes to a host you control; the observation is what the application did, not what an internal host would have returned",
            ),
            (
                "Redirect note",
                "if redirects are followed, record the maximum hop count and whether headers survive the hop",
            ),
        ],
        "pitfalls": [
            "Requesting an internal address to prove a point the boundary never allowed",
            "Failing to notice that your own client followed a redirect the application would not have",
            "Reporting a scheme acceptance without confirming whether a request is ever issued for it",
        ],
        "done_when": [
            "A scheme table records acceptance and whether a request was issued, for each scheme tested",
            "Redirect and header-leakage behaviour are recorded with the owned-target request that showed them",
        ],
        "refs": [
            "[OWASP - SSRF prevention cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)",
            "[CWE-918 - Server-side request forgery](https://cwe.mitre.org/data/definitions/918.html)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "redirect-following-on-outbound-fetch",
        "title": "Redirect Following on Outbound Fetch",
        "summary": "Determine whether an outbound callback follows redirects to a second destination, since a target you are allowed to name can otherwise reach one you are not",
        "use_when": "the application fetches a stored or supplied URL and outbound testing is permitted by the boundary",
        "avoid_when": "the boundary forbids outbound requests or the fetcher explicitly does not follow redirects",
        "tags": ["probe", "ssrf", "redirects"],
        "steps": [
            "Re-read the boundary and record whether outbound requests and redirect-following tests are permitted.",
            "Set up a redirect on a host you own that points to a second host you also own.",
            "Issue one outbound fetch against the first host and record whether a second request arrives at the second host.",
            "Check whether credentials, authorization headers or cookies survive the redirect to the second destination.",
            "Note the maximum redirect depth the client enforces, if any, and whether a loop is detected.",
            "Record the chain with hop count, surviving headers and the destination ultimately reached.",
        ],
        "signals": [
            "A redirect from an allowed host is followed to a destination the validator would have rejected",
            "An authorization header is forwarded across the redirect to a different host",
            "The client has no redirect depth limit and accepts a loop",
            "The validator runs on the first URL only and never re-checks the redirect target",
        ],
        "patterns": [
            (
                "Chain record",
                "hop 1: your host -> 302 -> hop 2: your second host; headers carried: authorization yes, cookie no",
            ),
            (
                "Re-validation question",
                "does the validator run again on the redirect target? no -> the allow-list applies to the first URL only",
            ),
            (
                "Header rule",
                "the safe behaviour is to strip credentials on any cross-host redirect; record whether yours does",
            ),
        ],
        "pitfalls": [
            "Running an outbound test the boundary forbids and reporting it as a pass",
            "Using a client that strips credentials by default and assuming the application's client behaves the same",
            "Reporting a redirect finding without stating whether credentials survived the hop",
        ],
        "done_when": [
            "A redirect chain is recorded with hop count, surviving headers and final destination",
            "Whether re-validation occurs on the redirect target is stated explicitly",
        ],
        "refs": [
            "[OWASP - SSRF prevention cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)",
            "[CWE-601 - Open redirect](https://cwe.mitre.org/data/definitions/601.html)",
        ],
        "meta": {"phase": "probe"},
    },
    {
        "slug": "retry-semantics-and-amplification",
        "title": "Retry Semantics and Amplification",
        "summary": "Establish which responses make a sender retry and how aggressively, because the retry schedule multiplies every rejection your tests produce into partner-visible volume",
        "use_when": "the sending provider's retry behaviour has not been recorded and probes will cause rejections",
        "avoid_when": "the provider documents its retry classes and your tests stay inside a single delivery each",
        "tags": ["probe", "retries", "operations"],
        "steps": [
            "Read the provider's retry documentation and record which status classes trigger a retry and the backoff schedule.",
            "Ask the owner whether the receiver returns a status in a retried class for a verification failure.",
            "Estimate your effective volume: deliveries you send multiplied by the retry count for the status you will produce.",
            "Set a stop condition that fires on repeated deliveries of the same event identifier.",
            "Check whether rejected deliveries are queued for later redelivery, which extends the effect past your session.",
            "Record the retry class, schedule and your measured effective volume beside the plan.",
        ],
        "signals": [
            "A verification failure returns 500, which the sender treats as transient and retries",
            "Retries continue after your session ends because the queue holds the event",
            "The same event identifier arrives several times within seconds of one test",
            "No one on the team knows the sender's backoff schedule",
        ],
        "patterns": [
            (
                "Amplification line",
                "1 delivery x 401 -> no retry; 1 delivery x 500 -> up to N retries over T; choose the status you produce accordingly",
            ),
            (
                "Queue check",
                "record queue depth before and after the probe family; growth that outlives the session must be reported as a side effect you caused",
            ),
            (
                "Stop rule",
                "stop after M deliveries of one event identifier and record M, rather than finishing the planned step count",
            ),
        ],
        "pitfalls": [
            "Choosing a response that triggers retries and unintentionally multiplying your own volume",
            "Measuring volume without knowing the backoff schedule and underestimating it",
            "Leaving queued retries to drain after the assessment ends without telling the owner",
        ],
        "done_when": [
            "The retry class, schedule and estimated effective volume are recorded before the first probe",
            "A stop condition keyed to repeated event identifiers is defined and observed",
        ],
        "refs": [
            "[Stripe - Webhook retry schedule](https://docs.stripe.com/webhooks#handle-retry-events)",
            "[GitHub - Failed webhook delivery retries](https://docs.github.com/en/webhooks/using-webhooks)",
        ],
        "meta": {"phase": "probe"},
    },
]