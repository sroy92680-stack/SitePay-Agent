# SitePay Agent

An evidence-based construction progress and payment-claim intelligence platform for contractors, site engineers and project managers.

**Current status: Phase 0 foundation. This repository is not yet a functioning construction payment application.**

## Source of truth

The authoritative specification is *SitePay Agent: Project Roadmap, Build Plan and Operating Rules, Version 2.0, 18 November 2026*, including the Implementation Addendum. It defines 395 globally ordered file/folder entries, 11 development phases (0 to 10), strict evidence and human-approval rules, and a mandatory product-validation gate.

## Product mission

- Capture site photos, voice notes, documents and measurements, including durable offline storage.
- Link extracted facts to original source records, location, confidence and units.
- Compare completed work with the Bill of Quantities, contract terms and previously claimed/certified quantities.
- Flag missing evidence, duplicates, contradictions and unapproved extra work.
- Calculate all financial amounts using deterministic, versioned decimal arithmetic, never model-generated final figures.
- Draft progress reports and payment claims with a full calculation trace and human review/approval.
- Track claim submission, certification, payment records, outstanding amounts and audit histories.

## Strict engineering rules

No invented evidence or financial figures, no autonomous approvals or payments, tenant-isolated access, protected originals, append-only audit, source-tagged code, meaningful tests, reproducible calculations and permissioned test data. Never commit API keys, .env files, private documents or real client records.

## Phase 0 work and blocker

A Phase 0 local engineering package has been produced with project governance, source policy checks, architecture drafts, an issue/risk register, 395 file-level requirements and 77 cross-cutting functional requirements. **The local checks passed 13 tests and verified 34 text files against the repository policy. These results are local, not GitHub CI results.** The complete local package is available as a downloadable archive from the project execution conversation, not yet uploaded to this repository.

The mandatory validation gate is not passed. It requires 5 to 10 real participant interviews, observation of a real payment claim, permissioned sample documents, pilot commitments, an approved scope and a signed architecture decision. See [Phase 0 validation issue](https://github.com/sroy92680-stack/SitePay-Agent/issues/1). Phase 1 application code must not be described as implemented until the gate is passed.

The original roadmap's claim lifecycle labels differ from the implementation addendum's labels. A canonical state machine requires explicit review before Phase 6.

## Planned technology

Python 3.12 / FastAPI, PostgreSQL, React / TypeScript Progressive Web App, private S3-compatible storage, durable device outbox, a constrained multimodal AI provider, deterministic Decimal financial engine, HTML-to-PDF, openpyxl, pytest, Vitest and Playwright.

## Important limitation

This repository currently does **not** contain a deployable application. Completion, production deployment, verified financial calculations, independent security audit and pilot outcomes must not be claimed before actual implementation and testing.
