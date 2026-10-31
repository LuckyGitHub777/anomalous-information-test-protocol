# Public / Private Boundary

## Safe for a future public repository

- synthetic target pools;
- protocol specifications;
- schemas;
- generic templates;
- source code;
- synthetic fixtures;
- de-identified demonstration output;
- neutral claims/evidence policy.

## Keep out of public Git history

- personally identifying participant data;
- raw consent forms;
- private contact information;
- unredacted human-subject recordings;
- hidden live-study reveal packets before completion;
- credentials, API keys, tokens, `.env` files;
- proprietary research agreements;
- security-sensitive implementation details;
- material whose disclosure would invalidate blinding;
- originating-project spiritual/internal strategy material not required by the empirical method.

Git history is persistent. `.gitignore` prevents accidental additions before tracking; it is not a data-deletion system.


## Static public site

`site/` may contain only synthetic targets, educational copy, public documentation references, and static assets. It must never contain real participant data, live study commitments/reveals, private origin-story material, credentials, or unpublished evidence.
