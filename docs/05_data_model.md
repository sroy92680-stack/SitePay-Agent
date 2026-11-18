# Core database model, Phase 1

The initial migration is `backend/migrations/versions/0001_create_core_and_audit_tables.py`. This is a tested development schema, not an approved financial-data design.

## Tables
| Table | Important columns | Relationship / protection |
|---|---|---|
| `users` | id, unique normalised email, Argon2 password hash, name, language, creation time | No plaintext password |
| `organizations` | id, name, India country pack, created time | Primary tenant boundary |
| `memberships` | user_id, organization_id, role, pending/active status | Unique per user and tenant; explicit acceptance |
| `projects` | organization_id, name, client, nullable Decimal contract value, dates | FK to organization; scoped queries |
| `sites` | project_id, name, entered location description | Project access before site reads |
| `audit_logs` | actor, organization, action, target, before/after, reason, time | DB triggers block UPDATE and DELETE |

All identifiers are UUID strings rather than incrementing business counters. Unknown contract values are represented by SQL NULL. Money is stored as `NUMERIC(18,2)`, not binary floating point, but contract quantity and advanced calculation tables are Phase 4 work and must not be inferred from this core schema.

## Permissions
Roles: owner, project_manager, site_engineer, accounts and worker. Permissions are derived from server-side active membership rows and tenant ownership. Pending invitations confer **no data access** until the invited user signs in and explicitly accepts.

- Tenant owners create organisations and invite existing accounts.
- Owners and managers create projects.
- Owners, managers and site engineers create sites.
- Active members can read their organisation's projects and project sites.
- Owners and managers read their organisation's audit event history.
- Anonymous, inactive, unauthorised and cross-tenant requests are denied.

This is an initial role matrix, not final contractual or claim approval authority.

## Migration safety
Alembic provides `upgrade head` and a documented downgrade. Never automatically downgrade or overwrite production data. PostgreSQL and SQLite each use audit immutability triggers in the migration; development SQLite must enable foreign keys per connection. Before shipping, test PostgreSQL migrations, recovery, role revocation and permission policy with a security reviewer.

## Future tables
Evidence, upload/sync, Bill of Quantities, contracts, verified measurements, financial calculation records, variations, issues, claims, status histories and payments follow the roadmap's later phase order. No unimplemented table is represented as existing.
