# Change summary

Describe the user-visible or internal engineering change and link the numbered roadmap requirements. Do not claim a phase gate is passed without signed evidence.

## Requirement traceability
- Roadmap order / control IDs:
- Exact source pages and implementation files:
- Modules and API/database dependencies:
- Acceptance criteria and tests:

## Security and finance impact
- Tenant boundaries and role checks:
- Uploaded or personal data handling:
- Contract, quantity, tax or financial effects:
- AI output/trusted-tool effects:
- Migration and rollback considerations:

## Verified testing
- [ ] Repository rule checker passed
- [ ] Relevant Python and API integration tests passed
- [ ] PostgreSQL migration and constraint tests passed if schema changed
- [ ] Container build and configuration checked if deployment changed
- [ ] Test failures and skipped cases documented
- [ ] No sample customer records, private assets or secrets committed
- [ ] Reviewers approved the risk and architecture impact

## Gate status
- Phase 0 interviews and real workflow evidence:
- Scope freeze and owner approval:
- Phase 1 backend acceptance decision:
- Production deployment status:

When the gate is blocked, the pull request stays unmerged. A green CI does not imply business validation or production readiness.
