import json
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from aitp.anchor import export_anchor, record_anchor_receipt
from aitp.audit import audit_trial
from aitp.freeze import freeze_artifact
from aitp.ledger import append_event
from aitp.trial import create_trial, release_candidates, reveal_target


class TestEndToEnd(unittest.TestCase):
    def _finish(self, root: Path, trial_id: str, condition: str, text: str = "synthetic response"):
        response=root/"evidence"/"response.raw"; response.write_text(text,encoding="utf-8")
        rf=freeze_artifact(response,"response",root/"evidence"/"response.freeze.json")
        append_event(root/"evidence"/"ledger.jsonl","RESPONSE_FROZEN",rf)
        packet=release_candidates(root)
        append_event(root/"evidence"/"ledger.jsonl","CANDIDATES_RELEASED",{
            "trial_id":packet["trial_id"],"target_pool_sha256":packet["target_pool_sha256"],"candidate_count":len(packet["candidates"]),
        })
        ranking=[x["id"] for x in packet["candidates"]]
        judgment={"trial_id":trial_id,"judge_id":"J1","condition":condition,"ranking":ranking}
        jp=root/"evidence"/"judgment.json"; jp.write_text(json.dumps(judgment,indent=2)+"\n",encoding="utf-8")
        jf=freeze_artifact(jp,"judgment",root/"evidence"/"judgment.freeze.json")
        append_event(root/"evidence"/"ledger.jsonl","JUDGMENT_FROZEN",jf)
        reveal=reveal_target(root)
        pub=json.loads((root/"public"/"PUBLIC_commitment.json").read_text())
        append_event(root/"evidence"/"ledger.jsonl","TARGET_REVEALED",{"trial_id":reveal["trial_id"],"commitment_sha256":pub["commitment_sha256"]})

    def test_valid_dry_run(self):
        repo=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as td:
            t=Path(td); pub=create_trial(repo/"examples"/"target_pool.json","E2E-001",t,4)
            append_event(t/"evidence"/"ledger.jsonl","TARGET_COMMITTED",pub)
            self._finish(t,"E2E-001","DRY_RUN")
            result=audit_trial(t)
            self.assertEqual(result["protocol_status"],"VALID")
            self.assertEqual(result["inference_eligibility"],"MECHANICAL_VALIDATION_ONLY")
            self.assertTrue(result["ledger_sequence_verified"])
            self.assertTrue(result["ledger_payloads_verified"])

    def test_formal_trial_requires_pre_response_bound_anchor_receipt(self):
        repo=Path(__file__).resolve().parents[1]
        # Missing receipt can never be promoted after the session.
        with tempfile.TemporaryDirectory() as td:
            t=Path(td); pub=create_trial(repo/"examples"/"target_pool.json","E2E-002A",t,4)
            append_event(t/"evidence"/"ledger.jsonl","TARGET_COMMITTED",pub)
            anchor=export_anchor(t,t/"public"/"ANCHOR.json"); append_event(t/"evidence"/"ledger.jsonl","ANCHOR_EXPORTED",anchor)
            self._finish(t,"E2E-002A","CONTROL","formal response")
            result=audit_trial(t); self.assertEqual(result["protocol_status"],"INVALID_NO_EXTERNAL_ANCHOR")
            now=datetime.now(timezone.utc).replace(microsecond=0)
            with self.assertRaises(ValueError):
                record_anchor_receipt(t,{"external_reference":"late","anchored_at_utc":now.isoformat().replace("+00:00","Z"),"evidence_class":"THIRD_PARTY_REFERENCE"})

        # Proper formal path records and ledger-binds reviewed anchor evidence before response freeze.
        with tempfile.TemporaryDirectory() as td:
            t=Path(td); pub=create_trial(repo/"examples"/"target_pool.json","E2E-002B",t,4)
            append_event(t/"evidence"/"ledger.jsonl","TARGET_COMMITTED",pub)
            anchor=export_anchor(t,t/"public"/"ANCHOR.json"); append_event(t/"evidence"/"ledger.jsonl","ANCHOR_EXPORTED",anchor)
            now=datetime.now(timezone.utc).replace(microsecond=0)
            receipt=record_anchor_receipt(t,{
                "external_reference":"independent-witness:test-reference",
                "anchored_at_utc":now.isoformat().replace("+00:00","Z"),
                "evidence_class":"THIRD_PARTY_REFERENCE",
                "human_review":{"status":"VERIFIED_BY_HUMAN","reviewer_id":"reviewer-1","verified_at_utc":(now+timedelta(seconds=1)).isoformat().replace("+00:00","Z")},
            })
            append_event(t/"evidence"/"ledger.jsonl","ANCHOR_RECEIPT_RECORDED",receipt)
            self._finish(t,"E2E-002B","CONTROL","formal response")
            result=audit_trial(t)
            self.assertEqual(result["protocol_status"],"VALID")
            self.assertTrue(result["anchor_ledger_binding_verified"])
            self.assertTrue(result["anchor_formal_sequence_verified"])
            self.assertEqual(result["inference_eligibility"],"ELIGIBLE_FOR_PREREGISTERED_ANALYSIS_WITH_RECORDED_HUMAN_ANCHOR_REVIEW")
            self.assertEqual(result["anchor_tool_validation_level"],"REFERENCE_NOT_VALIDATED_BY_TOOL")


if __name__ == "__main__":
    unittest.main()
