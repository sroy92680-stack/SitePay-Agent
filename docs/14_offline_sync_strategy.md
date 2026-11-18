# Offline capture and synchronisation strategy

**Status:** Phase 2 design and incremental development. This is not a complete offline feature.

The authoritative PDF specifies durable photo and voice capture, device storage, visible pending/synced/failed states, idempotency, checksums, retries and explicit conflict resolution.

## Proposed device protocol
1. The mobile app saves the original bytes to device-controlled persistent storage and records a unique device ID plus client record ID in IndexedDB **before** reporting the capture saved.
2. The outbox state is `saved_locally`, `pending`, `uploading`, `synced`, `failed`, or `conflict`, with retry attempts and the original checksum retained.
3. When connectivity is available, the app sends the bytes and stable operation IDs. The server authenticates the actor and checks project and site association.
4. The server returns an accepted evidence ID and checksum only after private storage and database acknowledgement have succeeded.
5. The outbox verifies the returned checksum and operation IDs and may then mark `synced`. It must not silently discard the only copy of the original.
6. Retried identical operations return the same acknowledgement. Reusing an operation ID with different bytes returns a conflict and requires human intervention.
7. A different device reusing identical source bytes may share an evidence record but has its own operation acknowledgement.

## Failure cases to test
- Network failure before or during upload
- API crash after S3 storage but before database commit
- Client restart while an item is queued or uploading
- Storage quota exhaustion and device loss warning
- Invalid authentication or membership revoked while offline
- Duplicate bytes, conflicting operation IDs and concurrent edits
- Project or site changed since offline capture
- Sync response loss after server acknowledgement
- Original checksum mismatch on download
- Weak network and retry backoff without data loss

## Current implementation boundary
Phase 2 backend is being developed on a gated branch. Frontend IndexedDB outbox, capture UI, browser service worker and storage-quota behaviour are **not yet implemented**. An accepted server acknowledgement is not equivalent to a complete, lossless offline mobile workflow. No permissioned customer material is included.

## Backend implementation evidence, 18 November 2026

The server now verifies original bytes, stores a private S3 object, inserts an immutable evidence record and records a separate accepted device operation in PostgreSQL. The device may query a prior acceptance with `GET /projects/{project_id}/sync/operations/{device_id}/{client_record_id}`. Duplicate upload retries return the original receipt. A conflicting client operation ID is rejected rather than silently overwriting an accepted source. An identical byte stream attributed to a different site or kind is rejected for review rather than automatically relabelled. A storage failure never produces a database acknowledgement. See GitHub Actions run 44327768382.

**This is only the server half**. No browser IndexedDB capture queue, sync-conflict review interface, local deletion policy, mobile voice recorder, storage-quota test or failure-recovery exercise has passed. Users must not rely on this branch as a complete offline capture system.
