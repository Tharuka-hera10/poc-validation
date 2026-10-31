# GIR-ER Phase 1 execution report

Status: **PASS**.

| Split | Nodes validated | Edges validated | Nonempty pointers | Empty pointers | Absent pointers |
|---|---:|---:|---:|---:|---:|
| train | 59359 | 85932 | 47260 | 38672 | 0 |
| dev | 9684 | 17284 | 7473 | 9811 | 0 |
| test | 9779 | 17448 | 7547 | 9901 | 0 |

Every node and edge was compared with its original annotation, including nested source values and provenance. Counts matched both Phase 0 expectations and source-derived mappings. Input hashes matched before and after construction.

Warnings by split: `{"dev":{"name_span_text_difference":284},"test":{"name_span_text_difference":317},"train":{"name_span_text_difference":1821}}`.

Train demonstration: document 0 (AirAsia Zest), 3 original relation records. See provenance_demo.json for node identifiers, source labels, mentions and sentence tokens.

## Design and limits

A NetworkX MultiDiGraph preserves one node per document-scoped group and one edge per source label, including isolates, duplicates, parallel predicates and loops. Explicit IDs use split and original indices. Mutable source dictionaries are deep-copied into node/edge attributes; verified source documents remain external to the graph. No full graph dump is generated.

Missing evidence is retained as absent, empty or nonempty; malformed evidence fails validation. These are pointer-availability states, not truth classifications. Sentence arrays are lossless; joined text is labelled rendered_view.

The source loader and validator are reused without modifying Phase 0. Test is used only for integrity verification. No candidates, fragmentation, merges, counterfactual analysis, risk scores or verified QA were implemented.

The independent PASS WITH CONDITIONS review is student-reported; its detailed conditions are unavailable locally. No claim is made that unseen conditions were satisfied. Known deferred limitations include source licence/release authenticity, relation semantics, independent identity/QA annotation, and train/dev text overlap. Source hashes identify bytes, not truth.

LACE/ASPEN/ASPEN+ boundaries remain governing; graph construction is not claimed as a novel contribution. GIR-ER's incremental benefit over an equally informed matcher is untested.

## Reproduce

```bash
.venv/bin/python -B scripts/build_graph.py --data-dir data/raw/re_docred/data --manifest results/phase0/input_manifest.json --output-dir results/phase1
.venv/bin/python -B -m pytest -q -p no:cacheprovider
```

See validation_record.md for actual test output, repeated-run comparison and final repository integrity checks. run_manifest.json records the invocation, input hashes and implementation versions. Machine-specific metadata is not required to be byte-identical.

Phase 2 requires student approval plus review of genuine identity evidence, permitted inputs, private-map safeguards, annotation protocol and partition policy. No candidate work was started. STOP.
