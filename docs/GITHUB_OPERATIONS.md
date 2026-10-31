# GitHub Operations — v1.1.0-rc4

AITP v1.1.0-rc4 is a public-release candidate with a static GitHub Pages experience and a local-first research Laboratory.

## Candidate workflow

1. Push the **exact locally validated candidate** to a bounded branch/PR or initial public `main` only when authorized.
2. Require the hosted CI matrix and Browser UAT workflows to pass on the exact commit.
3. Review CodeQL results when available/applicable.
4. Deploy Pages from GitHub Actions using `site/` only.
5. Read back the deployed Pages URL while logged out at desktop/mobile widths.
6. Perform explicit Human Authority claims/UAT sign-off.
7. Freeze/tag only the exact commit that passed every applicable gate.

Do not modify the release candidate after UAT and still call the earlier evidence controlling.

## Continuous integration

CI runs:

- Python compilation;
- 26+ unit/API/end-to-end regression tests;
- bounded overclaim tripwire;
- adversarial release-blocker regressions;
- repository-boundary lint;
- secret-pattern lint;
- public/Laboratory UX structure lint;
- JavaScript syntax;
- deterministic release construction.

## Browser UAT

`.github/workflows/browser-uat.yml` installs a pinned Playwright development dependency and Chromium, then executes `tools/browser_uat.py`.

The browser suite measures the defects that static lint previously missed, including:

- 320/390 horizontal overflow;
- mobile navigation reachability;
- keyboard focus retention after candidate reorder;
- live reorder announcement;
- visible Laboratory focus;
- invalid-state semantics;
- reduced motion;
- routing/history recovery;
- canonical public/local prediction fingerprint identity.

## CodeQL

CodeQL runs only when the repository is public. Do not describe CodeQL as passed until GitHub-hosted execution has actually completed and findings are reviewed.

## GitHub Pages

The Pages workflow deploys `site/` only. The public site must never receive real participant responses, live target/reveal packets, credentials, or study evidence.

The HTML CSP meta policy is a static-host fallback for directives browsers permit through meta. Controls requiring HTTP response headers must be evaluated against the actual deployed service rather than inferred from `run_site.py`.

## Evidence classes

- **Local deterministic build:** source/release reproducibility.
- **Local rendered UAT:** browser behavior against the exact source.
- **GitHub CI/Browser UAT:** hosted runner behavior on the exact commit.
- **Pages readback:** actual deployed public behavior.
- **Human claims/UAT sign-off:** final judgment gate not replaceable by automation.

Keep these evidence classes separate.
