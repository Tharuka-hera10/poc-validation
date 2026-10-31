# GIR-ER exploratory pilot — Phase 0

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

Git and `.gitignore` were preserved. Current configuration tracks raw JSON, ignores `docs/`, and does **not** ignore `data/private_gold/`, bytecode or pytest caches. No private gold directory was created. The commands above avoid bytecode and pytest caches. Correcting Git exclusions and determining redistribution rights remain student decisions before any private annotation or publishing. Do not publish source-derived audit examples before the licence is checked.

Only Phase 0 is implemented. No persistent graph, candidate generation, query-answer evaluator, matcher, risk rule, merge simulator or ASPEN reproduction exists. Phase 1 needs separate approval.
