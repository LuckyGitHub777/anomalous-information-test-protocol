import json
import tempfile
import unittest
from pathlib import Path

from aitp.anchor import export_anchor
from aitp.core import sha256_file
from aitp.freeze import freeze_artifact, verify_freeze
from aitp.ledger import append_event, verify_ledger, verify_sequence
from aitp.scoring import compare_rank1_conditions, exact_rank1_summary
from aitp.trial import create_trial, release_candidates, reveal_target, verify_target_packets

class TestAITP(unittest.TestCase):
    def setUp(self):
        self.pool = Path(__file__).resolve().parents[1] / "examples" / "target_pool.json"

    def _response(self,td):
        p=Path(td)/"evidence"/"response.raw"; p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text("alpha",encoding="utf-8")
        return freeze_artifact(p,"response",Path(td)/"evidence"/"response.freeze.json")

    def test_staged_target_integrity(self):
        with tempfile.TemporaryDirectory() as td:
            create_trial(self.pool,"T-001",td,4)
            self.assertFalse((Path(td)/"judge"/"JUDGE_candidates.json").exists())
            self._response(td)
            release_candidates(td)
            judgment=Path(td)/"evidence"/"judgment.json"
            candidates=json.loads((Path(td)/"judge"/"JUDGE_candidates.json").read_text())["candidates"]
            judgment.write_text(json.dumps({"trial_id":"T-001","condition":"DRY_RUN","ranking":[x["id"] for x in candidates]}),encoding="utf-8")
            freeze_artifact(judgment,"judgment",Path(td)/"evidence"/"judgment.freeze.json")
            reveal_target(td)
            result=verify_target_packets(td)
            self.assertTrue(result["target_packets_valid"])

    def test_cannot_release_candidates_before_response_freeze(self):
        with tempfile.TemporaryDirectory() as td:
            create_trial(self.pool,"T-002",td,4)
            with self.assertRaises(ValueError):
                release_candidates(td)

    def test_cannot_reveal_before_judgment_freeze(self):
        with tempfile.TemporaryDirectory() as td:
            create_trial(self.pool,"T-003",td,4)
            self._response(td); release_candidates(td)
            with self.assertRaises(ValueError):
                reveal_target(td)

    def test_candidate_tamper_detected(self):
        with tempfile.TemporaryDirectory() as td:
            create_trial(self.pool,"T-004",td,4)
            self._response(td); release_candidates(td)
            p=Path(td)/"judge"/"JUDGE_candidates.json"
            obj=json.loads(p.read_text()); obj["candidates"][0]["content"] += " TAMPERED"
            p.write_text(json.dumps(obj),encoding="utf-8")
            judgment=Path(td)/"evidence"/"judgment.json"
            judgment.write_text(json.dumps({"trial_id":"T-004","condition":"DRY_RUN","ranking":[x["id"] for x in obj["candidates"]]}),encoding="utf-8")
            freeze_artifact(judgment,"judgment",Path(td)/"evidence"/"judgment.freeze.json")
            reveal_target(td)
            result=verify_target_packets(td)
            self.assertFalse(result["candidate_content_verified"])

    def test_artifact_freeze_detects_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"response.txt"; p.write_text("alpha",encoding="utf-8")
            f=Path(td)/"response.freeze.json"
            freeze_artifact(p,"response",f)
            self.assertTrue(verify_freeze(p,f))
            p.write_text("beta",encoding="utf-8")
            self.assertFalse(verify_freeze(p,f))

    def test_ledger_tamper_and_sequence(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"ledger.jsonl"
            append_event(p,"TARGET_COMMITTED",{"x":1})
            append_event(p,"RESPONSE_FROZEN",{"x":2})
            append_event(p,"CANDIDATES_RELEASED",{"x":3})
            append_event(p,"JUDGMENT_FROZEN",{"x":4})
            append_event(p,"TARGET_REVEALED",{"x":5})
            self.assertTrue(verify_ledger(p)[0])
            self.assertTrue(verify_sequence(p,["TARGET_COMMITTED","RESPONSE_FROZEN","CANDIDATES_RELEASED","JUDGMENT_FROZEN","TARGET_REVEALED"])[0])
            lines=p.read_text().splitlines(); obj=json.loads(lines[0]); obj["payload"]["x"]=99; lines[0]=json.dumps(obj)
            p.write_text("\n".join(lines)+"\n")
            self.assertFalse(verify_ledger(p)[0])

    def test_exact_score(self):
        rows=[
          {"protocol_status":"VALID","candidate_count":4,"true_target_id":"A","judge_rank_1":"A"},
          {"protocol_status":"VALID","candidate_count":4,"true_target_id":"B","judge_rank_1":"C"},
          {"protocol_status":"VALID","candidate_count":4,"true_target_id":"D","judge_rank_1":"D"},
          {"protocol_status":"VALID","candidate_count":4,"true_target_id":"E","judge_rank_1":"F"},
        ]
        s=exact_rank1_summary(rows)
        self.assertEqual(s["rank1_hits"],2)
        self.assertAlmostEqual(s["exact_one_sided_binomial_p"],0.26171875)

    def test_condition_comparison(self):
        rows=[]
        for i in range(8):
            rows.append({"protocol_status":"VALID","condition":"BASELINE","candidate_count":4,"true_target_id":"A","judge_rank_1":"A" if i<2 else "B"})
            rows.append({"protocol_status":"VALID","condition":"CLAIMED_CHANNELING","candidate_count":4,"true_target_id":"A","judge_rank_1":"A" if i<5 else "B"})
        result=compare_rank1_conditions(rows,"BASELINE","CLAIMED_CHANNELING")
        self.assertEqual(result["a_hits"],2)
        self.assertEqual(result["b_hits"],5)
        self.assertTrue(0 <= result["fisher_exact_two_sided_p"] <= 1)

if __name__ == "__main__":
    unittest.main()
