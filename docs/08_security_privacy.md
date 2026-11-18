# Phase 1 API security and privacy controls

**Engineering development branch only. No independent penetration audit or production launch approval.**

## Controls implemented
1. Passwords are hashed with Argon2, with no password/hash serialized in public responses or stored in audit details.
2. Access tokens are HS256-signed with issuer, audience, mandatory expiry and a secret of at least 32 characters from runtime environment. Every request still checks current database membership.
3. Production/staging reject local SQLite settings and do not accept missing or short JWT signing keys.
4. Tenant-owned project and site records are fetched only through verified active membership.
5. Only owners invite members, and an invitation is pending until accepted by that authenticated user.
6. Owner/manager/engineer/worker role checks are enforced server-side on relevant write operations.
7. Audit entries are inserted in the same database transaction as changes, and UPDATE/DELETE are rejected by database triggers.
8. Validation errors return generic messages rather than echoing submitted passwords.
9. Development Docker binds API to localhost; no payment or external integration endpoints exist.

## Remaining material risks
- Registration and login rate limiting, account verification, lockout, password reset, refresh/revocation, invitation expiry and MFA have not been implemented.
- No TLS termination, public cloud controls, audit log archival, sealed secret service, managed backup or signed tenant isolation review is configured.
- The initial audit history view is limited to 500 entries and is not a paginated compliance archive.
- PostgreSQL integration and concurrency testing must pass before further trust in the data layer.
- Privacy compliance, client documents, face redaction, retention and deletion are later phases requiring validated business policies.

## Production boundary
This code must not be exposed to real contractor data, payment authorisation or public traffic until security review, validation gate and further controls pass. No credentials are checked into GitHub.
