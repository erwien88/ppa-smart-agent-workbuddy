# Security Model and Limitations

## What the demonstration supports

- Human approval is required before the documented write operation.
- The write is scoped to a sandbox file and limited data range.
- Protected master data are excluded from that approved operation.
- The integrity gate is tested with six negative cases, each rejected as expected with exit code `1` and `FATAL = 0`.
- Results are corroborated by file read-back and comparisons where available.

## What remains a limitation

- The gate is an **integrity checkpoint**, **not** an access-control enforcement layer.
- The file allowlist is a code-defined constant, not a deployed organizational authorization system.
- The baseline is one-shot; this produces a documented post-write baseline `FAIL` in the demonstration.
- Unapproved-write refusal, batch operation, save-failure recovery, and full end-to-end security have not been established as passing production tests.
- The environment is isolated and the dataset is simulated.

## Publication safety

Do not commit account passwords, API keys, access tokens, `.env` files, client identifiers, real personal data, internal paths, proprietary contracts, or screenshots exposing private information. Inspect both file contents and metadata before changing a repository to Public.
