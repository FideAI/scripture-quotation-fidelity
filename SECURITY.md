# Security Policy

## Reporting

Report privately to **alex@fideai.org**. Please do not open a public issue.

Report anything of this kind:

- Credentials, API keys, or tokens appearing anywhere in this repository or its
  history.
- Private partner traces, raw model outputs, or held-out prompts.
- Restricted or licensed source text that should not have been released.
- A defect in the release tooling that could cause any of the above.

Include the file and line if you can, and the commit you observed it in. We aim
to acknowledge within five business days.

If you believe credentials are live, say so in the subject line so we can
rotate them before triage.

## Scope

This is a research repository. It publishes derived scores, protocol,
documentation, and analysis code. It does not run a hosted service, so there is
no production system to test against and no penetration testing is invited.

The release boundary is documented in
[`docs/repository_boundary.md`](docs/repository_boundary.md). Automated checks
run on every push via `make release-audit`, which scans for credentials,
private paths, and forbidden artifact types. Those checks are a floor, not a
guarantee — reports of anything they miss are genuinely useful.

## Source text

No authoritative passage text from the evaluated BSB, WEBU, or LSV editions is
released. Their passage identity is disclosed through normalized-text SHA-256
digests only. The `examples/` directory intentionally contains a small amount
of public-domain KJV wording and is not study data. If you find passage text
from an evaluated edition or outside those declared examples, treat it as a
rights disclosure and report it privately.
