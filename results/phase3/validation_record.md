# Phase 3 actual validation record

Verdict: **PASS for technical implementation; scientific QA verification remains pending.** Ready for independent code/methodology review, not a verified-gold workload or approval of Phase 4.

## Starting state and authority

Planning began on clean main at 9c2fb77 (merged Phase 2 PR #3; local origin/main agrees). The unchanged preflight suite passed 113 tests in 1.08s; implementation-entry repeat passed 113 in 1.01s. Python remains 3.12.15 with NetworkX 3.7/pytest 9.2.0. No dependency/environment/configuration changes.

The sandbox denied branch creation (exit 128, phase-three.lock Operation not permitted). The student created phase-three; clean state and base commit were confirmed before repository code changes. Work remained on phase-three. No staging, commits, pushes, merge, remote action or new repository was performed. Live upstream freshness was not independently queried.

AGENTS.md, governing plan/amendments/Phase 3, README, data dictionary, decision log, candidate methodology, annotation guide, available master research context, audit/builder/candidate/worklist code, existing tests, public input manifests and Phase 0/1/2 validation/output contracts were inspected. Separate supervisor feedback, current proposal/literature drafts, critical review and primary papers remain unavailable locally. No supervisor decision or new primary-source comparison is invented.

## Design and frozen selection

Version phase3-structural-v1: exactly 2/3 outgoing original relation codes, simple paths with distinct vertices, optional type-set intersection constraints. Answer IDs deduplicate; occurrence paths retain original keyed edges and exact evidence states/arrays. Numeric source ordering is insertion-independent. Every published occurrence reconstructs against original labels/tokens. Original graph/source remain unchanged.

The student approved the 12-case mix and numeric source-order diversity before real selected answers were inspected. Methodology was written before the first real invocation. Endpoint reservations precede general cases, then zero diagnostics; 2 hops precede 3 in each role. One query per original document/anchor and no repeated relation sequence within hop length. No answer-count/semantic/outcome filtering or quota relaxation. Zero diagnostics use zero-outdegree anchors with unused observed relation sequences and separately recorded template examples.

100000 examined occurrence extensions per original document during discovery/per query evaluation is a computation cap. Exact-boundary natural completion is COMPLETE; further required work yields INCOMPLETE. Partial/empty answers cannot establish complete zero. Incomplete CLI discovery/evaluation fails explicitly without complete-workload publication. No cap was exhausted on actual train.

## Actual tests and failures

```bash
.venv/bin/python -B -m pytest -q -p no:cacheprovider
```

Final actual output: `159 passed in 1.44s`, exit 0 (113 unchanged existing tests plus 46 Phase 3 tests). Tests cover direction/sequence, 2/3 hops, zero/missing/wrong references, mixed types, duplicate/parallel occurrences, answer/path deduplication, exact pointer arrays, loops, budgets, shuffled insertion, private injection/reads, train-only discovery AND selection, quota shortages, full 12-slot role mix, blank review rows, old annotation preservation, output protections, publication failures, failed final PASS, status initialization and interruption.

Actual development failures, preserved rather than hidden:

- First installed suite: 1 failed, 154 passed (exit 1). The synthetic fixture tried augmented assignment to frozen SourceSplit.documents; fixed by constructing a new fixture source. No production contract changed. After envelope checks: 156 passed in 1.25s.
- First real CLI: exit 1 at discovery_and_selection, reason Invalid split or hop count. A zero-diagnostic generator reused the relation-list variable as its loop target, eventually yielding one code string. Fixed the variable binding and added a full 12-slot regression test. Latest status correctly recorded FAILED and no successful package was published. After the fix: 157 passed in 1.20s.
- Final hardening explicitly rejects dev/test at the selection interface in addition to discovery. Added status-initialization/final-PASS tests; final suite is 159. This changes no train selection rule or result.
- A documentation/edit patch was rejected atomically because it contained duplicate update operations for one test file; split/corrected before applying. No partial implementation from that rejected call.
- The real failure-check harness initially replaced the output flag rather than the manifest argument (argument parsing failure and harness assertion). Its next missing path was beside the temporary output, correctly rejected by input/output protection before status initialization. Corrected to a missing file outside the output root. These harness errors did not require production changes; the final intended regression passed.

## Actual real-data runs

This command completed successfully three times (exit 0), preserving each immutable run:

```bash
.venv/bin/python -B scripts/query_workload.py --data-dir data/raw/re_docred/data --manifest results/phase0/input_manifest.json --output-dir results/phase3 --review-dir data/private_gold/phase3
```

Actual final stdout:

```text
Phase 3 PASS: 12 structural queries; hops {2: 6, 3: 6}; 16 query/answer pairs; 23 occurrence paths
Train: 59359 nodes / 85932 edges individually validated; hashes unchanged
Outputs: results/phase3/runs/e71e70e24e264281b856e709f0555db7; private blank QA package: data/private_gold/phase3/runs/e71e70e24e264281b856e709f0555db7; preparation seconds: 18.143
```

The first two completed runs (33853cf3204b4d1894d2e2acf17e412e and 51a32745b8654b9f91683dd475f34b1f) preceded the explicit selector-boundary guard. Their source-derived deterministic results are unchanged; manifests preserve their actual implementation hashes. The final run and separate successful regression run both executed the final implementation and are the reproducibility comparison pair. No historical directories were deleted.

FULL_SPLIT source reconciliation: 3053 train documents, 59359 nodes, 85932 edges, 47260 nonempty and 38672 empty evidence-pointer occurrences, zero absent fields. Each original node/edge was checked, not just totals. Test is hashed only. Dev/test graphs were not rebuilt during Phase 3 and their annotations did not design queries. Phase 0/1/2 public references and recorded implementation hashes verified. No private historical annotations were read.

Discovery: 28585 relation/type patterns; 184983 two-hop and 320579 three-hop occurrence chains. Maximum examined extensions per document: 9267 of 100000. Source self-loops: 0. Repeated-vertex exclusions remain recorded per document and selected query; synthetic loop tests establish behaviour.

| Role | Hops | Target | Selected | Shortfall |
|---|---:|---:|---:|---:|
| candidate_endpoint | 2 | 1 | 1 | 0 |
| candidate_endpoint | 3 | 1 | 1 | 0 |
| general | 2 | 4 | 4 | 0 |
| general | 3 | 4 | 4 | 0 |
| zero_diagnostic | 2 | 1 | 1 | 0 |
| zero_diagnostic | 3 | 1 | 1 | 0 |

All 12 anchors/documents are distinct. Six queries per hop; 16 query/answer pairs and 23 occurrence paths overall. Independent direct source-JSON checking reconciled all 52 edge positions across those paths, including endpoint indices, relation codes and exact optional evidence lists. These are graph-theoretic answers, not semantic correctness findings. Two zero diagnostics have COMPLETE empty answer sets.

Endpoint feasibility: 31/48 Phase 2 endpoints anchor a two-hop chain and 26/48 a three-hop chain. Exactly two selected queries use Phase 2 endpoints. Coverage is not evidence of useful ER or multi-hop merge effects; no merge was simulated. Phase 2 remains LOC-heavy (35 LOC, 11 ORG, 2 PER endpoints) with eight source-linked components and uninspected private identity-review status.

Train 3052/dev 469 exact-content overlap and later dev-469 evaluation exclusion remain governing. Phase 2 public overlap inventory was verified; no new dev/test discovery or private outcome inspection occurred. Exact-text grouping is not entity/paraphrase-disjoint evaluation.

## Blank QA review package

Verified both new final-code packages contain 12 query entries, 12 QUERY CSV rows and 16 ANSWER rows. All 13 human fields are blank in CSV, query records and answer reviews; preparation status is NOT_ASSESSED. All returned occurrences reconstruct against original JSON through Phase 1. Registries preserve original mentions, spans, sentence/evidence arrays and rendered-view labels. Template examples are explicitly separate from actual supporting paths.

These initial private snapshots are Git-ignored and untracked. The generator read guard rejects private reads; initial private output hashes use write buffers. A separate evaluation-side verifier inspected only newly generated blank snapshots. No existing private identity/QA annotations or parent mappings were accessed as inputs. Human verification, confidence, adjudication and agreement are not claimed.

## Reproducibility and real stale-PASS regression

Final repository run: `runs/e71e70e24e264281b856e709f0555db7`. Comparison success: `/var/folders/j8/lzvjf1bn667_4z3tk_r4r0sw0000gr/T/girer-phase3-regression-zty8g13h/outputs/runs/9a03744d6ed5401ea424709fa22f34db`. Preparation times before publication: 18.143s and 18.016s (observations, not a benchmark).

All five deterministic public files and both initially blank private files match byte-for-byte. Every completed package matches its recorded artifact hashes; final code hashes match its run manifest. Runtime/invocation metadata and unique run IDs are excluded.

| Artifact | SHA-256 in both final-code executions |
|---|---|
| phase3_report.md | `34e07836711f71e3ea9a131cefcec578766681bacad0685d68608e34b9eb142c` |
| queries_train.json | `39c1a99255ef2e1f25cacdd01543fe329592d55c6b2a1f4b0295058d16347981` |
| query_feasibility_report.md | `30c1b176b0f0105690773db11936fdcce6c027e7ff519909d5c95b8f541987ac` |
| query_inventory.json | `b81424409c0e66dd79a7801b583f65dcf2239f2d3722416486e21e6aca8bdc25` |
| structural_query_results.json | `23152baea04df9e219b8b95afa34d6ca5e1823c3b44dbe508d17a5f169541c0f` |
| Private initial qa_review_dossier.json | `fa6c932b71ab8108467206d190f3ccdfbeeffdf11e17b6e5df63ed8d18af6795` |
| Private initial qa_review_worklist.csv | `13c0301d6d829c1bf2d9e695f7af5f9c3fde0d181bf3c00756b31965b13ea855` |

Actual successful separate-output command (exit 0):

```bash
.venv/bin/python -B scripts/query_workload.py --data-dir data/raw/re_docred/data --manifest results/phase0/input_manifest.json --output-dir /var/folders/j8/lzvjf1bn667_4z3tk_r4r0sw0000gr/T/girer-phase3-regression-zty8g13h/outputs --review-dir data/private_gold/phase3/regression
```

Actual missing-manifest rerun in that same location (exit 1):

```bash
.venv/bin/python -B scripts/query_workload.py --data-dir data/raw/re_docred/data --manifest results/phase0/missing_phase3_manifest.json --output-dir /var/folders/j8/lzvjf1bn667_4z3tk_r4r0sw0000gr/T/girer-phase3-regression-zty8g13h/outputs --review-dir data/private_gold/phase3/regression
```

Actual stderr:

```text
Phase 3 failed at baselines_and_sources: [Errno 2] No such file or directory: 'results/phase0/missing_phase3_manifest.json'
```

The latest record became FAILED at baselines_and_sources with FileNotFoundError and run_directory=null. Every file in the previous successful public/private packages remained byte-identical. The repository latest record remains PASS, as the deliberate failure used its own output location. Pre-initialization failures establish no new recorded attempt and cannot be attributed to an older PASS.

## Preservation and exact files

All baseline files other than the three expressly updated documentation files remain byte-identical, including raw sources, earlier implementation/tests/results, AGENTS.md, governing plan, dependencies and .gitignore. Staging index SHA-256 and cached diff match baseline. git diff --check exited 0. No private files are tracked.

| Source | Before/after SHA-256 |
|---|---|
| dev | `051ee1d057204a5d08ef5502beacdadf191245b5eaf0e29ec2c607cf002c016f` |
| test | `ea673b7ef91e16510d7eb88863d3903e47318dc5653ef361266f27ae3b84723c` |
| train | `c40a137a1c57f3e2daaf5ebf511eaa1518f9305ffaa3052d46271921a91826f2` |

Modified: README.md; docs/data_dictionary.md; docs/decision_log.md.

New implementation/tests/docs:

- scripts/query_workload.py
- scripts/prepare_qa_worklist.py
- tests/test_query_workload.py
- tests/test_qa_worklist.py
- docs/phase3_query_methodology.md
- docs/qa_annotation_guide.md

New repository public outputs:

- results/phase3/latest_run.json
- results/phase3/validation_record.md
- results/phase3/runs/33853cf3204b4d1894d2e2acf17e412e/phase3_report.md
- results/phase3/runs/33853cf3204b4d1894d2e2acf17e412e/queries_train.json
- results/phase3/runs/33853cf3204b4d1894d2e2acf17e412e/query_feasibility_report.md
- results/phase3/runs/33853cf3204b4d1894d2e2acf17e412e/query_inventory.json
- results/phase3/runs/33853cf3204b4d1894d2e2acf17e412e/run_manifest.json
- results/phase3/runs/33853cf3204b4d1894d2e2acf17e412e/structural_query_results.json
- results/phase3/runs/51a32745b8654b9f91683dd475f34b1f/phase3_report.md
- results/phase3/runs/51a32745b8654b9f91683dd475f34b1f/queries_train.json
- results/phase3/runs/51a32745b8654b9f91683dd475f34b1f/query_feasibility_report.md
- results/phase3/runs/51a32745b8654b9f91683dd475f34b1f/query_inventory.json
- results/phase3/runs/51a32745b8654b9f91683dd475f34b1f/run_manifest.json
- results/phase3/runs/51a32745b8654b9f91683dd475f34b1f/structural_query_results.json
- results/phase3/runs/e71e70e24e264281b856e709f0555db7/phase3_report.md
- results/phase3/runs/e71e70e24e264281b856e709f0555db7/queries_train.json
- results/phase3/runs/e71e70e24e264281b856e709f0555db7/query_feasibility_report.md
- results/phase3/runs/e71e70e24e264281b856e709f0555db7/query_inventory.json
- results/phase3/runs/e71e70e24e264281b856e709f0555db7/run_manifest.json
- results/phase3/runs/e71e70e24e264281b856e709f0555db7/structural_query_results.json

New ignored private snapshots (never commit):

- data/private_gold/phase3/runs/33853cf3204b4d1894d2e2acf17e412e/qa_review_dossier.json
- data/private_gold/phase3/runs/33853cf3204b4d1894d2e2acf17e412e/qa_review_worklist.csv
- data/private_gold/phase3/runs/51a32745b8654b9f91683dd475f34b1f/qa_review_dossier.json
- data/private_gold/phase3/runs/51a32745b8654b9f91683dd475f34b1f/qa_review_worklist.csv
- data/private_gold/phase3/runs/e71e70e24e264281b856e709f0555db7/qa_review_dossier.json
- data/private_gold/phase3/runs/e71e70e24e264281b856e709f0555db7/qa_review_worklist.csv
- data/private_gold/phase3/regression/runs/9a03744d6ed5401ea424709fa22f34db/qa_review_dossier.json
- data/private_gold/phase3/regression/runs/9a03744d6ed5401ea424709fa22f34db/qa_review_worklist.csv

Separate regression public artifacts remain under `/var/folders/j8/lzvjf1bn667_4z3tk_r4r0sw0000gr/T/girer-phase3-regression-zty8g13h/outputs`; its latest record intentionally shows FAILED. Temporary verification evidence is under /tmp/girer_phase3_* and is not a repository artifact.

## Scientific limits and next gate

Technical acceptance passes. Correct traversal and exact annotation provenance establish neither interpreted relation composition nor independently supported answers. Complete zero is graph absence only. Source-order/diversity/diagnostic selection is biased; 12 cases are not an independent representative evaluation sample. No candidate utility or GIR-ER improvement follows from coverage or answer counts.

Before Phase 4, the student must review interpretations and individual triple/path/answer evidence, preserve UNKNOWN/UNRESOLVED, determine usable cases and annotation effort, handle source-linked evaluation partitions and explicitly approve the next phase. Current identity-review status was intentionally not inspected. Licence/release authenticity and authoritative relation definitions remain unresolved. A final scientific QA workload must not be declared verified/frozen yet.

Limits: exact fixed-depth enumeration can grow with occurrence multiplicity and returns INCOMPLETE at its cap; one writer per output root; no cross-directory transaction/power-loss guarantee; orphan packages may remain after failures. Future unwritten inference modules need their own leakage tests. Code/tests/docs are AI-assisted and require student ownership and independent review.

No fragment creation, identity merge, temporary merge, before/after comparison, answer delta, evidence classifier, baseline, risk score, API or UI was implemented. LACE/ASPEN prior-art boundaries and B3+same-evidence remain governing.

**STOP after Phase 3. No Phase 4 without explicit approval.**
