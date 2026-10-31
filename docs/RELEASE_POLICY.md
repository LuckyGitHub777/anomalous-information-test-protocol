# Release Policy

## v1.1 corrective posture

v1.1.0-rc4 is a **release candidate**, not a final release, until local + hosted + human gates close on one exact commit.

## Required local automated gate

1. Python compile PASS.
2. Unit/API/end-to-end regression tests PASS.
3. Bounded overclaim tripwire PASS.
4. Adversarial release-blocker suite PASS.
5. Repository-boundary lint PASS.
6. Secret-pattern lint PASS.
7. Public/Laboratory UX structure lint PASS.
8. JavaScript syntax PASS.
9. Deterministic build / manifest PASS.
10. ZIP integrity / path-safety PASS.
11. No private lineage, participant data, or live-study artifacts in release.

## Required local rendered gate

Rendered Chromium UAT must pass the public and Laboratory checks in `tools/browser_uat.py`, including 1440/720/390/320 reflow, mobile navigation, keyboard focus/reorder, reduced motion, invalid-state semantics, routing/history, and prediction fingerprint interoperability.

## Required hosted gate

After upload:

1. GitHub CI PASS.
2. GitHub Browser UAT PASS.
3. CodeQL findings reviewed where applicable.
4. Pages deploy PASS.
5. Logged-out production desktop/mobile readback PASS.
6. Production security claims reconciled to actual deployed behavior.

## Required human gate

Human Authority claims and first-time-user UAT sign-off must be recorded before the final tag/release.

Automation can establish machine-verifiable facts; it cannot replace scientific/editorial judgment.

## Protocol-version rule

Any change to the meaning of a ledger digest, commitment, canonical evidence identity, formal eligibility rule, or other inference-relevant record semantics requires explicit protocol/schema versioning and migration/compatibility treatment.

## Research claims

No software release may be described as scientific evidence for H2/H3/H4. Real scientific claims require separate preregistered data, valid controls, analysis, and replication.
