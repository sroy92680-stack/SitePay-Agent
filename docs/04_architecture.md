# Architecture proposal and dependency review

**Status: draft, awaiting Phase 0 owner sign-off.** No runtime service is claimed to exist. The roadmap mandates the technical choices below; this document does not silently change them.

## Planned technology
- Python 3.12 and FastAPI for backend API, authorization, background jobs and typed request schemas.
- PostgreSQL for transactional records; SQLite is an optional development-only convenience with known behavioural differences.
- React and TypeScript mobile-first Progressive Web App, using IndexedDB as a persistent offline capture queue.
- S3-compatible private object storage for immutable uploaded originals, protected by short-lived scoped access.
- Controlled Claude API for visual/text extraction; an appropriately configured multilingual speech model for voice notes.
- HTML templates for PDF documents and openpyxl for Excel output.
- Database-backed jobs initially; Redis and separate workers after scaling and explicit review.
- Docker Compose for development and separate deployment containers for staged promotion.
- pytest, Vitest, Playwright, approved golden-set evaluation and CI release gates.

## Trust boundaries
Browser clients never choose their own tenant or role claims without server verification. Every API and job rechecks membership, project tenancy, state and permissions. Uploaded files are untrusted: enforce size/type limits, hashing, malware defenses, safe parsing and immutable storage. AI outputs are untrusted recommendations, validated against typed schemas and source records. No AI tool may authorise, certify, pay or externally submit.

## Logical data flow
```text
Mobile capture + durable outbox -> authenticated upload -> original object store
                                        |
                                        v
                                 Evidence record + audit
                                        |
                                        v
                            Extractor with source/confidence
                                        |
                                  Human fact review
                                        |
                         Contract + BOQ + measurement ledger
                                        |
                        Duplicate/conflict/variation detection
                                        |
                           Deterministic finance engine
                                        |
                       Claim draft + calculation record
                                        |
                  Human review -> approval -> manual submission
                                        |
                          Certification / receipts / audit
```

## Proposed PostgreSQL entities
Users, organisations, memberships, projects, sites; contracts and terms; Bill of Quantities items; evidence and sync records; measurements and progress entries; bills and bill lines; issues, evidence conflicts and variations; claim and claim lines; approvals, claim status history and payment records; calculation records; agent runs, corrections, audit logs and usage records.

All tenant-owned entities require relational tenant boundaries with explicit, indexed organisational or project keys. Foreign-key paths between tenants are rejected, not assumed safe from UI filtering. Application checks and carefully evaluated database constraints should reinforce one another. Financial and evidence-critical records use append-only history.

## Offline and idempotency
Each device persists an entry and content hash before trying network transfer, preserving a unique client-generated operation key. Upload acknowledgement occurs only after server persistence. Version conflicts are surfaced to the operator instead of last-writer-wins updates. Duplicate content does not silently double-count physical evidence. Queue retention, storage exhaustion and retry behaviour require independent tests.

## Calculation and claim controls
Authoritative quantities come from verified measurements and contract rules. The engine produces Decimal calculations with explicit currency, units, versioned rounding, remaining quantity checks and a step-by-step trace. Claims are drafts until permitted roles explicitly approve. Prior claimed and certified quantities are separately reconciled.

## Architecture decisions still open
- Exact India tax and retention rules must come from actual client contracts and reviewed country-pack configuration.
- Main roadmap payment statuses conflict with the Implementation Addendum state names. An approved canonical model is needed.
- Cloud provider, storage credentials, backup regime, jurisdiction and AI data-handling terms require review.
- The architecture cannot be frozen without validation and owner sign-off.
