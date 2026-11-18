# SitePay Agent concept

## Problem
Small and medium construction contractors often track site evidence in messaging apps, daily measurements in paper registers, contract quantities in spreadsheets, and submitted bills in separate files. Missing, contradictory or previously claimed quantities can delay certification and payment. The product targets evidence-to-payment work, not a general chatbot or a complete enterprise resource planning system.

## Primary users
- Small contractor or owner: a mobile workflow and reliable claim proof without an administration team.
- Site engineer: rapid photo, voice and measurement capture, low typing overhead and offline resilience.
- Project manager: trustworthy progress, exceptions and review queues.
- Office/accounts staff: auditable Bill of Quantities matching, prior claim reconciliation and financial breakdown.
- Subcontractor: traceable measurements and claim history.

Client or consultant portals and full accounting integrations are later phases, not first-release promises.

## Evidence-to-payment loop
1. A permitted user creates a project, site and contract, and imports the Bill of Quantities.
2. Site evidence is captured on a mobile device with an offline outbox that does not delete unsynchronised work.
3. Evidence is uploaded idempotently with its immutable original and source metadata.
4. A constrained AI extraction step proposes source-linked facts, units and confidence, without making payment decisions.
5. Human reviewers resolve ambiguous facts and conflicts.
6. Deterministic code connects accepted measurements to contract items and compares planned, previously claimed and certified quantities.
7. A rules engine flags missing evidence, unsupported variations, duplicates, rate mismatches and remaining quantities.
8. An isolated Decimal calculation engine produces amounts and a reproducible financial trace.
9. The agent drafts reports and claims; authorised humans review and approve.
10. Users track submission, certification, partial receipts, overdue position and remaining balance with an immutable audit trail.

## First release
India rule pack; English and Hindi interface; photos and voice notes with offline capture; spreadsheet Bill of Quantities import; validated extraction with sources and confidence; deterministic quantities, contract checks and a payment calculation engine; PDF and Excel exports; approval and audit; variation records and explicit evidence conflict review; manual payment lifecycle tracking.

## Deferred capabilities
Scheduling optimisation, inventory, full accounting integration, standalone portals, multiple country packs, automated submission, cash-flow forecasting, full dispute handling, electronic signatures and enterprise resource planning features belong to later phases unless an approved change request says otherwise.

## Current state
This is product intent, not a record of deployed features. Phase 0 validation, documented in `docs/21_product_validation_gate.md`, has not passed.
