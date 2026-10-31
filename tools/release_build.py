#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'release'
EXCLUDE_TOP={'.git','release','work','private','sessions','raw-data','participant-data'};EXCLUDE_NAMES={'__pycache__','.DS_Store'}
FIXED_TIME=(2026,10,31,0,0,0);ARTIFACT='anomalous-information-test-protocol-v1.1.0-rc4.zip'
def included_files():
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(ROOT)
        if rel.parts[0] in EXCLUDE_TOP:continue
        if any(part in EXCLUDE_NAMES for part in rel.parts):continue
        if p.suffix in {'.pyc','.zip'}:continue
        yield p,rel
def main():
    OUT.mkdir(exist_ok=True);zip_path=OUT/ARTIFACT;manifest=[]
    with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
        for p,rel in included_files():
            data=p.read_bytes();manifest.append({'path':rel.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()});info=zipfile.ZipInfo(rel.as_posix(),FIXED_TIME);info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;zf.writestr(info,data)
    zip_sha=hashlib.sha256(zip_path.read_bytes()).hexdigest();out={'artifact':zip_path.name,'artifact_sha256':zip_sha,'files':manifest};(OUT/'RELEASE_MANIFEST.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(f'PASS — deterministic release built: {zip_path}');print(f'SHA-256: {zip_sha}')
if __name__=='__main__':main()
