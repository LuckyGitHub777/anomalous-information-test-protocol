from __future__ import annotations

from pathlib import Path
from .anchor import evaluate_anchor_receipt
from .core import load_json, write_json
from .freeze import verify_freeze
from .ledger import LedgerFormatError, records, verify_ledger, verify_sequence
from .trial import verify_target_packets


def _payload_matches(ledger_records: list[dict], event_type: str, expected: dict) -> bool:
    matches=[r for r in ledger_records if r.get("event_type")==event_type]
    return len(matches)==1 and matches[0].get("payload")==expected


def audit_trial(trial_dir: str | Path) -> dict:
    root=Path(trial_dir); target=verify_target_packets(root,require_reveal=True)
    response_file=root/"evidence"/"response.raw"; response_freeze=root/"evidence"/"response.freeze.json"
    judgment_file=root/"evidence"/"judgment.json"; judgment_freeze=root/"evidence"/"judgment.freeze.json"
    ledger_file=root/"evidence"/"ledger.jsonl"
    response_ok=response_file.exists() and response_freeze.exists() and verify_freeze(response_file,response_freeze)
    judgment_ok=judgment_file.exists() and judgment_freeze.exists() and verify_freeze(judgment_file,judgment_freeze)
    ledger_ok,ledger_message=verify_ledger(ledger_file) if ledger_file.exists() else (False,"ledger missing")
    seq_ok,seq_message=verify_sequence(ledger_file,["TARGET_COMMITTED","RESPONSE_FROZEN","CANDIDATES_RELEASED","JUDGMENT_FROZEN","TARGET_REVEALED"]) if ledger_file.exists() else (False,"ledger missing")
    try: recs=records(ledger_file) if ledger_file.exists() else []
    except LedgerFormatError: recs=[]
    public=load_json(root/"public"/"PUBLIC_commitment.json")
    response_record=load_json(response_freeze) if response_freeze.exists() else {}
    judgment_record=load_json(judgment_freeze) if judgment_freeze.exists() else {}
    payloads_ok=(
        _payload_matches(recs,"TARGET_COMMITTED",public)
        and _payload_matches(recs,"RESPONSE_FROZEN",response_record)
        and _payload_matches(recs,"JUDGMENT_FROZEN",judgment_record)
    )
    judgment=load_json(judgment_file) if judgment_file.exists() else {}; ranking=judgment.get("ranking",[])
    judge_path=root/"judge"/"JUDGE_candidates.json"
    judge_ids=[x["id"] for x in load_json(judge_path).get("candidates",[])] if judge_path.exists() else []
    ranking_ok=sorted(ranking)==sorted(judge_ids) and len(ranking)==len(judge_ids) and bool(judge_ids)
    contamination=root/"evidence"/"contamination.flag"; deviation=root/"evidence"/"material_deviation.flag"
    anchor=evaluate_anchor_receipt(root)
    anchor_artifact=load_json(root/"public"/"ANCHOR.json") if (root/"public"/"ANCHOR.json").exists() else {}
    anchor_receipt=load_json(root/"evidence"/"anchor_receipt.json") if (root/"evidence"/"anchor_receipt.json").exists() else {}
    anchor_ledger_binding=(
        bool(anchor_artifact) and bool(anchor_receipt)
        and _payload_matches(recs,"ANCHOR_EXPORTED",anchor_artifact)
        and _payload_matches(recs,"ANCHOR_RECEIPT_RECORDED",anchor_receipt)
    )
    formal_seq_ok,formal_seq_message=verify_sequence(ledger_file,["TARGET_COMMITTED","ANCHOR_EXPORTED","ANCHOR_RECEIPT_RECORDED","RESPONSE_FROZEN","CANDIDATES_RELEASED","JUDGMENT_FROZEN","TARGET_REVEALED"]) if ledger_file.exists() else (False,"ledger missing")
    protocol_status="VALID"
    if contamination.exists(): protocol_status="INVALID_LEAKAGE"
    elif deviation.exists(): protocol_status="INVALID_DEVIATION"
    elif not all([target["target_packets_valid"],response_ok,judgment_ok,ledger_ok,seq_ok,payloads_ok,ranking_ok]): protocol_status="INVALID_INTEGRITY"
    condition=judgment.get("condition","DRY_RUN")
    if protocol_status=="VALID" and condition!="DRY_RUN":
        if not anchor["anchor_receipt_present"]:
            protocol_status="INVALID_NO_EXTERNAL_ANCHOR"
        elif not anchor["anchor_sufficient_for_formal_analysis"]:
            protocol_status="INVALID_ANCHOR_EVIDENCE"
        elif not anchor_ledger_binding or not formal_seq_ok:
            protocol_status="INVALID_ANCHOR_INTEGRITY"
    if protocol_status!="VALID": inference="NONE"
    elif condition=="DRY_RUN": inference="MECHANICAL_VALIDATION_ONLY"
    else: inference="ELIGIBLE_FOR_PREREGISTERED_ANALYSIS_WITH_RECORDED_HUMAN_ANCHOR_REVIEW"
    result={
        "trial_id":target["trial_id"],"condition":condition,"candidate_count":target["candidate_count"],
        "true_target_id":target["true_target_id"],"judge_rank_1":ranking[0] if ranking else "",
        "commitment_verified":target["commitment_verified"],
        "candidate_packet_verified":target["candidate_content_verified"] and target["candidate_order_verified"] and target["target_pool_verified"],
        "response_freeze_verified":response_ok,"judgment_freeze_verified":judgment_ok,
        "ledger_chain_verified":ledger_ok,"ledger_sequence_verified":seq_ok,"ledger_payloads_verified":payloads_ok,
        **anchor,
        "anchor_ledger_binding_verified": anchor_ledger_binding,
        "anchor_formal_sequence_verified": formal_seq_ok if condition!="DRY_RUN" else False,
        "anchor_formal_sequence_note": formal_seq_message if condition!="DRY_RUN" else "not required for dry run",
        "protocol_status":protocol_status,"inference_eligibility":inference,
        "contamination_notes":"flag present" if contamination.exists() else "",
        "deviation_notes":("flag present" if deviation.exists() else "")+(f"; {ledger_message}; {seq_message}" if not (ledger_ok and seq_ok) else ""),
    }
    write_json(root/"evidence"/"audit.json",result); return result
