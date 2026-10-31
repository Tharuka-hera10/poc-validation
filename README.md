# GIR-ER exploratory pilot — Phases 0–1

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

`load_split` verifies raw fingerprints, byte counts and schema. `build_document_graph` supports one original document; `build_split_graph` supports a loaded split. `validate_graph_provenance` checks every source node and edge occurrence. `reconstruct_edge_source` returns original relation dictionaries, endpoint mentions, mention-span tokens and evidence-sentence token arrays. File-backed callers should use `load_split`; direct document construction trusts the caller's supplied source fingerprint and is also used for explicitly synthetic tests.

IDs are `split:document_index:entity_index`; edge keys are `split:document_index:label_index`. Preserve all groups, occurrences, isolates, loops and parallel relations. Names do not determine identity. Mutable source dictionaries are copied into graph attributes; original source documents remain external. SHA-256 per document detects wrong-source reconstruction. Absent, empty and nonempty pointers remain distinct availability states, not evidence truth classifications.

Outputs are concise [graph statistics](results/phase1/graph_summary.json), [train-only provenance examples](results/phase1/provenance_demo.json), a [run manifest](results/phase1/run_manifest.json), and an [execution report](results/phase1/phase1_report.md). See [validation evidence](results/phase1/validation_record.md) for tests and reproducibility. CLI errors exit nonzero and do not write success artifacts; an older output directory from a prior successful run is not automatically deleted, so always check the current exit status and manifest. Output paths inside raw data, Phase 0 results or private gold are rejected.

For deterministic reruns compare `graph_summary.json`, `provenance_demo.json` and `phase1_report.md`; machine-specific `run_manifest.json` is not required to be byte-identical. The manifest records hashes of the builder, reused validator, Phase 0 audit/manifest and all raw inputs.

No candidate generation, fragmentation, query-answer evaluator, matcher, risk rule, merge simulator or ASPEN reproduction is implemented. Phase 2 requires separate approval.
