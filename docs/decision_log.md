# GIR-ER decision log

| Status | Choice / issue | Authority |
|---|---|---|
| CONFIRMED | Phase 0 only; preserve JSON and existing Git/ignore configuration; use existing Python 3.12.15 environment | Student implementation approval, 31 October 2026 |
| CONFIRMED | Re-DocRED annotations may be fixed extracted graph inputs equally available across methods; they are not independent truth verification | Student selected option during Phase 0 planning |
| CONFIRMED | Reserve test from candidate/query design; allow schema, integrity, aggregate coverage and overlap inspection | Student selected option during Phase 0 planning |
| CONFIRMED | Updated LACE/ASPEN/ASPEN+ research boundaries apply; no reproduction required in Phase 0 | Updated AGENTS.md and student instruction, 31 October 2026 |
| IMPLEMENTATION DEFAULT | 100000 attempted edge extensions per document, depth at most three; deterministic order; incomplete flag if exhausted | Computational bound chosen for the approved bounded audit, not a scoring threshold |
| OBSERVED | Exact train/dev sentence-content overlap; raw JSON tracked; docs ignored; private gold not ignored | Local audit/Git checks; no files removed or Git settings changed |
| OPEN | Correct Git exclusions before private annotation or publication | Student decision needed; no private gold produced |
| OPEN | Acquisition/version/licence and authoritative relation definitions | Not supplied locally |
| OPEN | Overlap exclusion/grouping policy for future development/held-out partitions | Audit reports locations; no partition altered |
| OPEN | Genuine identity cases, source adjudication, controlled fragmentation and edge allocation | Later phase review; group separation is not negative identity gold |
| OPEN | Semantically interpretable patterns, independent QA references and frozen workload | Later phase review; structural counts only now |
| OPEN | Evidence targets/protocol, risk policy, thresholds, optional constraint comparator and sequential diagnostic | Future phase-specific student approvals; none adopted here |
| OPEN | Phase 1 entry | Data are technically usable; Phase 1 still requires student approval |

## Phase 1 update

The table above records Phase 0 status and is retained as history. The student subsequently approved the complete Phase 1 plan and clarified preservation of staging, exact per-record validation, repeated deterministic artifacts and before/after source hashes. Phase 1 entry is therefore approved; Phase 2 entry remains OPEN.

| Status | Choice / issue | Authority |
|---|---|---|
| CONFIRMED | Phase 1 only; no staging, commits, pushes or unrelated Phase 0 changes | Student implementation approval in this session |
| CONFIRMED | One document-scoped node per original group; one keyed directed edge per relation occurrence, preserving isolates/loops/duplicates | Approved Phase 1 plan |
| IMPLEMENTED | NetworkX MultiDiGraph; explicit split/index IDs; deep-copied node/edge source fields; external source lookup; document hash verification | Approved design implemented with installed NetworkX 3.7 |
| OBSERVED | All raw source fingerprints match Phase 0 before implementation | Local preflight |
| OBSERVED | Git is clean at entry; private gold and research context are now ignored, general docs are tracked; raw JSON remains tracked | Current Git preflight; no configuration changed by Phase 1 |
| STUDENT-REPORTED | Independent Phase 0 review verdict: PASS WITH CONDITIONS | Student statement; detailed review is unavailable locally |
| OPEN | Unseen independent-review conditions cannot be classified as satisfied | Obtain review text before asserting condition closure; no demonstrated Phase 1 blocker found in available material |
| DEFERRED | Source licence/authenticity, relation semantics, train/dev overlap partition policy and independently checked identity/QA references | Preserve Phase 0 limitations; no labels or workload selected |
| OPEN | Phase 2 entry, case preparation and annotation safeguards | Requires explicit student approval; no candidate/fragmentation work started |

Phase 1 execution observed exact reconciliation on train/dev/test: 78,822 nodes and 120,664 edges validated individually. All 51 applicable tests passed. Raw JSON fingerprints remained unchanged. Final repeated-run and staging-integrity evidence is recorded in results/phase1/validation_record.md. These observations establish software/provenance correctness on the supplied annotations, not independent factual verification or GIR-ER effectiveness.

Code, tests and report drafts were generated with Codex assistance. Synthetic fixtures test mechanics only and are not research observations. No supervisor approval of a risk rule, final dataset or empirical improvement is asserted.
