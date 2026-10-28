"""hookproof skills 1-15: scope and identify phases."""

from __future__ import annotations

SKILLS: list[dict] = [
    {
        "slug": "callback-authorization-boundary",
        "title": "Callback Authorization Boundary",
        "summary": "Write down exactly which endpoints, secrets, providers and payload shapes the webhook assessment may touch before any delivery request leaves the workstation",
        "use_when": "a webhook or callback assessment is about to start and the rules of engagement name no endpoint list, secret set or permitted delivery method",
        "avoid_when": "the program already publishes a machine-readable scope listing endpoints, providers and the permitted test method",
        "tags": ["scope", "authorization", "rules-of-engagement"],
        "steps": [
            "Collect the signed rules of engagement, the provider's testing documentation and any internal endpoint list into one place and note the versions used.",
            "List every in-scope receiver path, sender provider, callback URL class and environment exactly as written, without normalizing or guessing wildcards.",
            "Record the permitted delivery method (sandbox simulator, replay tool, own account), the request-rate ceiling and the explicit ban list in one table.",
            "Confirm whether replaying a previously signed delivery is allowed, since that single permission decides whether the replay tests exist at all.",
            "Write the boundary as a short pre-flight checklist you re-read before the first request of every session, not as a note you recall from memory.",
            "Save the boundary text beside the evidence you collect so a reviewer can prove every recorded delivery fell inside the permitted set.",
        ],
        "signals": [
            "Rules of engagement list endpoints but say nothing about replay or rate",
            "The provider page describes live delivery while the assessment only permits a sandbox",
            "A previous session recorded deliveries against an endpoint you cannot find in writing",
            "Rate limits are described in prose rather than as a number you can enforce",
        ],
        "patterns": [
            (
                "Boundary record",
                "scope:\n  endpoints: [/hooks/stripe, /hooks/github]\n  senders: [stripe, github]\n  methods: [sandbox-simulator, replay-tool]\n  replay_signed: forbidden\n  rate_rps: 1\n  live_delivery: forbidden",
            ),
            (
                "Pre-flight echo",
                "Before session start, restate: endpoints, senders, permitted methods, rate ceiling and the two explicit bans. Any element you cannot quote from the document is a gap to resolve, not a permission to assume.",
            ),
            (
                "Evidence binding",
                "Store boundary.md beside evidence/ so each recorded delivery line can be checked against a document version during review.",
            ),
        ],
        "pitfalls": [
            "Reading a wildcard host as permission for every path the application exposes",
            "Assuming staging and production share scope because they share a provider configuration",
            "Treating an old thread as current authorization after the provider or program changed its rules",
        ],
        "done_when": [
            "A written boundary table names endpoints, senders, methods, rate ceiling and explicit bans",
            "Every later evidence file carries the document version used to justify it",
        ],
        "refs": [
            "[PortSwigger - Webhook security testing](https://portswigger.net/web-security)",
            "[OWASP - Testing for improper access control](https://owasp.org/www-project-web-security-testing-guide/)",
        ],
        "meta": {"phase": "scope"},
    },
    {
        "slug": "webhook-endpoint-inventory",
        "title": "Webhook Endpoint Inventory",
        "summary": "Enumerate every inbound webhook receiver and outbound callback target the application exposes, because an unlisted endpoint is where an unsigned delivery usually lands",
        "use_when": "the application is known to receive or send webhooks and no maintained list of those endpoints exists",
        "avoid_when": "a current inventory already lists each receiver route, sender provider and outbound target with its owner",
        "tags": ["scope", "inventory", "webhooks"],
        "steps": [
            "Walk the routing table and middleware chain to find every path that accepts an external delivery, including ones registered dynamically.",
            "Separate receivers from senders: inbound deliveries you verify, and outbound target URLs you request on someone else's behalf.",
            "Record for each receiver its provider, expected signature header, environment and owning team.",
            "Record for each sender its target URL source (config, database, request field) and whether the target can be changed at runtime.",
            "Note endpoints that exist only in one environment, since a sandbox-only receiver often skips verification entirely.",
            "Mark each entry verified or unconfirmed, and carry every unconfirmed entry into the identify phase as a question.",
        ],
        "signals": [
            "A route accepts deliveries but no one can name the provider that sends to it",
            "A receiver exists in the sandbox only and no one remembers why",
            "An outbound target URL is stored in a field a user or API client can edit",
            "A legacy receiver path still returns 200 to any body",
        ],
        "patterns": [
            (
                "Inventory row",
                "path | direction | provider | signature header | env | owner\n/hooks/stripe | inbound | stripe | stripe-signature | prod | payments\n/hooks/legacy | inbound | unknown | none observed | prod | unowned\n/api/notify | outbound | self | n/a | prod | integrations",
            ),
            (
                "Direction split",
                "inbound -> you must verify a signature; outbound -> you must constrain the target. Writing the direction beside each row decides which half of the pack applies.",
            ),
            (
                "Unconfirmed rule",
                "any row with owner unknown or provider unknown is carried into identify as an open question rather than dropped from the list",
            ),
        ],
        "pitfalls": [
            "Inventorying only inbound receivers and missing the outbound targets that make requests for you",
            "Finding routes by URL pattern alone while another set is registered through a framework hook",
            "Assuming an unowned legacy receiver is harmless because no one sends to it today",
        ],
        "done_when": [
            "Every receiver and outbound target appears as a row with provider, header, environment and owner",
            "Unconfirmed rows are listed explicitly and assigned to an identify question",
        ],
        "refs": [
            "[OWASP - Server-side request forgery](https://owasp.org/SSRF_Sheet/)",
            "[MDN - HTTP request handling](https://developer.mozilla.org/en-US/docs/Web/HTTP)",
        ],
        "meta": {"phase": "scope"},
    },
    {
        "slug": "secret-inventory-and-ownership",
        "title": "Secret Inventory and Ownership",
        "summary": "Establish which signing secrets exist, where each one lives and who may rotate it, so a rotation test never breaks a partner you did not intend to touch",
        "use_when": "several providers sign deliveries into the application and no single list states secret location, owner and rotation rights",
        "avoid_when": "one provider signs with one secret held in a managed secret store with a documented rotation owner",
        "tags": ["scope", "secrets", "rotation"],
        "steps": [
            "List one row per provider and environment: secret identifier, storage location, retrieval code path and the role allowed to rotate it.",
            "Confirm whether older secrets are still accepted, since overlapping acceptance is what makes a safe rotation possible.",
            "Check whether the secret is reachable from logs, error messages, debug endpoints or client-visible configuration.",
            "Note whether the sandbox uses a different secret from production, so a test never crosses the two.",
            "Record the partner notification path for a rotation, including who contacts whom and how long the overlap must last.",
            "Carry the inventory into the probe phase as the set of secrets you are and are not permitted to exercise.",
        ],
        "signals": [
            "Two environments share one secret with no documented reason",
            "A signing secret appears in a log line or a debug response",
            "No one can name the role allowed to rotate a secret",
            "Rotation would have an immediate effect because no overlap window exists",
        ],
        "patterns": [
            (
                "Secret row",
                "provider | env | location | retrieval path | rotator role | overlap\nstripe | prod | secret manager | settings.stripe_signing | payments-oncall | 24h\nstripe | sandbox | env var | settings.stripe_signing | payments-oncall | n/a",
            ),
            (
                "Acceptance check",
                "does the verifier accept more than one secret per provider? yes -> rotation is safe; no -> any rotation is an outage, record it before testing",
            ),
            (
                "Leak sweep",
                "search logs, error bodies and config responses for the secret prefix you know exists; a hit is a finding independent of the webhook tests",
            ),
        ],
        "pitfalls": [
            "Rotating a secret during an assessment and breaking a live partner integration",
            "Testing the production secret against a sandbox receiver or the reverse",
            "Finding a secret in a log and continuing with the rest of the plan without escalating it",
        ],
        "done_when": [
            "Every provider and environment has a secret row with location, rotator and overlap status",
            "A leak sweep of logs, errors and config responses is recorded as pass or finding",
        ],
        "refs": [
            "[OWASP - Secrets management guidance](https://owasp.org/www-project-secretshub/)",
            "[NIST SP 800-57 - Key management recommendations](https://csrc.nist.gov/pubs/sp/800/57/r5/final)",
        ],
        "meta": {"phase": "scope"},
    },
    {
        "slug": "outbound-target-scope-classification",
        "title": "Outbound Target Scope Classification",
        "summary": "Decide whether you may exercise the application's outbound callback targets at all, because a target URL you control is a server-side request primitive the rules must cover explicitly",
        "use_when": "the application makes requests to URLs it stores or receives, and the rules of engagement are silent on outbound testing",
        "avoid_when": "the program states plainly that outbound target requests are out of scope and only inbound delivery verification may be tested",
        "tags": ["scope", "ssrf", "outbound"],
        "steps": [
            "Search the rules of engagement for outbound, callback, redirect, target and URL, and quote the surrounding sentences verbatim in your notes.",
            "Ask a direct yes-or-no question about outbound target requests when the document is silent, and wait for the answer before proceeding.",
            "If outbound testing is out of scope, restrict yourself to reading how the target is stored and validated, without issuing the request.",
            "When permitted, plan a request to a target you own that returns an observable difference, with a rate ceiling and a stop condition.",
            "Record which findings depend on outbound access, so a reader can separate a target-validation defect from an inbound signature defect.",
            "Re-confirm the decision at any change of engagement, since a scope update often reverses this item without changing endpoint lists.",
        ],
        "signals": [
            "Rules list receiver endpoints but never mention outbound target requests",
            "A target URL field is editable through an API the program exposes",
            "The application follows redirects when fetching a stored target",
            "No written answer exists to a direct outbound-request question",
        ],
        "patterns": [
            (
                "Decision record",
                "outbound_target: unknown | permitted | forbidden\nsource: <document section or program reply>\ndate: <ISO date>\nconsequence: read validation only | one request to owned target allowed",
            ),
            (
                "Passive fallback",
                "if outbound contact is forbidden, describe the validation you observed in code or configuration and mark the claim as untested rather than as a finding",
            ),
            (
                "Owned-target rule",
                "when permitted, the only target you request is one you control; a response difference from that target is the entire evidence, nothing more",
            ),
        ],
        "pitfalls": [
            "Requesting an internal address because a target field accepted it, when outbound testing was never cleared",
            "Reporting an untested outbound claim as though a request had been made",
            "Forgetting that redirect-following turns your owned target into a chain you did not choose",
        ],
        "done_when": [
            "Outbound target testing is recorded as permitted or forbidden with a quoted source",
            "Every later finding carries an inbound-observed or outbound-observed label",
        ],
        "refs": [
            "[OWASP - SSRF prevention cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)",
            "[PortSwigger - SSRF](https://portswigger.net/web-security/ssrf)",
        ],
        "meta": {"phase": "scope"},
    },
    {
        "slug": "synthetic-event-only-policy",
        "title": "Synthetic Event Only Policy",
        "summary": "Keep every delivery you send and every payload you store synthetic, so a webhook assessment never moves real customer data through a test harness",
        "use_when": "testing requires constructing deliveries or replaying bodies and real events are present in the environment",
        "avoid_when": "the whole test surface already runs on fixture data that no customer record can reach",
        "tags": ["scope", "data-handling", "privacy"],
        "steps": [
            "Identify which data classes the receiver handles: payment, identity, message or internal-only, since each raises the cost of a leak.",
            "Construct synthetic events with invented identifiers and amounts that cannot collide with a real record.",
            "If a real delivery must be examined, record only its headers and a hash of its body, never the body itself.",
            "Store test deliveries in a directory that is excluded from version control and delete them once the report is filed.",
            "Mark any step that would require a real customer record as skipped, with the reason, so the gap is visible in the report.",
            "Confirm before starting that the environment you are pointed at is not receiving live customer traffic.",
        ],
        "signals": [
            "The endpoint you are about to test is the production receiver rather than a sandbox",
            "A captured delivery body contains a real email address, card fragment or account id",
            "A test payload was copied from a support ticket rather than constructed",
            "Test deliveries are being written into a tracked directory",
        ],
        "patterns": [
            (
                "Synthetic marker",
                "id: test_evt_0001, email: tester@example.test, amount: 100, note: synthetic fixture for authorized assessment",
            ),
            (
                "Redaction rule",
                "real delivery -> headers verbatim + sha256 of body only; if no non-sensitive region exists, record the header evidence alone",
            ),
            (
                "Skip note",
                "when a step is skipped for data reasons, write one line naming the step and the reason so the gap appears in the report",
            ),
        ],
        "pitfalls": [
            "Copying a live event into a test fixture and committing someone else's data to a repository",
            "Running synthetic tests against the production receiver where they will be processed as real",
            "Retaining captured deliveries after the report is filed because they were never cleaned up",
        ],
        "done_when": [
            "Every payload used in the assessment carries an explicit synthetic marker",
            "No stored artifact contains a real customer identifier, and skipped steps are listed with reasons",
        ],
        "refs": [
            "[OWASP - Sensitive data protection](https://owasp.org/www-project-top-ten/)",
            "[NIST SP 800-53 - PII handling controls](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)",
        ],
        "meta": {"phase": "scope"},
    },
    {
        "slug": "delivery-volume-and-rate-budget",
        "title": "Delivery Volume and Rate Budget",
        "summary": "Agree a numeric delivery budget before testing, so a retry storm caused by a rejection behaviour never becomes an incident for you or the sending partner",
        "use_when": "the assessment will send or trigger deliveries and no numeric ceiling has been agreed with the owner",
        "avoid_when": "the rules of engagement already state a per-minute ceiling and a maximum total delivery count",
        "tags": ["scope", "rate-limit", "operations"],
        "steps": [
            "Record a numeric ceiling: deliveries per minute, total deliveries for the session and the pause used between probe families.",
            "Ask whether the sender retries rejected deliveries and how aggressively, because that multiplies your effective volume.",
            "Set a stop condition tied to observed behaviour, such as five consecutive retries, rather than to a fixed plan step count.",
            "Check what your own receiver logs and queues will hold, since a test that fills a queue creates work for someone else.",
            "Re-read the ceiling before starting a new probe family, not only once at the start of the session.",
            "Log your actual delivery count beside the plan so the owner can see the session stayed inside the budget.",
        ],
        "signals": [
            "The sender retries on 4xx as well as 5xx and nobody knows the backoff schedule",
            "Your test queue is growing while the plan still has steps remaining",
            "The ceiling exists in prose with no number attached to it",
            "A single rejected delivery produced several more deliveries within seconds",
        ],
        "patterns": [
            (
                "Budget record",
                "per_minute: 3\nsession_total: 40\npause_between_families: 10s\nstop_condition: 5 consecutive sender retries\nactual_this_session: 17",
            ),
            (
                "Multiplier check",
                "one request x sender retries N times = actual volume; write N next to the ceiling before the first request",
            ),
            (
                "Queue note",
                "record queue depth before and after each probe family; growth that outlives the test is a side effect you caused and must report",
            ),
        ],
        "pitfalls": [
            "Sending a delivery that the sender retries aggressively and unintentionally amplifying your own volume",
            "Setting a ceiling without knowing the retry schedule, so the real volume is a multiple of what you planned",
            "Filling a shared queue and leaving someone else to drain it after you finish",
        ],
        "done_when": [
            "A numeric ceiling, multiplier and stop condition are written down before the first delivery",
            "The session's actual delivery count is recorded beside the plan and stayed inside the budget",
        ],
        "refs": [
            "[PortSwigger - Burp Suite rate limiting guidance](https://portswigger.net/burp/documentation/desktop)",
            "[NIST - Availability control considerations](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)",
        ],
        "meta": {"phase": "scope"},
    },
    {
        "slug": "provider-terms-and-testing-mode",
        "title": "Provider Terms and Testing Mode",
        "summary": "Confirm which testing facility the sending provider intends you to use, so verification work happens in a simulator or sandbox instead of against a live partner account",
        "use_when": "a third-party provider signs deliveries into the application and its testing method has not been confirmed",
        "avoid_when": "the provider documents a sandbox or CLI simulator and the assessment already uses it exclusively",
        "tags": ["scope", "provider", "sandbox"],
        "steps": [
            "Read the provider's testing documentation and record the supported method: CLI simulator, dashboard trigger, sandbox account or test event.",
            "Confirm whether that method reproduces the real signature scheme, since a simulator that omits signing tests nothing that matters.",
            "Record whether the sandbox uses separate credentials and endpoints from production, and which one your endpoint currently points at.",
            "Check whether the provider's testing method respects your rate budget, and note any method that could trigger live deliveries.",
            "Decide the single method you will use for the session and write it into the boundary document.",
            "Note any provider capability the assessment cannot use, such as replay of a signed event, and record the resulting coverage gap.",
        ],
        "signals": [
            "The only documented way to trigger a delivery sends it to a live customer flow",
            "The simulator does not produce a signature header at all",
            "Sandbox and production share a receiver path with no distinguishing marker",
            "No documented method exists for replaying a previously signed event",
        ],
        "patterns": [
            (
                "Method record",
                "provider: stripe | method: CLI trigger | signature produced: yes | sandbox separate: yes | rate safe: yes",
            ),
            (
                "Gap note",
                "provider X has no replay capability -> replay tests marked untestable with this reason rather than reported as passing",
            ),
            (
                "Environment marker",
                "request the receiver with the provider's own test flag and confirm the handler treats it as sandbox before any signature test runs",
            ),
        ],
        "pitfalls": [
            "Triggering a live delivery through a provider tool intended for demos",
            "Accepting a simulator as proof of verification when it never attaches a signature",
            "Recording a passing replay test that was never actually executed because no facility exists",
        ],
        "done_when": [
            "One provider testing method is chosen, documented and written into the boundary",
            "Untestable capabilities are listed as coverage gaps with the reason",
        ],
        "refs": [
            "[Stripe - Webhook testing documentation](https://docs.stripe.com/webhooks/test)",
            "[GitHub - Webhook deliveries and testing](https://docs.github.com/en/webhooks/using-webhooks/creating-webhooks)",
        ],
        "meta": {"phase": "scope"},
    },
    {
        "slug": "signature-scheme-identification",
        "title": "Signature Scheme Identification",
        "summary": "Determine how the sender signs a delivery and which header carries the result, because every later test depends on knowing exactly what the verifier is supposed to check",
        "use_when": "an inbound endpoint receives deliveries and the signing scheme or signature header has not been confirmed from a real delivery",
        "avoid_when": "the provider documents the scheme and a captured delivery confirms the header and format match",
        "tags": ["identify", "signature", "scheme"],
        "steps": [
            "Capture one delivery from the provider's own testing facility and record the complete header set verbatim, without altering the body.",
            "Identify the header carrying the signature and its format: bare hex, base64, a prefixed value, or a list of attributes.",
            "Read the provider documentation for what bytes are signed: body only, timestamp plus body, method and path plus body, or a subset of fields.",
            "Determine whether the scheme is symmetric (shared secret) or asymmetric (provider key pair), since the failure modes differ completely.",
            "Note whether the signature is versioned or carries an algorithm field, because versioned schemes change what the canonical string contains.",
            "Write a one-paragraph scheme statement naming header, format, signed bytes and key type, and keep it beside the evidence.",
        ],
        "signals": [
            "The signature header name is not mentioned anywhere in the receiver code",
            "A captured delivery carries several candidate headers and only one is checked",
            "The signed byte set described in documentation differs from what the handler computes",
            "The signature value carries a version or algorithm segment the handler ignores",
        ],
        "patterns": [
            (
                "Scheme statement",
                "header: stripe-signature\nformat: t=<timestamp>,v1=<hex hmac>\nsigned bytes: <timestamp>.<raw body>\nkey: shared secret (symmetric)",
            ),
            (
                "Header candidates",
                "common names: stripe-signature, x-hub-signature-256, x-signature, x-webhook-signature, authorization bearer when no dedicated header exists",
            ),
            (
                "Signed-byte question",
                "ask three things: does it include the timestamp, does it include method and path, does it cover the raw bytes or a re-encoded form of them",
            ),
        ],
        "pitfalls": [
            "Reading a scheme from a blog post instead of from a delivery your own environment received",
            "Assuming the body alone is signed when the timestamp is part of the signed string",
            "Ignoring an algorithm or version field, which is exactly where scheme confusion lives",
        ],
        "done_when": [
            "A scheme statement names the header, value format, signed bytes and key type",
            "The statement is backed by a captured delivery from the provider's own testing facility",
        ],
        "refs": [
            "[Stripe - Signature verification](https://docs.stripe.com/webhooks/signature)",
            "[GitHub - Validating webhook deliveries](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)",
        ],
        "meta": {"phase": "identify"},
    },
    {
        "slug": "canonical-string-construction-audit",
        "title": "Canonical String Construction Audit",
        "summary": "Reconstruct precisely which bytes the verifier hashes, including separators and ordering, so a signature mismatch is explained by the canonical form rather than by guesswork",
        "use_when": "the scheme statement names signed bytes but the exact concatenation, separators and field order are unconfirmed",
        "avoid_when": "the provider specifies an explicit canonical form and your reconstruction reproduces a valid signature from a captured delivery",
        "tags": ["identify", "canonicalization", "signature"],
        "steps": [
            "Write the canonical string as a template with named placeholders for every element the scheme includes.",
            "List the separators explicitly, including whether an empty element contributes an empty field rather than disappearing.",
            "Reproduce one captured signature yourself using the known secret and compare byte for byte with the header value.",
            "If reproduction fails, vary one element at a time: separator, order, encoding of the body, presence of the timestamp.",
            "Record the encoding used for each element, such as lowercase hex versus base64, because a mismatch here looks like a bad secret.",
            "Store the working template as the reference against which later canonicalization tests are compared.",
        ],
        "signals": [
            "Your reconstruction of a valid signature does not match the header value",
            "An empty or optional element disappears from the string rather than leaving an empty field",
            "The handler joins fields in a different order from the one the provider documents",
            "The body is hashed after re-encoding rather than as the raw received bytes",
        ],
        "patterns": [
            (
                "Template",
                "canonical = timestamp + \".\" + raw_body_bytes\nempty element -> contributes \"\" between separators, it does not vanish\nencode -> lowercase hex for HMAC-SHA256 output",
            ),
            (
                "Reproduction check",
                "recompute from a captured delivery with the known secret; a byte match proves you understand the scheme, a mismatch means one element is wrong",
            ),
            (
                "One-at-a-time rule",
                "when reproduction fails, change exactly one thing per attempt and record which change produced the match",
            ),
        ],
        "pitfalls": [
            "Concluding the secret is wrong when the real defect is an ordering or encoding difference",
            "Ignoring optional fields that the provider includes only when present",
            "Trusting a re-encoded body when the scheme signs the raw bytes you received",
        ],
        "done_when": [
            "A canonical template with named placeholders and explicit separators is written down",
            "At least one captured signature is reproduced byte for byte from the known secret",
        ],
        "refs": [
            "[RFC 8785 - Canonical JSON](https://www.rfc-editor.org/rfc/rfc8785)",
            "[Stripe - Computing a signature](https://docs.stripe.com/webhooks/signature)",
        ],
        "meta": {"phase": "identify"},
    },
    {
        "slug": "signature-header-vocabulary-mapping",
        "title": "Signature Header Vocabulary Mapping",
        "summary": "Map every header a delivery can carry and classify which are provider-set, which are client-controlled, and which the handler actually reads",
        "use_when": "a delivery arrives with several candidate headers and it is unclear which of them the receiver trusts",
        "avoid_when": "the receiver reads exactly one documented header and all others are stripped at the edge",
        "tags": ["identify", "headers", "trust"],
        "steps": [
            "Capture the full header list from a provider-generated delivery and label each header with its likely producer.",
            "Re-send a synthetic delivery with one candidate header added or altered to see whether the handler's decision changes.",
            "Separate headers the sender sets from headers a client can set on any request reaching your edge.",
            "Note headers that duplicate the signature information in a weaker form, such as an unsigned summary of the payload.",
            "Record which header the handler reads for its verification decision, and which headers it merely logs or passes downstream.",
            "Write a mapping table so later tests know which header they are manipulating and which one carries the verdict.",
        ],
        "signals": [
            "Two headers both claim to carry a signature and only one is verified",
            "A header that identifies the sender is copied from a value any client can supply",
            "The handler reads a header the edge never strips from external traffic",
            "A downstream worker trusts a header the receiver set after verification",
        ],
        "patterns": [
            (
                "Header map",
                "header | producer | read for verdict | stripped at edge\nstripe-signature | provider | yes | no\nx-forwarded-for | client | no | no\nx-internal-user | receiver | downstream only | no",
            ),
            (
                "Mutate test",
                "add one candidate header to a synthetic delivery and observe whether the accept or reject decision changes; that header carries authority",
            ),
            (
                "Boundary note",
                "which headers arrive already stripped by the gateway? record them, because a header stripped upstream can never be the defect you are hunting",
            ),
        ],
        "pitfalls": [
            "Assuming a header named signature is the one the handler actually checks",
            "Mutating two headers in one delivery and losing the attribution for the changed decision",
            "Forgetting that a header set by your own edge can be spoofed by a client that reaches the origin directly",
        ],
        "done_when": [
            "A header map lists producer, verdict authority and edge treatment for every candidate",
            "A mutate test confirms which header actually drives the accept or reject decision",
        ],
        "refs": [
            "[MDN - HTTP headers overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers)",
            "[OWASP - Input validation cheat sheet](https://cheatsheetseries.owasp.org/)",
        ],
        "meta": {"phase": "identify"},
    },
    {
        "slug": "timestamp-and-tolerance-format-audit",
        "title": "Timestamp and Tolerance Format Audit",
        "summary": "Establish how the timestamp is encoded and how wide the acceptance window is, since the replay window is defined entirely by those two facts",
        "use_when": "the signed string includes a timestamp and the tolerance the verifier enforces has not been confirmed",
        "avoid_when": "the scheme carries no timestamp and replay defence rests on something other than a time window",
        "tags": ["identify", "timestamp", "replay"],
        "steps": [
            "Capture the timestamp element from a real delivery and record its unit: seconds, milliseconds or a formatted date string.",
            "Locate the tolerance value in configuration or code and record it in seconds, noting whether it is configurable per environment.",
            "Check which clock the verifier compares against, because a receiver with drifting clock rejects valid deliveries silently.",
            "Determine whether the timestamp is inside the signed string, because an unsigned timestamp can simply be replaced.",
            "Note whether the window is applied symmetrically (past and future) or only to stale values.",
            "Write both numbers next to each other: the encoded unit and the tolerance, plus the maximum replay window they imply.",
        ],
        "signals": [
            "The tolerance lives in a constant nobody has reviewed since the integration shipped",
            "The timestamp sits outside the signed bytes and can be rewritten independently",
            "Seconds and milliseconds are mixed between the sender and the receiver",
            "Future timestamps are accepted without limit while only stale ones are rejected",
        ],
        "patterns": [
            (
                "Window record",
                "unit: unix seconds | tolerance: 300s | signed: yes | clock: receiver system clock | symmetric: past only\n-> replay window = 300s",
            ),
            (
                "Unit check",
                "1778900000 is seconds; 1778900000000 is milliseconds; if one side treats the other as its own unit the window becomes effectively infinite",
            ),
            (
                "Signed-or-not",
                "timestamp outside the signature -> replaceable; record that as a scheme weakness separate from the tolerance value",
            ),
        ],
        "pitfalls": [
            "Assuming the documented default is the deployed value without reading the configuration",
            "Testing replay against a receiver whose clock differs from the sender's, which distorts every result",
            "Ignoring that an unsigned timestamp reduces the replay defence to a value the sender's opponent controls",
        ],
        "done_when": [
            "The timestamp unit, tolerance value, signing status and clock source are all recorded",
            "The resulting maximum replay window is stated as a number in seconds",
        ],
        "refs": [
            "[Stripe - Tolerance and replay](https://docs.stripe.com/webhooks/signature)",
            "[IETF RFC 9110 - Date and time semantics](https://www.rfc-editor.org/rfc/rfc9110)",
        ],
        "meta": {"phase": "identify"},
    },
    {
        "slug": "raw-body-versus-decoded-body",
        "title": "Raw Body Versus Decoded Body",
        "summary": "Determine whether the signature is verified over the exact bytes received or over a re-encoded parse of them, because the difference decides whether legitimate deliveries fail and which bypasses exist",
        "use_when": "the receiver parses a body before verifying it, or a framework middleware decodes content before your handler runs",
        "avoid_when": "verification demonstrably runs on a buffer captured before any parsing or decoding step",
        "tags": ["identify", "parsing", "signature"],
        "steps": [
            "Read the receiver path and identify the exact point where the body is first parsed or decoded relative to verification.",
            "Capture the raw bytes of a delivery and the parsed object the handler sees, and compare their serializations.",
            "Check how the framework handles content encoding and charset, since either can change bytes between receipt and verification.",
            "Send a delivery whose JSON formatting differs but whose parsed content is identical, and observe whether verification still passes.",
            "Note whether re-serializing the parsed body can produce different bytes from the original, which is the classic failure mode.",
            "Record the verification point as raw-buffer or re-encoded, with the code location that proves it.",
        ],
        "signals": [
            "Verification reads a parsed object rather than a request buffer",
            "A delivery with reordered JSON keys fails signature verification",
            "A compressed delivery is rejected while an uncompressed one with the same content passes",
            "The handler parses the body in middleware before the verification code runs",
        ],
        "patterns": [
            (
                "Order record",
                "receive -> buffer raw bytes -> verify signature over buffer -> parse -> handle\nany other order is a finding to explain, not an assumption to make",
            ),
            (
                "Re-encode probe",
                "same logical content, different whitespace or key order: pass means raw bytes are used, fail means a re-encoded form is being verified",
            ),
            (
                "Encoding note",
                "record content-encoding and charset handling; if either is applied before verification, the signed bytes and the hashed bytes differ",
            ),
        ],
        "pitfalls": [
            "Concluding verification is broken when a framework's default body parser simply ran first",
            "Testing only well-formed UTF-8 bodies and missing the encoding path entirely",
            "Reporting a false failure because your own client re-encoded the body before sending",
        ],
        "done_when": [
            "The verification point is identified with a code location and labelled raw-buffer or re-encoded",
            "A formatting-variant delivery demonstrates which behaviour actually occurs",
        ],
        "refs": [
            "[PortSwigger - HTTP request smuggling basics](https://portswigger.net/web-security/request-smuggling)",
            "[MDN - Content-Encoding header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Encoding)",
        ],
        "meta": {"phase": "identify"},
    },
    {
        "slug": "delivery-envelope-taxonomy",
        "title": "Delivery Envelope Taxonomy",
        "summary": "Classify the shapes a delivery can take: single JSON, form-encoded, multipart or batch array, because each shape changes what the signature must cover",
        "use_when": "the receiver accepts more than one content type or a provider batches several events into one request",
        "avoid_when": "exactly one content type is accepted and verification covers the entire body",
        "tags": ["identify", "content-type", "parsing"],
        "steps": [
            "List every content type the receiver accepts, including defaults it falls back to when the header is absent.",
            "For each type, record how the body reaches application code: parsed object, raw string, file upload or key-value pairs.",
            "Identify whether a batch envelope carries multiple events under one signature or one signature per item.",
            "Check whether an absent or unusual content type triggers a different code path with weaker verification.",
            "Record which envelope shapes the provider actually sends today, so untested shapes are visible as gaps.",
            "Write a taxonomy table with one row per accepted content type and the verification treatment it receives.",
        ],
        "signals": [
            "The receiver accepts both JSON and form-encoded bodies on the same path",
            "A batch endpoint signs the array header but not the individual items inside it",
            "An unexpected content type falls through to a handler that skips verification",
            "Multipart parsing produces fields the signature never covered",
        ],
        "patterns": [
            (
                "Taxonomy row",
                "content-type | accepted | reaches code as | signed coverage\napplication/json | yes | parsed dict | whole raw body\napplication/x-www-form-urlencoded | yes | parsed dict | whole raw body\nmultipart/form-data | unknown | - | not tested",
            ),
            (
                "Batch rule",
                "one signature over an array -> record whether item-level fields are covered; an unsigned item inside a signed array is a finding",
            ),
            (
                "Fallback note",
                "what happens with no content-type at all? record the status and which handler ran",
            ),
        ],
        "pitfalls": [
            "Testing only the default JSON path when the receiver also answers to a second content type",
            "Assuming a batch signature covers each item without checking what bytes it hashes",
            "Missing the fallback handler that runs when a header is absent or malformed",
        ],
        "done_when": [
            "A taxonomy table lists every accepted content type with its verification treatment",
            "Batch behaviour records whether signature coverage is array-level or item-level",
        ],
        "refs": [
            "[IETF RFC 7578 - Multipart form data](https://www.rfc-editor.org/rfc/rfc7578)",
            "[MDN - Content-Type header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Type)",
        ],
        "meta": {"phase": "identify"},
    },
    {
        "slug": "delivery-metadata-header-trust",
        "title": "Delivery Metadata Header Trust",
        "summary": "Establish which delivery metadata the handler treats as authoritative, since a client-controlled event identifier or tenant claim redirects the effect of an otherwise valid delivery",
        "use_when": "the receiver derives account, tenant or event identity from headers or top-level fields rather than from the signed body",
        "avoid_when": "all routing decisions are made from fields the signature demonstrably covers",
        "tags": ["identify", "routing", "trust"],
        "steps": [
            "Trace where the receiver obtains tenant, account and event identifiers, and mark each source as signed or unsigned.",
            "Send a synthetic delivery where an unsigned metadata value differs from the signed one, and observe which the handler uses.",
            "Check whether the handler trusts a header that any client can set when reaching the origin directly.",
            "Note whether downstream workers read metadata the receiver wrote after verification, since that boundary can be crossed.",
            "Record which values are derived from verified content and which are taken at face value.",
            "Write a trust table: value, source, signed coverage, who consumes it.",
        ],
        "signals": [
            "The tenant used for processing comes from a header rather than from the signed body",
            "An event identifier used for deduplication is never part of the signature",
            "A worker trusts a field the receiver populated after verification finished",
            "A client-supplied header reaches the handler when the request bypasses the gateway",
        ],
        "patterns": [
            (
                "Trust table",
                "value | source | signed | consumer\ntenant_id | body field | yes | handler\nevent_id | header | no | dedup store\ntarget_url | request field | no | outbound sender",
            ),
            (
                "Split probe",
                "same signed body, different unsigned metadata: whichever value the handler acts on is the one it trusts",
            ),
            (
                "Boundary note",
                "record the point where the receiver writes metadata for downstream use, because anything added after verification carries no signature",
            ),
        ],
        "pitfalls": [
            "Verifying a signature correctly and then routing the event on an unsigned identifier",
            "Assuming a header was stripped at the edge without checking the direct-to-origin path",
            "Missing that a downstream worker re-reads metadata the verification step never saw",
        ],
        "done_when": [
            "A trust table marks each routing value as signed or unsigned with its consumer",
            "A split probe confirms which source the handler actually acts on",
        ],
        "refs": [
            "[OWASP - Mass assignment and untrusted input](https://owasp.org/www-project-web-security-testing-guide/)",
            "[PortSwigger - HTTP request header injection](https://portswigger.net/web-security/request-smuggling)",
        ],
        "meta": {"phase": "identify"},
    },
    {
        "slug": "rejection-and-error-shape-mapping",
        "title": "Rejection and Error Shape Mapping",
        "summary": "Record how the endpoint reports a failed verification in status, body and timing, since those differences both leak verification state and determine how a provider retries",
        "use_when": "the endpoint's behaviour on a rejected delivery has not been observed and later probes depend on reading that response",
        "avoid_when": "the receiver returns one fixed response for every rejection and the provider's retry policy is documented",
        "tags": ["identify", "errors", "responses"],
        "steps": [
            "Capture the response for a delivery with no signature at all, including status, body and the time taken.",
            "Capture the same for a malformed signature and for a well-formed signature with the wrong key.",
            "Compare the three: an endpoint that distinguishes them tells an attacker how close they are to a valid value.",
            "Check whether the response body names the failing check, which decides what a sending partner sees in their dashboard.",
            "Note which statuses the provider treats as retryable, since a 500 on a bad signature creates a retry storm.",
            "Record the response map beside the boundary so later probes can be read against it without re-deriving the baseline.",
        ],
        "signals": [
            "The body says signature expired for one case and signature missing for another",
            "A bad signature returns 500, which the provider interprets as a transient failure worth retrying",
            "Rejection timing is visibly different from acceptance timing",
            "The error body includes a stack trace or a fragment of the secret comparison",
        ],
        "patterns": [
            (
                "Response map",
                "case | status | body marker | median ms\nno signature | 401 | missing signature | 9\nmalformed | 401 | malformed header | 8\nwrong key | 401 | invalid signature | 10\nvalid | 200 | ok | 34",
            ),
            (
                "Retry class",
                "4xx usually terminal, 5xx usually retried; record which class this endpoint uses for a bad signature",
            ),
            (
                "Leak check",
                "if bodies differ per failure reason, record the exact markers so the fix (one uniform response) has evidence to point at",
            ),
        ],
        "pitfalls": [
            "Reporting a timing difference without enough samples to separate it from normal variance",
            "Missing that a 500 on rejection causes a partner to retry, which is a real operational impact",
            "Reading your own client's added latency as endpoint behaviour",
        ],
        "done_when": [
            "A response map records status, body marker and timing for at least three rejection cases",
            "The retry class for each rejection status is stated with the provider policy it comes from",
        ],
        "refs": [
            "[OWASP - Error handling guidance](https://owasp.org/www-project-web-security-testing-guide/)",
            "[Stripe - Webhook retries](https://docs.stripe.com/webhooks#handle-retry-events)",
        ],
        "meta": {"phase": "identify"},
    },
]