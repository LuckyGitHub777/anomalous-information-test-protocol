# Security Policy

## Supported version

Security fixes target the latest release candidate on `main`.

## Sensitive reports

Do not put exploitable security details, participant data, private reveal packets, credentials, or confidential research information into a public issue.

If this repository becomes public, enable GitHub private vulnerability reporting and use that channel for security-sensitive findings.

## Security model

The core toolkit is offline-first and has no runtime network dependency. Security-relevant invariants include:

- hidden reveal confidentiality before judgment freeze;
- response and judgment immutability after freeze;
- target-pool and candidate integrity;
- ledger/audit integrity;
- chronology evidence described without false tool-verification claims;
- exclusion of private human-subject data from Git history.

SHA-256 commitments provide tamper evidence, not encryption or access control. Operators remain responsible for file permissions and secure storage.

## Local Laboratory

The server binds to loopback, validates allowed local Host values, requires JSON plus a custom local-request header for mutations, enables no cross-origin API access, and caps request size.

This does not make one shared machine an adversarial role-isolation boundary.

## Public site

`site/` is static and synthetic. It must not transmit/store real study data. The HTML CSP meta policy is a static-host fallback; response-header behavior must be evaluated on the actual deployment rather than inferred from the local preview server.
