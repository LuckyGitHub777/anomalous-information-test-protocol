# Worked Example — From Hidden Target to Auditable Evidence

This is a **synthetic educational example**. It demonstrates the AITP workflow and evidence products; it is not scientific evidence of anomalous information acquisition or any proposed mechanism.

## The question

Can a participant describe a hidden target before the candidate set and correct answer are available to them, while preserving enough evidence to audit the order later?

## 1. Create the dry run

A four-candidate `DRY_RUN` is created. The true target is selected privately and a public cryptographic commitment is written before the participant responds.

At this point the participant does not know the candidate set or target identity.

## 2. Capture and seal the response

Example response:

> Tall red structure near water; open sky; strong vertical lines; metallic or architectural feeling; cool air.

The response is sealed before candidates are released. A later rewrite would change the evidence fingerprint and/or violate the event sequence.

## 3. Release candidates to the blinded judge

Example candidates:

1. Desert telescope — a large telescope observatory in a dry desert.
2. Snowy bridge — a stone bridge crossing a snowy river.
3. Yellow balloon — a yellow hot-air balloon above farmland.
4. Clock workshop — a workshop wall covered with mechanical clocks.

The judge sees the frozen participant response and ranks the candidates while the true target remains hidden.

Example ranking:

1. Snowy bridge
2. Desert telescope
3. Yellow balloon
4. Clock workshop

The judgment is then sealed.

## 4. Reveal and audit

The true target is revealed as **Snowy bridge**. In this example the judge ranked it first.

AITP does not convert that observation into a mechanism claim. The audit asks whether the protocol record itself remained valid:

- target commitment verified;
- candidate packet verified;
- response freeze verified;
- judgment freeze verified;
- ledger sequence verified;
- ledger cross-binding verified.

For a guided dry run, the correct interpretation is mechanical validation of the workflow. One rank-1 result is not evidence of telepathy, remote viewing, nonhuman intelligence, or any other mechanism.

## 5. What the user keeps

A completed trial produces role-separated artifacts such as:

```text
custodian/
  PRIVATE_candidates.json
  PRIVATE_reveal.json

public/
  PUBLIC_commitment.json
  ANCHOR.json
  LAB_META.json

judge/
  JUDGE_candidates.json

evidence/
  response.raw
  response.freeze.json
  judgment.json
  judgment.freeze.json
  REVEAL.json
  ledger.jsonl
  audit.json
```

The value is not simply whether the trial was a hit or miss. The value is that later reviewers can inspect **what was fixed, what was said, what was judged, what was revealed, and whether the ordering rules held**.

## 6. Repeat before interpreting

One trial is not the research product. A serious study defines the hypothesis, null model, candidate count, conditions, stopping rule, primary analysis, contamination/deviation rules, and chronology controls prospectively. Repeated valid trials can then be scored and compared without silently discarding failures.

## Prediction Ledger companion use

The same integrity doctrine applies to future-facing claims:

1. record exact wording;
2. define success and failure;
3. define the outcome window;
4. freeze the canonical prediction content;
5. wait for reality;
6. append adjudication without rewriting the frozen claim.

This is useful anywhere hindsight could otherwise change what someone remembers having predicted.
