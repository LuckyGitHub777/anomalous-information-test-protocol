import json, socket, tempfile, threading, unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from aitp.anchor import export_anchor, evaluate_anchor_receipt, record_anchor_receipt
from aitp.audit import audit_trial
from aitp.core import sha256_file
from aitp.freeze import freeze_artifact
from aitp.ledger import append_event, verify_ledger
from aitp.prediction import freeze_prediction, prediction_content_sha256, resolve_prediction
from aitp.scoring import exact_rank1_summary
from aitp.trial import create_trial, release_candidates, reveal_target
from aitp.webapp import LabHandler, LabServer

class TestReleaseRegressions(unittest.TestCase):
    def _complete(self, root:Path, condition='DRY_RUN', anchor_receipt=None):
        repo=Path(__file__).resolve().parents[1]
        pub=create_trial(repo/'examples'/'target_pool.json','REG-001',root,4); append_event(root/'evidence'/'ledger.jsonl','TARGET_COMMITTED',pub)
        anchor=export_anchor(root,root/'public'/'ANCHOR.json'); append_event(root/'evidence'/'ledger.jsonl','ANCHOR_EXPORTED',anchor)
        if anchor_receipt is not None:
            receipt=record_anchor_receipt(root,anchor_receipt); append_event(root/'evidence'/'ledger.jsonl','ANCHOR_RECEIPT_RECORDED',receipt)
        response=root/'evidence'/'response.raw'; response.write_text('synthetic response',encoding='utf-8'); rf=freeze_artifact(response,'response',root/'evidence'/'response.freeze.json'); append_event(root/'evidence'/'ledger.jsonl','RESPONSE_FROZEN',rf)
        packet=release_candidates(root); append_event(root/'evidence'/'ledger.jsonl','CANDIDATES_RELEASED',{'trial_id':packet['trial_id'],'target_pool_sha256':packet['target_pool_sha256'],'candidate_count':len(packet['candidates'])})
        judgment={'trial_id':'REG-001','judge_id':'J','condition':condition,'ranking':[x['id'] for x in packet['candidates']]}; jp=root/'evidence'/'judgment.json'; jp.write_text(json.dumps(judgment),encoding='utf-8'); jf=freeze_artifact(jp,'judgment',root/'evidence'/'judgment.freeze.json'); append_event(root/'evidence'/'ledger.jsonl','JUDGMENT_FROZEN',jf)
        reveal=reveal_target(root); append_event(root/'evidence'/'ledger.jsonl','TARGET_REVEALED',{'trial_id':reveal['trial_id'],'commitment_sha256':pub['commitment_sha256']})
        return pub

    def test_backdated_self_attested_anchor_never_promotes(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td); self._complete(t,'BASELINE')
            anchor=t/'public'/'ANCHOR.json'; (t/'evidence'/'anchor_receipt.json').write_text(json.dumps({'anchor_artifact_sha256':sha256_file(anchor),'external_reference':'self note','anchored_at_utc':'2019-01-01T00:00:00Z','evidence_class':'SELF_ATTESTED'}),encoding='utf-8')
            a=evaluate_anchor_receipt(t); self.assertFalse(a['anchor_chronology_consistent']); self.assertFalse(a['anchor_sufficient_for_formal_analysis'])
            r=audit_trial(t); self.assertEqual(r['protocol_status'],'INVALID_ANCHOR_EVIDENCE'); self.assertEqual(r['inference_eligibility'],'NONE'); self.assertNotIn('external_anchor_reference_verified', r); self.assertEqual(r['anchor_tool_validation_level'],'REFERENCE_NOT_VALIDATED_BY_TOOL')

    def test_human_reviewed_external_reference_can_be_formally_eligible_without_tool_verification_claim(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td); now=datetime.now(timezone.utc).replace(microsecond=0); receipt={'external_reference':'independent-witness:case-123','anchored_at_utc':now.isoformat().replace('+00:00','Z'),'evidence_class':'THIRD_PARTY_REFERENCE','human_review':{'status':'VERIFIED_BY_HUMAN','reviewer_id':'reviewer-1','verified_at_utc':(now+timedelta(seconds=1)).isoformat().replace('+00:00','Z')}}
            self._complete(t,'CONTROL',receipt)
            a=evaluate_anchor_receipt(t); self.assertTrue(a['anchor_sufficient_for_formal_analysis']); self.assertEqual(a['anchor_tool_validation_level'],'REFERENCE_NOT_VALIDATED_BY_TOOL')
            r=audit_trial(t); self.assertEqual(r['protocol_status'],'VALID'); self.assertTrue(r['anchor_ledger_binding_verified']); self.assertTrue(r['anchor_formal_sequence_verified']); self.assertIn('RECORDED_HUMAN_ANCHOR_REVIEW',r['inference_eligibility'])

    def test_formal_anchor_receipt_is_bound_and_cannot_be_rewritten_after_response(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td); now=datetime.now(timezone.utc).replace(microsecond=0); receipt={'external_reference':'independent-witness:case-123','anchored_at_utc':now.isoformat().replace('+00:00','Z'),'evidence_class':'THIRD_PARTY_REFERENCE','human_review':{'status':'VERIFIED_BY_HUMAN','reviewer_id':'reviewer-1','verified_at_utc':(now+timedelta(seconds=1)).isoformat().replace('+00:00','Z')}}
            self._complete(t,'CONTROL',receipt); rp=t/'evidence'/'anchor_receipt.json'; obj=json.loads(rp.read_text()); obj['external_reference']='rewritten-after-session'; rp.write_text(json.dumps(obj),encoding='utf-8')
            r=audit_trial(t); self.assertEqual(r['protocol_status'],'INVALID_ANCHOR_INTEGRITY'); self.assertFalse(r['anchor_ledger_binding_verified'])
            with self.assertRaises(ValueError): record_anchor_receipt(t,receipt)

    def test_ledger_unknown_key_and_malformed_record_fail(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'ledger.jsonl'; append_event(p,'A',{'x':1}); lines=p.read_text().splitlines(); obj=json.loads(lines[0]); obj['injected']='x'; p.write_text(json.dumps(obj)+'\n'); self.assertFalse(verify_ledger(p)[0])
            p.write_text('{bad json\n'); ok,msg=verify_ledger(p); self.assertFalse(ok); self.assertIn('malformed ledger record',msg)

    def test_scoring_rejects_non_string_ids(self):
        with self.assertRaises(ValueError): exact_rank1_summary([{'protocol_status':'VALID','candidate_count':4,'true_target_id':1,'judge_rank_1':'1'}])

    def test_prediction_canonical_content_and_resolution_binding(self):
        data={'exact_wording':'X occurs','source':'A','target_event':'X','time_window':'2027','success_condition':'X occurs','failure_condition':'X does not occur'}
        a=freeze_prediction(data,'P1','2026-08-13T00:00:00Z'); b=freeze_prediction(data,'P2','2026-08-13T01:00:00Z')
        self.assertEqual(a['content_sha256'],b['content_sha256']); self.assertNotEqual(a['frozen_sha256'],b['frozen_sha256']); self.assertEqual(a['content_sha256'],prediction_content_sha256(data))
        res=resolve_prediction(a,{'disposition':'SUCCESS','outcome_summary':'X occurred','evidence_reference':'source-1'},'2027-01-01T00:00:00Z'); self.assertEqual(res['prediction_frozen_sha256'],a['frozen_sha256']); self.assertEqual(len(res['resolution_sha256']),64)

class TestWebRegressions(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory(); self.server=LabServer(('127.0.0.1',0),LabHandler,Path(self.td.name)); self.port=self.server.server_address[1]; self.th=threading.Thread(target=self.server.serve_forever,daemon=True); self.th.start(); self.base=f'http://127.0.0.1:{self.port}'
    def tearDown(self): self.server.shutdown(); self.server.server_close(); self.td.cleanup()
    def post(self,path,obj):
        req=Request(self.base+path,data=json.dumps(obj).encode(),method='POST',headers={'Content-Type':'application/json','X-AITP-Request':'1'})
        try:
            with urlopen(req,timeout=3) as r:return r.status,json.loads(r.read())
        except HTTPError as e:return e.code,json.loads(e.read())
    def test_lab_rejects_formal_condition(self):
        code,j=self.post('/api/trials',{'condition':'BASELINE','candidate_count':4}); self.assertEqual(code,400); self.assertIn('DRY_RUN only',j['error'])
    def test_second_response_seal_is_409_and_first_is_preserved(self):
        code,c=self.post('/api/trials',{'label':'X','condition':'DRY_RUN','candidate_count':4}); tid=c['trial']['trial_id']; self.assertEqual(self.post(f'/api/trials/{tid}/response',{'text':'FIRST'})[0],200); self.assertEqual(self.post(f'/api/trials/{tid}/response',{'text':'SECOND'})[0],409); raw=(Path(self.td.name)/'trials'/tid/'evidence'/'response.raw').read_text().strip(); self.assertEqual(raw,'FIRST')
    def test_foreign_host_rejected(self):
        s=socket.create_connection(('127.0.0.1',self.port),timeout=3); req=f'GET /api/health HTTP/1.1\r\nHost: evil.example.com\r\nConnection: close\r\n\r\n'.encode(); s.sendall(req); raw=s.recv(4096).decode('latin1'); s.close(); self.assertIn('421',raw.splitlines()[0])
    def test_unknown_api_get_is_404(self):
        try: urlopen(self.base+'/api/typo',timeout=3)
        except HTTPError as e: self.assertEqual(e.code,404)
        else: self.fail('expected 404')
    def test_prediction_adjudication_append_only(self):
        code,r=self.post('/api/predictions',{'exact_wording':'X','success_condition':'X','failure_condition':'not X'}); self.assertEqual(code,201); pid=r['prediction']['prediction_id']; content=r['prediction']['content_sha256']; code,res=self.post(f'/api/predictions/{pid}/resolve',{'disposition':'AMBIGUOUS','outcome_summary':'Evidence mixed','evidence_reference':'E1'}); self.assertEqual(code,201); self.assertEqual(res['prediction']['content_sha256'],content); self.assertEqual(self.post(f'/api/predictions/{pid}/resolve',{'disposition':'SUCCESS','outcome_summary':'rewrite attempt'})[0],409)

if __name__=='__main__': unittest.main()
