# GIR-ER Pilot: AGENTS.md

## Research context and authority

This repository hosts an *exploratory*, research-driven FYP pilot for GIR-ER: Graph Impact Risk-Aware Entity Resolution for Reliable Knowledge Graph Construction. The distinct, unvalidated hypothesis is whether candidate-specific counterfactual 2/3-hop query-answer changes, checked against independent source evidence, improve identity merge decisions beyond an equally informed ordinary matcher. Do not claim novelty or improvement without controlled results. Read the updated `GIR_ER_PyCharm_Codex_Plan.md` and authoritative project research context before proceeding. The existing `poc/` Git repository and `.gitignore` are already configured; do not recreate them.

Preserve text-to-KG entity consolidation scope. Keep extraction fixed for controlled comparisons. Do not redesign as chatbot, GraphRAG, GNN, full external KGGen/Graphusion reproduction, or deploy a UI during the pilot.

## Literature boundary update — 31 October 2026

LACE (2022) already formalises recursive collective ER, merge justifications, constraints, and possible/certain query answers; ASPEN (2024) implements LACE; LACE+ (2023) and ASPEN+ (2025) address local value merging and advanced preferred-solution criteria. **Do not claim novelty for these established features.** GIR-ER's *hypothesis* is the **incremental utility** of a source-evidence-conditioned, candidate-specific before-commit 2/3-hop answer-impact signal over an equally informed strong matcher. A constraint-aware comparator may be considered where compatible; an ad hoc imitation must not be described as a published ASPEN reproduction.

Before Phases 5–6, distinguish candidate identity evidence, source triple support, path composition validity, and resulting answer evidence. Separate matcher confidence, counterfactual impact, and final risk decision. In Phase 7 include a bounded A–B–C sequential two-order diagnostic (not a full collective ER reimplementation). Keep natural/controlled cases and isolated/sequential outputs separately reported.

## Data safeguards

- `data/raw/re_docred/` is immutable; hash and audit but never edit.
- `data/private_gold/` must be Git-ignored and evaluation-only. Inference modules must not read it.
- Do not treat different `vertexSet` groups or different documents as gold negative identities. `vertexSet` already groups within-document coreferent mentions.
- Controlled-fragmentation parent mappings are private and forbidden to inference/feature modules.
- Missing `labels[].evidence` means missing sentence pointer; it is not proof of error or contradiction.
- Preserve original source-triple and sentence references through graph-building and temporary merges.
- Query workloads/templates must not be selected after inspecting private labels to favour GIR-ER.
- Never manufacture gold candidate labels, QA answers, source quotes or experimental measurements.

## Implementation quality

- Prefer minimal deterministic Python (3.11+) with `networkx`, `pytest`, and explicitly justified optional dependencies. No LLM API call or cost without separate approval.
- Graph is directed, relation typed and provenance preserving. Simulated merges must not mutate input graphs. Query differences must ignore identifier-only changes.
- Every evidence judgement must be SUPPORTED, CONTRADICTED or UNRESOLVED under a written protocol; incomplete search cannot imply safety.
- Test negative cases, beneficial joins, no-change harmful joins, wrong IDs, missing provenance, timeout, rollback, and gold leakage.
- Matchers have comparable permitted evidence. The B3+same-evidence control is mandatory before impact-attribution claims.
- Preserve independent source evidence vs private reference labels; REVIEW is not ACCEPT.
- Report both experiment success and failures; small pilot size does not establish statistical generalisation.

## Process / stop gates

- Work on *one approved phase at a time* using `GIR_ER_PyCharm_Codex_Plan.md`. If Phase 0 has already been executed and reviewed, do not repeat it; otherwise execute only the approved Phase 0. Preserve existing Git and `.gitignore` configuration.
- Finish each phase with changed files, actual commands/output, test results, unresolved questions, research implications, and a STOP; do not auto-start later phases.
- Ask for explicit approval before selecting/scoring thresholds, adopting a risk formula, using human-generated labels as runtime inputs, paid API calls, deleting files, publishing data, or committing/pushing to a remote.
- Keep a concise `docs/decision_log.md` with genuine student-approved choices and status of open decisions; distinguish suggestions from confirmed decisions.
