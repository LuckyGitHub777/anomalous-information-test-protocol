# GitHub Actions / Browser-UAT Pins

The workflows use exact full commit SHAs for external GitHub Actions.

| Component | Release label | Frozen reference |
|---|---|---|
| `actions/checkout` | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `actions/setup-python` | v7.1.0 | `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` |
| `github/codeql-action` | v4.39.1 | `9b3254085494b55a0f7c4c2b3d2d52cc712ce370` |
| `actions/configure-pages` | v6.0.0 | `45bfe0192ca1faeb007ade9deae92b16b8254a0d` |
| `actions/upload-pages-artifact` | v5.0.0 | `fc324d3547104276b827a68afc52ff2a11cc49c9` |
| `actions/deploy-pages` | v5.0.1 | `368f82528645a54fb793d4d04e342629a3f51346` |

Rendered Browser UAT uses `playwright==1.62.1` as a pinned **development-only Python dependency** and installs its Chromium build on the hosted runner. AITP runtime remains standard-library Python with self-contained browser assets.

Pins should be re-verified against official upstream releases before a later release rather than silently floated.
