# Deterministic financial specification audit

**State: draft, not an implemented finance engine.** Source: roadmap Parts 4, 12 and 13, plus Addendum 6.

## Essential input provenance
Project and contract identifier, contract version, Bill of Quantities item code, unit, original contract quantity and rate, approved variation quantity and rate, evidence-linked verified current measurement, previous claimed quantity, previous certified quantity, prior paid amount, retention and release conditions, advance balance/recovery policy, tax parameters, deductions, currency and approved country rule-pack version.

Every input must be verified and attached to an immutable source. Absence or conflicting values must block consequential calculations or final approval rather than trigger guessed defaults.

## Core principles
- Store money as exact decimal values with defined currency precision, never binary floating point.
- Distinguish measured, claimed, certified and paid ledgers. A previous claim is not equivalent to previous certification.
- Use explicit unit conversions and reject incompatible units.
- Reject quantities exceeding remaining approved contract scope unless an approved variation covers the excess.
- Retention, deductions, tax and advance recovery order must be a versioned per-contract policy, reviewed by an appropriate finance specialist.
- A model may propose an item match, but it cannot modify a verified quantity or authoritative financial result.
- Save engine version, rule-pack version, source references, intermediate amounts and final reconciliation trace.

## Formula constraints
For each line, candidate current quantity must come from a reviewed measurement and not exceed remaining permitted claimable quantity. Gross line amount is derived deterministically from the accepted quantity and applicable approved rate. Aggregation and deductions follow explicit contract definitions.

**Do not assume universal India tax rates, withholding, retention or rounding values.** The source does not establish a sufficient claim-specific financial policy. Missing terms remain unresolved, flagged and prevent final financial certification.

## Test matrix required before claiming finance completion
- Exact decimal representation and deliberate rounding boundaries.
- Zero or negative quantity, unsupported unit, missing contract rate and over-claim.
- Previously claimed quantity greater/less than previously certified quantity.
- Variation before and after approval.
- Multiple currencies or mismatched tax configuration rejected.
- Retention release condition and advance recovery limit.
- Duplicate source record or a repeated claim line.
- Partial certification and receipts not conflated with claim gross.
- Reproduction of every output from persisted inputs, rule versions and engine version.
- Strict access checks and immutability of approved calculation records.

## Open decisions
Policy approval for taxes, arithmetic order, retention, advance recovery, certificates, tender unit conversion, currency and final-rounding placement is required before Phase 4. Any future change requires an approved versioned migration and regression tests.
