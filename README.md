# SitePay Agent

Evidence-based construction site progress and payment-claim intelligence for small and medium contractors, site engineers, project managers and payment staff.

> **Branch status: Phase 1 backend under development and tested in CI. The Phase 0 product-validation gate is still blocked, and the construction payment application is not completed or deployed.** This branch must not be merged or treated as production-ready without explicit gate approval.

## Product mission
SitePay Agent connects site photographs, voice notes, drawings, Bill of Quantities items, measurements, contract terms, previous claims and certifications. It should surface missing or conflicting evidence, use deterministic quantity and financial rules to draft supported payment claims, and require qualified human review for consequential actions.

The agent **never invents evidence or financial amounts, autonomously certifies work, authorises payment or submits a legally consequential claim**.

## Roadmap and implementation order
The governing source is *SitePay Agent: Project Roadmap, Build Plan and Operating Rules, Version 2.0*, 18 November 2026, including its Implementation Addendum. It specifies 395 ordered file/folder deliverables across 11 phases (0 to 10), source ownership rules, acceptance gates, test standards and a mandatory pre-development validation stage.

- [395-file master inventory](docs/requirements/roadmap_inventory.csv) tracks source locations, priorities, phases and status.
- [77 cross-cutting requirements](docs/requirements/functional_requirements.csv) track functional, security, financial, AI and operational controls.
- [Product validation gate](docs/21_product_validation_gate.md) is blocked until customer interviews, observed claims and permissioned pilot evidence exist.
- [Readiness audit](docs/audits/readiness_audit.md) records what can and cannot be verified.
- [Architecture proposal](docs/04_architecture.md) and [open design conflicts](docs/audits/specification_conflicts.md) document decisions required before application work.
- [Engineering rules](PROJECT_RULES.md) and [contributor guide](CONTRIBUTING.md) apply to every change.

## Repository status (18 November 2026)
Phase 0 source documentation and checking tools are committed directly to GitHub. On the gated `development/phase1-backend` branch, Python/FastAPI endpoints and migrations are being built and tested, with no deployment or business acceptance claimed. **20 of 21 Phase 0 listed file deliverables exist.** The `LICENSE` file remains blocked because the owner has not selected distribution terms. Some Phase 0 deliverables are only drafts and have not passed their business acceptance gates. The early CI workflow is deliberately present to validate Phase 0 source rules.

Relevant GitHub issues:
- [#1: Validate the product, pilot and architecture](https://github.com/sroy92680-stack/SitePay-Agent/issues/1)
- [#2: Approve the canonical payment lifecycle](https://github.com/sroy92680-stack/SitePay-Agent/issues/2)
- [#3: Confirm financial and India policy assumptions](https://github.com/sroy92680-stack/SitePay-Agent/issues/3)
- [#4: Choose distribution licence](https://github.com/sroy92680-stack/SitePay-Agent/issues/4)

## Reproduce the available Phase 0 checks
Requires Python 3.12 or newer and a Git checkout of this repository. These commands run the **foundation checks**, not a functioning application.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python scripts/check_project_rules.py .
python -m pytest -q scripts/tests
ruff check scripts
python -m compileall -q scripts
```

On Windows, activate with `.venv\Scripts\activate`. GitHub Actions runs the same checks automatically; inspect the [CI workflow and actual run history](https://github.com/sroy92680-stack/SitePay-Agent/actions).

## Planned system architecture
Python 3.12/FastAPI; PostgreSQL; React/TypeScript offline-capable Progressive Web App; protected S3-compatible original object storage; constrained, evaluated vision and language extraction; versioned Decimal financial calculations; HTML-to-PDF and openpyxl exports; append-only audit, tenant and role checks; pytest, Vitest, Playwright and golden AI evaluation. None of those runtime modules should be represented as operational until their respective phase tests and gates pass.

## Privacy and security
Never commit customer documents, site photos of real people, bank data, secrets, private keys, access tokens or populated `.env` files. Original evidence, financial results and approvals require immutable provenance and appropriate access. Public repository access is not permission to use construction project data.

## Completion standard
A CI pass currently shows source-policy enforcement and register integrity only. It **does not** mean authentication, offline capture, finance, claim approvals, AI extraction, deployment or pilot acceptance passed. The project remains incomplete until the documented phase exits and final readiness gate pass.

## Licensing
No source-code licence has been granted. The roadmap owner must choose and authorise distribution terms before a `LICENSE` file is added. See issue #4.

## Backend development branch

The `development/phase1-backend` branch adds the first working API: registration, sign-in, JWT authentication, owner-reviewed membership invitations, tenant-scoped projects, site records and immutable audit logging. It provides a versioned Alembic migration, development Docker Compose and automated SQLite integration tests, plus separate PostgreSQL migration and container-build jobs.

Run it only with synthetic test accounts. Installation, migration and local startup instructions are at [Environment setup](docs/26_environments_and_release_process.md). You must create an untracked `.env` with your own random credentials. The `/docs` endpoint describes the available API.

**The Phase 1 phase-exit and Phase 0 gates have not been signed.** No file or test represents a completed AI agent, payment claim engine, offline mobile application or commercial release.
