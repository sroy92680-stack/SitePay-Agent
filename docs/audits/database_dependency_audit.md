# Database and migration dependency audit

**Status: logical audit only. No database or migration is deployed.**

## Sequenced data dependencies
1. Users and organisations plus memberships, with explicit roles and verified tenant boundaries.
2. Projects and sites, with all tenant-owned references scoped to their organisation.
3. Evidence and durable sync records, immutable originals and stable device operation keys.
4. Bill/agent-run/correction records and a validated provenance model.
5. Bill of Quantities items, measurements, contracts, contract terms and calculation records.
6. Issues, evidence conflicts and variations, with reviewer resolution histories.
7. Claims, claim lines, approvals, status history and separate payment records.

This follows the roadmap's Phase 1 through 6 file order. Do not create later tables or APIs as verified until prior migration and integration tests pass.

## Tenant safety
Normalise owner organisation IDs, index them and enforce project-to-organisation integrity. A cross-tenant foreign key reference should fail, even when user input is syntactically valid. Service accounts must not bypass tenant checks by accident.

## Audit and immutability
Uploaded originals, certified quantities and approved calculations require protected immutable records. Material changes create new versions or append-only events, not destructive updates. Audit logs capture principal, organisation, action, target, changed values, reason and timestamp. Consider database grants and triggers to harden append-only constraints.

## Transaction model
Deduplication keys, evidence metadata and upload acknowledgement need consistent transaction boundaries; physical object writes use a recoverable reservation/outbox protocol. Payment approval and financial snapshots must be atomic with the audit trail. Concurrent edits need optimistic version checks and explicit merge resolution.

## Required migration tests
Fresh database setup; migration from prior schema; rollback where safe; foreign-key and uniqueness enforcement; tenant isolation; process crash; duplicate upload; approval concurrency; data preservation and integrity checks after restore.

## Blocker
No approved architecture freeze, database credentials, deployment environment or phase gate evidence exists. This audit is not proof that PostgreSQL is configured or safe.
