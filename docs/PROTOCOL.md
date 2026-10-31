# AITP Protocol v1.1

## Purpose

AITP is a research-integrity protocol for testing whether a claimed information-producing condition performs above a preregistered null model while controlling ordinary information leakage, post-hoc alteration, and flexible scoring.

A positive result does not establish a source identity or mechanism.

## Roles

- **Target Custodian (TC):** creates hidden target state and holds private reveal/candidate packets.
- **Session Facilitator (SF):** interacts with the participant and must not know target/candidates.
- **Judge (J):** ranks candidates only after the response is frozen.
- **Analyst (A):** verifies integrity and computes preregistered analyses.
- **Human Authority (HA):** authorizes formal anchor-review status and any study/claim promotion.

## Staged lifecycle

**PRECOMMIT → EXTERNAL ANCHOR → RESPOND → FREEZE → RELEASE CANDIDATES → JUDGE → FREEZE → REVEAL → VERIFY → AUDIT → SCORE → PRESERVE**

### 1. Create trial

`create-trial` generates:
- `public/PUBLIC_commitment.json`
- `custodian/PRIVATE_reveal.json`
- `custodian/PRIVATE_candidates.json`

No judge packet exists yet.

### 2. External anchor

Formal non-dry-run trials require evidence that the target commitment was exported before the response session.

`export-anchor` creates `public/ANCHOR.json`. The local timestamp is explicitly untrusted as independent chronology.

The operator then records an anchor receipt with `record-anchor-receipt`. The receipt identifies:

- the anchor artifact SHA-256;
- an evidence class;
- an external reference where applicable;
- the claimed anchored time;
- a separate Human Authority review record when formal promotion is requested.

AITP v1.1 distinguishes **recorded evidence** from **tool-verified third-party existence**. It does not claim to have contacted or cryptographically validated an external witness/service merely because a receipt contains a reference.

See `docs/ANCHOR_EVIDENCE.md`.

Dry runs may omit the anchor and are eligible only for mechanical validation.

### 3. Record and freeze response

The participant response is copied into `evidence/response.raw` and frozen by SHA-256 before any candidate packet is released.

Once a response freeze exists, both CLI and Laboratory reject resealing/overwrite attempts.

### 4. Release candidates

Only after response-freeze verification may the custodian release `judge/JUDGE_candidates.json`.

### 5. Judge and freeze

The judge ranks every candidate exactly once. The judgment artifact is frozen before target reveal. Once frozen, judgment resealing is rejected.

### 6. Reveal

Only after judgment-freeze verification may the target reveal be copied into `evidence/REVEAL.json`.

### 7. Ledger

AITP-LEDGER-1.1 hashes the complete serialized record body except `record_hash` itself. Legacy v1.0 records remain readable only when they contain exactly the legacy key set; injected unknown fields invalidate them.

Malformed ledger JSON produces a controlled verification failure rather than an unhandled parse exception.

### 8. Audit

Audit evaluates:

- target commitment integrity;
- candidate content/order integrity;
- response freeze;
- judgment freeze;
- ledger hash chain;
- required event order;
- ledger payload cross-binding;
- complete ranking;
- leakage/deviation flags;
- anchor receipt/hash/chronology/evidence class/human review for formal inference.

Formal anchor-related audit fields describe what is actually established, including:

- `anchor_receipt_present`
- `anchor_artifact_hash_matches`
- `anchor_chronology_consistent`
- `anchor_evidence_class`
- `anchor_human_review_recorded`
- `anchor_tool_validation_level`
- `anchor_sufficient_for_formal_analysis`

No field claims that the software independently verified an external witness when it did not.

### 9. Score

Use only audited `VALID` trials.

Primary chance scoring assumes constant candidate count. Record IDs must satisfy the expected string data contract; malformed hand-authored records are rejected rather than silently scored as misses.

If a baseline-vs-condition comparison is preregistered, use the condition-comparison command and report its result separately from the chance test.

## Guided Laboratory scope

The v1.1 guided Laboratory deliberately supports **DRY_RUN only**. This ensures every condition exposed in the UI has a complete and truthful workflow.

Formal anchored workflows remain available through the core/CLI. They should not be promoted into the guided Laboratory until the external-anchor UX is independently tested and its evidence semantics remain accurate end to end.

## Critical boundary

The local hash chain is tamper-evident, not an independent trusted timestamp. A formal trial needs external chronology evidence and explicit review. AITP can validate its own artifacts and chronology relationships; it cannot infer that a third-party service actually witnessed an artifact merely from user-entered text.

## Claims

Use:
1. What we observed
2. What was claimed
3. What we tested
4. What we found
5. What it may mean
6. What we do not know
