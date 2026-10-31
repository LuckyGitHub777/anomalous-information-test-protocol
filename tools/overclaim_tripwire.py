#!/usr/bin/env python3
from __future__ import annotations
import re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXACT=["proves psychic ability","proves telepathy","proves channeling","proves extraterrestrial contact","proves nonhuman intelligence","proves interdimensional communication","proves remote viewing","proves supernatural"]
ASSERT=re.compile(r"\b(proves?|proven|demonstrates?|confirms?|establishes?|validates?|definitive|conclusive(?:ly)?|beyond (?:any )?(?:reasonable )?doubt)\b",re.I)
CLAIM=re.compile(r"\b(telepath\w*|psychic|paranormal|supernatural|nonhuman|extraterrestrial|interdimensional|channel(?:ing|led)?|remote viewing|anomalous information transfer)\b",re.I)
HEDGE=re.compile(r"\b(may|might|could|suggests?|consistent with|does not establish|is not evidence|cannot determine|does not prove|unestablished|hypothesis)\b",re.I)

def scan_text(text:str)->list[str]:
    findings=[]; low=text.lower()
    for phrase in EXACT:
        if phrase in low: findings.append(f"literal overclaim phrase: {phrase}")
    for sentence in re.split(r"(?<=[.!?])\s+|\n+",text):
        if ASSERT.search(sentence) and CLAIM.search(sentence) and not HEDGE.search(sentence): findings.append(f"assertive extraordinary-claim language: {sentence.strip()[:180]}")
    return findings

def candidate_paths():
    p=subprocess.run(["git","ls-files"],cwd=ROOT,text=True,capture_output=True)
    if p.returncode==0: return [ROOT/x for x in p.stdout.splitlines() if x]
    skip={".git","release","work","private","sessions","raw-data","participant-data","__pycache__"}
    return [x for x in ROOT.rglob('*') if x.is_file() and not any(part in skip for part in x.relative_to(ROOT).parts)]

def main():
    errors=[]
    for path in candidate_paths():
        if path.name==Path(__file__).name or path.name=='adversarial_vv.py' or 'tests' in path.relative_to(ROOT).parts: continue
        try:text=path.read_text(encoding='utf-8')
        except (UnicodeDecodeError,OSError):continue
        errors.extend(f"{path.relative_to(ROOT)}: {x}" for x in scan_text(text))
    if errors:
        print('FAIL — overclaim tripwire'); print('\n'.join(sorted(set(errors)))); print('HUMAN REVIEW REQUIRED — this tripwire is not semantic scientific review.'); raise SystemExit(1)
    print(f'PASS — overclaim tripwire ({len(EXACT)} literal phrases + assertive-language heuristic; NOT a substitute for human claims review)')

if __name__=='__main__': main()
