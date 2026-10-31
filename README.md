# Anomalous Information Test Protocol (AITP)

> **Test the claim. Preserve the evidence.**

AITP is a local-first, tamper-evident research toolkit for prospectively testing hidden-information claims under blinded, preregistered conditions while controlling ordinary information leakage, flexible scoring, and post-hoc alteration.

It is designed to answer a narrow question well:

> **Can a condition produce reproducible information about blinded targets beyond chance, matched baseline performance, controls, and known leakage pathways?**

AITP does **not** establish a paranormal, extraterrestrial, interdimensional, spiritual, psychic, or other source identity. An unusual result earns investigation only as far as the experiment supports.

## Experience

AITP has two browser experiences backed by one integrity doctrine.

### Public Web Experience

A static, synthetic, zero-telemetry demonstration that teaches the method by experience.

```bash
python run_site.py
```

The public experience is the static application in [`site/`](site/).

### AITP Laboratory

A private local browser workspace for **dry-run protocol validation**. It guides design → participant → judge → reveal → evidence without requiring an operator to work directly with JSON or hashes.

```bash
python run_lab.py
```

Windows: double-click `AITP_LAB.cmd`.

The local Laboratory interface is in [`web/`](web/) and is served by the Python core.

Formal anchored studies remain available through the core/CLI, where anchor evidence can be recorded and reviewed explicitly. The guided Laboratory intentionally exposes only `DRY_RUN` until formal anchor handling can be represented without overstating what the software verifies.

## Protocol lifecycle

**PRECOMMIT → EXTERNAL ANCHOR → RESPOND → FREEZE → RELEASE CANDIDATES → JUDGE → FREEZE → REVEAL → VERIFY → AUDIT → SCORE → PRESERVE**

The interface and core enforce ordering constraints. Serious multi-party studies still require real role/device/storage separation; one shared computer cannot create adversarial separation by UI alone.

## Evidence ladder

| Level | Working hypothesis | What evidence here means |
|---|---|---|
| H0 | Conventional cognition / ordinary information | No anomaly required |
| H1 | Condition-dependent cognition | Performance/state difference only |
| H2 | Anomalous information acquisition | Reproducible blinded-target effect after controls |
| H3 | Additional-agent model | Additional-agent model outperforms cognition/leakage alternatives |
| H4 | Specific source ontology | Identity-discriminating evidence favors a particular source |

**No rung may be skipped.**

## Prediction Ledger

AITP-PRED-1.1 defines one canonical prediction content fingerprint across the public synthetic experience and local Laboratory. The Laboratory can append a separate adjudication record without altering the frozen prediction.

**Freeze → wait for reality → adjudicate against the original criteria → preserve both records.**

## V&V

The v1.1 corrective candidate adds regression coverage for the release-blocking defects found by independent v1.0 adversarial review:

- self-attested/backdated anchor evidence cannot be promoted as independently verified;
- duplicate response sealing is rejected immediately;
- malformed or extra-key ledger records fail cleanly;
- foreign Host headers are rejected by the local Laboratory;
- the guided Laboratory exposes only a workflow it can complete honestly;
- prediction freeze and adjudication use canonical content identity;
- public/Laboratory focus, reorder behavior, errors, mobile navigation, and narrow reflow are rendered in Chromium UAT.

Run local non-browser gates:

```bash
python tools/vv_all.py
```

Run rendered browser UAT (developer/release dependency only):

```bash
python -m pip install playwright==1.64.1
python -m playwright install chromium
python tools/browser_uat.py --chromium __playwright_managed__
```

The core and the actual browser applications require no third-party runtime package.

## Claims assurance

`tools/overclaim_tripwire.py` is deliberately named and documented as a **tripwire**, not a semantic scientific reviewer. It catches a bounded set of literal and assertive extraordinary-claim patterns. Final release still requires explicit human claims review; see [`docs/CLAIMS_REVIEW_GATE.md`](docs/CLAIMS_REVIEW_GATE.md).

## External-anchor assurance

AITP records anchor evidence and human review. It does **not** claim that a third-party service or witness was cryptographically verified unless a future verifier actually implements that proposition. See [`docs/ANCHOR_EVIDENCE.md`](docs/ANCHOR_EVIDENCE.md).

## Broader evidence-bound use

For adjacent problems, AITP documents a generalized discipline:

**Claim → Observable → Null Model → Confounders → Minimum Distinguishing Test → Measurement → Replication → Qualification → Decision**

See [`docs/GENERALIZED_CLAIM_TESTING.md`](docs/GENERALIZED_CLAIM_TESTING.md).

## Documentation

- [Plain-English guide](docs/LAYMAN_GUIDE.md)
- [Quickstart](docs/QUICKSTART.md)
- [Protocol v1.1](docs/PROTOCOL.md)
- [Anchor evidence](docs/ANCHOR_EVIDENCE.md)
- [Claims review gate](docs/CLAIMS_REVIEW_GATE.md)
- [Public web experience](docs/PUBLIC_WEB.md)
- [Product experience](docs/PRODUCT_EXPERIENCE.md)
- [UX](docs/UX.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Threat model](docs/THREAT_MODEL.md)
- [Claims policy](docs/CLAIMS_POLICY.md)
- [Use cases](docs/USE_CASES.md)
- [Public/private boundary](docs/PUBLIC_BOUNDARY.md)
- [GitHub operations](docs/GITHUB_OPERATIONS.md)
- [Hosted UAT checklist](docs/HOSTED_UAT_CHECKLIST.md)
- [Security](SECURITY.md)
- [v1.1 V&V report](docs/VV_REPORT_v1.1.0-rc5.md)
- [v1.1 closure matrix](docs/VV_CLOSURE_MATRIX_v1.1.0-rc5.md)
- [Historical v1.0 V&V](docs/VV_REPORT_v1.0.0.md)

## Privacy

Public-site data is synthetic. Local Laboratory working state is written under ignored `work/`. Do not commit participant recordings, personally identifying information, unredacted consent materials, private target/reveal packets, or live study data.

## Release state

**v1.1.0-rc5 — corrective public-release candidate.**

Local automated, adversarial, and rendered browser gates must pass on the exact candidate. Public release is complete only after the same candidate also passes GitHub-hosted CI, Browser UAT, CodeQL review where applicable, Pages deployment, production readback, and human claims/UAT sign-off.

## License

Source may be publicly inspected but is **not open-source licensed** in this release candidate. All rights are reserved. See [`LICENSE`](LICENSE) and [`LICENSE_DECISION.md`](LICENSE_DECISION.md).
