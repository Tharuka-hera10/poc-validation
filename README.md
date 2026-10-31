# GIR-ER exploratory pilot — Phases 0–3

This repository audits the local Re-DocRED annotations for a future entity-consolidation pilot. GIR-ER's incremental benefit is an unvalidated hypothesis. Phase 0 creates no identity labels, verified QA answers, merge decisions or performance results.

Use the existing Python **3.12.15** environment; no runtime packages need installing:

```bash
.venv/bin/python -B scripts/audit_dataset.py --data-dir data/raw/re_docred/data --output-dir results/phase0
.venv/bin/python -B -m pytest -q -p no:cacheprovider
```

`requirements-dev.txt` pins the already installed pytest. The standard library handles the audit; NetworkX, pandas and RapidFuzz are not needed in this phase. In PyCharm, select `poc/.venv/bin/python`; the IDE's active selection was not independently confirmed.

The audit reads only the three named JSON files. Raw files stay byte-identical. Outputs contain input hashes, schema diagnostics, descriptive statistics, environment metadata and train/dev structural patterns. See [the generated report](results/phase0/audit_report.md), [the Phase 0 feasibility assessment](results/phase0/feasibility_report.md), and [the data dictionary](docs/data_dictionary.md).

`--max-extensions-per-document` defaults to **100000 attempted edge extensions** in deterministic node/edge order, at depth at most three. This is a computation cap, not a risk threshold. An interrupted document produces `INCOMPLETE` with lower-bound counts and a nonzero exit code. Test is not inspected for patterns or name collisions. Re-running regenerates the five audit-owned files; the separate feasibility assessment records the reviewed interpretation.

An ERROR yields `INVALID` and a nonzero exit code; name/span formatting differences and absent evidence are warnings. Null/malformed evidence is an error. Even when a document is excluded from structural statistics, its evidence objects and diagnostics remain counted separately. No missing evidence is treated as contradiction.

For repeatability, run the same command twice and compare SHA-256 hashes of `input_manifest.json`, `dataset_audit.json`, `pattern_inventory.json` and `audit_report.md`. `environment.json` is run metadata and can change with Git state or invocation. The manifest includes the audit script hash. Schema and pattern outputs carry the input fingerprints and format version.

Git and `.gitignore` were preserved by the implementation. The historical Phase 0 reports describe the configuration at that phase. At Phase 1 preflight, private gold and research context are ignored, the general `docs/` directory is no longer ignored, and raw JSON remains tracked. No private gold directory was created. The commands above avoid bytecode and pytest caches. Redistribution rights remain unresolved; do not publish source-derived audit examples before the licence is checked.

## Phase 1 annotated graph construction

```bash
.venv/bin/python -B scripts/build_graph.py --data-dir data/raw/re_docred/data --manifest results/phase0/input_manifest.json --output-dir results/phase1
.venv/bin/python -B -m pytest -q -p no:cacheprovider
```

`requirements-dev.txt` now also pins the already installed NetworkX 3.7 used in Phase 1. No installation or upgrade was needed. Each split is built in memory as a `MultiDiGraph`, validated and released separately; full graph dumps are not generated. Recreate a graph through the builder interfaces when needed.

`load_split` verifies raw fingerprints, byte counts and schema. `build_document_graph` supports one original document; `build_split_graph` supports a loaded split. `validate_graph_provenance(graph, source, *, require_full_split=False)` checks every declared source node and edge occurrence and returns explicit FULL_SPLIT/SUBSET scope, full_split, documents_available and documents_validated. The CLI uses `require_full_split=True`, rejecting a consistent partial graph. `reconstruct_edge_source` returns original relation dictionaries, endpoint mentions, mention-span tokens and evidence-sentence token arrays. File-backed callers should use `load_split`; direct document construction trusts the caller's supplied source fingerprint and is also used for explicitly synthetic tests.

IDs are `split:document_index:entity_index`; edge keys are `split:document_index:label_index`. Preserve all groups, occurrences, isolates, loops and parallel relations. Names do not determine identity. Mutable source dictionaries are copied into graph attributes; original source documents remain external. SHA-256 per document detects wrong-source reconstruction. Absent, empty and nonempty pointers remain distinct availability states, not evidence truth classifications.

## Latest attempt and immutable results (Phase 1 output contract v2)

The reviewed stale-PASS issue is corrected: a failed rerun must not make earlier results look current. Inspect [latest_run.json](results/phase1/latest_run.json) first. Only `status: PASS` with its referenced run_directory and matching artifact_sha256 values establishes success of the latest recorded attempt. RUNNING, FAILED, missing or unreadable status is not success. Failed records include stage, exception type and reason. Handled build failures exit 1; success exits 0. Argument syntax errors exit 2 before build-attempt recording.

```text
results/phase1/
  latest_run.json
  runs/<unique-run-id>/
    graph_summary.json
    provenance_demo.json
    run_manifest.json
    phase1_report.md
  validation_record.md
  ...preserved historical top-level artifacts...
```

Each invocation atomically writes RUNNING before reading the manifest. All four artifacts are prepared in a hidden directory, which is atomically renamed into runs/ only after writing finishes. PASS is then atomically published. Handled failures publish FAILED without a successful-run reference. Interrupted execution may leave RUNNING, hidden partial files or an uncommitted completed directory; none establishes latest-attempt success. Previous completed runs and historical top-level files are never overwritten or deleted. Their embedded PASS describes that historical result only.

If output protection rejects a location, nothing is written there. If latest-run status cannot be initialized, the CLI aborts before loading inputs and reports that no new attempt was recorded; an older status must not be attributed to that failed invocation. Status-write errors are explicit. Use one writer per output directory; concurrent runs need separate directories. Atomic publication protects against partial process-visible results, not every possible filesystem/power-loss failure.

For deterministic reruns compare `graph_summary.json`, `provenance_demo.json` and `phase1_report.md` inside the two completed run directories. Unique IDs, latest-run state and machine-specific run_manifest metadata are not required to match. The manifest records hashes of the builder, reused validator, Phase 0 audit/manifest and all raw inputs. Format version 2 adds scope metadata and the new publication contract; graph record construction remains unchanged. See [validation evidence](results/phase1/validation_record.md) for actual commands, regressions and checks. Protected raw, Phase 0 and private-gold output locations and symlinked status/run paths are rejected.

No candidate generation, fragmentation, query-answer evaluator, matcher, risk rule, merge simulator or ASPEN reproduction is implemented. Phase 2 requires separate approval.

## Phase 2 unlabelled candidate preparation

Work on the separate phase-two branch. Reuse the existing environment; no new dependencies:

```bash
.venv/bin/python -B scripts/candidate_discovery.py --data-dir data/raw/re_docred/data --manifest results/phase0/input_manifest.json --output-dir results/phase2 --review-dir data/private_gold/phase2
.venv/bin/python -B -m pytest -q -p no:cacheprovider
```

The pipeline discovers exact normalized-name and initialism pairs from train only. It validates train's original graph record by record, counts all types and selects up to 24 PER/ORG/LOC cases using frozen source-based categories and endpoint/key diversity. No category is an identity label. Dev supports exact-text overlap checks only; test is hashed only. Dev document 469 duplicates train document 3052 and is recorded as excluded from later dev evaluation; raw documents remain unchanged.

Inspect `results/phase2/latest_run.json`, then its referenced immutable run directory and hashes. That directory contains candidates_train.json, candidate_inventory.json, candidate_feasibility_report.md, phase2_report.md and run_manifest.json. Only a complete referenced PASS establishes latest success. Each invocation creates new packages; failures preserve earlier results and explicitly record FAILED when status initialization succeeded. One writer per output directory is required.

The source-rich review_dossier.json and blank review_worklist.csv are written under Git-ignored data/private_gold/phase2/runs/<run-id>/. They are evaluation/preparation-only; the generator never reads earlier private files. Inspect them locally using the [annotation guide](docs/annotation_guide.md), preserve the blank snapshot and save actual annotations separately. Do not publish private files or source-derived excerpts. Candidate names are local inputs, not cleared for redistribution.

Compare the four deterministic public artifacts excluding run_manifest.json and both initially blank private artifacts across repeated runs. Timing, invocation metadata, latest status and unique run IDs may differ. A failure between the two package publications can leave an orphan directory; it is not latest success without the final PASS record.

See [Phase 2 methodology and leakage policy](docs/phase2_candidate_methodology.md). Controlled fragmentation is feasibility-only: no fragments, private parent map, controlled pairs or reassigned edges. Identity annotation, QA workloads, merges, counterfactual effects and GIR-ER effectiveness remain unperformed. STOP after Phase 2 for independent review.

## Phase 3 fixed structural QA workload

```bash
.venv/bin/python -B scripts/query_workload.py --data-dir data/raw/re_docred/data --manifest results/phase0/input_manifest.json --output-dir results/phase3 --review-dir data/private_gold/phase3
.venv/bin/python -B -m pytest -q -p no:cacheprovider
```

Use the existing Python 3.12.15 environment and a separate phase-three branch. No dependencies are added. The original train MultiDiGraph is validated before/after query preparation. Queries follow exactly two or three outgoing relation codes through distinct vertices. Answers are unique IDs; every supporting edge-occurrence path remains traceable. Optional type constraints match the original annotated type sets by intersection. Self-loops/cycles stay in the graph but cannot satisfy simple-path queries.

The frozen 12-case target reserves one candidate-endpoint query per hop, four general queries per hop and one real zero-answer diagnostic per hop. Global document/anchor and per-hop relation diversity apply; shortfalls remain explicit. Discovery and selection use train only. Dev/test never select templates; test is hashed only. Discovery/evaluation resource exhaustion is INCOMPLETE and cannot publish a complete workload.

Read results/phase3/latest_run.json before following its immutable public run directory. Only PASS and matching artifact hashes establish latest success. Five deterministic public artifacts contain specifications, structural results, inventory and reports; run_manifest.json records invocation/runtime and fingerprints. A separate validation_record.md records actual checks. Initial private QA dossier/CSV snapshots are written under ignored data/private_gold/phase3/runs/<run-id>/; earlier annotations are never read or overwritten.

See [query methodology](docs/phase3_query_methodology.md) and [QA review guide](docs/qa_annotation_guide.md). Blank query-level and answer-level review rows distinguish interpretation, individual triple support, composition and answer correctness. Structural answers are not gold; semantic relation meanings and independent verification remain unresolved. No natural-language questions, merging, counterfactual analysis, risk scoring or Phase 4 work is implemented. Source excerpts and private reviewer files are not cleared for publication. STOP for independent review.

## Phase 3 post-review annotation supplements

Run `.venv/bin/python -B scripts/prepare_qa_annotation_supplement.py` to prepare additional blank triple-level and path-composition sheets from frozen public Phase 3 results and original source. Output goes only to new ignored data/private_gold/phase3/annotation_supplements/runs/<id>/ packages; no existing private annotations are read or overwritten. The original query/answer worklist and all public Phase 3 results remain unchanged. See [review findings](docs/phase3_review_findings.md) and the [QA guide](docs/qa_annotation_guide.md). Cleanup of duplicate historical artifacts is proposed only, awaiting separate approval; no Phase 4 work is included.
