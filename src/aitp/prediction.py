from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .core import canonical_json_bytes, sha256_bytes

PREDICTION_SCHEMA_VERSION = "AITP-PRED-1.1"
CONTENT_FIELDS = (
    "exact_wording",
    "source",
    "target_event",
    "time_window",
    "probability_language",
    "conditional_language",
    "success_condition",
    "failure_condition",
)
RESOLUTION_DISPOSITIONS = {"SUCCESS", "FAILURE", "AMBIGUOUS", "NOT_YET_DETERMINABLE"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _text(value: Any) -> str:
    return str(value or "").strip()


def canonical_prediction_content(data: dict) -> dict:
    record = {"schema_version": PREDICTION_SCHEMA_VERSION}
    for key in CONTENT_FIELDS:
        record[key] = _text(data.get(key))
    for key in ("exact_wording", "success_condition", "failure_condition"):
        if not record[key]:
            raise ValueError(f"{key.replace('_', ' ')} is required")
    return record


def prediction_content_sha256(data: dict) -> str:
    return sha256_bytes(canonical_json_bytes(canonical_prediction_content(data)))


def freeze_prediction(data: dict, prediction_id: str, claimed_at_utc: str | None = None) -> dict:
    content = canonical_prediction_content(data)
    record = {
        "prediction_id": prediction_id,
        "date_time_claimed": claimed_at_utc or utc_now(),
        **content,
        "content_sha256": prediction_content_sha256(content),
        "status": "FROZEN",
    }
    record["frozen_sha256"] = sha256_bytes(canonical_json_bytes(record))
    return record


def resolve_prediction(prediction: dict, data: dict, resolved_at_utc: str | None = None) -> dict:
    disposition = _text(data.get("disposition")).upper()
    if disposition not in RESOLUTION_DISPOSITIONS:
        raise ValueError("disposition must be SUCCESS, FAILURE, AMBIGUOUS, or NOT_YET_DETERMINABLE")
    summary = _text(data.get("outcome_summary"))
    if not summary:
        raise ValueError("outcome summary is required")
    resolution = {
        "schema_version": PREDICTION_SCHEMA_VERSION,
        "prediction_id": prediction["prediction_id"],
        "prediction_frozen_sha256": prediction["frozen_sha256"],
        "prediction_content_sha256": prediction["content_sha256"],
        "disposition": disposition,
        "outcome_summary": summary,
        "evidence_reference": _text(data.get("evidence_reference")),
        "adjudicator": _text(data.get("adjudicator")) or "local-human-authority",
        "resolved_at_utc_untrusted_local": resolved_at_utc or utc_now(),
        "interpretation_boundary": "Adjudication applies the frozen criteria to the cited evidence; it does not rewrite the original prediction.",
    }
    resolution["resolution_sha256"] = sha256_bytes(canonical_json_bytes(resolution))
    return resolution
