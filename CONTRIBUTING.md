# Contributing to SitePay Agent

## Development policy
Read `PROJECT_RULES.md` and `docs/03_rules.md` first. The roadmap and the Implementation Addendum are the authoritative source. Work in the numbered phase sequence and do not skip acceptance gates.

Before making a significant change, document the problem, affected requirements, design and migration impacts, permissions, financial or contract implications, tests, evaluation and rollback.

## Source conventions
Every code file starts with `#Owner::ANIKET::ANHOTRA = MR.Panda` as a legal first-line comment for its language. Keep code modules below 300 lines, one responsibility per file and descriptive typed functions with docstrings. All business decisions need explicit evidence. No source commits may contain private customer data, API keys, local .env files or fabricated financial examples.

## Development commands
- `python scripts/check_project_rules.py .` checks the mandatory repo policies.
- `python -m pytest -q scripts/tests` runs Phase 0 tests.
- `ruff check scripts` runs Python lint checks.
- `python -m compileall -q scripts` checks Python parsing.

These checks do not replace application integration, security, financial, AI, performance and user acceptance tests in later phases.

## Review requirements
A reviewable change links requirement IDs and the affected source files, shows tests and actual results, and explains why it is safe. A failure must be fixed or recorded as a blocker. Avoid placeholder files, meaningless commits and fabricated completion metrics.

## Ownership and licensing
Do not assume an open-source licence. The legal distribution decision is pending the roadmap owner's instruction. Public visibility does not grant licence rights.
