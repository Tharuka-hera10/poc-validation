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
