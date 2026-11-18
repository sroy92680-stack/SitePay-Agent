# Architecture and product decision log

All material choices need a dated decision, alternatives, impact and approval. Records must not imply approval when the owner has not signed.

| ID | Decision or proposal | Current status | Basis |
|---|---|---|---|
| ADR-001 | Python 3.12/FastAPI, PostgreSQL, React/TypeScript, private object storage | Proposed, awaiting sign-off | Roadmap Part 5 |
| ADR-002 | Immutable uploaded originals plus separate processing derivatives | Proposed, awaiting sign-off | Roadmap Part 4 |
| ADR-003 | Decimal calculations in isolated deterministic engine | Proposed, awaiting financial sign-off | Roadmap Parts 4, 13 |
| ADR-004 | India first release with English and Hindi | Proposed, awaiting user validation | Roadmap Part 3 |
| ADR-005 | Human-only consequential approval and payment controls | Non-negotiable rule | Roadmap Parts 4, 11 |
| ADR-006 | Canonical claim lifecycle labels and allowed transitions | Unresolved | Base Part 11 vs. Addendum 1 |
| ADR-007 | Role and tenancy constraints at database and API layers | Proposed, awaiting threat-model review | Roadmap Parts 4, 10 |
| ADR-008 | Scoped offline IndexedDB outbox with idempotent upload | Proposed, awaiting test and privacy review | Roadmap Parts 5, 16 |
| ADR-009 | Public GitHub repository contains no permissioned client samples | Implemented as operating constraint | Confidentiality and security |
| ADR-010 | Phase 0 must pass before dependent Phase 1 work | Gate currently blocked | Roadmap Part 6 and Addendum 8, 12 |

## Decision record format
Date, decision owner, requirement IDs and source pages, decision statement, alternatives and consequences, security and contractual implications, implementation paths, tests, reviewer, approval and migration or rollback. Append a new record to supersede an old one rather than silently changing history.
