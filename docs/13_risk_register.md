# Initial project risk register

This register reflects engineering risks identified in the roadmap. No product risks are marked resolved until reviewed and evidenced.

| ID | Risk | Severity | Proposed control | Current status |
|---|---|---|---|---|
| R-01 | Building an unvalidated workflow | Critical | 5 to 10 interviews, one observed claim and pilot agreement | Blocked |
| R-02 | Claim amount is fabricated or misrounded | Critical | Isolated Decimal engine, contract policy and reconciliation tests | Not started |
| R-03 | Tenant leaks or unauthorised project access | Critical | Scoped queries, tested role checks, signed storage URLs | Not started |
| R-04 | Evidence lost during offline sync | Critical | Durable outbox, acknowledgement protocol, retry and chaos tests | Not started |
| R-05 | Conflicting photo and measurement incorrectly accepted | Critical | Explicit conflict record and reviewer resolution | Not started |
| R-06 | AI hallucination or prompt injection changes claim | Critical | Schema validation, provenance, registry tools and human checks | Not started |
| R-07 | An unapproved variation increases payable quantity | Critical | Variation authorisation and remaining quantity constraint | Not started |
| R-08 | Contract clauses or India taxes treated as universal | High | Permissioned source clauses and reviewed country pack | Blocked |
| R-09 | Duplicate evidence reused across claims | High | File hashes plus semantic and ledger checks | Not started |
| R-10 | Contractor confidentiality exposed in public repo | Critical | No client data in git, private storage and redaction | In progress |
| R-11 | Payment state and certified amount confused | Critical | Approved transition model and separate certificate ledger | Blocked |
| R-12 | Backups exist but are not restorable | Critical | Documented restore tests and integrity verification | Not started |
| R-13 | Deployment claimed without security and pilot evidence | High | Staging, threat review and signed launch gate | Not started |
| R-14 | AI golden-set accuracy regresses | High | Versioned evaluations and critical release gate | Not started |

Risk reviews should add owners, likelihood, evidence, due dates and decisions when real stakeholders are identified. The priorities above are engineering assessments, not claims of field validation.
