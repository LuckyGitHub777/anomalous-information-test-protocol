# AITP Laboratory UX

## Product promise

A nontechnical operator should be able to complete a protocol dry run without learning Git, JSON, SHA-256, or the CLI.

## UX principles

1. **One action per step.**
2. **Evidence first, explanation last.**
3. **Progressive disclosure.** Plain-language state first; technical detail remains inspectable.
4. **Role-aware views.** Each role sees only what it needs for that phase.
5. **No spectacle.** Modern scientific instrumentation, not paranormal/UFO visual tropes.
6. **Fail closed.** Candidate/reveal/seal ordering cannot be bypassed through the normal interface.
7. **Private by default.** No accounts, analytics, telemetry, CDN, remote fonts, or cloud storage.
8. **Accessible.** Keyboard operation, visible focus, live reorder announcements, persistent errors, reduced motion, responsive layout.
9. **Invalid means visibly invalid.** Preserved evidence is not presented with success semantics when the overall trial is ineligible for analysis.

## v1.1 guided scope

The Laboratory intentionally exposes **DRY_RUN only**. Formal conditions require anchor-evidence handling that the guided UI does not yet attempt to represent.

This is a product-integrity decision: the interface should never offer a path it cannot complete honestly.

## Current UI flows

- Guided dry run
- Participant response sealing
- Candidate release after freeze
- Blinded ranking with focus retention
- Judgment sealing
- Reveal + validity/ineligibility explanation
- Local Evidence Cabinet
- Prediction freeze + append-only adjudication

## Accessibility acceptance

Rendered UAT covers:

- 1440 desktop;
- 720 narrow/zoom-equivalent layout;
- 390 mobile;
- 320 narrow mobile;
- public/Laboratory keyboard navigation;
- visible focus;
- candidate focus retention and live announcements;
- reduced-motion behavior;
- no horizontal overflow;
- reachable mobile navigation;
- explicit invalid-state styling.

## Security boundary

The local UI provides **workflow separation, not adversarial multi-user access control**. A technically privileged user with filesystem access can inspect the custodian directory.

For a serious blinded study requiring true role separation, use separate custodians/devices/storage and the packet/export workflow.

## Irreversible actions

The local Laboratory requires explicit user confirmation before sealing a participant response, locking a judgment, freezing a prediction, or appending an adjudication. Synthetic public-demo actions remain restartable and do not create research evidence.
