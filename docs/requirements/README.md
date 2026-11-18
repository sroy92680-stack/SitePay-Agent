# Roadmap implementation register

This master tracker was transcribed from the phase-by-phase tables on pages 13 through 27 of the authoritative **SitePay Agent Roadmap Version 2.0 (18 November 2026)**. It contains precisely 395 numbered file and folder deliverables. The `order`, path, phase and priority columns follow the PDF, without speculative changes.

## Status rules

- Not started: no implementation or test evidence
- In progress: an implementation task is actively underway
- Blocked: a named dependency is missing
- Implemented: source exists, but tests and validation may still be outstanding
- Tested: relevant tests were executed successfully, but acceptance review is pending
- Verified complete: test evidence plus phase acceptance and reviewer sign-off exist

**Implementation existence is not product completion.** A file can be present while its phase remains blocked. The document only records source paths present at register-generation time. Files added later require a tracker update. No code, API, finance module, offline sync, commercial launch, pilot or deployed application is asserted to be finished simply because the row exists.

## Source requirements
- The 395 file deliverables are tracked by `roadmap_inventory.csv`.
- Functional, security, financial, human approval, AI and operational requirements must also be tracked, with source page, code reference, test and result, before being marked verified.
- The Phase 0 gate register is `docs/21_product_validation_gate.md`.
- No sample source documents or private pilot data should be committed to this public repository.
- The implementation addendum introduces additional audit checks that remain subject to the same sign-off process.

## Current gate
Phase 0 product validation is **blocked**. See GitHub issue #1. The project is not a finished application.
