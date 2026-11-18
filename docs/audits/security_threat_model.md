# Initial security and privacy threat model

**Review status: draft.** Threat scenarios and controls are proposals, not deployed protections.

## Assets and trust boundaries
- Sensitive assets: original images and audio, contracts, certified and claimed amounts, bills, personal information, organisation membership, approval records, AI prompts and processing logs.
- Boundaries: browser to API, authenticated user to organisation, API to storage, ingestion to model provider, async jobs to database, and offline phone storage to server.
- Actors: worker, engineer, project manager, office/accounts user, tenant owner, system administrator and external client in later phases.

## Threats and planned controls
| Threat | Impact | Planned prevention / detection | Validation |
|---|---|---|---|
| Cross-tenant object reference | Confidential project disclosure | Authorise every project ID through verified membership and tenant-scoped database keys | Request and worker tests across two tenants |
| Stolen token or weak password | Account and financial data exposure | Strong password hashing, short-lived signed sessions, secret rotation, audit and rate limits | Auth and negative access tests |
| Malicious document / archive | Server compromise or parser abuse | MIME sniffing, bounded sizes, safe parsers, virus scanning and sandboxed processing | Adversarial file tests |
| AI prompt injection | Incorrect tool use or altered claim | Uploaded content is untrusted; allowlisted tools, schema validation, no approval authority | Injection regression cases |
| Forged approval | Unauthorised claim release | Explicit authenticated role, workflow transition checks and immutable audit | Role matrix and lifecycle tests |
| Missing offline encryption | Data leakage from lost phone | Minimise cached data, set retention and lock-screen requirements, user warning | Device privacy assessment |
| Payment detail exposure | Fraud and confidentiality breach | Minimise collection, mask display, scoped access, no secrets in logs | Privacy tests |
| Unsafe public file access | Disclosure of evidence | Private object buckets, signed short-lived URLs and object key scoping | Storage policy inspection |
| Tampering with evidence | False claims | Immutable original, cryptographic hash, provenance, versioned derivatives | Integrity and upload tests |
| Deleted or altered audit | Untraceable decisions | Append-only storage and restricted service writes | Database permission tests |
| Supply-chain compromise | Malicious CI or dependencies | Pinned releases, dependency audit, minimal GitHub token scopes | CI and dependency inspection |
| Unverified backup | Irrecoverable project data | Encrypted periodic backup and tested restore with checksums | Restore drill records |

## Data handling
Do not commit real project documents, personal photographs or customer bank details to a public repository. Validate lawful bases, consent, purposes, retention and data subject handling with qualified privacy review. Use India's applicable data-protection requirements for the pilot deployment after legal review.

## Remaining blockers
No production cloud account, penetration testing, signed privacy assessment, migration or storage policy has been reviewed. This threat model cannot be used as evidence that controls are deployed.
