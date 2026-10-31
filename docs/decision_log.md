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

## Phase 1 post-review corrections

- STUDENT-PROVIDED REVIEW: Phase 1 PASS WITH CONDITIONS, confirming original counts/provenance/reproducibility, with two correction requests: stale successful artifacts after a failed rerun and insufficiently explicit validation scope.
- CONFIRMED: Student approved only these corrections and the reviewed implementation plan; no Phase 2, source/Phase 0 changes, configuration edits, staging or commits.
- IMPLEMENTED: Immutable run directories, atomic RUNNING/FAILED/PASS latest_run.json and staged directory publication. Earlier top-level outputs remain historical; users determine latest-attempt success through the status record and its referenced artifacts/hashes.
- IMPLEMENTED: Optional keyword-only require_full_split=False preserves document/subset validation; returned scope is explicit. The full-dataset CLI uses True and rejects consistent partial coverage.
- LIMITATION: One writer per output directory. Unsafe/unwritable output preflight may prevent recording a new attempt; stderr/exit status then remain authoritative for that invocation. Power/storage-loss durability is not guaranteed.
- OPEN: Independent review of corrected code and evidence before declaring Phase 1 conditions finally closed. Research limitations and Phase 2 approval gates remain unchanged.
- OBSERVED: All 70 applicable tests pass. Two real-data repository runs validate FULL_SPLIT provenance for all 78,822 nodes and 120,664 edges; three deterministic artifacts match byte-for-byte. The real-data success-then-missing-manifest regression records FAILED without changing prior results. Source/Phase 0/configuration/staging preservation checks pass. Detailed commands and hashes are appended to results/phase1/validation_record.md. These observations support closure review of the two technical conditions, not Phase 2 approval or GIR-ER effectiveness.

## Phase 2 approval and method freeze

- CONFIRMED: Student approved Phase 2 only and the full implementation plan; no staging, commit, push, merge, Git configuration change or Phase 3 work.
- CONFIRMED: Train-only exact normalized-alias and exact-initialism discovery. Dev is limited to overlap/schema checking; test to fingerprint integrity.
- CONFIRMED: Provisional natural targets: 4 sparse, 4 different-name abbreviation, 8 challenging name collisions and 8 compatible-name/context cases, with no identity labels inferred from these categories.
- CONFIRMED: Discover all types, but sample only singleton PER/ORG/LOC groups; no repeated selected endpoints or matching alias/initialism keys. Fixed numeric source order and documented category priority; report shortages without retuning.
- CONFIRMED: Controlled-fragmentation feasibility only. No fragment nodes, controlled pairs, parent maps or edge reassignments. Actual attribution policy needs separate student approval.
- CONFIRMED: Keep raw train 3052 and dev 469 unchanged; exclude exact train-duplicate dev content from later dev evaluation and record affected IDs. Future evaluation needs source-group-aware partitioning.
- DESIGN: Explicit inference-field allowlist, separate source-rich private dossier and blank annotation sheet, unique output packages and atomic latest status. Private outputs are written without reading existing private material.
- OPEN: Independent identity annotation, source/licence authenticity, unavailable standalone research feedback, useful natural answer-impact cases, defensible controlled attribution if needed, later QA/evidence/baseline protocols and independent Phase 2 review.
- AI ASSISTANCE: Code, synthetic tests and documentation prepared with Codex assistance; synthetic checks are not empirical identity findings. Actual execution evidence must be reported separately, including any blockers.

### Phase 2 observed execution

- OBSERVED: Installed on student-created phase-two at the merged Phase 1 base; 113 repository tests pass (70 unchanged regressions plus 43 new synthetic tests).
- OBSERVED: Two actual CLI runs discover 856,836 proposed train pairs and select 24 unlabelled natural cases (4 sparse, 4 abbreviation, 8 challenging, 8 compatible); no shortfalls. Every train graph node/edge reconciles and all three raw fingerprints remain unchanged.
- OBSERVED: Four deterministic public artifacts and both initial private reviewer artifacts match across runs. Real success-then-missing-manifest rerun records FAILED while preserving earlier results; final repeat restores PASS. Private reviewer fields are blank, Git-ignored and never inference inputs.
- OBSERVED LIMITATION: Selected endpoints are LOC 35, ORG 11, PER 2; shared source documents link the 24 cases into eight components. Preserve this observed bias; do not present the sample as representative or independent.
- OBSERVED: Train 3052/dev 469 overlap is preserved and dev 469 recorded for later evaluation exclusion; no selected pair touches that group. Controlled fragmentation remains feasibility-only with zero fragments/maps/allocations.
- OPEN: Independent Phase 2 review and human identity annotation. No QA/identity effectiveness claim or Phase 3 approval follows from technical PASS. See results/phase2/validation_record.md for exact files, commands, failures, counts, hashes and remaining decisions.
