# GitHub Rules / Branch Protection

Protect `main` using the strongest native rules available on the repository/account.

## Recommended controls

- require a pull request before merge for nontrivial changes;
- require **CI** and **Browser UAT** status checks after their first successful hosted runs establish exact check names;
- require conversation resolution;
- block force pushes;
- block branch deletion;
- prefer linear history where it fits the workflow;
- avoid routine bypass.

## CodeQL

Require a CodeQL/security status only after the public hosted workflow has successfully run and the exact check name/availability is known. Do not create a required check that cannot report.

## Release baseline

Freeze the exact candidate commit and manifest before public-release sign-off. Any source change after V&V creates a new candidate identity and reruns affected gates.
