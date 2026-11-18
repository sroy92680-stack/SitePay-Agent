# Strict operating rules

This document extends `PROJECT_RULES.md`. The authoritative language is in Roadmap Part 4 (pages 7 to 9) and must be consulted if a summary is ambiguous.

## A. Project
- Evidence first. Every claim line requires proof with a stable source reference.
- Qualified human review before final reports, approved variations, submitted consequential claims and payment decisions.
- No guessing. Preserve missing fields and conflicting observations.
- The first workflow is site progress evidence to draft payment claim.
- Phase exit gates must pass in order.
- Uploaded originals are not overwritten or deleted; derivatives are separate.
- Immutable append-only audit of actor, event, before/after, reason and time.
- Accessibility and usability for non-technical site users.

## B. Code
- Exact first-line owner comment on code: `#Owner::ANIKET::ANHOTRA = MR.Panda`; adapt syntax for the language.
- No placeholder implementations, magical constants or duplicate responsibilities.
- Files fewer than 300 lines. Descriptive names, Python types and docstrings.
- Quantity, finance and rounding are deterministic code outside models.
- Secrets outside version control, tests with every feature and formatter/linter enforcement.
- Small meaningful commits with reviewable changes.

## C. AI
- Schema-validated structured output with mandatory units, confidence and original source reference.
- Below-threshold extraction requires human review. Conflicting evidence is never silently merged.
- Only approved registry tools may run, with explicit user/tenant permissions.
- Versioned prompts and model records. Evaluate changes on permitted, representative golden-set cases.
- A failing regression gate prevents production model/prompt release.
- Uploaded prompts and text are untrusted data, not executable instructions.

## D. Language
- Plain English or Hindi, following the person's selected language.
- Explain shortened terms on first use.
- Do not use em dash punctuation in code, reports, interface or documentation.

## E. Privacy and security
- Enforce tenant isolation in each query and background task, with explicit role permissions.
- Protect personal faces in site photographs where required.
- Encryption in transit and at rest; masked payment details; customer data exports/deletions through controlled requests.
- Follow applicable laws and obtain consent for pilot samples. No real client documents in the public repo.

## F. Finance
- Versioned Decimal-based engine, clear precision and country-pack rounding policy, separate from the AI agent.
- Record input provenance, rule versions, engine versions, intermediate calculations and outputs.
- Never claim more than the remaining contract quantity without approved variation coverage.
- A contract entitlement flag is not legal advice or authorisation.

## G. Evidence conflict and offline
- Show both contradictory records and an authorised resolution with reason, actor and time.
- Persist offline records durably until server acknowledgement; no silent data loss.
- Fingerprint duplicates and use idempotent ingestion and explicit edit version conflicts.
- Show pending, synchronised and failed items and allow retry.

## H. Change and release
- Freeze the architecture only with a signed Phase 0 decision.
- Significant changes require an approved change record and rollback.
- Regression evaluation, automated testing and security review precede staging and production.
- Never claim completion without acceptance and test evidence.
