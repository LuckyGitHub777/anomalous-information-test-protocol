# Public Web Experience

The `site/` directory is a static, synthetic, zero-telemetry educational experience designed for GitHub Pages or another static host.

## Local preview

```bash
python run_site.py
```

Windows: double-click `AITP_WEB.cmd`.

## Public demo boundary

The demo:

- uses synthetic targets;
- creates browser-local fingerprints;
- sends no data to a server;
- does not create trusted external chronology;
- is not research-grade evidence.

## Prediction demo

The public Prediction Ledger demo computes the same **AITP-PRED-1.1 canonical content fingerprint** used by the local Laboratory. It remains synthetic/browser-local; the local Laboratory is the place where a frozen record can later receive an append-only adjudication record.

## Security boundary

The public HTML contains a CSP meta policy for directives supported through meta and has no external executable/style/font/media dependencies or telemetry.

`run_site.py` additionally emits local preview response headers. Those local headers are **not evidence that a static production host emits the same headers**. Production claims must be based on deployed readback.

## GitHub Pages

`.github/workflows/pages.yml` deploys `site/` only when the repository is public. Configure Pages deployment to **GitHub Actions** and verify the deployed result using `docs/HOSTED_UAT_CHECKLIST.md`.

Never place real participant data, private target packets, or live study evidence in `site/`.
