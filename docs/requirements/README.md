# Requirements and verification

The authoritative PDF is *SitePay Agent: Project Roadmap, Build Plan and Operating Rules, Version 2.0*, 18 November 2026, including its Implementation Addendum. The PDF is the authority. This directory is its traceability index, not a replacement specification.

## Registries
- `roadmap_inventory.csv` tracks all **395 numbered file/folder deliverables** from the phase tables on PDF pages 13 to 27. Each has source order, exact path, phase, priority, status, test reference and result columns.
- `functional_requirements.csv` tracks **77 cross-cutting functional and governance controls** extracted for engineering traceability, including the addendum. These are a curated checklist rather than a claim that the PDF has exactly 77 requirements.

## Meaning of each status
- **Not started:** no implementation.
- **In progress:** actively being developed and not complete.
- **Blocked:** human evidence, approval or prerequisite missing.
- **Implemented:** source exists, with no claim that all tests passed.
- **Tested:** relevant automated or manual checks passed, but independent acceptance review is pending.
- **Verified complete:** evidence is linked, tests passed and an authorised reviewer accepted the requirement.

A file's existence is not proof that its feature works. The product-validation gate is still **blocked**, regardless of which Phase 0 source documents are present.

## Update protocol
For every completed change, link the source file, test path, exact CI or manual result and acceptance decision to the corresponding rows. Update the development log and decisions. No unsupported status promotions; never fake a CI run or measured user result. Source/customer test documents belong in access-controlled private storage, not this public repository.

## Automation
`scripts/tests/test_requirement_inventory.py` guards against missing rows, broken phase boundaries, duplicate entries, absent implemented files, invalid statuses and unevidenced verified claims.
