import json
import os
import socket
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from aitp.webapp import LabHandler, LabServer

class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory()
        self.server=LabServer(("127.0.0.1",0),LabHandler,Path(self.td.name))
        self.port=self.server.server_address[1]
        self.th=threading.Thread(target=self.server.serve_forever,daemon=True); self.th.start()
        self.base=f"http://127.0.0.1:{self.port}"
    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.td.cleanup()
    def get(self,path):
        with urlopen(self.base+path,timeout=3) as r: return r.status,r.headers,r.read()
    def post(self,path,obj):
        req=Request(self.base+path,data=json.dumps(obj).encode(),method="POST",headers={"Content-Type":"application/json","X-AITP-Request":"1"})
        with urlopen(req,timeout=3) as r:return r.status,json.loads(r.read())
    def test_home_security_headers(self):
        status,h,b=self.get('/')
        self.assertEqual(status,200); self.assertIn(b'AITP Laboratory',b)
        self.assertIn("default-src 'self'",h['Content-Security-Policy']); self.assertEqual(h['X-Frame-Options'],'DENY')
    def test_api_guard(self):
        req=Request(self.base+'/api/trials',data=b'{}',method='POST',headers={'Content-Type':'application/json'})
        with self.assertRaises(HTTPError) as cm:urlopen(req,timeout=3)
        self.assertEqual(cm.exception.code,400)
    def test_guided_dry_run_api(self):
        _,created=self.post('/api/trials',{'label':'Web E2E','condition':'DRY_RUN','candidate_count':4}); tid=created['trial']['trial_id']
        self.post(f'/api/trials/{tid}/response',{'text':'bright tower near water'})
        self.post(f'/api/trials/{tid}/release',{})
        _,_,raw=self.get(f'/api/trials/{tid}/candidates'); c=json.loads(raw)['candidates']; ranking=[x['id'] for x in c]
        self.post(f'/api/trials/{tid}/judgment',{'ranking':ranking,'judge_id':'J1'})
        self.post(f'/api/trials/{tid}/reveal',{})
        _,_,raw=self.get(f'/api/trials/{tid}/result'); result=json.loads(raw)
        self.assertEqual(result['audit']['protocol_status'],'VALID')
        self.assertEqual(result['audit']['inference_eligibility'],'MECHANICAL_VALIDATION_ONLY')
    def test_prediction_freeze(self):
        _,r=self.post('/api/predictions',{'exact_wording':'X will happen by date Y','success_condition':'X happens by Y','failure_condition':'X does not happen by Y'})
        self.assertEqual(len(r['prediction']['frozen_sha256']),64)

if __name__=='__main__':unittest.main()
