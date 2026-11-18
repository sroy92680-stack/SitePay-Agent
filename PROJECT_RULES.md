# SitePay Agent engineering rules

Authoritative source: SitePay Agent Roadmap, Version 2.0 (18 November 2026), including the Implementation Addendum.

## Phase gates
Phase 0 customer and product validation **has not passed**. Do not claim the product is ready or start dependent development as though the gate has passed. The owner must approve the documented architecture, country-specific financial assumptions, sample data provenance, user research and first pilot before Phase 1.

## Evidence and human controls
1. No invented site evidence, measurements, quantities, rates, contractual terms, approvals or financial amounts.
2. Every extracted fact contains a source file, page or timestamp, confidence and units where applicable.
3. An uncertain or contradictory fact stays unresolved until an authorised human reviews it.
4. Preserve original uploaded files. Duplicate fingerprints must not create duplicate evidence.
5. No claim without linked proof. Final report, claim submission, variation approval, certification and payment require appropriate human authorisation.
6. All financial arithmetic uses deterministic Decimal code and configured versions; language models never set final money values.
7. Tenant isolation and role-based authorisation apply to all routes and queries; all changes and consequential actions need an append-only audit.
8. Offline entries must persist until the server acknowledges them. Conflicts are shown, never silently overwritten.

## Source code standards
1. Every code file starts with the owner marker `#Owner::ANIKET::ANHOTRA = MR.Panda`, using legal comment syntax for its language.
2. Every file has one responsibility and every code file contains fewer than 300 lines.
3. Typed Python functions, clear docstrings, full descriptive names, tests for every feature and explicit errors.
4. No secrets or customer data in git. Encryption in transit and at rest.
5. All text must avoid em dash punctuation. Interface language follows user preference.
6. A model or prompt change must pass golden-set regression tests before release.
7. Production deployment requires development, staging, recovery plan and a manual release decision.
8. Never mark an untested change verified. Do not manufacture commits or results.

## Change approval
Any important change must document its reason, modules, database, AI, finance and security impacts; acceptance tests; rollback; and owner authorisation. Follow `docs/17_change_control.md`.

## Status terminology
Exactly one of: Not started, In progress, Blocked, Implemented, Tested, Verified complete. The final state requires evidence from executable checks and a named reviewer.
