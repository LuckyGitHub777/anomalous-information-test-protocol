from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path

from .core import PROTOCOL_VERSION, load_json, sha256_file, write_json
from .ledger import LedgerFormatError, records

ANCHOR_EVIDENCE_CLASSES={"SELF_ATTESTED","THIRD_PARTY_REFERENCE","RFC3161_TOKEN","CHAIN_TXID"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_utc(value: str) -> datetime:
    if not isinstance(value,str) or not value.strip():
        raise ValueError("timestamp required")
    text=value.strip().replace("Z","+00:00")
    dt=datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError("timestamp must include UTC offset")
    return dt.astimezone(timezone.utc)


def export_anchor(trial_dir: str | Path, out_path: str | Path) -> dict:
    root=Path(trial_dir); public_path=root/"public"/"PUBLIC_commitment.json"; public=load_json(public_path)
    record={
        "protocol_version": PROTOCOL_VERSION,
        "trial_id": public["trial_id"],
        "commitment_sha256": public["commitment_sha256"],
        "target_pool_sha256": public["target_pool_sha256"],
        "public_commitment_file_sha256": sha256_file(public_path),
        "exported_at_utc_untrusted_local": utc_now(),
        "instruction": "Send this exact artifact/hash to an independent timestamped witness or trusted timestamp channel before the response session. AITP does not independently verify third-party existence unless separately reviewed.",
    }
    write_json(out_path,record); return record


def _commit_time(root: Path) -> str | None:
    try:
        for rec in records(root/"evidence"/"ledger.jsonl"):
            if rec.get("event_type") == "TARGET_COMMITTED":
                return rec.get("timestamp_utc_untrusted_local")
    except LedgerFormatError:
        return None
    return None


def evaluate_anchor_receipt(trial_dir: str | Path) -> dict:
    root=Path(trial_dir); anchor_path=root/"public"/"ANCHOR.json"; receipt_path=root/"evidence"/"anchor_receipt.json"
    result={
        "anchor_receipt_present": False,
        "anchor_artifact_hash_matches": False,
        "anchor_chronology_consistent": False,
        "anchor_evidence_class": "NONE",
        "anchor_human_review_recorded": False,
        "anchor_tool_validation_level": "REFERENCE_NOT_VALIDATED_BY_TOOL",
        "anchor_sufficient_for_formal_analysis": False,
        "anchor_note": "external anchor receipt missing",
    }
    if not anchor_path.exists():
        result["anchor_note"]="anchor artifact missing"; return result
    if not receipt_path.exists():
        return result
    result["anchor_receipt_present"]=True
    receipt=load_json(receipt_path)
    expected=sha256_file(anchor_path)
    if receipt.get("anchor_artifact_sha256") != expected:
        result["anchor_note"]="anchor receipt hash mismatch"; return result
    result["anchor_artifact_hash_matches"]=True
    ext=str(receipt.get("external_reference") or "").strip(); anchored=str(receipt.get("anchored_at_utc") or "").strip()
    if not ext or not anchored:
        result["anchor_note"]="anchor receipt lacks external reference/timestamp"; return result
    evidence_class=str(receipt.get("evidence_class") or "SELF_ATTESTED").strip().upper()
    if evidence_class not in ANCHOR_EVIDENCE_CLASSES:
        result["anchor_note"]="unsupported anchor evidence class"; return result
    result["anchor_evidence_class"]=evidence_class
    try:
        anchor_dt=_parse_utc(anchored)
        commit_text=_commit_time(root)
        if not commit_text:
            result["anchor_note"]="target commitment time unavailable"; return result
        commit_dt=_parse_utc(commit_text)
    except ValueError as e:
        result["anchor_note"]=f"invalid anchor chronology: {e}"; return result
    if anchor_dt < commit_dt:
        result["anchor_note"]="anchor receipt predates the target commitment"; return result
    if anchor_dt > datetime.now(timezone.utc).replace(microsecond=0) + timedelta(minutes=5):
        result["anchor_note"]="anchor receipt timestamp is implausibly in the future"; return result
    result["anchor_chronology_consistent"]=True
    review=receipt.get("human_review") if isinstance(receipt.get("human_review"),dict) else {}
    human_ok=False
    if str(review.get("status") or "").upper()=="VERIFIED_BY_HUMAN" and str(review.get("reviewer_id") or "").strip() and str(review.get("verified_at_utc") or "").strip():
        try:
            review_dt=_parse_utc(str(review.get("verified_at_utc")))
            human_ok=review_dt >= anchor_dt and review_dt <= datetime.now(timezone.utc).replace(microsecond=0) + timedelta(minutes=5)
        except ValueError:
            human_ok=False
    result["anchor_human_review_recorded"]=human_ok
    sufficient=(evidence_class != "SELF_ATTESTED" and human_ok)
    result["anchor_sufficient_for_formal_analysis"]=sufficient
    if sufficient:
        result["anchor_note"]="external anchor evidence and human review are recorded; AITP does not cryptographically verify the third-party system itself"
    elif evidence_class == "SELF_ATTESTED":
        result["anchor_note"]="self-attested anchor receipt recorded; insufficient for formal analysis"
    else:
        result["anchor_note"]="external anchor reference recorded; independent human review is required before formal analysis"
    return result


def verify_anchor_receipt(trial_dir: str | Path) -> tuple[bool,str]:
    """Compatibility wrapper. True means the receipt is sufficient under v1.1 policy, not tool-verified third-party existence."""
    result=evaluate_anchor_receipt(trial_dir)
    return bool(result["anchor_sufficient_for_formal_analysis"]), result["anchor_note"]


def record_anchor_receipt(trial_dir: str | Path, receipt: dict) -> dict:
    root=Path(trial_dir); anchor_path=root/"public"/"ANCHOR.json"
    if not anchor_path.exists():
        raise ValueError("anchor artifact missing; export anchor first")
    if (root/"evidence"/"response.freeze.json").exists():
        raise ValueError("anchor receipt must be recorded before the response is sealed")
    if (root/"evidence"/"anchor_receipt.json").exists():
        raise ValueError("anchor receipt already recorded for this trial")
    obj={
        "anchor_artifact_sha256": sha256_file(anchor_path),
        "external_reference": str(receipt.get("external_reference") or "").strip(),
        "anchored_at_utc": str(receipt.get("anchored_at_utc") or "").strip(),
        "evidence_class": str(receipt.get("evidence_class") or "SELF_ATTESTED").strip().upper(),
        "human_review": receipt.get("human_review") if isinstance(receipt.get("human_review"),dict) else {},
    }
    write_json(root/"evidence"/"anchor_receipt.json",obj)
    evaluation=evaluate_anchor_receipt(root)
    if not evaluation["anchor_artifact_hash_matches"] or not evaluation["anchor_chronology_consistent"]:
        (root/"evidence"/"anchor_receipt.json").unlink(missing_ok=True)
        raise ValueError(evaluation["anchor_note"])
    return obj
