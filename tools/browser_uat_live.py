#!/usr/bin/env python3
"""Hosted/live HTTP browser UAT. Intended for GitHub runners or another environment that permits browser access to loopback."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'src'))

from run_site import Handler as PublicHandler
from aitp.prediction import prediction_content_sha256
from aitp.webapp import LabHandler, LabServer


def require(value,msg):
    if not value: raise AssertionError(msg)
    print('PASS — '+msg)


def start(server):
    t=threading.Thread(target=server.serve_forever,daemon=True); t.start(); return t


def fill_public(page):
    page.locator('#demo-start').click(); page.locator('#demo-response').fill('Tall red structure near water'); page.locator('#seal-response').click(); page.wait_for_selector('#candidate-list .candidate'); btn=page.locator('#candidate-list [data-dir="down"]').first; cid=btn.get_attribute('data-id'); btn.focus(); btn.press('Enter'); page.wait_for_timeout(80); require(page.evaluate('document.activeElement && document.activeElement.getAttribute("data-id")')==cid,'live public reorder retains focus'); page.locator('#lock-ranking').click(); require(page.locator('.meaning strong').is_visible(),'live public reveal retains interpretation boundary')


def run(browser):
    with tempfile.TemporaryDirectory() as td:
        pub=ThreadingHTTPServer(('127.0.0.1',0),PublicHandler); start(pub); pub_url=f'http://127.0.0.1:{pub.server_address[1]}/'
        lab=LabServer(('127.0.0.1',0),LabHandler,Path(td)); start(lab); lab_url=f'http://127.0.0.1:{lab.server_address[1]}/'
        try:
            # Public actual HTTP/static server.
            ctx=browser.new_context(viewport={'width':390,'height':844}); page=ctx.new_page(); resp=page.goto(pub_url,wait_until='domcontentloaded'); require(resp and resp.status==200,'live public HTTP 200'); require("connect-src 'none'" in (resp.headers.get('content-security-policy') or ''),'live preview response CSP is present'); require(page.evaluate('document.documentElement.scrollWidth')<=390,'live public 390px reflow'); require(page.locator('header.bar nav').is_visible(),'live public mobile navigation visible'); ctx.close()
            ctx=browser.new_context(viewport={'width':1440,'height':900}); page=ctx.new_page(); page.goto(pub_url,wait_until='domcontentloaded'); fill_public(page)
            page.locator('#pred-wording').fill('X will occur'); page.locator('#pred-event').fill('X'); page.locator('#pred-window').fill('2027'); page.locator('#pred-source').fill('Source A'); page.locator('#pred-success').fill('X occurs'); page.locator('#pred-failure').fill('X does not occur'); page.locator('#prediction-form button[type="submit"]').click(); got=page.locator('#prediction-output code').text_content().strip(); expected=prediction_content_sha256({'exact_wording':'X will occur','target_event':'X','time_window':'2027','source':'Source A','success_condition':'X occurs','failure_condition':'X does not occur','probability_language':'','conditional_language':''}); require(got==expected,'live public canonical prediction hash matches Python core'); ctx.close()

            # Laboratory actual HTTP + actual API/core.
            ctx=browser.new_context(viewport={'width':1440,'height':900}); page=ctx.new_page(); resp=page.goto(lab_url,wait_until='domcontentloaded'); require(resp and resp.status==200,'live Laboratory HTTP 200'); require("connect-src 'self'" in (resp.headers.get('content-security-policy') or ''),'live Laboratory CSP is present')
            page.locator('[data-route="lab"]').click(); require(page.locator('#trial-condition option').count()==1 and page.locator('#trial-condition').input_value()=='DRY_RUN','live Laboratory exposes DRY_RUN only'); page.locator('#create-trial').click(); page.locator('#response-text').fill('Tall red structure near water'); page.locator('#seal-response').click(); require(page.locator('#alert').is_visible(),'Laboratory requires confirmation before irreversible response seal'); page.locator('#confirm-response-seal').check(); page.locator('#seal-response').click(); page.wait_for_selector('#candidate-list .candidate'); btn=page.locator('#candidate-list [data-dir="down"]').first; cid=btn.get_attribute('data-id'); btn.focus(); btn.press('Enter'); page.wait_for_timeout(80); require(page.evaluate('document.activeElement && document.activeElement.getAttribute("data-id")')==cid,'live Laboratory reorder retains focus'); page.locator('#confirm-judgment-seal').check(); page.locator('#seal-judgment').click(); page.wait_for_timeout(120); require(page.locator('#result-badge').text_content()=='VALID','live Laboratory dry run reaches VALID')
            page.locator('[data-route="ledger"]').click(); page.locator('#pred-wording').fill('X will occur'); page.locator('#pred-success').fill('X occurs'); page.locator('#pred-failure').fill('X does not occur'); page.locator('#prediction-form button[type="submit"]').click(); require(page.locator('#alert').is_visible(),'Laboratory requires confirmation before prediction freeze'); page.locator('#confirm-prediction-freeze').check(); page.locator('#prediction-form button[type="submit"]').click(); page.wait_for_timeout(100); page.locator('.resolution-form textarea[name="summary"]').fill('Evidence was mixed'); page.locator('.resolution-form select[name="disposition"]').select_option('AMBIGUOUS'); page.locator('.resolution-form button[type="submit"]').click(); require(page.locator('#alert').is_visible(),'Laboratory requires confirmation before append-only adjudication'); page.locator('.resolution-form input[name="confirm"]').check(); page.locator('.resolution-form button[type="submit"]').click(); page.wait_for_timeout(120); require(page.locator('.prediction-status strong').text_content().startswith('ADJUDICATED'),'live Laboratory prediction adjudication completes')
            # Actual API negative paths from browser context.
            api=ctx.request
            r=api.post(lab_url+'api/trials',headers={'X-AITP-Request':'1','Content-Type':'application/json'},data={'condition':'BASELINE','candidate_count':4}); require(r.status==400,'live API rejects unsupported formal guided condition')
            r=api.get(lab_url+'api/typo'); require(r.status==404,'live API unknown GET is 404')
            ctx.close()
        finally:
            pub.shutdown(); pub.server_close(); lab.shutdown(); lab.server_close()


def main():
    try: from playwright.sync_api import sync_playwright
    except ImportError: raise SystemExit('STOP — Playwright required')
    ap=argparse.ArgumentParser(); ap.add_argument('--chromium',default='__playwright_managed__'); args=ap.parse_args()
    with sync_playwright() as p:
        kwargs={'headless':True,'args':['--no-sandbox']}; cp=Path(args.chromium)
        if cp.exists(): kwargs['executable_path']=str(cp)
        browser=p.chromium.launch(**kwargs); run(browser); browser.close()
    print('PASS — LIVE HTTP BROWSER UAT')

if __name__=='__main__': main()
