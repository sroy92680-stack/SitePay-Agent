# Phase 1 environment setup and release controls

## Configuration
Never commit populated `.env` files. Copy `.env.example` to `.env` locally, choose a random secret of 32 or more characters, a unique PostgreSQL password, and environment-specific credentials. The backend fails startup if its required database URL or token secret is absent.

## Run locally with Python
1. Install Python 3.12+, PostgreSQL and a local virtual environment.
2. Run `python -m pip install -e ".[dev]"`.
3. Export `SITEPAY_DATABASE_URL` as `postgresql+psycopg://...@localhost:5432/sitepay`.
4. Export `SITEPAY_JWT_SECRET` with an unpredictable value at least 32 characters long.
5. Run `python -m alembic -c backend/alembic.ini upgrade head`.
6. Run `uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`.
7. Check `http://127.0.0.1:8000/health/live` and `/health/ready`. The OpenAPI development contract is at `/docs`.

## Docker Compose development option
Set `SITEPAY_DB_PASSWORD` and `SITEPAY_JWT_SECRET` securely in an untracked `.env`. Run `docker compose up --build -d`; then, in a separate explicit operation, run `docker compose run --rm api python -m alembic -c backend/alembic.ini upgrade head`. Check `/health/ready` only after migration. The Compose file currently starts PostgreSQL and the **backend API only**; the mobile PWA is a later phase.

## Roles and example API
Use `POST /auth/register` to create a test owner account and organisation. Use the returned bearer token for `POST /projects`, `GET /projects` and `POST /projects/{project_id}/sites`. Existing users may be invited as pending members and must accept with `POST /organizations/{organization_id}/invitations/accept`.

## Deployment status
No staging cluster, production domain, TLS termination, cloud object storage, backup, operational monitoring or commercial deployment exists. Docker Compose is a **local development definition**, not a statement that production is running.

## Release gating
Maintain a versioned migration, run source checks and tests, complete security review and AI/finance gates for affected phases, stage the release, rehearse rollback and obtain owner approval. The mandatory Phase 0 product-validation and architecture freeze remains blocked. No automatic merge of the development branch.
