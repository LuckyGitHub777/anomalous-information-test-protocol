from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .anchor import export_anchor, record_anchor_receipt
from .audit import audit_trial
from .core import load_json, sha256_file, write_json
from .freeze import freeze_artifact
from .ledger import append_event, verify_ledger
from .scoring import compare_rank1_conditions, exact_rank1_summary
from .trial import create_trial, release_candidates, reveal_target, verify_target_packets


def ledger_path(trial: str | Path) -> Path: return Path(trial)/"evidence"/"ledger.jsonl"

def cmd_create(args):
    public=create_trial(args.pool,args.trial_id,args.out,args.candidates); append_event(ledger_path(args.out),"TARGET_COMMITTED",public)
    print("PASS — target state committed"); print(public["commitment_sha256"]); print("STOP — keep custodian/ private. Export an anchor before any formal response session.")

def cmd_export_anchor(args):
    trial=Path(args.trial); out=trial/"public"/"ANCHOR.json"; record=export_anchor(trial,out); append_event(ledger_path(trial),"ANCHOR_EXPORTED",record)
    print("PASS — anchor artifact exported"); print(sha256_file(out)); print("STOP — send this exact anchor/hash to an independent timestamped witness before the response session.")

def cmd_record_anchor_receipt(args):
    trial=Path(args.trial); source=load_json(args.file); obj=record_anchor_receipt(trial,source); append_event(ledger_path(trial),"ANCHOR_RECEIPT_RECORDED",obj)
    print("PASS — anchor receipt recorded"); print("HUMAN AUTHORITY — AITP records the review; it does not cryptographically verify the third-party system.")

def cmd_record_response(args):
    trial=Path(args.trial)
    if (trial/"judge"/"JUDGE_candidates.json").exists(): raise SystemExit("FAIL — candidate packet was released before response freeze")
    if (trial/"evidence"/"response.freeze.json").exists(): raise SystemExit("FAIL — response already sealed for this trial")
    src=Path(args.file); dst=trial/"evidence"/"response.raw"; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dst)
    rec=freeze_artifact(dst,"response",trial/"evidence"/"response.freeze.json"); append_event(ledger_path(trial),"RESPONSE_FROZEN",rec); print("PASS — response copied and frozen"); print(rec["artifact_sha256"])

def cmd_release_candidates(args):
    trial=Path(args.trial); packet=release_candidates(trial); append_event(ledger_path(trial),"CANDIDATES_RELEASED",{"trial_id":packet["trial_id"],"target_pool_sha256":packet["target_pool_sha256"],"candidate_count":len(packet["candidates"])}); print("PASS — judge candidate packet released after response freeze")

def cmd_record_judgment(args):
    trial=Path(args.trial)
    if (trial/"evidence"/"REVEAL.json").exists(): raise SystemExit("FAIL — target was revealed before judgment freeze")
    if (trial/"evidence"/"judgment.freeze.json").exists(): raise SystemExit("FAIL — judgment already sealed for this trial")
    source=load_json(args.file); ranking=source.get("ranking",[]); candidates=load_json(trial/"judge"/"JUDGE_candidates.json").get("candidates",[]); candidate_ids=[x["id"] for x in candidates]
    if len(ranking)!=len(candidate_ids) or sorted(ranking)!=sorted(candidate_ids): raise SystemExit("FAIL — judgment ranking must contain every candidate exactly once")
    if source.get("trial_id")!=load_json(trial/"public"/"PUBLIC_commitment.json").get("trial_id"): raise SystemExit("FAIL — judgment trial_id mismatch")
    dst=trial/"evidence"/"judgment.json"; write_json(dst,source); rec=freeze_artifact(dst,"judgment",trial/"evidence"/"judgment.freeze.json"); append_event(ledger_path(trial),"JUDGMENT_FROZEN",rec); print("PASS — judgment frozen"); print(rec["artifact_sha256"])

def cmd_reveal(args):
    trial=Path(args.trial); reveal=reveal_target(trial); append_event(ledger_path(trial),"TARGET_REVEALED",{"trial_id":reveal["trial_id"],"commitment_sha256":load_json(trial/"public"/"PUBLIC_commitment.json")["commitment_sha256"]}); print("PASS — target revealed after judgment freeze")

def cmd_verify_target(args):
    result=verify_target_packets(args.trial,require_reveal=True); print(json.dumps(result,indent=2)); raise SystemExit(0 if result["target_packets_valid"] else 1)

def cmd_verify_trial(args):
    result=audit_trial(args.trial); print(json.dumps(result,indent=2)); raise SystemExit(0 if result["protocol_status"]=="VALID" else 1)

def cmd_ledger(args):
    ok,msg=verify_ledger(args.file); print(("PASS" if ok else "FAIL")+" — "+msg); raise SystemExit(0 if ok else 1)

def cmd_score(args):
    data=load_json(args.records)
    if not isinstance(data,list): raise SystemExit("FAIL — records JSON must be an array")
    print(json.dumps(exact_rank1_summary(data),indent=2))

def cmd_compare(args):
    data=load_json(args.records)
    if not isinstance(data,list): raise SystemExit("FAIL — records JSON must be an array")
    print(json.dumps(compare_rank1_conditions(data,args.condition_a,args.condition_b),indent=2))

def main():
    p=argparse.ArgumentParser(prog="aitp"); sub=p.add_subparsers(required=True)
    c=sub.add_parser("create-trial"); c.add_argument("--pool",required=True); c.add_argument("--trial-id",required=True); c.add_argument("--out",required=True); c.add_argument("--candidates",type=int,default=4); c.set_defaults(func=cmd_create)
    a=sub.add_parser("export-anchor"); a.add_argument("--trial",required=True); a.set_defaults(func=cmd_export_anchor)
    ar=sub.add_parser("record-anchor-receipt"); ar.add_argument("--trial",required=True); ar.add_argument("--file",required=True); ar.set_defaults(func=cmd_record_anchor_receipt)
    rr=sub.add_parser("record-response"); rr.add_argument("--trial",required=True); rr.add_argument("--file",required=True); rr.set_defaults(func=cmd_record_response)
    rc=sub.add_parser("release-candidates"); rc.add_argument("--trial",required=True); rc.set_defaults(func=cmd_release_candidates)
    rj=sub.add_parser("record-judgment"); rj.add_argument("--trial",required=True); rj.add_argument("--file",required=True); rj.set_defaults(func=cmd_record_judgment)
    rv=sub.add_parser("reveal-target"); rv.add_argument("--trial",required=True); rv.set_defaults(func=cmd_reveal)
    vt=sub.add_parser("verify-target"); vt.add_argument("--trial",required=True); vt.set_defaults(func=cmd_verify_target)
    va=sub.add_parser("verify-trial"); va.add_argument("--trial",required=True); va.set_defaults(func=cmd_verify_trial)
    l=sub.add_parser("verify-ledger"); l.add_argument("--file",required=True); l.set_defaults(func=cmd_ledger)
    s=sub.add_parser("score"); s.add_argument("--records",required=True); s.set_defaults(func=cmd_score)
    cp=sub.add_parser("compare-conditions"); cp.add_argument("--records",required=True); cp.add_argument("--condition-a",required=True); cp.add_argument("--condition-b",required=True); cp.set_defaults(func=cmd_compare)
    args=p.parse_args()
    try: args.func(args)
    except SystemExit: raise
    except (ValueError,FileNotFoundError,json.JSONDecodeError) as e: raise SystemExit(f"FAIL — {e}") from None

if __name__=="__main__": main()
