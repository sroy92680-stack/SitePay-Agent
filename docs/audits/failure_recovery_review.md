# Failure, offline and disaster recovery review

**Review state: planned, not tested.** Source: roadmap Parts 16 and 19 plus Addendum 7 and 9.

## Offline capture invariants
- Save a local operation and its content fingerprint before displaying it as captured.
- Do not discard queued data before durable server acknowledgement.
- Use idempotency keys and retry with controlled backoff to avoid duplicate records.
- Show pending, synchronised, errored and conflicted states with user-visible action options.
- Stop a stale or conflicting write and route it to explicit reconciliation rather than last-writer-wins.
- Test app kill/restart, low power, device storage exhaustion, intermittent network, invalid auth, upload interruption, duplicate evidence, editing after capture and conflicting project updates.
- Encrypt/minimise sensitive device cache where feasible. Document lost-device and retention policy.

## Server failure controls
Queue processing retries are bounded and auditable; irrecoverable jobs appear in a manual recovery queue. Every raw upload original has a hash and a separate protected copy. Database state is not declared recovered until foreign keys, calculations and evidence references pass integrity checks.

## Roadmap recovery targets
- Daily encrypted database backups; additional backup before each release.
- Initial retention: 14 daily, 8 weekly and 12 monthly points, subject to documented review.
- Independent evidence object backup.
- Monthly isolated full restore test with verified data integrity.
- Initial Recovery Point Objective: 24 hours maximum.
- Initial Recovery Time Objective: 8 hours maximum.
- Incident runbooks available if the primary app is down.

## Incident procedure
Detect and time-stamp; contain damage; assess affected organisations, source files and claims; communicate according to contract and legal duties; restore and verify; document cause and preventive action.

## Acceptance and blockers
There is currently no production database, object store, backup, offline client or restore infrastructure. No tests of data preservation or recovery have been performed. This document specifies required validation; it does not certify a recovery capability.
