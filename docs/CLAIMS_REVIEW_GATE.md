# Claims Review Gate

## Principle

A machine can detect some dangerous wording patterns. It cannot replace scientific/editorial judgment.

`tools/overclaim_tripwire.py` is intentionally a **tripwire**, not semantic claim validation.

## Automated tripwire

The automated check flags:

- a bounded list of literal prohibited overclaim phrases;
- assertive extraordinary-claim language that combines strong certainty verbs with extraordinary-source/mechanism terms without an explicit hedge/boundary.

A PASS means only:

> **No configured tripwire pattern was detected.**

It does not mean every scientific sentence is justified.

## Required Human Authority release review

Before a final public tag/release, a Human Authority should review at least:

- README;
- public website copy;
- Laboratory interpretation text;
- release notes;
- claims policy;
- V&V report;
- any reported experimental result.

Confirm:

- [ ] Software/V&V results are not represented as scientific H2/H3/H4 evidence.
- [ ] Statistical significance is not equated with mechanism/source identity.
- [ ] “Verified,” “valid,” “sealed,” and “eligible” mean exactly what the named control establishes.
- [ ] Synthetic demo results are explicitly educational/non-research evidence.
- [ ] Formal anchor language distinguishes recorded human review from tool-level third-party verification.
- [ ] No private non-empirical origin material appears as empirical evidence.
- [ ] No public statement outruns the cited/tested evidence.

## Release status

The release candidate can be technically V&V-complete while this **human sign-off remains OPEN**. A final public release/tag should not be frozen until the Human Authority signs this gate.
