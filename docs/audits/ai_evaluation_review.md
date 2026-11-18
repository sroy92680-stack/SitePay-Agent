# Controlled AI evaluation specification

**Status: draft; no real or synthetic golden case is claimed evaluated.**

## Roles and prohibited authority
AI may identify work type, text, possible item matches, locations, related evidence, uncertainty and suggestions. It must not calculate authoritative totals, certify work, legally interpret entitlement, bypass role permissions, approve variations or submit consequential claims.

## Mandatory structured extraction fields
Task and source reference; original file identifier and page/timestamp; language; work location; item candidate; unit and candidate measured value, only if explicitly supported; extraction confidence; model ID; prompt version; processing time; human review state. Missing, unclear and contradictory values must remain explicit.

## Golden-set categories
1. Site photographs with ambiguous or incomplete visibility.
2. Hindi and English voice notes, including noisy recordings.
3. Bills with duplicate vendor numbers and altered amounts.
4. Measurements with unknown or conflicting units.
5. Revised drawings versus old drawings.
6. Bill of Quantities item matching and unmatched scope.
7. Missing supporting documents and low-confidence requests.
8. Adversarial prompt injections embedded in uploaded files.
9. Requests to override finance or approval controls.
10. Workflow retries, model timeout, malformed output and conflicting evidence.

## Metrics
Extraction precision/recall by task, Bill of Quantities matching accuracy, evidence classification quality, missing-document detection, conflict recall, transcription quality per language, hallucination incidence, false alarm rate, valid schema rate, tool selection accuracy, prohibited-action rejection, workflow completion, p95 latency and model cost. Critical financial hallucination must be zero in acceptance tests.

The roadmap requires at least 50 initial golden evaluation cases, 90 percent or better seeded discrepancy detection and a false alarm rate within configured thresholds. Choose all thresholds from the roadmap and recorded task requirements before trial.

## Regression gate
Every prompt, model, tool or agent-orchestration change runs the approved evaluations. Record permitted dataset version, prompt/model ID, threshold, pass/fail, reviewer and release outcome. Reject a production promotion if any critical safety or finance category worsens. Tests may contain labelled synthetic cases, but they cannot be presented as real pilot evidence.

## Current findings
Provider configuration not established; consented golden data missing; prompt and tool registry not implemented; no scoring run or regression evidence exists. Evaluation release gate remains blocked by Phase 3 prerequisites.
