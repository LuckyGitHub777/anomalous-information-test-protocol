# Changelog

## v1.1.0-rc5 — Hosted Browser UAT dependency correction

- Corrected the Browser UAT development-only dependency from nonexistent `playwright==1.62.1` to current PyPI release `playwright==1.64.1` after the GitHub-hosted verification gate failed during installation.
- Advanced candidate identity rather than mutating rc4 in place.
- Preserved all rc4 protocol, evidence, claims, security, accessibility, UX, and product behavior unchanged.
- Requires fresh local reproducibility plus GitHub-hosted CI / Browser UAT / CodeQL / Pages readback before final release.

## v1.1.0-rc4 — Public Git import simplification

- Removed committed documentation screenshots so the public source tree is text-only and does not depend on stale binary captures.
- Kept rendered browser screenshots as generated UAT evidence under ignored `work/` only.
- Replaced README screenshot embeds with durable links to the runnable `site/` and `web/` source surfaces.
- Preserved all rc3 scientific, protocol, security, accessibility, UX, and supply-chain behavior unchanged.
- rc4 exists because the frozen candidate identity changed before the full GitHub import.

## v1.1.0-rc3 — Pre-upload publication optimization

- Compressed documentation screenshots and moved generated UAT captures out of the release tree.
- Not promoted to the public branch; superseded by rc4 to remove committed screenshot dependencies entirely.

## v1.1.0-rc2 — Current-dependency revalidation

- Reverified the public-release candidate on 2026-10-31 before GitHub upload.
- Updated immutable GitHub Action pins to current official releases: `actions/setup-python` v7.1.0, `github/codeql-action` v4.39.1, and `actions/deploy-pages` v5.0.1.
- Preserved `actions/checkout` v7.0.1, `actions/configure-pages` v6.0.0, and `actions/upload-pages-artifact` v5.0.0 after current recheck.
- No scientific, protocol, claims, privacy, or UX scope expansion; rc2 exists because a frozen release-candidate identity changed.
- Requires the same hosted CI / Browser UAT / Pages / Human Authority gates before final tag or release.

## v1.1.0-rc1 — Corrective convergence

This candidate supersedes v1.0.0 for release evaluation.

### Assurance truthfulness
- Replaces the misleadingly broad `claims_lint` label with an explicitly bounded `overclaim_tripwire` and a separate human claims-review gate.
- Replaces false external-anchor “verified” semantics with explicit receipt/hash/chronology/evidence-class/human-review states.
- Rejects backdated anchor chronology.
- Keeps the tool honest about what it does not independently verify.

### Protocol enforcement
- Guided Laboratory is intentionally `DRY_RUN` only; formal anchored studies remain core/CLI workflows.
- Duplicate response and judgment sealing fail immediately.
- Ledger v1.1 hashes the full record body except `record_hash`; strict legacy records reject injected keys.
- Malformed ledger lines return controlled verification failure.
- Foreign Host headers are rejected by the loopback Laboratory.
- Unknown API GET routes return JSON 404 rather than the application shell.
- Scoring rejects malformed non-string target IDs.

### Human experience
- Adds visible Laboratory `:focus-visible` styling.
- Candidate reordering retains keyboard focus and announces the new position.
- Adds persistent assertive error regions and field association.
- Fixes public 320/390 px reflow and keeps primary navigation reachable on mobile.
- Invalid audits are visibly invalid and explain analysis ineligibility.
- Unknown Laboratory routes recover to Overview; browser Back navigates between views.
- Touch ranking controls meet the 44 px design target.

### Product completeness
- Adds canonical AITP-PRED-1.1 prediction content fingerprints across public and local experiences.
- Adds append-only local Prediction Ledger adjudication.
- Adds production-relevant CSP meta policy for the static site while preserving an explicit distinction between meta-enforceable and response-header-only controls.
- Adds rendered Chromium UAT and a GitHub Browser UAT workflow.

### V&V
- Expands Python suite from 16 to 26 tests before final closeout.
- Adds dedicated adversarial release-blocker regression suite.
- Adds public + Laboratory UX structure lint.
- Adds rendered browser checks at 1440 / 720 / 390 / 320 plus keyboard, reduced-motion, invalid-state, routing, and prediction interoperability checks.

## v1.0.0 — Historical audited baseline

v1.0.0 established deterministic release identity, a strong evidence-chain core, exact statistics, and the first public/Laboratory product surfaces. Independent adversarial V&V later reopened assurance, workflow, accessibility, and hosted-parity gates. It is retained as history and must not be used as the release candidate.
