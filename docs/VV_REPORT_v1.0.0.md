# V&V Report — v1.0.0

> **HISTORICAL / SUPERSEDED** — This report records the original v1.0.0 local evidence. Independent adversarial V&V later reopened release gates. Do not use this report as evidence that v1.0.0 is approved for public research-instrument release. See `VV_REPORT_v1.1.0-rc4.md` for the corrective candidate.


## Disposition

**PASS — LOCAL PUBLIC-RELEASE BASELINE / GITHUB ENVIRONMENT READBACK OPEN**

AITP v1.0.0 combines the neutral empirical core, local-first Laboratory, static synthetic public web experience, Prediction Ledger, evidence-bound Claim Test Card, security/repository controls, and deterministic release construction.

## Local executed gates

The final accompanying V&V evidence records:

- Python compile PASS;
- 16/16 unit, end-to-end, public-site, and local-web tests PASS;
- claims lint PASS;
- repository boundary lint PASS;
- secret-pattern lint PASS;
- public-site lint PASS;
- JavaScript syntax checks PASS;
- deterministic build identity PASS;
- ZIP CRC PASS;
- unsafe ZIP paths NONE;
- private lineage / live-study artifacts absent from the public release candidate.

## Web-experience evidence boundary

The public/static and local-web code paths are covered by automated server/API/static-site tests and JavaScript syntax validation.

A real Chromium render was attempted in the build sandbox, but the environment administrator blocked local/file browser navigation. Therefore this report does **not** claim rendered desktop/mobile Chromium UAT PASS.

The remaining environment-specific check is:

1. deploy the exact candidate to public GitHub Pages;
2. open it logged out on desktop and mobile browsers;
3. complete the synthetic demo;
4. verify responsive layout, keyboard/focus behavior, and links;
5. correct any hosted-environment issue if found.

This is a deployment UAT gate, not evidence of a known application defect.

## Scientific boundary

Software/protocol V&V does not establish anomalous information acquisition, an additional information-producing agent, a specific claimed source identity, or any supernatural/nonhuman mechanism.

The inference ladder remains deliberately separated:

- H0 — conventional/ordinary explanation;
- H1 — condition-dependent cognitive or behavioral difference;
- H2 — anomalous information effect under adequate controls;
- H3 — additional-agent model;
- H4 — specific source identity.

No rung may be skipped.

## Generalized evidence-bound engineering

The public method also preserves a broader claim-testing discipline:

**Claim → Observable → Null Model → Confounders → Minimum Distinguishing Test → Measurement → Replication → Qualification → Decision**

This is a methodological pattern, not evidence for any particular extraordinary claim.

## GitHub-hosted gates still open

Local preparation cannot prove hosted execution. After upload/publication, read back:

- GitHub CI;
- CodeQL;
- GitHub Pages deployment;
- logged-out public desktop/mobile UAT.

Those results should be recorded as a separate hosted-environment evidence artifact.
