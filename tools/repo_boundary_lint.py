#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

p = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True)
if p.returncode == 0:
    tracked = [x.strip() for x in p.stdout.splitlines() if x.strip()]
else:
    tracked = []
    skip = {"work", "private", "sessions", "raw-data", "participant-data", "release", "__pycache__", ".git"}
    for x in ROOT.rglob("*"):
        if not x.is_file():
            continue
        rel = x.relative_to(ROOT)
        if any(part in skip for part in rel.parts) or x.suffix == ".pyc":
            continue
        tracked.append(str(rel).replace("\\", "/"))

for path in tracked:
    parts = Path(path).parts
    if any(x in {"work", "private", "sessions", "raw-data", "participant-data", "release", "__pycache__"} for x in parts):
        errors.append(f"forbidden tracked/generated path: {path}")
    if Path(path).name.startswith("PRIVATE_"):
        errors.append(f"private reveal-like file tracked: {path}")

sha_ref = re.compile(r"^[0-9a-f]{40}$")
for wf in sorted((ROOT / ".github" / "workflows").glob("*.y*ml")):
    text = wf.read_text(encoding="utf-8")
    if "pull_request_target:" in text:
        errors.append(f"unsafe trigger present: {wf.relative_to(ROOT)}")
    for line_no, line in enumerate(text.splitlines(), 1):
        m = re.search(r"\buses:\s*([^\s@]+)@([^\s#]+)", line)
        if not m:
            continue
        action, ref = m.groups()
        if action.startswith("./"):
            continue
        if not sha_ref.match(ref):
            errors.append(f"un-pinned action {wf.relative_to(ROOT)}:{line_no}: {action}@{ref}")

codeql = ROOT / ".github" / "workflows" / "codeql.yml"
if codeql.exists():
    text=codeql.read_text(encoding="utf-8")
    if "github.event.repository.private == false" not in text:
        errors.append("CodeQL workflow lacks public-repository activation guard")

# Distinctive private-origin terms used in the v1.0 independent leakage probe must remain absent
# from the public repository, including explanatory prose. This keeps the empirical public tree
# free of origin-specific lineage markers rather than merely excluding private files.
private_origin_terms = [
    "Creative" + " Psionics",
    "spiritual" + " discernment",
    "PRIVATE_" + "LINEAGE",
    "metaph" + "ysical",
    "claimant" + "-specific",
]
text_exts={".md",".txt",".py",".js",".html",".css",".json",".yml",".yaml",".toml",".csv"}
for path in tracked:
    fp=ROOT/path
    if not fp.is_file() or fp.suffix.lower() not in text_exts:
        continue
    text=fp.read_text(encoding="utf-8", errors="ignore")
    for term in private_origin_terms:
        if term.lower() in text.lower():
            errors.append(f"private-origin marker present in public tree: {path}: {term}")


# Browser UI must remain self-contained: external navigation links are allowed,
# but remote executable/style/font/media dependencies and network telemetry are not.
ui_files = [
    ROOT / "web" / "index.html", ROOT / "web" / "app.js", ROOT / "web" / "app.css",
    ROOT / "site" / "index.html", ROOT / "site" / "app.js", ROOT / "site" / "styles.css",
]
remote_dependency_patterns = [
    re.compile(r"<(?:script|img|iframe)[^>]+src=[\"']https?://", re.I),
    re.compile(r"<link[^>]+href=[\"']https?://", re.I),
    re.compile(r"@import\s+(?:url\()?['\"]?https?://", re.I),
    re.compile(r"url\(\s*['\"]?https?://", re.I),
    re.compile(r"\b(?:fetch|sendBeacon)\s*\(\s*['\"]https?://", re.I),
    re.compile(r"\b(?:WebSocket|EventSource)\s*\(\s*['\"](?:wss?|https?)://", re.I),
]
for ui_file in ui_files:
    if ui_file.exists():
        text = ui_file.read_text(encoding="utf-8")
        if any(pattern.search(text) for pattern in remote_dependency_patterns):
            errors.append(f"remote dependency/network call in UI asset: {ui_file.relative_to(ROOT)}")

if errors:
    print("FAIL — repository boundary lint")
    print("\n".join(errors))
    raise SystemExit(1)
print(f"PASS — repository boundary lint ({len(tracked)} tracked/candidate files checked)")
