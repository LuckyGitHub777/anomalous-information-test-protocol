#!/usr/bin/env python3
from __future__ import annotations
import os, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; checks=[]
def run(name,cmd):
    env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,env=env); checks.append((name,p.returncode,p.stdout,p.stderr))
run('compile',[sys.executable,'-m','compileall','-q','src','tests','tools','run_aitp.py','run_lab.py','run_site.py'])
run('tests',[sys.executable,'-m','unittest','discover','-s','tests','-v'])
run('overclaim-tripwire',[sys.executable,'tools/overclaim_tripwire.py'])
run('adversarial-regressions',[sys.executable,'tools/adversarial_vv.py'])
run('repo-boundary',[sys.executable,'tools/repo_boundary_lint.py'])
run('secret-patterns',[sys.executable,'tools/secret_lint.py'])
run('ui-site',[sys.executable,'tools/site_lint.py'])
if shutil.which('node'):
    run('site-js-syntax',['node','--check','site/app.js']); run('lab-js-syntax',['node','--check','web/app.js'])
run('release',[sys.executable,'tools/release_build.py'])
failed=[x for x in checks if x[1]!=0]
for name,code,out,err in checks:
    print(f"{'PASS' if code==0 else 'FAIL'} — {name}")
    if out.strip(): print(out.strip())
    if err.strip(): print(err.strip())
if failed: raise SystemExit(1)
print('PASS — ALL LOCAL NON-BROWSER V&V CHECKS')
print('NEXT — run: python tools/browser_uat.py (requires Playwright; browser UAT is a separate release gate).')
