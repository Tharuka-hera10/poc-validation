# Phase 3 independent-review findings and annotation hardening

## Authority and verdict

Reviewed baseline: phase-three at `5bbed2d891e90111f431cb8b85ad35b864d20a0e` (PR #4). The working tree was clean before corrections. **PASS for the implemented technical correction; scientific annotation and independent closure review remain pending.** No core query-engine defect was confirmed by the supplied independent review. This task changes annotation granularity and documentation only, not queries, answers, selection or sources.

AGENTS.md, governing execution plan/Phase 3 amendments, methodology, QA guide, engine, dossier generator, existing tests and validation records were reviewed. Only the master research context is available locally; separate supervisor feedback, proposal/literature drafts and primary papers remain unavailable. No new supervisor approval or literature verification is claimed. GIR-ER remains an unvalidated incremental same-evidence hypothesis; ordinary traversal and collective/query ER are established capabilities, including LACE/ASPEN/LACE+/ASPEN+.

## Independent-review observations and local checks

The student supplied an independent review of the original private QA packages: 100 original mentions and 55 relation records reconciled, two source name/span differences preserved/flagged, all 13 original human fields blank and all four private QA packages identical. These private-content checks are attributed to that review, not claimed as new reads of historical annotations.

Local recomputation using frozen public outputs and raw train independently confirms the following structural counts:

| Observation | Count |
|---|---:|
| Queries (2-hop / 3-hop) | 12 (6 / 6) |
| Structural query/answer pairs | 16 |
| Supporting occurrence paths | 23 |
| Path-edge positions, counting shared occurrences each time | 52 |
| Distinct original supporting occurrences | 42 |
| Nonempty-pointer positions | 25 |
| Empty-pointer positions | 27 |
| Paths with every edge nonempty-pointed | 2 |
| Original occurrences in supporting/template registry union | 55 |
| Template-only occurrences | 13 |

Reconstructing the public supporting/template source references also yields 100 original mentions and two name/span differences. That is source/public consistency, not a new private-content adjudication or evidence truth assessment. Both candidate-endpoint paths contain at least one empty-pointer relation.

All selected anchor documents are train indices 0–11. Actual supporting paths occur in documents 0,2,3,4,5,6,7,8,9,10; document 3 contributes 9 of the 23 paths. The source-index ordering therefore concentrates the pilot in early documents despite distinct selected anchors/documents. No rules were retuned after seeing these findings.

## Scientific interpretation

1. A nonempty pointer is an annotation sentence reference, not verified support for a proposition.
2. Empty or absent pointers are not contradiction; insufficient evidence remains unresolved.
3. Original triple support differs from validity of joining a relation chain. Individually supported triples do not establish valid composition.
4. Valid composition differs from independently checked answer correctness. Structural answer completeness differs from real-world completeness.
5. Structural proximity/anchored chains around Phase 2 candidates do not establish useful ER merge impact. No merge or counterfactual analysis was performed.

The two zero-outdegree diagnostics are graph-mechanics cases, not real-world negative-answer evidence. The location-heavy Phase 2 population, shared-document dependence, uninspected identity-review status and unknown relation semantics remain limitations. There is no verified QA workload freeze or GIR-ER improvement claim. Human triple, composition and answer reviews may conclude UNKNOWN/UNRESOLVED or that cases are unsuitable.

## Additive annotation contract

The existing query/answer CSV and original dossier stay byte-identical. A standalone preparation tool reads only verified public Phase 3 artifacts and validated original train data. It does not read existing private annotation files, rerun discovery or alter scientific results. Query/inference modules do not import this preparer.

edge_review_worklist.csv has one record per distinct supporting occurrence, stable edge-review IDs, original coordinates/keys/relation, precise source fingerprint/reference, exact pointer state/array and all query/path/edge-position uses. Eight human fields are blank. path_composition_worklist.csv has one record per occurrence path, stable path/query IDs, ordered nodes/keys, structural answer and ordered edge-review references. Nine human fields are blank. Structured cells use canonical JSON.

Only actual supporting paths define these sheets. The dossier registry includes templates, but template-only occurrences are excluded from the 42-edge worklist. An edge used both in a template and in an actual supporting path is included because of the path use. Zero queries produce no invented path/edge review. No optional template-review table was added.

New immutable outputs are under ignored data/private_gold/phase3/annotation_supplements/runs/<id>/. CSV and source/code/public-reference hashes are recorded in supplement_manifest.json. All three files are written into a hidden staging directory before publication to runs/. Failed generation prints an error and exits 1 without establishing a new complete package. There is no replacement of Phase 3 latest_run.json and no global latest-supplement pointer; older complete packages remain historical snapshots. Single-writer and atomic-directory-rename limitations apply; partial hidden files may remain after failure.

## Actual execution and tests

Baseline command:

```bash
.venv/bin/python -B -m pytest -q -p no:cacheprovider
```

Actual baseline output: `159 passed in 1.30s`, exit 0. Final output after implementation and bounded output-parent checking: `178 passed in 1.49s`, exit 0. The first new-suite run also passed 178 tests in 1.54s. No unexpected test or real-data failures occurred in this correction task. Expected negative fixtures cover tampering, incomplete data, planted private fields, invalid/ignored/symlink output paths, missing manifests, public corruption and partial publication.

The 19 new tests also cover unique/shared original occurrences, duplicate labels, distinct occurrence paths, cross-references, zero/empty cases, exact pointer arrays, all blank decisions, reordered-input repeatability, private-read guards, prior source/public immutability and survival of synthetic existing reviewer notes. Synthetic assertions are software checks, not empirical QA verification.

The actual preparation command ran twice successfully, exit 0 each time:

```bash
.venv/bin/python -B scripts/prepare_qa_annotation_supplement.py
```

Both executions printed `QA supplement: 42 original-occurrence rows; 23 path rows; human fields blank` and a new immutable private package path. Completed directories:

- data/private_gold/phase3/annotation_supplements/runs/0815b6c8d1654e468081a791e39c407b
- data/private_gold/phase3/annotation_supplements/runs/aec5a71214f240a1a7a1f58e3a698baf

Post-generation evaluation-side checking of only these new blank snapshots confirmed 42 unique edge records, 23 stable path records, 52 linked edge positions, all human fields blank and every query/path/edge-position cross-reference consistent. Both CSVs and the complete manifest match byte-for-byte across runs; manifest hashes match actual new files and the recorded source code. No historical annotation content was read.

| Deterministic file | SHA-256 in both runs |
|---|---|
| edge_review_worklist.csv | `1f745dce6b566875fd92e10366fce00697fa51a9eb84479535f174a4b25e40fe` |
| supplement_manifest.json | `d0cf9cef5b4146df897ec8172665e89a80dc39c08ce27e3c534a5c35c9caeaf9` |
| path_composition_worklist.csv | `fad68c1cc55291d23f984c6c4915029f8af464c9b488a1bf04ee90fb501d7f3f` |

## Preservation and privacy

All 69 pre-correction protected fingerprints match, including raw files, original scripts/tests, Phase 0–3 public artifacts/status/validation records, authority/configuration and Git index. Cached Git diff remains unchanged. The eight prior private files retain identical size, mtime_ns and inode; their contents were intentionally not read for this check. Output-path restrictions and non-overwriting publication prevent writing to those earlier packages. All new files are Git-ignored; no private files are tracked. git diff --check exits 0.

| Raw source | Unchanged SHA-256 |
|---|---|
| train | `c40a137a1c57f3e2daaf5ebf511eaa1518f9305ffaa3052d46271921a91826f2` |
| dev | `051ee1d057204a5d08ef5502beacdadf191245b5eaf0e29ec2c607cf002c016f` |
| test | `ea673b7ef91e16510d7eb88863d3903e47318dc5653ef361266f27ae3b84723c` |

## Exact files added or modified

Added public code/tests/docs:

- scripts/prepare_qa_annotation_supplement.py
- tests/test_qa_annotation_supplement.py
- docs/phase3_review_findings.md

Modified documentation only: README.md; docs/data_dictionary.md; docs/qa_annotation_guide.md; docs/decision_log.md.

Added ignored private files:

- data/private_gold/phase3/annotation_supplements/runs/0815b6c8d1654e468081a791e39c407b/edge_review_worklist.csv
- data/private_gold/phase3/annotation_supplements/runs/0815b6c8d1654e468081a791e39c407b/path_composition_worklist.csv
- data/private_gold/phase3/annotation_supplements/runs/0815b6c8d1654e468081a791e39c407b/supplement_manifest.json
- data/private_gold/phase3/annotation_supplements/runs/aec5a71214f240a1a7a1f58e3a698baf/edge_review_worklist.csv
- data/private_gold/phase3/annotation_supplements/runs/aec5a71214f240a1a7a1f58e3a698baf/path_composition_worklist.csv
- data/private_gold/phase3/annotation_supplements/runs/aec5a71214f240a1a7a1f58e3a698baf/supplement_manifest.json

No query engine, dossier generator, historical result, source or selection-policy file was modified. No dependency, configuration, stage, commit, push, merge or remote action occurred. New preparation imports existing validators; no inference module imports the supplement. No generic annotation platform, UI, private-file checker tool or template supplement was needed.

## Historical inventory inspection and cleanup proposal — not executed

All three 11,983,772-byte query_inventory.json files have SHA-256 b81424409c0e66dd79a7801b583f65dcf2239f2d3722416486e21e6aca8bdc25 and Git blob ID b1717992fb4fccaa1871834124d55cfe9986d47e. The five deterministic public files match current references in every run. The current latest record points to runs/e71e70e24e264281b856e709f0555db7 and all six referenced hashes verify.

Computed historical run_manifest.json hashes (different invocations/implementation snapshots are expected):

- 33853cf3204b4d1894d2e2acf17e412e: 454722346d5dd95955b318eddca72d43d5c917aaaf5627aa8c9aa07c77678aa5
- 51a32745b8654b9f91683dd475f34b1f: 714fb7893d65301d186b405e935db33333a9af2004a64878af77adcd82f6342f
- e71e70e24e264281b856e709f0555db7: 5d7d030a677188ea6968beb488e29ce0944a69fc63909b3cc218a33ac7b65a79

Git already deduplicates identical blobs. Three working-tree inventories consume 35,951,316 bytes, but are not three distinct Git inventory blobs. This is checkout maintainability, not a demonstrated tripling of Git object storage.

Proposed smallest cleanup: keep the latest complete public run; after separate explicit approval, add an archival index mapping older run paths/hashes to immutable reviewed commit 5bbed2d891e90111f431cb8b85ad35b864d20a0e, then remove the two older tracked run directories from the current tree. Retain the latest pointer unchanged, clearly resolve historical references through the archival index, and do not rewrite history. Two inventories alone account for 23,967,544 bytes (about 24 MB) of potential checkout savings. Existing Git history would remain.

No archival rewrite, directory deletion, ignore change or published-reference change was executed. Cleanup requires student approval and is separate from scientific results or this completed annotation correction.

## Remaining work and STOP

Independent review of these corrections, human identity and QA decisions, triple support, composition validity, answer correctness and actual annotation effort remain outstanding. Neither pointer availability nor blank worklists resolves semantic feasibility. Preserve UNKNOWN/UNRESOLVED and source-linked partition limitations. Source redistribution/release authenticity and authoritative relation definitions remain unresolved.

Technical correction PASS does not close the scientific QA gate or authorize Phase 4. No fragment creation, identity merge, counterfactual delta, evidence classifier, baseline, risk score, agreement statistic or fabricated label was implemented. Code/tests/docs are AI-assisted and require student understanding and independent review.

**STOP after Phase 3 corrections.**
