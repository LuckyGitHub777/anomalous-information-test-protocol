# Anchor Evidence Model

## Why this document exists

A local hash proves internal artifact identity. It does not prove when an independent party first saw that artifact.

AITP therefore separates several propositions that must not be collapsed into one word such as **verified**.

## Evidence states

### Receipt present

A receipt file exists.

This alone proves only that a local record was supplied to the audit.

### Artifact hash matches

The receipt refers to the exact local `ANCHOR.json` SHA-256.

This binds the receipt to the local anchor artifact but still does not prove an external party saw it.

### Chronology consistent

The claimed anchor time is not earlier than target commitment and is not implausibly future-dated relative to the review time.

This catches impossible/backdated local claims. It does not authenticate the external clock/source.

### Evidence class

AITP v1.1 recognizes:

- `SELF_ATTESTED`
- `THIRD_PARTY_REFERENCE`
- `RFC3161_TOKEN`
- `CHAIN_TXID`

The class describes the supplied evidence type. A future implementation may add actual cryptographic verification for specific formats; until then, the tool states its validation level explicitly.

### Human review

Formal promotion requires a separate Human Authority review record with reviewer identity, review time, and `VERIFIED_BY_HUMAN` status for a non-self-attested evidence class.

This means:

> **a human reviewer accepted the supplied external-evidence record for the study workflow.**

It does **not** mean the AITP software independently contacted or validated the referenced service.

## Formal eligibility

A formal non-dry-run trial is not eligible merely because an anchor receipt exists.

The audit requires the configured evidence class, consistent chronology, matching artifact hash, and recorded Human Authority review. Output language remains bounded:

`ELIGIBLE_FOR_PREREGISTERED_ANALYSIS_WITH_RECORDED_HUMAN_ANCHOR_REVIEW`

This is intentionally more precise than saying “externally verified.”

## Stronger future option

A later version may implement actual format-specific verification, such as validating an RFC 3161 timestamp token against a trusted certificate chain. If that is added, it must receive its own verifier, threat analysis, regression tests, and explicit evidence field. It must not be inferred from a URL or operator-entered note.
