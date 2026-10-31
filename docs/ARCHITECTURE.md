# Architecture

## 1. Empirical core — `src/aitp/`

Standard-library Python implementing target commitment, staged disclosure, artifact freezing, anchor-evidence records, ledger v1.1, trial audit, prediction identity/adjudication, and exact scoring.

## 2. Local Laboratory — `web/` + `src/aitp/webapp.py`

A loopback-only browser interface over the same core. It uses no remote assets or telemetry and writes working state under ignored `work/` by default.

The guided Laboratory is deliberately **DRY_RUN only** in v1.1. Formal anchored studies remain core/CLI workflows until a formal anchor UI earns release through its own V&V.

## 3. Static public layer — `site/`

Standalone synthetic education/demo layer. It never imports or accesses `work/`, private trial artifacts, or the Laboratory API. It performs no telemetry/network call and uses a production-relevant CSP meta policy for controls that browsers permit through HTML meta.

The public Prediction experience and local Laboratory share the same AITP-PRED-1.1 canonical content fingerprint definition.

## 4. Data contracts — `schemas/`

Schemas for claims, predictions, and trial audit records.

## 5. Study templates — `templates/`

Preregistration, judge, contamination, deviation, claim-test, and anchor-receipt forms.

## 6. V&V — `tests/` + `tools/`

-  unit/API/end-to-end regression tests;
- bounded overclaim tripwire plus separate human claims gate;
- adversarial release-blocker regression suite;
- repository-boundary lint;
- secret-pattern lint;
- public/Laboratory UX structure lint;
- rendered Chromium UAT;
- deterministic release builder.

## 7. GitHub control plane — `.github/`

- cross-platform CI;
- rendered Browser UAT;
- conditional public CodeQL;
- static Pages deployment;
- Dependabot;
- issue/PR templates.

External GitHub Actions are pinned to exact commit SHAs.

## Security model

- Laboratory binds only to loopback.
- Request Host must resolve to the allowed local host/port form.
- Mutating API requests require JSON plus the local-request guard header.
- No CORS access is enabled.
- Working/private data is excluded from release packaging.
- Sealed response/judgment writes are append/lock governed rather than silently overwritten.
- Anchor evidence is described with bounded semantics rather than false external-verification claims.

## Important limitation

A single local filesystem is **not** a security boundary between mutually distrustful roles. The UI enforces workflow order; formal blinded studies should use separate custodians/devices/storage when genuine role isolation is required.
