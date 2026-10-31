# Quickstart

## Requirements

- Python 3.11+ for the local toolkit.
- No third-party runtime package is required for the core, public preview, or Laboratory.

## 1. Verify the repository

```bash
python tools/vv_all.py
```

This runs compile/tests/adversarial/security/UX-structure/release checks. It deliberately does not pretend to replace rendered browser UAT.

## 2. Public educational experience

```bash
python run_site.py
```

Open the loopback URL printed by the launcher.

## 3. Local Laboratory

```bash
python run_lab.py
```

The guided v1.1 Laboratory supports **DRY_RUN** only.

## 4. Formal expert/core workflow

Use the CLI for formal anchored work:

```bash
python run_aitp.py --help
```

The formal workflow includes exporting the anchor artifact and separately recording the reviewed anchor-evidence receipt. Read `docs/ANCHOR_EVIDENCE.md` before using formal eligibility language.

## 5. Rendered browser UAT for release engineering

Playwright is a **development/release dependency only**:

```bash
python -m pip install playwright==1.64.1
python -m playwright install chromium
python tools/browser_uat.py --chromium __playwright_managed__
```

The GitHub `Browser UAT` workflow performs the same rendered gate on hosted runners.
