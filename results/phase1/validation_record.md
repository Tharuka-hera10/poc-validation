# Phase 1 validation record

Phase 1 only. Executed in the existing Python 3.12.15 environment with NetworkX 3.7. No installation, staging, commits or pushes were performed.

## Actual commands and outcomes

```bash
.venv/bin/python -B -m pytest -q -p no:cacheprovider
```

Final observed output: `51 passed in 0.72s`, exit 0. Initial runs passed 49 and 50 tests; additional CLI-reconciliation and malformed-provenance checks were added, and the final suite passed all 51. No unexpected test failures occurred. Expected invalid-input failures were exercised by tests and are software checks, not empirical ER/QA results.

The final implementation was executed twice using:

```bash
.venv/bin/python -B scripts/build_graph.py --data-dir data/raw/re_docred/data --manifest results/phase0/input_manifest.json --output-dir results/phase1
```

Both runs exited 0 with the following output:

```text
train: 59359 nodes, 85932 edges validated; provenance PASS
dev: 9684 nodes, 17284 edges validated; provenance PASS
test: 9779 nodes, 17448 edges validated; provenance PASS
Phase 1 PASS; all source hashes unchanged; outputs: results/phase1
```

Every one of the 78,822 nodes and 120,664 edges was compared against its original source annotation. Checks include identifiers, topology, complete mention/relation values, JSON value types, evidence-pointer ordering and provenance. Split counts match the approved expectations and Phase 0 counts. The original 2,422 mention-name/span warnings remain warnings; no data was repaired or dropped.

## Reproducibility evidence

An inline Python harness used subprocess.run to execute the command twice and hashlib.sha256 to compare the following deterministic artifacts byte-for-byte:

| Artifact | SHA-256 from both executions |
|---|---|
| graph_summary.json | `90c5251403d1ab908b66019b7f89b4b76a5946a194f0165db966af010f6a3b3a` |
| provenance_demo.json | `f239b48ed3a80b3526c273555712c5d393a9c914882c19551aca0c453502546c` |
| phase1_report.md | `bacd22741df4d460c11aa92cdb6413e32830b15f24eee70c74a36fae00a8d98f` |

All three matched. Machine-specific run_manifest.json was not required to be byte-identical. Its recorded builder hash matches the final script and its invocation includes Python's `-B` flag. This is repeated execution of the same implementation, not independent empirical replication.

To repeat the comparison, hash these three files, rerun the builder and hash them again. Re-running replaces the four builder-owned Phase 1 outputs, not Phase 0 outputs or this validation record. Nonzero exits must be checked; an older successful output directory is not deleted automatically after a later failed execution.

## Preservation evidence

Before implementation an external temporary baseline recorded SHA-256 hashes of the Git index, .gitignore, Phase 0 code/tests and every existing Phase 0 output. All matched after the final runs. The staging area was initially empty and remained unchanged, including the Git index bytes. Original train/dev/test JSON hashes matched the original Phase 0 manifest before implementation, during both builder runs, and after implementation. Phase 0 code, tests and report artifacts were not modified.

`git diff --check` exited 0. No configuration was rewritten. The earlier Phase 0 reports retain their historical Git-ignore observations; README and the decision log explain the current configuration. No full graph exports, API calls, model downloads, private-gold input reads or later-phase implementations were produced.

## Source demonstration

The outcome-independent rule selected train document index 0, AirAsia Zest, and relation-label indices 0, 1 and 2. Edges retain keys train:0:0, train:0:1 and train:0:2 and relation codes P159, P17 and P17, respectively. provenance_demo.json shows their exact original relation dictionaries, endpoint mentions, token spans and bounded evidence-sentence arrays. Display omission counts are explicit. No semantic relation-name interpretation, identity truth or verified answer is asserted.

## Files changed

New:

- scripts/build_graph.py
- tests/test_build_graph.py
- results/phase1/graph_summary.json
- results/phase1/provenance_demo.json
- results/phase1/run_manifest.json
- results/phase1/phase1_report.md
- results/phase1/validation_record.md

Updated as approved:

- requirements-dev.txt: pin the installed NetworkX version alongside pytest.
- README.md: execution, interfaces, outputs, reproducibility and current configuration.
- docs/data_dictionary.md: graph/provenance contract and reconstruction semantics.
- docs/decision_log.md: student Phase 1 approval, implementation decisions and open limitations.

## Remaining limitations and Phase 2 gate

The independent Phase 0 PASS WITH CONDITIONS verdict is student-reported; its detailed review is not available locally. No unavailable condition is claimed satisfied. Available preflight material revealed no demonstrated blocker to this graph-construction phase. Source licence/release authenticity, readable relation metadata, independent identity/QA references, annotation cost and the train/dev text-overlap partition policy remain unresolved. Separate supervisor feedback and literature papers remain absent locally; supplied LACE/ASPEN/ASPEN+ boundaries were preserved rather than independently re-verified.

Deep copies increase memory use but isolate graph attributes from source documents. Processing one split at a time bounds simultaneous graph storage; no memory or runtime benchmark was claimed. File-backed callers should use load_split for verified raw bytes; direct document construction trusts its caller's fingerprint and supports synthetic fixtures. SourceSplit documents are externally mutable; callers must not modify them. Document hashes detect wrong/changed source during validation and reconstruction.

Phase 1 builds graphs of annotations, not verified facts, and does not test GIR-ER's incremental benefit. Before Phase 2, the student must approve case preparation, review genuine identity evidence and private-label/fragment-map safeguards, and address relevant review conditions and partition/annotation decisions. No candidate generation, fragmentation, merging, counterfactual analysis, risk scoring or verified QA was implemented.

**STOP. Phase 1 complete; Phase 2 requires explicit student approval.**


## Post-review corrections — output contract v2 and explicit scope

This section supersedes the earlier flat-output execution contract while preserving the historical evidence above. The student supplied the independent Phase 1 PASS WITH CONDITIONS findings and approved only the two corrections. No Phase 2 work was done.

### Confirmed issues and chosen fixes

A failed rerun previously left earlier PASS artifacts in place without recording its failure. Each new accepted build attempt now atomically writes latest_run.json RUNNING before reading inputs, stages four artifacts in a hidden directory, atomically renames the completed directory into runs/<unique-id>/, and commits a latest PASS with relative run path and artifact hashes. Handled failures record FAILED with stage/type/reason and no successful-run reference. The existing top-level results are historical snapshots and were not overwritten. Only the latest status plus its complete referenced artifacts establishes latest recorded success. This avoids replacing or deleting verified research results.

validate_graph_provenance now accepts keyword-only require_full_split=False and returns FULL_SPLIT/SUBSET, full_split, documents_available and documents_validated. Document/subset validation remains supported. The CLI uses True and rejects partial coverage even if all declared records and counts are consistent. Malformed/empty/duplicate/boolean/out-of-range scope cannot establish strict full-split success. Graph construction and evidence semantics are unchanged.

### Actual tests

```bash
.venv/bin/python -B -m pytest -q -p no:cacheprovider
```

Final output: `70 passed in 0.87s`, exit 0 (historical baseline: 51). The first correction run passed 65 tests; five more protected-path/publication-failure checks were added, and the final 70 passed. No unexpected failures occurred. Expected failures cover missing/malformed manifests, a dev acceptance failure after train processing, partial artifact publication, final status-publication failure, interrupted RUNNING, unwritable status initialization, protected paths and symlink redirects. Tests also verify immutable earlier results, repeated deterministic output, internally consistent subsets rejected by strict validation, and malformed scopes.

### Actual real-data execution and reproducibility

The following command executed successfully twice in the repository output location, both exit 0:

```bash
.venv/bin/python -B scripts/build_graph.py --data-dir data/raw/re_docred/data --manifest results/phase0/input_manifest.json --output-dir results/phase1
```

Both runs validated every original node and edge, not just totals:

| Split | Scope | Documents | Nodes | Edges | Nonempty pointers | Empty pointers |
|---|---|---:|---:|---:|---:|---:|
| Train | FULL_SPLIT | 3053 | 59359 | 85932 | 47260 | 38672 |
| Dev | FULL_SPLIT | 500 | 9684 | 17284 | 7473 | 9811 |
| Test | FULL_SPLIT | 500 | 9779 | 17448 | 7547 | 9901 |

Absent evidence was zero in each split. Original name/span warnings remained 1821/284/317. All source hashes matched before and after. Graph invariants, original source values and provenance round trips remained valid.

Completed repository run directories:

- `runs/ed510ef8f14b491b99291a104f4b61fd`
- `runs/5e2ac858263244c39f5a352b5804eefd`

The following deterministic artifact hashes matched byte-for-byte across both completed runs. Status IDs and machine metadata were excluded from deterministic comparison.

| Artifact | SHA-256 in both runs |
|---|---|
| graph_summary.json | `dfa9af63a4ead101a8730ff73a8f48bbca9aa5c99ae84db8b07818bc87d57886` |
| provenance_demo.json | `f239b48ed3a80b3526c273555712c5d393a9c914882c19551aca0c453502546c` |
| phase1_report.md | `ac6feac78c7cf30b1d33633a631a85503fc4e5bacb7252edfcf4cb6bb374c630` |

### Stale-PASS CLI regression on real data

A separate temporary output location was used to avoid marking the repository's final run failed. Actual commands and observed outputs:

```text
/Users/tharuka.herath/Downloads/KG/risk aware/poc/.venv/bin/python -B scripts/build_graph.py --data-dir data/raw/re_docred/data --manifest results/phase0/input_manifest.json --output-dir /var/folders/j8/lzvjf1bn667_4z3tk_r4r0sw0000gr/T/girer-stale-pass-ro0ami0p/outputs
Exit: 0
train: 59359 nodes, 85932 edges validated; provenance PASS
dev: 9684 nodes, 17284 edges validated; provenance PASS
test: 9779 nodes, 17448 edges validated; provenance PASS
Phase 1 PASS; all source hashes unchanged; outputs: /var/folders/j8/lzvjf1bn667_4z3tk_r4r0sw0000gr/T/girer-stale-pass-ro0ami0p/outputs/runs/db3aea6cd3e64288bf8ff51e06e30dda
```

```text
/Users/tharuka.herath/Downloads/KG/risk aware/poc/.venv/bin/python -B scripts/build_graph.py --data-dir data/raw/re_docred/data --manifest /var/folders/j8/lzvjf1bn667_4z3tk_r4r0sw0000gr/T/girer-stale-pass-ro0ami0p/missing_manifest.json --output-dir /var/folders/j8/lzvjf1bn667_4z3tk_r4r0sw0000gr/T/girer-stale-pass-ro0ami0p/outputs
Exit: 1
Phase 1 failed: [Errno 2] No such file or directory: '/var/folders/j8/lzvjf1bn667_4z3tk_r4r0sw0000gr/T/girer-stale-pass-ro0ami0p/missing_manifest.json'
```

Latest status after failure:

```json
{
  "command": [
    "/opt/homebrew/Cellar/python@3.12/3.12.15/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python",
    "-B",
    "scripts/build_graph.py",
    "--data-dir",
    "data/raw/re_docred/data",
    "--manifest",
    "/var/folders/j8/lzvjf1bn667_4z3tk_r4r0sw0000gr/T/girer-stale-pass-ro0ami0p/missing_manifest.json",
    "--output-dir",
    "/var/folders/j8/lzvjf1bn667_4z3tk_r4r0sw0000gr/T/girer-stale-pass-ro0ami0p/outputs"
  ],
  "error": {
    "reason": "[Errno 2] No such file or directory: '/var/folders/j8/lzvjf1bn667_4z3tk_r4r0sw0000gr/T/girer-stale-pass-ro0ami0p/missing_manifest.json'",
    "stage": "load_manifest",
    "type": "FileNotFoundError"
  },
  "format_version": 2,
  "run_directory": null,
  "run_id": "83e65c379c844e4f8b369f9db8215ba6",
  "status": "FAILED"
}
```

The previous successful run's four files remained byte-identical. The failed attempt referenced no successful run_directory. This resolves the demonstrated stale-PASS scenario; it does not claim that an older embedded summary PASS is itself invalid historical evidence.

### Preservation, changed files and limitations

Before corrections, SHA-256 baselines covered the Git index, .gitignore, raw JSON, Phase 0 code/tests/results and historical Phase 1 outputs. All matched after execution before this append. This file's original bytes remain intact as the historical prefix. The four original top-level builder artifacts remain byte-identical. Git staging is unchanged. No dependencies, configuration, source data, private gold or Phase 0 files were modified. git diff --check exited 0.

Modified: scripts/build_graph.py, tests/test_build_graph.py, README.md, docs/data_dictionary.md, docs/decision_log.md, and this validation_record.md. Created: latest_run.json plus the four artifacts in each of the two repository run directories listed above. Historical phase1_report.md is preserved; revised reports are in the immutable runs.

Output format is now version 2. Consumers must read latest_run.json first and follow its run_directory. Graph summary scope fields are additive; graph source data, IDs, edge occurrence preservation and the provenance demonstration are unchanged. No full graph dumps were produced.

One writer per output directory is required. Interrupted or failed publication may leave hidden partial files or an uncommitted completed directory; these are not latest successful results. Unsafe output paths are rejected without writes. If the output/status cannot be initialized, the CLI aborts before loading inputs and reports that no new attempt was recorded. Argument syntax errors likewise precede build-attempt recording. An unreadable/missing/non-PASS latest status is not evidence of current success; an old recorded status cannot be attributed to an invocation that failed before recording. Atomic process-visible publication is not an all-storage/power-loss durability guarantee.

Recommendation: both reviewed technical correction conditions pass the implemented regression and real-data checks. Phase 1 is ready for independent closure review. Do not treat this as final reviewer sign-off or approval of Phase 2. Licence/authenticity, relation semantics, train/dev overlap policy, independently checked identity/QA references and other research limitations remain unresolved. No GIR-ER effectiveness claim is made.

**STOP after Phase 1 corrections. Phase 2 requires independent review and explicit student approval.**
