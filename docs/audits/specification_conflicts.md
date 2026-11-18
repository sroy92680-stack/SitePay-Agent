# Material specification differences requiring review

## SC-01: Claim lifecycle status labels
**Status: unresolved, blocked for claim state-machine implementation.**

Roadmap Part 11 (page 50) defines: Draft, In internal review, Approved internally, Submitted, Received by client, Under client review, Queried, Rejected, Revision requested, Revised claim submitted, Certified, Partially paid, Fully paid, Overdue, Dispute or escalation, Closed.

Implementation Addendum item 1 (appendix page 1, PDF page 68) defines: Draft, Ready for Review, Submitted, Receipt Confirmed, Under Review, Query Raised, Revision Required, Revised and Resubmitted, Approved, Partially Certified, Certified, Partially Paid, Paid, Overdue, Disputed, Cancelled.

Differences affect state naming, internal approval versus externally approved, rejected, partially certified, disputed/cancelled/closed, revision versioning, and transition permissions. Both lists are part of the approved-source candidate. Neither can be silently dropped.

### Required resolution
Propose a canonical, versioned internal state machine with separate dimensions for internal review, client certification, payment settlement and calculated overdue status. Define lossless mappings from both document vocabularies, allowed transitions, role permissions, terminal states, audit and migration behaviour. Record decision and obtain owner sign-off before Phase 6.

## SC-02: Product scope and later lifecycle automation
Part 3 excludes automatic overdue reminders, dispute management and forecasting from the first release; Part 11 includes manual lifecycle tracking and a calculated Overdue state in Phase 6. The addendum mentions reminder and escalation drafts without automatic external sends. Track status and calculate due dates in the release; defer auto-notifications and dispute workflow until the roadmap's later phase, pending scope approval.

## SC-03: Required owner tag in syntaxes without hash comments
The roadmap explicitly requires the exact owner text but allows language-appropriate comment syntax. Use the same marker within //, /* */, <!-- --> or -- comments. It must be the very first line of code files and must not violate language parsers.

## SC-04: Financial and tax calculations with insufficient contract evidence
The roadmap specifies Decimal arithmetic, rule packs and an India launch but does not provide a complete legally reviewed contract-specific tax and rounding rule for every claim. Until actual clause and tax rules are supplied and signed off, the engine must treat those parameters as missing and block final approval. Do not invent defaults or perform final legal interpretation.
