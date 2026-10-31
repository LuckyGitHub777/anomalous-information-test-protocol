from __future__ import annotations

import argparse
import json
import mimetypes
import re
import secrets
import threading
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .anchor import export_anchor
from .audit import audit_trial
from .core import load_json, write_json
from .freeze import freeze_artifact
from .ledger import append_event
from .prediction import freeze_prediction, resolve_prediction
from .trial import create_trial, release_candidates, reveal_target

ROOT=Path(__file__).resolve().parents[2]
WEB_ROOT=ROOT/"web"
DEFAULT_WORKSPACE=ROOT/"work"/"lab"
TRIAL_ID=re.compile(r"^[A-Za-z0-9._-]{1,80}$")
PREDICTION_ID=re.compile(r"^[A-Za-z0-9._-]{1,100}$")


def utc_now()->str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")


def _safe_trial(workspace:Path,trial_id:str)->Path:
    if not TRIAL_ID.fullmatch(trial_id): raise ValueError("invalid trial id")
    p=(workspace/"trials"/trial_id).resolve(); base=(workspace/"trials").resolve()
    if base not in p.parents: raise ValueError("unsafe trial path")
    return p


def _prediction_dir(workspace:Path)->Path:
    p=workspace/"predictions"; p.mkdir(parents=True,exist_ok=True); return p


def _safe_prediction(workspace:Path,prediction_id:str)->Path:
    if not PREDICTION_ID.fullmatch(prediction_id): raise ValueError("invalid prediction id")
    return _prediction_dir(workspace)/(prediction_id+".json")


def _trial_state(trial:Path)->dict:
    pub=trial/"public"/"PUBLIC_commitment.json"
    if not pub.exists(): return {"trial_id":trial.name,"label":"Unreadable trial","condition":"UNKNOWN","state":"BROKEN","candidate_count":None,"created_at":"","audit":None}
    public=load_json(pub); state="COMMITTED"
    if (trial/"evidence"/"response.freeze.json").exists(): state="RESPONSE_FROZEN"
    if (trial/"judge"/"JUDGE_candidates.json").exists(): state="CANDIDATES_RELEASED"
    if (trial/"evidence"/"judgment.freeze.json").exists(): state="JUDGMENT_FROZEN"
    if (trial/"evidence"/"REVEAL.json").exists(): state="REVEALED"
    audit=load_json(trial/"evidence"/"audit.json") if (trial/"evidence"/"audit.json").exists() else None
    meta=load_json(trial/"public"/"LAB_META.json") if (trial/"public"/"LAB_META.json").exists() else {}
    return {"trial_id":trial.name,"label":meta.get("label","Untitled trial"),"condition":meta.get("condition","DRY_RUN"),"state":state,"candidate_count":public.get("candidate_count"),"created_at":meta.get("created_at",""),"audit":audit}


def _prediction_state(workspace:Path,p:Path)->dict:
    pred=load_json(p); res_path=_prediction_dir(workspace)/(pred["prediction_id"]+".resolution.json")
    if res_path.exists():
        pred={**pred,"status":"ADJUDICATED","resolution":load_json(res_path)}
    return pred


class LabHandler(BaseHTTPRequestHandler):
    server_version="AITPLab/1.1"
    @property
    def workspace(self)->Path: return self.server.workspace  # type: ignore[attr-defined]
    def log_message(self,fmt,*args): return

    def _security_headers(self,content_type="application/json; charset=utf-8",cache="no-store"):
        self.send_header("Content-Type",content_type); self.send_header("Cache-Control",cache)
        self.send_header("X-Content-Type-Options","nosniff"); self.send_header("Referrer-Policy","no-referrer"); self.send_header("X-Frame-Options","DENY")
        self.send_header("Permissions-Policy","camera=(), microphone=(), geolocation=(), payment=(), usb=()")
        self.send_header("Content-Security-Policy","default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'")

    def _json(self,obj,status=200):
        data=json.dumps(obj,ensure_ascii=False).encode("utf-8"); self.send_response(status); self._security_headers(); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def _error(self,message,status=400): self._json({"ok":False,"error":str(message)},status)

    def _host_ok(self)->bool:
        raw=(self.headers.get("Host") or "").strip().lower()
        port=self.server.server_address[1]
        allowed={f"127.0.0.1:{port}",f"localhost:{port}",f"[::1]:{port}"}
        return raw in allowed
    def _guard_host(self)->bool:
        if self._host_ok(): return True
        self._error("invalid Host header for loopback Laboratory",421); return False

    def _read_json(self):
        if self.headers.get("X-AITP-Request")!="1": raise ValueError("missing local-request guard")
        ctype=self.headers.get("Content-Type","")
        if not ctype.startswith("application/json"): raise ValueError("application/json required")
        length=int(self.headers.get("Content-Length","0"))
        if length>2_000_000: raise ValueError("request too large")
        raw=self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_GET(self):
        if not self._guard_host(): return
        path=urlparse(self.path).path
        try:
            if path=="/api/health": return self._json({"ok":True,"version":"1.1.0-rc4","workspace":str(self.workspace),"network":"loopback-only","telemetry":False,"laboratory_scope":"DRY_RUN"})
            if path=="/api/trials":
                base=self.workspace/"trials"; base.mkdir(parents=True,exist_ok=True)
                return self._json({"ok":True,"trials":[_trial_state(p) for p in sorted(base.iterdir(),reverse=True) if p.is_dir()]})
            if path=="/api/predictions":
                items=[]
                for p in sorted(_prediction_dir(self.workspace).glob("*.json"),reverse=True):
                    if p.name.endswith((".anchor.json",".resolution.json")): continue
                    try: items.append(_prediction_state(self.workspace,p))
                    except Exception: pass
                return self._json({"ok":True,"predictions":items})
            m=re.fullmatch(r"/api/trials/([^/]+)/candidates",path)
            if m:
                trial=_safe_trial(self.workspace,m.group(1)); p=trial/"judge"/"JUDGE_candidates.json"
                if not p.exists(): return self._error("candidates are not released yet",409)
                return self._json({"ok":True,**load_json(p)})
            m=re.fullmatch(r"/api/trials/([^/]+)/result",path)
            if m:
                trial=_safe_trial(self.workspace,m.group(1))
                if not (trial/"evidence"/"REVEAL.json").exists(): return self._error("target is not revealed yet",409)
                audit=audit_trial(trial); reveal=load_json(trial/"evidence"/"REVEAL.json"); candidates=load_json(trial/"judge"/"JUDGE_candidates.json")["candidates"]
                byid={x["id"]:x for x in candidates}; judgment=load_json(trial/"evidence"/"judgment.json"); response=(trial/"evidence"/"response.raw").read_text(encoding="utf-8")
                return self._json({"ok":True,"audit":audit,"response":response,"ranking":judgment.get("ranking",[]),"true_target":byid.get(reveal.get("true_target_id"),{}),"candidates":candidates})
            if path.startswith("/api/"): return self._error("unknown endpoint",404)
            return self._serve_static(path)
        except FileNotFoundError: self._error("not found",404)
        except ValueError as e: self._error(str(e),400)
        except Exception as e: self._error(str(e),500)

    def _serve_static(self,path):
        rel="index.html" if path in {"/",""} else path.lstrip("/"); target=(WEB_ROOT/rel).resolve()
        if WEB_ROOT.resolve() not in target.parents and target!=WEB_ROOT.resolve(): return self._error("unsafe path",403)
        if not target.exists() or not target.is_file(): target=WEB_ROOT/"index.html"
        data=target.read_bytes(); ctype=mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(200); self._security_headers(ctype,"no-cache" if target.suffix in {".html",".js",".css"} else "public, max-age=3600"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)

    def do_POST(self):
        if not self._guard_host(): return
        path=urlparse(self.path).path
        try:
            body=self._read_json()
            if path=="/api/trials":
                label=str(body.get("label") or "Untitled dry run")[:120]; condition=str(body.get("condition") or "DRY_RUN")
                if condition!="DRY_RUN": raise ValueError("AITP Laboratory v1.1 supports DRY_RUN only. Formal anchored conditions use the core/CLI workflow.")
                count=int(body.get("candidate_count",4)); trial_id=f"AITP-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{secrets.token_hex(2)}"; trial=_safe_trial(self.workspace,trial_id)
                pub=create_trial(ROOT/"examples"/"target_pool.json",trial_id,trial,count); append_event(trial/"evidence"/"ledger.jsonl","TARGET_COMMITTED",pub)
                write_json(trial/"public"/"LAB_META.json",{"label":label,"condition":"DRY_RUN","created_at":utc_now(),"target_pool":"bundled synthetic pool"})
                anchor=export_anchor(trial,trial/"public"/"ANCHOR.json"); append_event(trial/"evidence"/"ledger.jsonl","ANCHOR_EXPORTED",anchor)
                return self._json({"ok":True,"trial":_trial_state(trial)},201)
            m=re.fullmatch(r"/api/trials/([^/]+)/response",path)
            if m:
                trial=_safe_trial(self.workspace,m.group(1))
                if (trial/"judge"/"JUDGE_candidates.json").exists(): return self._error("candidate set already released",409)
                if (trial/"evidence"/"response.freeze.json").exists(): return self._error("response already sealed for this trial",409)
                text=str(body.get("text") or "").strip()
                if not text: raise ValueError("response cannot be empty")
                p=trial/"evidence"/"response.raw"; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text+"\n",encoding="utf-8")
                rec=freeze_artifact(p,"response",trial/"evidence"/"response.freeze.json"); append_event(trial/"evidence"/"ledger.jsonl","RESPONSE_FROZEN",rec)
                return self._json({"ok":True,"sealed":rec["artifact_sha256"],"trial":_trial_state(trial)})
            m=re.fullmatch(r"/api/trials/([^/]+)/release",path)
            if m:
                trial=_safe_trial(self.workspace,m.group(1)); packet=release_candidates(trial); append_event(trial/"evidence"/"ledger.jsonl","CANDIDATES_RELEASED",{"trial_id":packet["trial_id"],"target_pool_sha256":packet["target_pool_sha256"],"candidate_count":len(packet["candidates"])})
                return self._json({"ok":True,"trial":_trial_state(trial)})
            m=re.fullmatch(r"/api/trials/([^/]+)/judgment",path)
            if m:
                trial=_safe_trial(self.workspace,m.group(1))
                if (trial/"evidence"/"REVEAL.json").exists(): return self._error("target already revealed",409)
                if (trial/"evidence"/"judgment.freeze.json").exists(): return self._error("judgment already sealed for this trial",409)
                candidates=load_json(trial/"judge"/"JUDGE_candidates.json").get("candidates",[]); ids=[x["id"] for x in candidates]; ranking=body.get("ranking",[])
                if len(ranking)!=len(ids) or sorted(ranking)!=sorted(ids): raise ValueError("ranking must contain every candidate exactly once")
                obj={"trial_id":trial.name,"judge_id":str(body.get("judge_id") or "local-judge")[:80],"condition":"DRY_RUN","ranking":ranking}; p=trial/"evidence"/"judgment.json"; write_json(p,obj)
                rec=freeze_artifact(p,"judgment",trial/"evidence"/"judgment.freeze.json"); append_event(trial/"evidence"/"ledger.jsonl","JUDGMENT_FROZEN",rec)
                return self._json({"ok":True,"sealed":rec["artifact_sha256"],"trial":_trial_state(trial)})
            m=re.fullmatch(r"/api/trials/([^/]+)/reveal",path)
            if m:
                trial=_safe_trial(self.workspace,m.group(1)); reveal=reveal_target(trial); public=load_json(trial/"public"/"PUBLIC_commitment.json"); append_event(trial/"evidence"/"ledger.jsonl","TARGET_REVEALED",{"trial_id":reveal["trial_id"],"commitment_sha256":public["commitment_sha256"]}); audit=audit_trial(trial)
                return self._json({"ok":True,"audit":audit,"trial":_trial_state(trial)})
            if path=="/api/predictions":
                pid=f"PRED-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{secrets.token_hex(2)}"; obj=freeze_prediction(body,pid); p=_safe_prediction(self.workspace,pid); write_json(p,obj)
                write_json(_prediction_dir(self.workspace)/(pid+".anchor.json"),{"prediction_id":pid,"prediction_frozen_sha256":obj["frozen_sha256"],"prediction_content_sha256":obj["content_sha256"],"exported_at_utc_untrusted_local":utc_now(),"instruction":"Send this exact record/hash to an independent timestamped witness before relying on chronology."})
                return self._json({"ok":True,"prediction":obj},201)
            m=re.fullmatch(r"/api/predictions/([^/]+)/resolve",path)
            if m:
                p=_safe_prediction(self.workspace,m.group(1))
                if not p.exists(): return self._error("prediction not found",404)
                rp=_prediction_dir(self.workspace)/(m.group(1)+".resolution.json")
                if rp.exists(): return self._error("prediction already adjudicated",409)
                pred=load_json(p); resolution=resolve_prediction(pred,body); write_json(rp,resolution)
                return self._json({"ok":True,"prediction":_prediction_state(self.workspace,p),"resolution":resolution},201)
            return self._error("unknown endpoint",404)
        except json.JSONDecodeError: self._error("malformed JSON",400)
        except ValueError as e: self._error(str(e),400)
        except FileNotFoundError: self._error("required artifact not found",409)
        except Exception as e: self._error(str(e),500)


class LabServer(ThreadingHTTPServer):
    daemon_threads=True; allow_reuse_address=True
    def __init__(self,address,handler,workspace): super().__init__(address,handler); self.workspace=workspace


def main(argv=None):
    ap=argparse.ArgumentParser(description="Launch AITP Laboratory on loopback only."); ap.add_argument("--host",default="127.0.0.1"); ap.add_argument("--port",type=int,default=7777); ap.add_argument("--workspace",default=str(DEFAULT_WORKSPACE)); ap.add_argument("--no-browser",action="store_true"); args=ap.parse_args(argv)
    if args.host not in {"127.0.0.1","localhost","::1"}: raise SystemExit("STOP — AITP Laboratory is local-first. Bind only to loopback.")
    workspace=Path(args.workspace).resolve(); workspace.mkdir(parents=True,exist_ok=True); server=LabServer((args.host,args.port),LabHandler,workspace); port=server.server_address[1]; url=f"http://127.0.0.1:{port}/"
    print("WAIT — AITP LABORATORY"); print("Local-first · no telemetry · loopback only · guided Laboratory scope: DRY_RUN"); print(f"Workspace: {workspace}"); print(f"Open: {url}"); print("PASS — laboratory ready. Press Ctrl+C to stop; the terminal remains open.")
    if not args.no_browser: threading.Timer(0.35,lambda:webbrowser.open(url)).start()
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close(); print("PASS — laboratory stopped cleanly")

if __name__=="__main__": main()
