# V&V Closure Matrix — v1.1.0-rc5

This matrix traces the independent v1.0.0 findings into the corrective v1.1.0-rc5 candidate. A finding is marked **CLOSED LOCALLY** only when the corrective code/scope exists and a local regression/UAT gate exercises it. Environment-dependent production claims remain **HOSTED VERIFY** until GitHub/Pages readback.

| ID | v1.0 finding | v1.1 corrective disposition | Evidence state |
|---|---|---|---|
| H1 | `claims_lint` overstated semantic coverage | Replaced by explicitly bounded `overclaim_tripwire.py`; mandatory Human Authority claims gate added | **CLOSED LOCALLY; HUMAN SIGN-OFF OPEN** |
| H2 | self-attested/backdated anchor promoted as verified | Separate receipt/hash/chronology/evidence-class/human-review fields; no tool-level external-verification claim; backdated chronology rejected; formal anchor records ledger-bound before response | **CLOSED LOCALLY** |
| H3 | Laboratory offered formal conditions it could not complete | Guided Laboratory intentionally exposes `DRY_RUN` only; formal anchored conditions remain core/CLI workflow | **CLOSED BY HONEST SCOPE** |
| H4 | sealed response could be overwritten | Second seal rejected immediately; regression requires HTTP 409 and preservation of first response | **CLOSED LOCALLY** |
| M1 | Laboratory visible focus insufficient | Authored global `:focus-visible` styling; rendered Chromium UAT verifies focused controls | **CLOSED LOCALLY** |
| M2 | candidate reorder destroyed keyboard focus | Focus restored by candidate identity; position announced in live region on both surfaces | **CLOSED LOCALLY** |
| M3 | extra ledger keys outside digest | AITP-LEDGER-1.1 hashes complete record body except `record_hash`; strict legacy key handling | **CLOSED LOCALLY / VERSIONED** |
| M4 | malformed ledger raised exception | Malformed record returns controlled verifier FAIL | **CLOSED LOCALLY** |
| M5 | local preview headers were misrepresented as Pages headers | Public HTML includes deployable CSP meta subset; docs explicitly separate local response headers from static-host reality | **CODE CLOSED; HOSTED VERIFY** |
| M6 | transient/unbound errors | Persistent `role="alert"`; field focus/association on actionable validation failures | **CLOSED LOCALLY** |
| M7 | Prediction Ledger freeze-only | Append-only adjudication record implemented; second adjudication rejected | **CLOSED LOCALLY** |
| M8 | public/local prediction fingerprints differed | Shared AITP-PRED-1.1 canonical content serializer/fingerprint | **CLOSED LOCALLY** |
| M9 | 585 px mobile reflow floor | `.inspect-grid` and long technical strings reflow; rendered 390/320 UAT verifies `scrollWidth <= innerWidth` | **CLOSED LOCALLY** |
| M10 | public nav disappeared below 1000 px | Responsive reachable nav retained; rendered mobile UAT checks all five destinations | **CLOSED LOCALLY** |
| L1 | unknown hash blanked Laboratory | unknown/case-normalized routes recover to Overview | **CLOSED LOCALLY** |
| L2 | Back exited app rather than navigating views | `pushState`/`popstate` routing; rendered UAT verifies Back | **CLOSED LOCALLY** |
| L3 | CLI fail-closed paths emitted tracebacks | operator errors converted to concise `FAIL — ...` outcomes | **CLOSED LOCALLY** |
| L4 | broken trial label rendered `undefined` | fallback label is `Unreadable trial` | **CLOSED LOCALLY** |
| L5 | unknown `/api/*` returned HTML 200 | unknown API GET returns JSON 404 | **CLOSED LOCALLY** |
| L6 | GitHub link degraded to bare GitHub root | repository link is only surfaced when a meaningful hosted destination can be derived | **CLOSED IN CODE; HOSTED VERIFY** |
| L7 | candidate-count options out of order | options render 3, 4, 5, 6 | **CLOSED LOCALLY** |
| L8 | no Host validation | Laboratory rejects non-loopback Host values | **CLOSED LOCALLY** |
| L9 | bundled 8-target pool unsuitable for repeated formal work | bundled pool and guided Laboratory explicitly dry-run only; formal CLI supports explicit pool selection | **CLOSED BY SCOPE/DOCS** |
| L10 | 32 px touch controls below preferred guideline | ranking controls increased to 44 px target | **CLOSED LOCALLY** |
| L11 | missing `aria-current` / locked-step state | navigation exposes current state; locked steps expose `aria-disabled` | **CLOSED LOCALLY** |
| L12 | no confirmation on irreversible actions | Laboratory requires explicit confirmation before response seal, judgment lock, prediction freeze, and adjudication | **CLOSED LOCALLY** |
| L13 | unsupported Permissions-Policy feature warning | unsupported `bluetooth` feature removed | **CLOSED LOCALLY; HOSTED CONSOLE VERIFY** |
| L14 | type-sensitive scoring silently counted malformed IDs as misses | scorer validates non-empty string IDs and fails malformed external records | **CLOSED LOCALLY** |
| O1 | interpretation caveat asymmetric on hit/miss | both outcomes preserve bounded interpretation; one trial cannot establish/rule out mechanism | **DECISION DOCUMENTED / CLOSED** |
| O2 | result text hardcoded dry-run despite selectable formal conditions | guided Laboratory is intentionally dry-run only | **CLOSED BY SCOPE** |
| P1 | ledger cross-binding defeats re-freeze attack | retained and regression protected | **POSITIVE RETAINED** |
| P2 | binomial/Fisher match independent reference | algorithm retained; no inference broadening | **POSITIVE RETAINED** |
| P3 | target randomization shows no detected bias | randomization implementation retained | **POSITIVE RETAINED** |
| P4 | deterministic build path-independent | deterministic builder retained and final candidate must reproduce from clean independent paths | **POSITIVE RETAINED** |
| P5 | private lineage absent from public tree | boundary lint and release packaging preserve exclusion | **POSITIVE RETAINED** |

## Gates that remain environment/human dependent

The corrective source can be locally complete while the final public release remains legitimately open. Before a final tag/release:

1. GitHub CI must pass on the exact commit.
2. GitHub Browser UAT must run both rendered in-memory and live-loopback workflows.
3. CodeQL findings must be reviewed where applicable.
4. GitHub Pages must deploy the exact `site/` candidate.
5. Logged-out production desktop/mobile/readback must pass.
6. Production security statements must be reconciled to actual static-host behavior.
7. Human Authority claims/UAT sign-off must be recorded.

No failed hosted or human gate may be reinterpreted as a pass.
