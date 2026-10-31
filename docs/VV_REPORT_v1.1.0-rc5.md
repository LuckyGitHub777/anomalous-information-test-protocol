# V&V Report — v1.1.0-rc5

**Dependency revalidation:** 2026-10-31. The rc1 corrective scope is unchanged; rc2 refreshes immutable GitHub Action pins before hosted execution.

**Status:** **LOCAL CORRECTIVE RELEASE-CANDIDATE PASS · HOSTED + HUMAN GATES OPEN**

## Purpose

v1.1.0-rc5 is the bounded corrective convergence produced after independent adversarial review reopened the v1.0.0 public-release gates. It does not redesign AITP. It makes assurance language, workflow enforcement, accessibility, mobile behavior, and repeat-use product semantics match the strength of the underlying evidence core.

The governing rule is:

> **Never make a green check mean more than the system actually established.**

## Corrective scope

The candidate closes or truthfully downscopes the v1.0 findings in four workstreams:

1. **Assurance truthfulness** — bounded overclaim tripwire + Human Authority review; anchor evidence classes; no false tool-level external-verification label; chronology and formal sequence checks.
2. **Protocol enforcement** — dry-run-only guided Laboratory; immediate reseal rejection; AITP-LEDGER-1.1 full-record digest semantics; clean malformed-record failure; Host validation.
3. **Human experience** — visible focus; keyboard-focus retention; accessible live announcements; persistent errors; mobile reflow/nav; 44 px ranking controls; irreversible-action confirmations.
4. **Product completeness** — canonical AITP-PRED-1.1 content identity; append-only prediction adjudication; deployable public CSP meta subset; explicit hosted-parity gate.

See `VV_CLOSURE_MATRIX_v1.1.0-rc5.md` for all 35 independent findings.

## Local automated V&V

Executed on the exact working candidate:

- Python compile: **PASS**
- Python tests: **27/27 PASS**
- overclaim tripwire: **PASS** (bounded automation only; human review still required)
- adversarial release-blocker regression suite: **PASS**
- repository-boundary lint: **PASS**
- secret-pattern lint: **PASS**
- public/Laboratory UX structure lint: **PASS**
- public JavaScript syntax: **PASS**
- Laboratory JavaScript syntax: **PASS**
- deterministic release builder: **PASS**

Regression coverage includes:

- natural-language extraordinary overclaim tripwire behavior;
- backdated/self-attested anchor non-promotion;
- no false `external_anchor_reference_verified` assurance field;
- human-reviewed external-reference formal eligibility with bounded wording;
- formal anchor artifact/receipt ledger binding before response;
- anchor receipt cannot be added after response seal;
- unknown ledger-key rejection;
- malformed ledger controlled failure;
- duplicate response seal rejection with first response preserved;
- guided Laboratory rejection of unsupported formal conditions;
- foreign Host rejection;
- canonical prediction content fingerprint stability;
- append-only prediction adjudication;
- non-string scoring-ID rejection.

## Rendered Chromium UAT

`tools/browser_uat.py` executed successfully in Chromium using the exact public/Laboratory HTML, CSS, and JavaScript with deterministic browser-local/API mocks where required by the sandbox environment.

**PASS:**

- public reflow at 1440, 720, 390, and 320 px;
- `scrollWidth <= innerWidth` at 390/320;
- all five public primary nav destinations remain reachable on mobile;
- keyboard focus starts at skip links;
- public and Laboratory ranking reorder retain focus;
- ranking position changes are announced through live regions;
- public reveal retains interpretation boundary;
- public prediction SHA equals the Python AITP-PRED-1.1 canonical serializer;
- reduced-motion operation remains intact;
- Laboratory focused controls have authored visible outlines;
- guided Laboratory dry run reaches `VALID`;
- invalid audit uses explicit error styling and explains analysis ineligibility;
- Prediction Ledger completes append-only adjudication;
- unknown Laboratory hash recovers to Overview;
- browser Back moves between Laboratory views;
- Laboratory reflows and keeps navigation reachable at 390 px.

Screenshots generated from this gate are stored under `work/uat-screenshots/`.

## Live HTTP browser UAT

`tools/browser_uat_live.py` exists and is wired into `.github/workflows/browser-uat.yml`. It launches the actual public preview server and the actual Laboratory HTTP/API/core stack on loopback and drives Chromium through the real HTTP paths.

The present sandbox blocks browser navigation to loopback URLs with `ERR_BLOCKED_BY_ADMINISTRATOR`. Therefore **live-loopback HTTP browser UAT is not falsely labelled PASS locally**.

The GitHub Browser UAT workflow is the intended independent hosted gate and installs Playwright/Chromium before executing both browser suites.

## Security boundary

Local checks establish:

- Laboratory binds only to loopback;
- foreign Host values are rejected;
- state-changing API requests require the local-request guard and JSON;
- request size/input validation remains fail-closed;
- traversal probes remain refused;
- public HTML includes a CSP meta policy appropriate to controls supported through HTML;
- public runtime has no telemetry, CDN, external executable script/style/font/media dependencies;
- release boundary excludes private lineage and live participant/study material.

GitHub Pages is static hosting. Final production claims about response headers must be based on actual deployed readback, not local preview-server headers.

## Anchor assurance boundary

AITP v1.1 distinguishes:

- receipt present;
- anchor artifact hash match;
- chronology consistency;
- evidence class;
- recorded Human Authority review;
- tool validation level.

The software does **not** claim it contacted or cryptographically verified a third-party witness/service merely because a URL/reference or human review record exists.

Formal promotion additionally requires the anchor artifact and receipt to be ledger-bound **before** `RESPONSE_FROZEN` in the formal sequence.

## Claims boundary

`tools/overclaim_tripwire.py` is explicitly a bounded automation. Its PASS state means only that configured tripwire patterns were not detected.

Final release requires a Human Authority review of README, public copy, Laboratory interpretation copy, release notes, claims policy, and this V&V report.

No software V&V result is H2/H3/H4 scientific evidence.

## Release disposition

### Locally closed

- identity/provenance engineering;
- deterministic packaging logic;
- core evidence-chain regressions;
- statistics/randomization implementation retained from the independently cross-validated v1.0 core;
- assurance-semantics corrections;
- guided Laboratory workflow integrity;
- accessibility/responsive corrective implementation;
- rendered Chromium source-surface UAT;
- Prediction Ledger freeze/adjudication lifecycle;
- public/private source boundary.

### Still open before final public tag/release

- exact GitHub-hosted CI readback;
- live-loopback Browser UAT on GitHub runner;
- CodeQL review where applicable;
- GitHub Pages deployment;
- logged-out production desktop/mobile UAT;
- production security/readback reconciliation;
- Human Authority claims/UAT sign-off.

**v1.1.0-rc5 is therefore a public-release candidate, not yet the final public release.**
