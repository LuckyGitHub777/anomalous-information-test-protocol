# Contributing

AITP is publicly inspectable but not open-source licensed in this release candidate.

## Feedback

Bug reports, protocol defects, reproducibility concerns, accessibility defects, security reports, and methodological critique are welcome once the public issue process is enabled.

## Code contributions

Do not submit external code/documentation contributions unless the repository owner explicitly opens a contribution program and publishes the corresponding contribution-rights/license terms. Public source visibility alone grants no contribution or reuse rights.

## Authorized development

Run:

```bash
python tools/vv_all.py
```

Then run rendered browser UAT using the release procedure in `docs/QUICKSTART.md` / `docs/HOSTED_UAT_CHECKLIST.md`.

Protocol changes that affect evidence identity or inference require explicit versioning, claims review, adversarial regression coverage, and V&V evidence.
