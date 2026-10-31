# Hosted UAT Checklist — v1.1.0-rc5

Run this checklist against the **exact commit** proposed for final public release.

## GitHub readback

- [ ] CI matrix completes on Ubuntu and Windows for the configured Python versions.
- [ ] 27+ Python regression tests pass.
- [ ] Overclaim tripwire passes, with the understanding that it is not semantic claims review.
- [ ] Adversarial release-blocker suite passes.
- [ ] Repository-boundary lint passes.
- [ ] Secret-pattern lint passes.
- [ ] Public/Laboratory UX structure lint passes.
- [ ] JavaScript syntax checks pass.
- [ ] Deterministic release build passes and matches the expected candidate identity where applicable.
- [ ] Browser UAT workflow passes.
- [ ] CodeQL completes and findings are reviewed where applicable.
- [ ] Pages deploys from `site/` only.

## Logged-out public desktop — 1440 px class

- [ ] Hero states **Test the claim. Preserve the evidence.**
- [ ] No missing assets, unexpected console failures, or external runtime dependencies.
- [ ] Complete synthetic demo: commitment → response → candidates → ranking → reveal.
- [ ] Candidate reorder retains keyboard focus and announces the new position.
- [ ] Reveal always states that one demonstration is not research evidence for an anomalous effect/mechanism.
- [ ] Freeze a prediction and confirm the content fingerprint is shown.
- [ ] GitHub/repository destination resolves correctly in the actual Pages environment.
- [ ] Local Laboratory instructions are clear.

## Narrow desktop / zoom equivalent — ~720 px

- [ ] No horizontal overflow.
- [ ] Text remains readable and controls remain operable.
- [ ] Demo and Prediction form remain usable.

## Mobile — ~390 × 844 and 320 px narrow

- [ ] `scrollWidth <= innerWidth`.
- [ ] All primary navigation destinations remain reachable.
- [ ] Demo response field is usable.
- [ ] Candidate rank controls are at least the intended 44 px target and keyboard/touch operable.
- [ ] Reveal content remains readable.
- [ ] Inspect/V&V cards collapse without a fixed-width floor.
- [ ] Prediction form remains usable.

## Accessibility

- [ ] Complete public demo keyboard-only.
- [ ] Complete Laboratory dry run keyboard-only.
- [ ] Focus is visible on links, buttons, inputs, selects, and textareas.
- [ ] Candidate reorder retains focus.
- [ ] Candidate movement is announced through a live region.
- [ ] Persistent errors use alert semantics and identify/focus the relevant field where appropriate.
- [ ] Skip links work.
- [ ] No state relies on color alone.
- [ ] Reduced-motion preference leaves operation intact.
- [ ] 200% zoom remains usable.

## Local Laboratory

On a trusted local machine:

```bash
python run_lab.py
```

- [ ] Health endpoint reports `1.1.0-rc5` and `DRY_RUN` guided scope.
- [ ] Foreign Host header is rejected.
- [ ] Formal condition creation is rejected with a plain-language dry-run-only explanation.
- [ ] Complete dry run end to end.
- [ ] Irreversible Laboratory actions require explicit confirmation before submission.
- [ ] Candidate release is blocked before response freeze.
- [ ] Second response seal is rejected without changing the first response.
- [ ] Reveal is blocked before judgment freeze.
- [ ] Invalid audit is visually unmistakable and explains analysis ineligibility.
- [ ] Evidence Cabinet shows completed/invalid trial state without `undefined` labels.
- [ ] Prediction Ledger freezes a record and appends one adjudication.
- [ ] Second adjudication is rejected.
- [ ] Unknown hash route recovers to Overview.
- [ ] Browser Back moves between application views.

## Claims and assurance sign-off

- [ ] Human Authority completes `docs/CLAIMS_REVIEW_GATE.md` against README, public site, Laboratory interpretation copy, release notes, and V&V report.
- [ ] Anchor language never equates “receipt present” or “human review recorded” with tool-verified external existence.
- [ ] No software V&V result is presented as H2/H3/H4 scientific evidence.

## Production security reality

- [ ] Inspect actual Pages HTML and response behavior.
- [ ] Confirm the CSP meta policy is present in deployed HTML.
- [ ] Do not claim response-header controls that the static host does not provide.
- [ ] Confirm no runtime telemetry/external executable/style/font/media dependency was introduced.

## Closeout rule

Any failed item is corrective work. Patch the candidate, rerun affected local gates, and create a new candidate identity. Do not reinterpret a failed check as a pass.
