# Change request: Phase 2 evidence persistence foundation

**Decision status:** Engineering development proposal. Product and architecture approval NOT granted.
**Branch:** `development/phase2-evidence-foundation`
**Source:** SitePay Agent Roadmap v2, PDF pages 15 to 17 and 69 to 70, orders 61 to 72, 94 to 95.

## Reason and scope
The preceding Phase 1 branch has a working tenant-scoped project API, SQLAlchemy models and Alembic migration 0001. Phase 2 requires immutable source-backed site evidence before any AI, measurement or financial claim workflow can be implemented. Add evidence metadata, immutable original-byte storage, device operation acknowledgements, bounded content validation and permission-checked endpoints. This is an engineering slice, not the complete Phase 2 acceptance workflow.

## Dependencies
- Database migration 0001 and active tenant memberships must exist.
- S3-compatible private object storage is required for original bytes.
- Development proof uses disposable MinIO and PostgreSQL containers, not real site data.
- The pre-implementation Product Validation Gate remains **blocked**; no production merge or release is authorised.

## Architectural decision proposal
Use SHA-256 content fingerprints and a private content-addressed S3 key scoped by organisation and project. Apply conditional object creation and database uniqueness to avoid duplicate originals. Preserve one immutable evidence row per unique project/file hash, and store a distinct immutable acknowledgement for each accepted device operation. Conflicting reuse of a device operation key returns HTTP 409.

## Security impact
- Authorise every request through an active membership and the parent project. Check selected site belongs to the project.
- Never trust browser-supplied MIME types, object keys, uploaded paths or tenant IDs.
- Limit upload size and accept only positively recognised formats. Do not execute or render uploads as HTML.
- Originals are private. GET requires the same tenant authorisation, and received bytes are checksum verified.
- Object insertion can succeed before database commit; preserve the orphan safely for later reconciler review. Never automatically delete an original.

## Finance/contract and AI impact
None of the stored bytes constitutes verified work, a contractual entitlement or a claimable quantity. No AI extraction or financial approval is added. Missing work evidence remains missing.

## Testing and exit criteria
- Migration 0002 applies to SQLite and PostgreSQL.
- Database evidence records cannot be updated or deleted.
- Cross-tenant access denied, including guessed IDs.
- Upload is bounded, source type validated and never changes original bytes.
- Retry of same device operation with identical checksum returns same accepted evidence; altered checksum yields conflict.
- Duplicate bytes from separate devices reuse one evidence row without double-counting.
- Interrupted/failed object storage must not mark an upload acknowledged.
- Real MinIO and PostgreSQL integration tests run in CI.

## Rollback
Do not downgrade production databases with evidence. Reverse API deployment by disabling the development-only route flag, and preserve object originals and immutable rows. Schema downgrade may destroy data and requires owner-authorised backup verification.

## Review and approval
Engineering review pending. Product validation, permissioned pilot samples, threat review, cloud storage policy and release sign-off pending. **No gate has been silently passed.**

## Container registry compatibility resolution

The original planned developer object store used official MinIO images. GitHub Actions run 44326028722 proved that `quay.io/minio/minio:RELEASE.2025-09-07T16-13-09Z` rejects anonymous pulls (HTTP 401). No unverified third-party mirror will be used for production data. The local developer and CI stack now uses version-pinned, actively maintained `pgsty/silo` and `pgsty/mc` S3-compatible containers. The application depends on the S3 API rather than a proprietary MinIO interface, so this is a replaceable developer infrastructure component. Production storage provider, encryption, IAM isolation, retention, object lock and backup remain unapproved. Review the container source, licences and pinned release before any production decision.

## Bucket initialization adjustment

GitHub Actions run 44326555671 proved the published S3 CLI container was pullable, but its original shell-entrypoint initialization exited unsuccessfully. The developer stack now initializes its private bucket through the same pinned Python boto3 client used by evidence storage, in a short-lived `minio_init` build container. This removes a separate CLI image dependency and ensures no script exposes credentials through shell command arguments. The S3 server itself remains replaceable. The initialization code never turns on public bucket access and creates a bucket only when it is missing.
