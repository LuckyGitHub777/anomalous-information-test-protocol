#!/usr/bin/env python3
from __future__ import annotations
import json, socket, tempfile, threading
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from aitp.anchor import export_anchor, evaluate_anchor_receipt
from aitp.audit import audit_trial
from aitp.core import sha256_file
from aitp.freeze import freeze_artifact
from aitp.ledger import append_event, verify_ledger
from aitp.prediction import freeze_prediction
from aitp.trial import create_trial, release_candidates, reveal_target
from aitp.webapp import LabHandler, LabServer
import importlib.util

ROOT=Path(__file__).resolve().parents[1]

def expect(ok,msg):
    if not ok: raise AssertionError(msg)
    print('PASS — '+msg)

def complete_formal(t:Path):
    pub=create_trial(ROOT/'examples'/'target_pool.json','ADV-1',t,4); append_event(t/'evidence'/'ledger.jsonl','TARGET_COMMITTED',pub); export_anchor(t,t/'public'/'ANCHOR.json')
    rp=t/'evidence'/'response.raw'; rp.write_text('response'); rf=freeze_artifact(rp,'response',t/'evidence'/'response.freeze.json'); append_event(t/'evidence'/'ledger.jsonl','RESPONSE_FROZEN',rf)
    packet=release_candidates(t); append_event(t/'evidence'/'ledger.jsonl','CANDIDATES_RELEASED',{'trial_id':packet['trial_id'],'target_pool_sha256':packet['target_pool_sha256'],'candidate_count':len(packet['candidates'])})
    jp=t/'evidence'/'judgment.json'; jp.write_text(json.dumps({'trial_id':'ADV-1','judge_id':'J','condition':'BASELINE','ranking':[x['id'] for x in packet['candidates']]})); jf=freeze_artifact(jp,'judgment',t/'evidence'/'judgment.freeze.json'); append_event(t/'evidence'/'ledger.jsonl','JUDGMENT_FROZEN',jf)
    reveal=reveal_target(t); append_event(t/'evidence'/'ledger.jsonl','TARGET_REVEALED',{'trial_id':reveal['trial_id'],'commitment_sha256':pub['commitment_sha256']})

def main():
    spec=importlib.util.spec_from_file_location('trip',ROOT/'tools'/'overclaim_tripwire.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    over='Our trials conclusively demonstrate telepathic information transfer. The evidence confirms nonhuman intelligence and establishes extraterrestrial origin.'
    expect(bool(m.scan_text(over)),'H1 natural-language overclaim is flagged (human review still required)')
    with tempfile.TemporaryDirectory() as td:
        t=Path(td); complete_formal(t); anchor=t/'public'/'ANCHOR.json'; (t/'evidence'/'anchor_receipt.json').write_text(json.dumps({'anchor_artifact_sha256':sha256_file(anchor),'external_reference':'self','anchored_at_utc':'2019-01-01T00:00:00Z','evidence_class':'SELF_ATTESTED'})); a=evaluate_anchor_receipt(t); expect(not a['anchor_sufficient_for_formal_analysis'] and not a['anchor_chronology_consistent'],'H2 backdated self-attested anchor cannot promote formal analysis'); expect(a['anchor_tool_validation_level']=='REFERENCE_NOT_VALIDATED_BY_TOOL','H2 tool does not label external existence verified')
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'l.jsonl'; append_event(p,'A',{'x':1}); x=json.loads(p.read_text()); x['injected']='x'; p.write_text(json.dumps(x)+'\n'); expect(not verify_ledger(p)[0],'M3 unknown ledger key invalidates record'); p.write_text('{oops\n'); ok,msg=verify_ledger(p); expect(not ok and 'malformed ledger' in msg,'M4 malformed ledger returns controlled FAIL')
    with tempfile.TemporaryDirectory() as td:
        server=LabServer(('127.0.0.1',0),LabHandler,Path(td)); port=server.server_address[1]; th=threading.Thread(target=server.serve_forever,daemon=True); th.start(); base=f'http://127.0.0.1:{port}'
        def post(path,obj):
            req=Request(base+path,data=json.dumps(obj).encode(),method='POST',headers={'Content-Type':'application/json','X-AITP-Request':'1'})
            try:
                with urlopen(req,timeout=3) as r:return r.status,json.loads(r.read())
            except HTTPError as e:return e.code,json.loads(e.read())
        code,c=post('/api/trials',{'condition':'DRY_RUN','candidate_count':4}); tid=c['trial']['trial_id']; expect(post(f'/api/trials/{tid}/response',{'text':'first'})[0]==200 and post(f'/api/trials/{tid}/response',{'text':'second'})[0]==409,'H4 response reseal rejected immediately')
        expect(post('/api/trials',{'condition':'BASELINE','candidate_count':4})[0]==400,'H3 guided Laboratory rejects unsupported formal condition')
        s=socket.create_connection(('127.0.0.1',port)); s.sendall(b'GET /api/health HTTP/1.1\r\nHost: evil.example.com\r\nConnection: close\r\n\r\n'); line=s.recv(1024).decode('latin1').splitlines()[0]; s.close(); expect('421' in line,'L8 foreign Host header rejected')
        server.shutdown(); server.server_close()
    a=freeze_prediction({'exact_wording':'X','success_condition':'X','failure_condition':'not X'},'A','2026-01-01T00:00:00Z'); b=freeze_prediction({'exact_wording':'X','success_condition':'X','failure_condition':'not X'},'B','2026-01-02T00:00:00Z'); expect(a['content_sha256']==b['content_sha256'],'M8 canonical prediction content fingerprint is stable across record IDs/times')
    print('PASS — ADVERSARIAL RELEASE-BLOCKER REGRESSION SUITE')

if __name__=='__main__': main()
