# Engineering change control

The roadmap freezes the architecture at the end of Phase 0. No material financial, schema, contract, AI, or security design changes may bypass an approved change request.

1. Open a change record with reason, affected requirements, files, dependencies, schema and migrations.
2. Describe threat-model impact, financial and contractual consequence, AI/tool authority impact, data migration and tenant implications.
3. Define acceptance criteria, tests, evaluation metrics, rollout and rollback.
4. Obtain owner approval before the dependent work starts.
5. Implement on a reviewable branch with meaningful commits, and verify CI, security and financial regression suites.
6. Record the deployment stage and explicit release decision. Preserve original customer data.

## Unresolved specification decision
The base roadmap and implementation addendum differ on detailed payment lifecycle state names. Do not silently choose either for production. Record all states, transitions, invariants and migration impact in a change request and secure sign-off before implementing Phase 6.

## Change request template
See `docs/change_requests/change_request_template.md`.
