# Threat Model

AITP treats methodological failure as an engineering problem.

## Assets to protect

- Hidden target identity
- Candidate-set integrity
- Participant response integrity
- Judge-ranking integrity
- Trial chronology
- Negative-result completeness
- Raw evidence provenance
- Human-subject privacy
- Truthful assurance semantics

## Threat classes

### Information leakage
Target known by participant, facilitator, judge, device, network service, metadata, or prior target-pool familiarity.

### Cueing
Verbal, nonverbal, procedural, or audience feedback changes participant/judge behavior.

### Flexible scoring
Vague matching, selective feature weighting, undisclosed rescoring, or outcome switching.

### Statistical flexibility
Optional stopping, multiple uncorrected analyses, undisclosed exclusions, repeated looks, or selective reporting.

### Artifact mutation
Response, judgment, target packet, transcript, prediction, or result changed after the relevant protocol gate.

### Ledger-format ambiguity
Unhashed/injected record fields, malformed records, or silent interpretation across incompatible ledger versions.

### Chronology overclaim
A locally authored or backdated receipt is promoted as if a third party were independently verified.

### Assurance-label drift
A green check or words such as “verified,” “sealed,” “valid,” or “eligible” imply more than the named control actually establishes.

### Tool/AI leakage
Internet search, model assistance, hidden devices, or software exposing target information.

### Local web exposure
Unexpected Host handling, cross-origin access, path traversal, or accidental non-loopback binding exposes Laboratory state.

### Governance capture
A spiritually compelling or narratively exciting interpretation is allowed to override empirical controls or vice versa.

## Controls

- role separation;
- offline/local-first operation;
- loopback + Host validation;
- SHA-256 commitments/artifact freezes;
- candidate-content digests;
- versioned hash-chained ledger;
- preregistration;
- blinded judging;
- immediate reseal rejection;
- trial-validity audit;
- negative-result/invalid-trial retention;
- explicit anchor evidence classes and chronology checks;
- Human Authority before formal anchor/claim promotion;
- bounded automated overclaim tripwire plus human claims review;
- rendered accessibility/UX UAT as a release gate.
