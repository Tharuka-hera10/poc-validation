# GIR-ER Phase 0 feasibility assessment

Status: **Phase 0 completed; technically suitable for Phase 1, subject to student approval.** This is a data-preparation judgement, not a final dataset adoption or research-effectiveness result.

## Actual execution

Executed with the existing `.venv/bin/python`, Python 3.12.15:

```text
$ .venv/bin/python -B scripts/audit_dataset.py --data-dir data/raw/re_docred/data --output-dir results/phase0
Schema: VALID; patterns: COMPLETE; outputs: results/phase0
Diagnostics: {"name_span_text_difference":2422}
```

Exit code: 0. This command was rerun after the final script changes; an inline Python verification harness reran the same CLI and compared SHA-256 hashes of the manifest, dataset audit, pattern inventory and audit report. Observed output:

```text
Reproducibility: 4/4 audit outputs byte-identical
Raw JSON 3/3 and .gitignore match pre-implementation SHA-256
Maximum extensions: 9625
```

`environment.json` is separate run metadata and was not required to be byte-identical. The manifest records the exact script hash and input hashes. This is deterministic reproducibility, not independent experimental replication.

```text
$ .venv/bin/python -B -m pytest -q -p no:cacheprovider
..........................                                               [100%]
26 passed in 0.32s
```

Exit code: 0. The initial test run also passed (25 tests); a further boundary test was added and the final run above passed all 26. No unexpected test or dataset-run failures occurred. Negative fixtures exercised invalid JSON, wrong indices/types, absent/null/malformed evidence, source changes, protected paths, missing files, symlinks and exhausted inspection bounds. Their expected failure states/nonzero exits passed. They are authored software tests, not experimentally measured GIR-ER identity or answer outcomes.

`pip check` reported `No broken requirements found.` It warned that the user-level pip cache was not writable; no installation was attempted. Imports of installed dependencies succeeded. `git diff --check` exited 0. Read-only searches found no separate supervisor-feedback or literature-review files and no PyCharm interpreter selection; these are environment/context gaps, not audit failures.

## Observed data findings

All 4,053 documents validated. The files contain 78,822 entity groups, 105,688 mentions and 120,664 annotated relation records. Required counts reconcile with the three source files; no malformed/null/absent evidence field, out-of-range source reference, duplicate relation record or self-relation was found in these particular inputs. Empty evidence lists remain present and explicitly counted.

| Split | Relations | Nonempty sentence pointers | Empty sentence pointers | Distinct relation codes |
|---|---:|---:|---:|---:|
| Train | 85,932 | 47,260 | 38,672 | 96 |
| Dev | 17,284 | 7,473 | 9,811 | 95 |
| Test | 17,448 | 7,547 | 9,901 | 95 |

There are 2,422 mention-name/token-span differences: 1,821 train, 284 dev and 317 test. They are retained warnings, not corrections or declarations of annotation error. Mixed-type groups number 29 train, 9 dev and 9 test; their semantics remain unverified. Auxiliary `global_pos` zero pairs occur 2,275/374/369 times, respectively, and are preserved without relying on them for provenance.

Train index 3052 and dev index 469 share a title and exact sentence content; their full annotation objects are not identical. No document was removed, merged or repartitioned. Future split-independence claims require an explicit policy for this overlap.

## Structural feasibility

Train/dev inspection completed for all 3,553 documents at the predeclared computational cap of 100,000 attempted extensions per document, depth at most three. The largest observed count was 9,625 extensions; no document was truncated. Test did not participate in pattern discovery.

| Hops | Ordered relation/type patterns | Distinct typed structural paths | Relation-occurrence paths with every edge pointed |
|---|---:|---:|---:|
| 2 | 6,404 | 229,812 | 74,683 |
| 3 | 26,262 | 410,929 | 74,145 |

These are directed document-local chains with distinct vertices. The pointed-path column describes annotation-pointer availability, not source-verified inference. Repeated-vertex extensions are separately counted and excluded. Typed parallel edges and duplicate occurrence semantics are documented in `docs/data_dictionary.md`; no cross-document joins or inverse relations were introduced. All pattern examples retain original file hashes, entity indices, relation-label indices and evidence sentence references.

The corpus therefore supports the mechanics of future provenance-preserving graph construction and has substantial structural 2/3-hop material. It has not yet established interpretable relation compositions, valid QA templates, verified answers, beneficial/harmful merges or the incremental value of GIR-ER.

## Identity candidate feasibility

Train contains 10,993 multi-mention groups, of which 4,715 have distinct casefolded/whitespace-normalized aliases; dev contains 1,891 and 815, respectively. These are potential controlled-fragmentation resources. They are already grouped within-document coreference annotations, not naturally unmerged positive identity pairs.

Within train, 4,542 normalized name strings occur in multiple groups and 4,332 occur across documents; dev counts are 750 and 739. These are discovery opportunities only. Neither name agreement nor group/document separation provides a true positive/negative label. No candidate pair list was generated, no annotation was performed, and no preparation-time or identity-accuracy measurement was made.

Genuine natural identity cases and hard negatives require independent source checking. Controlled fragmentation would require private parent maps and defensible edge allocation; copying every incident relation to both aliases could erase or fabricate the mechanism being studied. Missing evidence makes such allocation harder. The audit alone cannot determine how many independently verifiable cases exist.

## Preserved state and changed files

Preserved byte-for-byte: all three source JSON files and the existing `.gitignore`. Existing AGENTS.md, execution plan, research context and Git configuration were not rewritten. No commits, pushes, downloads, API calls or private gold data were produced. `.gitignore` was already modified before this session; that existing change was left intact.

New implementation and documentation:

- `scripts/audit_dataset.py`, `tests/test_audit_dataset.py`, `requirements-dev.txt`, `README.md`.
- `docs/data_dictionary.md`, `docs/decision_log.md`, `docs/pilot_feasibility_contract.md`.
- `results/phase0/input_manifest.json`, `dataset_audit.json`, `pattern_inventory.json`, `environment.json`, `audit_report.md`, and this `feasibility_report.md`.

`docs/` is currently Git-ignored. Raw source JSON files are already tracked. `data/private_gold/`, bytecode and pytest caches are not ignored. These configuration gaps were reported without modifying the student's configuration. No private data was created; `-B` and `-p no:cacheprovider` avoid interpreter/pytest cache output in the documented commands. Exclusion changes need resolution before private annotation or publication.

## Unresolved limitations and next entry gate

The local source README is only `data dir`; acquisition URL, authoritative release checksums, licence and readable relation definitions remain unavailable. Local hashes establish byte identity, not authenticity or redistribution permission. The master context was reviewed; separate supervisor feedback, current proposal/literature drafts and original LACE/ASPEN/ASPEN+ papers were not available. Their updated boundaries were taken from the governing instructions, not independently re-verified here.

Before later risk-method design, resolve authoritative context, identity/reference annotation and source access, separate evidence targets (identity, triple, composition, answer), semantic workload selection and duplicate-aware partitioning. Do not treat missing evidence or zero observed impact as safety. The B3+same-evidence control and future threshold/risk approvals remain mandatory. No comparison system, threshold, risk formula or success target was selected.

**Phase 1 recommendation:** technically ready to build a document-scoped directed relation-typed graph preserving every original occurrence and pointer, including missing-pointer status. Readable relation metadata and independent truth checks may remain explicit limitations; they must be resolved before semantic/effectiveness claims. This recommendation does not approve Phase 1 or establish suitability for a fully labelled final ER benchmark.

**STOP. Phase 1 has not been started and requires separate student approval.**
