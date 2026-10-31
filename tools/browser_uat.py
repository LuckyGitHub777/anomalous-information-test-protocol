#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; PUBLIC=ROOT/'site'; LAB=ROOT/'web'; SHOTS=ROOT/'work'/'uat-screenshots'
sys.path.insert(0,str(ROOT/'src'))
from aitp.prediction import prediction_content_sha256

def require(value,msg):
    if not value: raise AssertionError(msg)
    print('PASS — '+msg)

def tab_to(page, selector, limit=40):
    for _ in range(limit):
        page.keyboard.press('Tab')
        if page.evaluate('(s)=>document.activeElement===document.querySelector(s)',selector): return True
    return False

def stripped_html(root:Path):
    html=(root/'index.html').read_text(encoding='utf-8')
    html=re.sub(r'<link[^>]+(?:styles\.css|app\.css)[^>]*>','',html)
    html=re.sub(r'<script[^>]+(?:app\.js)[^>]*></script>','',html)
    html=re.sub(r'<meta\s+http-equiv="Content-Security-Policy"[^>]*>','',html)
    return html

def make_page(browser, root:Path, viewport, kind:str):
    ctx=browser.new_context(viewport=viewport,bypass_csp=True); page=ctx.new_page(); page.set_content(stripped_html(root));
    css=(root/('styles.css' if kind=='public' else 'app.css')).read_text(encoding='utf-8'); page.add_style_tag(content=css)
    js=(root/'app.js').read_text(encoding='utf-8')
    if kind=='public':
        page.expose_function('__uatSha256',lambda text:hashlib.sha256(text.encode('utf-8')).hexdigest())
        js=re.sub(r'async function sha256\(text\)\{[^\n]*\}', "async function sha256(text){return await window.__uatSha256(text);}", js, count=1)
    else:
        page.evaluate(LAB_FETCH_MOCK)
    page.add_script_tag(content=js); page.wait_for_timeout(60); return ctx,page

LAB_FETCH_MOCK=r'''() => {
  const candidates=[
    {id:'LIGHTHOUSE',label:'Red lighthouse',content:'A red lighthouse on a rocky coast.'},
    {id:'GREENHOUSE',label:'Glass greenhouse',content:'A glass greenhouse filled with plants.'},
    {id:'BRIDGE',label:'Snowy bridge',content:'A stone bridge over a snowy river.'},
    {id:'BALLOON',label:'Yellow balloon',content:'A hot-air balloon over farmland.'}
  ];
  const db={preds:{},resolved:{}};
  const response=(body,status=200)=>({ok:status>=200&&status<300,status,json:async()=>body});
  window.fetch=async (path,opts={})=>{
    const method=(opts.method||'GET').toUpperCase();
    if(path==='/api/trials'&&method==='GET')return response({ok:true,trials:[]});
    if(path==='/api/trials'&&method==='POST')return response({ok:true,trial:{trial_id:'MOCK-1',label:'Browser UAT',condition:'DRY_RUN',state:'COMMITTED',candidate_count:4}},201);
    if(path.endsWith('/response')&&method==='POST')return response({ok:true,sealed:'a'.repeat(64),trial:{trial_id:'MOCK-1'}});
    if(path.endsWith('/release')&&method==='POST')return response({ok:true,trial:{trial_id:'MOCK-1'}});
    if(path.endsWith('/candidates')&&method==='GET')return response({ok:true,trial_id:'MOCK-1',candidates});
    if(path.endsWith('/judgment')&&method==='POST')return response({ok:true,sealed:'b'.repeat(64),trial:{trial_id:'MOCK-1'}});
    if(path.endsWith('/reveal')&&method==='POST')return response({ok:true,audit:{protocol_status:'VALID'},trial:{trial_id:'MOCK-1'}});
    if(path.endsWith('/result')&&method==='GET')return response({ok:true,audit:{protocol_status:'VALID',commitment_verified:true,candidate_packet_verified:true,response_freeze_verified:true,judgment_freeze_verified:true,ledger_sequence_verified:true,ledger_payloads_verified:true},response:'Tall red structure near water',ranking:candidates.map(x=>x.id),true_target:candidates[0],candidates});
    if(path==='/api/predictions'&&method==='GET'){const predictions=Object.values(db.preds).map(p=>db.resolved[p.prediction_id]?{...p,status:'ADJUDICATED',resolution:db.resolved[p.prediction_id]}:p);return response({ok:true,predictions})}
    if(path==='/api/predictions'&&method==='POST'){const b=JSON.parse(opts.body||'{}'),pid='PRED-MOCK';const p={prediction_id:pid,date_time_claimed:'2026-08-13T00:00:00Z',schema_version:'AITP-PRED-1.1',...b,content_sha256:'c'.repeat(64),frozen_sha256:'d'.repeat(64),status:'FROZEN'};db.preds[pid]=p;return response({ok:true,prediction:p},201)}
    if(path.endsWith('/resolve')&&method==='POST'){const b=JSON.parse(opts.body||'{}'),pid=path.split('/').slice(-2)[0];const r={prediction_id:pid,disposition:b.disposition,outcome_summary:b.outcome_summary,evidence_reference:b.evidence_reference||'',resolution_sha256:'e'.repeat(64)};db.resolved[pid]=r;return response({ok:true,prediction:{...db.preds[pid],status:'ADJUDICATED',resolution:r},resolution:r},201)}
    return response({ok:false,error:'unknown endpoint'},404);
  };
}'''

def public_uat(browser):
    for width,height in [(1440,900),(720,900),(390,844),(320,800)]:
        ctx,page=make_page(browser,PUBLIC,{'width':width,'height':height},'public'); sw=page.evaluate('document.documentElement.scrollWidth'); iw=page.evaluate('innerWidth'); require(sw<=iw,f'public reflow {width}px: scrollWidth {sw} <= {iw}')
        if width==390:
            require(page.locator('header.bar nav').is_visible(),'public primary navigation remains visible at 390px'); require(page.locator('header.bar nav a').count()==5,'public mobile navigation retains all five destinations')
        ctx.close()
    ctx,page=make_page(browser,PUBLIC,{'width':1440,'height':900},'public'); SHOTS.mkdir(parents=True,exist_ok=True); page.screenshot(path=str(SHOTS/'public-home.png')); require(tab_to(page,'.skip'),'public keyboard focus starts with skip link')
    page.locator('#demo-start').click(); page.locator('#demo-response').fill('Tall red structure near water'); page.locator('#seal-response').click(); page.wait_for_selector('#candidate-list .candidate'); btn=page.locator('#candidate-list [data-dir="down"]').first; cid=btn.get_attribute('data-id'); btn.focus(); btn.press('Enter'); page.wait_for_timeout(80); active=page.evaluate('document.activeElement && document.activeElement.getAttribute("data-id")'); require(active==cid,'public candidate reorder restores keyboard focus to moved candidate'); require(bool(page.locator('#ranking-live').text_content().strip()),'public candidate reorder announces new position')
    page.locator('#lock-ranking').click(); require(page.locator('.meaning strong').is_visible(),'public reveal retains interpretation boundary'); SHOTS.mkdir(parents=True,exist_ok=True); page.screenshot(path=str(SHOTS/'public-reveal.png'))
    page.locator('#pred-wording').fill('X will occur'); page.locator('#pred-event').fill('X'); page.locator('#pred-window').fill('2027'); page.locator('#pred-source').fill('Source A'); page.locator('#pred-success').fill('X occurs'); page.locator('#pred-failure').fill('X does not occur'); page.locator('#prediction-form button[type="submit"]').click(); browser_hash=page.locator('#prediction-output code').text_content().strip(); expected=prediction_content_sha256({'exact_wording':'X will occur','target_event':'X','time_window':'2027','source':'Source A','success_condition':'X occurs','failure_condition':'X does not occur','probability_language':'','conditional_language':''}); require(browser_hash==expected,'public prediction content SHA matches Python canonical AITP-PRED-1.1 serializer')
    page.emulate_media(reduced_motion='reduce'); transition=page.locator('.button').first.evaluate('e=>getComputedStyle(e).transitionDuration'); require(transition in {'0s','0ms'},'public reduced-motion removes UI transitions'); ctx.close()

def lab_uat(browser):
    ctx,page=make_page(browser,LAB,{'width':1440,'height':900},'lab'); SHOTS.mkdir(parents=True,exist_ok=True); page.screenshot(path=str(SHOTS/'laboratory-home.png')); require(tab_to(page,'.skip'),'Laboratory keyboard focus starts with skip link'); page.locator('[data-route="lab"]').click(); page.locator('#trial-label').focus(); page.keyboard.press('Tab'); focused=page.evaluate('document.activeElement.id'); require(focused in {'trial-condition','candidate-count'},'Laboratory keyboard navigation reaches form controls'); outline=page.evaluate('getComputedStyle(document.activeElement).outlineStyle'); require(outline!='none','Laboratory focused control has visible authored outline')
    page.locator('#create-trial').click(); page.locator('#response-text').fill('Tall red structure near water'); page.locator('#seal-response').click(); require(page.locator('#alert').is_visible(),'Laboratory requires confirmation before irreversible response seal'); page.locator('#confirm-response-seal').check(); page.locator('#seal-response').click(); page.wait_for_selector('#candidate-list .candidate'); btn=page.locator('#candidate-list [data-dir="down"]').first; cid=btn.get_attribute('data-id'); btn.focus(); btn.press('Enter'); page.wait_for_timeout(80); active=page.evaluate('document.activeElement && document.activeElement.getAttribute("data-id")'); require(active==cid,'Laboratory candidate reorder restores keyboard focus'); require(bool(page.locator('#ranking-live').text_content().strip()),'Laboratory candidate reorder announces new position'); page.locator('#confirm-judgment-seal').check(); page.locator('#seal-judgment').click(); page.wait_for_timeout(100); require(page.locator('#result-badge').text_content()=='VALID','Laboratory guided dry-run reaches VALID audit in rendered UI'); SHOTS.mkdir(parents=True,exist_ok=True); page.screenshot(path=str(SHOTS/'laboratory-result.png'))
    page.evaluate("renderResult({audit:{protocol_status:'INVALID_INTEGRITY',commitment_verified:true,candidate_packet_verified:true,response_freeze_verified:true,judgment_freeze_verified:true,ledger_sequence_verified:false,ledger_payloads_verified:false},ranking:['LIGHTHOUSE'],true_target:{id:'LIGHTHOUSE',label:'Red lighthouse',content:'x'},candidates:[]})"); require('error' in page.locator('#result-badge').get_attribute('class'),'Laboratory invalid audit uses explicit error badge styling'); require('not eligible' in page.locator('#result-meaning').text_content().lower(),'Laboratory invalid audit explains analysis ineligibility')
    page.locator('[data-route="ledger"]').click(); page.locator('#pred-wording').fill('X will occur'); page.locator('#pred-success').fill('X occurs'); page.locator('#pred-failure').fill('X does not occur'); page.locator('#prediction-form button[type="submit"]').click(); require(page.locator('#alert').is_visible(),'Laboratory requires confirmation before prediction freeze'); page.locator('#confirm-prediction-freeze').check(); page.locator('#prediction-form button[type="submit"]').click(); page.wait_for_timeout(100); page.locator('.resolution-form textarea[name="summary"]').fill('Evidence was mixed'); page.locator('.resolution-form select[name="disposition"]').select_option('AMBIGUOUS'); page.locator('.resolution-form button[type="submit"]').click(); require(page.locator('#alert').is_visible(),'Laboratory requires confirmation before append-only adjudication'); page.locator('.resolution-form input[name="confirm"]').check(); page.locator('.resolution-form button[type="submit"]').click(); page.wait_for_timeout(120); require(page.locator('.prediction-status strong').text_content().startswith('ADJUDICATED'),'Laboratory Prediction Ledger completes append-only adjudication')
    # Unknown route + history.
    page.evaluate("location.hash='#Bogus'; window.dispatchEvent(new PopStateEvent('popstate'))"); require('active' in page.locator('#view-home').get_attribute('class'),'Laboratory unknown hash recovers to home instead of blank screen'); page.locator('[data-route="lab"]').click(); page.locator('[data-route="ledger"]').click(); page.go_back(); page.wait_for_timeout(60); require('active' in page.locator('#view-lab').get_attribute('class'),'Laboratory browser Back moves between views'); ctx.close()
    ctx,m=make_page(browser,LAB,{'width':390,'height':844},'lab'); require(m.evaluate('document.documentElement.scrollWidth')<=390,'Laboratory reflows at 390px'); require(m.locator('.topbar nav').is_visible(),'Laboratory primary nav remains reachable at 390px'); ctx.close()

def main():
    try: from playwright.sync_api import sync_playwright
    except ImportError: raise SystemExit('STOP — Playwright is required for browser UAT. See docs/HOSTED_UAT_CHECKLIST.md.')
    ap=argparse.ArgumentParser(); ap.add_argument('--chromium',default='/usr/bin/chromium'); args=ap.parse_args()
    with sync_playwright() as p:
        kwargs={'headless':True,'args':['--no-sandbox']};
        if Path(args.chromium).exists(): kwargs['executable_path']=args.chromium
        browser=p.chromium.launch(**kwargs); public_uat(browser); lab_uat(browser); browser.close()
    print('PASS — RENDERED BROWSER UAT (public + Laboratory)')
if __name__=='__main__': main()
