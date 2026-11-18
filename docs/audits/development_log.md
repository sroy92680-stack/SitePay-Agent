# Development log

## 2026-11-18, GitHub execution session

### Completed GitHub operations
- Updated the repository README with an explicit Phase 0 status.
- Created [issue #1](https://github.com/sroy92680-stack/SitePay-Agent/issues/1) for missing real-world product validation and owner sign-off.
- Committed source-policy checking, first-line owner tag validation, source size and punctuation checks, tests and GitHub Actions CI.
- Generated and committed the 395-row ordered roadmap deliverable register directly from PDF pages 13 to 27.
- Added the 77-control engineering requirement register with a test that guards the count and ID sequence.
- Committed product concept, draft architecture, validation protocol, risk register, decisions and change control.
- Recorded the payment state-machine conflict and the India financial policy blocker.

### Verification observations
- GitHub Actions runs for the initial commits passed policy, Python syntax, lint and Phase 0 tests.
- Successful run for the requirements-register commit: https://github.com/sroy92680-stack/SitePay-Agent/actions/runs/44292244027
- These tests do not establish that the application exists. They validate only repository metadata and policy logic.

### Blockers and non-claims
- Customer interviews, field workflow observation, licensed sample documents and pilot commitment are missing.
- Architecture, taxes, legal assumptions, claim state names and scope freeze require a signed decision.
- No backend, frontend, AI model, production finance calculation or deployable application is implemented.

### Next dependency
Complete real Phase 0 validation, sign the readiness and architecture decisions, then implement Phase 1 in order. No automatic continuation is scheduled from this conversation.

## 2026-11-18, gated Phase 1 backend development branch

- Created `development/phase1-backend` from main without overriding the Phase 0 gate.
- Implemented FastAPI authentication, Argon2 credential hashing, validated JWTs, users, organisations and pending membership acceptance.
- Added projects, sites, role-based access, tenant filtering, confidential input validation and scoped audit history.
- Added Alembic revision 0001 with PostgreSQL/SQLite audit immutability triggers and DB foreign keys.
- Added Dockerfile, local Compose environment, health probes and Phase 1 environment, security, data model and testing documents.
- Integration tests cover sign-in, expired tokens, role restrictions, membership revocation, another-tenant project IDs, migrations, Decimal contracts and audit immutability.
- GitHub Actions `44295897022`: **success** for Python tests, lint, syntax, full policy check, PostgreSQL migration/constraints, Docker configuration and API image build.
- Complete Phase 1 file list exists in this **unmerged development branch**, but the phase exit remains **blocked** by missing real product validation, architecture sign-off and approved business scope.
- No upload, AI extraction, finance, claim, or mobile PWA functionality has been represented as working. No production deployment performed.

## 2026-11-18, container integration hardening

- Added a real HTTP smoke workflow that builds the backend container, runs Alembic against a live PostgreSQL service, starts the API, registers a synthetic account, signs in, creates a project and site, and checks the tenant audit trail.
- Initial CI run 44296682000 failed. Python lint detected an unused retry counter, and the synthetic test account used an email domain rejected by validation. These were corrected in commit adde243.
- Verified follow-up GitHub Actions run [44296887975](https://github.com/sroy92680-stack/SitePay-Agent/actions/runs/44296887975) passed **31 Python tests**, PostgreSQL migration/constraint checks, Docker image build and the live HTTP smoke workflow.
- Synthetic CI project data was destroyed through the container cleanup step. No production server was created or deployed.
- Draft pull request #5 remains unmerged pending the Phase 0 product-validation and architecture decision gates.

## 2026-11-18, Phase 2 evidence foundation

- Created `development/phase2-evidence-foundation` stacked on Phase 1 without merging or declaring the PDF gate passed.
- Committed `backend/app/models/evidence_model.py`, `sync_record_model.py`, migration 0002, file integrity and S3 storage services, source schemas and upload/list/download/sync acknowledgement routes.
- Committed a real private S3-compatible developer server, bucket initialization through boto3, developer-only feature gate and live Docker integration workflow.
- CI initially failed lint and infrastructure startup: official upstream MinIO/Quay images became unpullable; replaced with pinned maintained S3-compatible SILO and a Python bucket bootstrap. Fixed import formatting and original metadata conflict checks.
- Validated safe duplicate retry, checksum equality, cross-tenant rejection, same-byte site mismatch, invalid file type, receipt query and atomic audit. Added failure injection proving unavailable storage produces no acknowledgement.
- [Run 44327768382](https://github.com/sroy92680-stack/SitePay-Agent/actions/runs/44327768382) succeeded: **47 Python tests**, all 3 jobs successful, real PostgreSQL constraints and live S3 HTTP smoke.
- Offline mobile outbox, capture UI, document parsers, OCR, speech transcription and the complete Phase 2 exit are still **not implemented or verified**. Product validation and scope freeze remain blocked.
