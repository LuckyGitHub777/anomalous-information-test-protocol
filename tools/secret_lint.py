#!/usr/bin/env python3
from __future__ import annotations
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

p = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True)
if p.returncode == 0:
    files = [ROOT / x.strip() for x in p.stdout.splitlines() if x.strip()]
else:
    skip = {".git","release","work","private","sessions","raw-data","participant-data","__pycache__"}
    files = [x for x in ROOT.rglob("*") if x.is_file() and not any(part in skip for part in x.relative_to(ROOT).parts)]

forbidden_names = {".env","id_rsa","id_ed25519","credentials.json","secrets.json"}
for pth in files:
    rel = pth.relative_to(ROOT).as_posix()
    if pth.name in forbidden_names or pth.suffix.lower() in {".p12",".pfx"}:
        errors.append(f"suspicious secret-bearing filename: {rel}")

patterns = [
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b")),
    ("github-fine-grained-token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("openai-like-key", re.compile(r"\bsk-[A-Za-z0-9_-]{24,}\b")),
]

for pth in files:
    if pth.name == "secret_lint.py":
        continue
    try:
        text = pth.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    for label, pattern in patterns:
        if pattern.search(text):
            errors.append(f"{label} pattern detected: {pth.relative_to(ROOT).as_posix()}")

if errors:
    print("FAIL — secret-pattern lint")
    print("\n".join(sorted(set(errors))))
    raise SystemExit(1)
print(f"PASS — secret-pattern lint ({len(files)} files checked)")
