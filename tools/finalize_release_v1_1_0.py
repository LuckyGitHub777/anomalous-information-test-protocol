#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, pathlib, shutil, subprocess, sys, tempfile, time

REPO = os.environ["GITHUB_REPOSITORY"]
SHA = os.environ["GITHUB_SHA"]
TAG = "v1.1.0"
OWNER = "LuckyGitHub777"
ASSET_NAME = "anomalous-information-test-protocol-v1.1.0.zip"
REQUIRED = {
    "test (ubuntu-latest, 3.11)",
    "test (ubuntu-latest, 3.13)",
    "test (ubuntu-latest, 3.14)",
    "test (windows-latest, 3.11)",
    "test (windows-latest, 3.13)",
    "test (windows-latest, 3.14)",
    "chromium",
    "analyze",
    "deploy",
}

def run(*args: str, check: bool = True, capture: bool = False, env=None):
    print("+", " ".join(args), flush=True)
    return subprocess.run(args, check=check, text=True,
                          capture_output=capture, env=env)

def out(*args: str) -> str:
    return run(*args, capture=True).stdout.strip()

def gh_json(path: str):
    return json.loads(out("gh", "api", path))

def resolve_tag_target() -> str | None:
    p = run("gh", "api", f"repos/{REPO}/git/ref/tags/{TAG}",
            check=False, capture=True)
    if p.returncode != 0:
        return None
    ref = json.loads(p.stdout)
    obj = ref["object"]
    if obj["type"] == "tag":
        tag = gh_json(f"repos/{REPO}/git/tags/{obj['sha']}")
        return tag["object"]["sha"]
    return obj["sha"]

def wait_for_checks(timeout_seconds: int = 900) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        data = gh_json(f"repos/{REPO}/commits/{SHA}/check-runs?per_page=100")
        seen = {}
        for item in data.get("check_runs", []):
            name = item.get("name")
            if name in REQUIRED:
                seen[name] = (item.get("status"), item.get("conclusion"))
        missing = REQUIRED - set(seen)
        bad = {k: v for k, v in seen.items()
               if v[0] == "completed" and v[1] not in ("success", None)}
        if bad:
            raise SystemExit(f"SAFE STOP — hosted gate failed: {bad}")
        if not missing and all(status == "completed" and conclusion == "success"
                               for status, conclusion in seen.values()):
            print("PASS — exact release commit has green CI / Browser UAT / CodeQL / Pages")
            return
        print("Waiting for hosted gates:",
              "missing=", sorted(missing),
              "pending=", sorted(k for k,v in seen.items() if v[0] != "completed"),
              flush=True)
        time.sleep(10)
    raise SystemExit("SAFE STOP — timed out waiting for hosted gates")

def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> None:
    if REPO != f"{OWNER}/anomalous-information-test-protocol":
        raise SystemExit(f"SAFE STOP — unexpected repository: {REPO}")
    if out("git", "rev-parse", "HEAD") != SHA:
        raise SystemExit("SAFE STOP — checkout SHA does not match GITHUB_SHA")

    existing = resolve_tag_target()
    if existing is not None and existing != SHA:
        print(f"v1.1.0 already exists at {existing}; this workflow is inert on later commits.")
        return

    wait_for_checks()

    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    run(sys.executable, "tools/vv_all.py", env=env)

    release = pathlib.Path("release")
    asset = release / ASSET_NAME
    run(sys.executable, "tools/release_build.py")
    first = sha256(asset)
    asset.unlink()
    manifest = release / "RELEASE_MANIFEST.json"
    if manifest.exists():
        manifest.unlink()
    run(sys.executable, "tools/release_build.py")
    second = sha256(asset)
    if first != second:
        raise SystemExit(f"SAFE STOP — nondeterministic release: {first} != {second}")
    checksum = asset.with_suffix(asset.suffix + ".sha256")
    checksum.write_text(f"{second}  {ASSET_NAME}\n", encoding="utf-8")
    print(f"PASS — deterministic release SHA-256 {second}")

    if existing is None:
        run("git", "config", "user.name", OWNER)
        run("git", "config", "user.email", "71360116+LuckyGitHub777@users.noreply.github.com")
        run("git", "tag", "-a", TAG, SHA, "-m", "AITP v1.1.0 — First Public Release")
        run("git", "push", "origin", f"refs/tags/{TAG}")
        existing = resolve_tag_target()
    if existing != SHA:
        raise SystemExit(f"SAFE STOP — tag resolves to {existing}, expected {SHA}")
    print(f"PASS — annotated {TAG} resolves to exact release commit {SHA}")

    notes = f"""AITP v1.1.0 is the first stable public release of the Anomalous Information Test Protocol.

Verified commit: {SHA}

What this release delivers:
- a calm public educational experience with a synthetic hidden-target demonstration;
- a local-first Laboratory for dry-run protocol validation;
- Prediction Ledger freeze + append-only adjudication;
- tamper-evident evidence, fail-closed audit, exact scoring, and condition comparison;
- a worked example plus machine-readable citation metadata;
- public stewardship attribution for LuckyGitHub777.

Release gates:
- 27/27 Python tests plus adversarial, repository-boundary, secret, UX, and deterministic-build gates;
- GitHub CI on Ubuntu and Windows / Python 3.11, 3.13, and 3.14;
- rendered and live-HTTP Chromium Browser UAT;
- CodeQL;
- GitHub Pages deployment with production readback.

Scientific boundary: software V&V validates properties of the instrument. It does not establish anomalous information acquisition, an independent agent, or a specific source ontology.
"""
    notes_file = pathlib.Path(tempfile.gettempdir()) / "aitp-v1.1.0-release-notes.md"
    notes_file.write_text(notes, encoding="utf-8")

    view = run("gh", "release", "view", TAG, "-R", REPO,
               check=False, capture=True)
    if view.returncode == 0:
        run("gh", "release", "upload", TAG,
            f"{asset}#AITP v1.1.0 repository ZIP",
            f"{checksum}#SHA-256", "-R", REPO, "--clobber")
    else:
        run("gh", "release", "create", TAG,
            f"{asset}#AITP v1.1.0 repository ZIP",
            f"{checksum}#SHA-256",
            "-R", REPO, "--verify-tag", "--latest",
            "--title", "AITP v1.1.0 — First Public Release",
            "--notes-file", str(notes_file))

    with tempfile.TemporaryDirectory(prefix="aitp-release-readback-") as td:
        run("gh", "release", "download", TAG, "-R", REPO, "-D", td,
            "-p", ASSET_NAME)
        downloaded = pathlib.Path(td) / ASSET_NAME
        got = sha256(downloaded)
        if got != second:
            raise SystemExit(f"SAFE STOP — published asset hash {got} != {second}")
    print(f"PASS — published release asset readback matches {second}")

    for branch in (
        "verify/rc4-hosted-gates",
        "verify/rc5-hosted-gates",
        "release/v1.1.0",
        "ops/finalize-v1.1.0",
        "ux/luxury-finalization",
    ):
        run("git", "push", "origin", "--delete", branch, check=False)

    print("PASS — v1.1.0 immutable release complete")
    print("RELEASE_ZIP_SHA256=" + second)

if __name__ == "__main__":
    main()
