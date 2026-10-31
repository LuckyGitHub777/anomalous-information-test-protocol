#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'; LAB=ROOT/'web'; errors=[]
for folder,names in [(SITE,['index.html','styles.css','app.js','favicon.svg']),(LAB,['index.html','app.css','app.js'])]:
    for name in names:
        if not (folder/name).is_file(): errors.append(f'missing UI asset: {folder.name}/{name}')
site_html=(SITE/'index.html').read_text(encoding='utf-8'); site_js=(SITE/'app.js').read_text(encoding='utf-8'); site_css=(SITE/'styles.css').read_text(encoding='utf-8')
lab_html=(LAB/'index.html').read_text(encoding='utf-8'); lab_js=(LAB/'app.js').read_text(encoding='utf-8'); lab_css=(LAB/'app.css').read_text(encoding='utf-8')
for marker in ['Test the claim.','A single demonstration is not evidence','Synthetic public demo','Prediction Ledger demo','Run AITP locally']:
    if marker not in site_html: errors.append(f'missing public UX marker: {marker}')
for bad in ['google-analytics','googletagmanager','segment.com','mixpanel','hotjar','fonts.googleapis.com']:
    if bad in (site_html+site_js+site_css+lab_html+lab_js+lab_css).lower(): errors.append(f'external/telemetry dependency present: {bad}')
for pattern in [r'fetch\s*\(\s*["\']https?://',r'XMLHttpRequest',r'WebSocket\s*\(\s*["\'](?:wss?|https?)://',r'sendBeacon\s*\(']:
    if re.search(pattern,site_js,re.I): errors.append(f'public external network-capable API present: {pattern}')
for attr in re.findall(r'(?:src|href)=["\']([^"\']+)',site_html):
    if attr.startswith(('http://','https://','//')): errors.append(f'external asset/link hardcoded in public site: {attr}')
if 'http-equiv="Content-Security-Policy"' not in site_html: errors.append('public production-relevant CSP meta missing')
if "connect-src 'none'" not in site_html: errors.append('public CSP must disable connect-src')
for name,css in [('public',site_css),('laboratory',lab_css)]:
    if 'prefers-reduced-motion' not in css: errors.append(f'{name}: reduced-motion support missing')
    if ':focus-visible' not in css: errors.append(f'{name}: visible focus styling missing')
for name,html in [('public',site_html),('laboratory',lab_html)]:
    if 'aria-live' not in html: errors.append(f'{name}: aria-live status region missing')
    if 'role="alert"' not in html: errors.append(f'{name}: persistent alert region missing')
if re.search(r'@media\(max-width:1000px\)[^{]*\{[^}]*\.bar nav\s*\{[^}]*display\s*:\s*none',site_css,re.S): errors.append('public mobile nav is hidden')
compact=re.sub(r'\s+','',site_css)
if not re.search(r'@media\(max-width:650px\)\{.*?\.inspect-grid[^}]*grid-template-columns:minmax\(0,1fr\)',compact,re.S): errors.append('public narrow reflow rule for inspect-grid missing')
if 'DRY_RUN">Dry run</option>' not in lab_html or 'value="BASELINE"' in lab_html: errors.append('Laboratory must expose DRY_RUN only in v1.1')
if 'innerHTML=\'\';' in site_js and 'requestAnimationFrame' not in site_js: errors.append('public reorder appears to rebuild without focus restoration')
if 'requestAnimationFrame' not in lab_js or 'ranking-live' not in lab_html: errors.append('laboratory reorder focus/live announcement support missing')
for marker in ['confirm-response-seal','confirm-judgment-seal','confirm-prediction-freeze']:
    if marker not in lab_html: errors.append(f'laboratory irreversible-action confirmation missing: {marker}')
if 'name="confirm"' not in lab_js: errors.append('prediction adjudication confirmation missing')
if errors:
    print('FAIL — UI/site lint'); print('\n'.join(errors)); raise SystemExit(1)
print('PASS — UI/site lint (public + Laboratory)')
