# Phase 2 validation record

Phase 2 implemented on `phase-two`, based on merged Phase 1 commit `9b9b41d8a3a3317331c0b858d37d67e899a6b2ee`. Technical preparation is ready for independent review; this is not an identity-labelled benchmark or approval of Phase 3.

## Preflight and branch boundary

Python 3.12.15, NetworkX 3.7 and pytest 9.2.0 were already installed; no dependencies changed. The original 70 tests passed during planning. Phase 1 latest status, four referenced artifact hashes and audit/builder implementation hashes matched. All raw fingerprints matched Phase 0. The local main history contained merge PR #2. No live upstream freshness or new primary-paper review is asserted.

Initial branch creation was denied by sandbox permissions (`cannot lock ref ... phase-two.lock: Operation not permitted`, exit 128). Implementation was prepared and tested outside the repository, without modifying main. The student created phase-two; branch, clean state, base commit and portable-patch applicability were verified before installation. No stage, commit, push, merge or Git configuration change was performed by Codex.

## Actual repository tests

```bash
.venv/bin/python -B -m pytest -q -p no:cacheprovider
```

Output: `113 passed in 1.25s`, exit 0. This includes the unchanged 70 Phase 0/1 tests and 43 new synthetic Phase 2 checks. No failures occurred in the installed repository test run. Tests cover deterministic IDs/pairs, every selection category, normalization and abbreviation signals, mixed types, diversity/shortages/empty results, source preservation, missing pointers, nested private-field rejection, train-only discovery, overlap, blank annotation reconstruction, no private reads, protected paths, status/publication failures, interrupted RUNNING and preservation of earlier synthetic annotation notes.

Preparation history: the first temporary test run reported 6 failures and 34 passes because the authored CLI fixture incorrectly declared no duplicate sentence content despite containing repeated synthetic documents. The fixture was corrected to derive its overlap reference; the conservative production overlap check was retained. An attempted combined pytest invocation spanning repository and /tmp roots exited 4 after traversing an inaccessible /tmp/codex-daemon directory; tests were then confined to the temporary workspace (111 passed before two further regression tests were added, then 113 passed). These are software-fixture/harness issues, not dataset identity findings.

## Actual CLI execution

The following command ran successfully twice, exit 0 each time:

```bash
.venv/bin/python -B scripts/candidate_discovery.py --data-dir data/raw/re_docred/data --manifest results/phase0/input_manifest.json --output-dir results/phase2 --review-dir data/private_gold/phase2
```

Both executions printed:

```text
Phase 2 PASS: 856836 discovered pairs; 24 unlabelled natural review cases; controlled pairs 0
Train graph: 59359 nodes / 85932 edges individually reconciled; all source hashes unchanged
```

Completed runs: `runs/837f55d310a64db5b1618d554b3f375d` and `runs/4f974b4911804c1db29777c7e6d1177f`. Preparation time before publication: 15.644s and 17.267s. These are two observations, not a performance benchmark. Unique IDs/timing/invocation metadata are excluded from deterministic comparison.

Every original train node/edge was validated against its annotation under FULL_SPLIT scope: 3,053 documents, 59,359 nodes, 85,932 edges, 47,260 nonempty-pointer occurrences and 38,672 empty-pointer occurrences; zero absent fields. The graph was not merged or fragmented. Dev was loaded only for schema/overlap; test was hashed only. Dev/test graphs were not rebuilt during Phase 2; their Phase 1 artifacts and all source bytes remain unchanged.

## Real-data discovery and worklist

Unique proposed pairs: 856,836. Exact-name: 790,659; exact initialism: 74,989; both rules: 8,812. Source scopes: 466 within-document and 856,370 cross-document discovery pairs. All remain unlabelled. Selection-type exclusions: 417,568; these pairs remain counted in discovery.

| Category | Available | Selected | Target | Diversity skips before quota |
|---|---:|---:|---:|---:|
| sparse_context | 139052 | 4 | 4 | 4 |
| different_name_abbreviation | 39512 | 4 | 4 | 1 |
| challenging_name_collision | 248057 | 8 | 8 | 124 |
| compatible_name_context | 12647 | 8 | 8 | 40 |

All 24 selected pairs are naturally observed and cross-document; 48 distinct source entity endpoints, with no reused matching diversity key. Type counts: LOC 35, ORG 11, PER 2. There are eight selected-case components linked by shared source documents, containing 4, 4, 3, 3, 3, 3, 3 and 1 cases. These are not 24 independent evaluation units. No selection rule was tuned after these observations.

All 24 dossiers have inspectable mention tokens; identity-evidence sufficiency is NOT_ASSESSED for all 24. Five endpoints have no incident relations; 17 have no nonempty incident evidence pointers. Across selected endpoint incidences: 206 nonempty and 134 empty pointers, zero absent. These are availability counts, not truth judgements.

Bounded source-reference examples (selection order, no source excerpts or identity claims):

- `cand_476c46a18fbd09f2baa4b7a9f8687a48b9b9ecd36cc9381829b788338ffa74d4`: `train:0:4` / `train:770:17`, `sparse_context`.
- `cand_4a05495e201b430d1d4e1ecc1e2836f6e5799ce6082dfcd58eeea6cd636bc705`: `train:0:5` / `train:2091:15`, `sparse_context`.

The corresponding private dossier exposes exact source mentions, span tokens, sentence tokens, original incident relationship occurrences, label indices and evidence arrays. CSV and dossier decisions, evidence references, rationale, confidence, reviewer ID/date and adjudication status were independently checked as blank in both newly generated snapshots. No human review, independent identity verification or agreement measurement is claimed.

## Controlled feasibility and overlap

Train contains 10,993 multi-mention groups, including 4,715 with distinct normalized aliases, 9,410 spanning multiple mention sentences and 1,817 with no incident relation. Eligible group/relation incidence counts: 23,778 unique mention-sentence locations, 7,862 multiple compatible locations, 1,543 no matching mention sentence and 23,945 empty-pointer incidences. These are not fragmented edge assignments or verified support. Zero fragments, controlled pairs, parent maps and edge allocations were created. The sentence-bundle proposal and alternatives are documented for separate approval.

The known exact-text group reconciles with Phase 0: train 3052 and dev 469 (Lark Force), sentence-array SHA-256 `f2cc214552dfcd2a98a58cb4b097fe326faa9817e4fb34469faa78381ee5c3c2`. Dev 469 is recorded as ineligible for a later dev evaluation; raw splits are unchanged. None of the 24 selected pairs touches train 3052. Future partitioning must group exact-text content and shared selected source documents; paraphrases and real-world identity overlap remain unresolved.

## Reproducibility and latest-attempt failure regression

All four deterministic public artifacts and both initially blank private artifacts matched byte-for-byte across the two successful CLI executions. Every file also matched the SHA-256 in its status reference. run_manifest.json is excluded because it contains actual invocation/timing metadata.

| Deterministic public artifact | SHA-256 in both runs |
|---|---|
| candidate_feasibility_report.md | `a87c0a3ae0e015d6397778cf10ef99962648dab10e49b914ef12a63a1eab007c` |
| candidate_inventory.json | `ecbadf339811ac5c75b921c57379a4eb65307d97aec7bcb0004cb94318310576` |
| candidates_train.json | `3585ca9f328aece3c6b158367bdc219d5252e6575b66b74a38a09fa6e52f1dcb` |
| phase2_report.md | `8351302803ee2cfa3ef9c529f9305b7d245aad3e0ab819c284deeed59a8b2245` |
| Private initial review_dossier.json | `56ae3b488931d7d8f23d59b1b40acc8ee1e7663b70ea4dcecff2fe99467dfbd8` |
| Private initial review_worklist.csv | `f675701dd08a66146dcabb99c28d4e66cde6eccd9f3cf31b9e2c5436b01c855f` |

After the first real-data success, the same output location was rerun with a missing manifest:

```bash
.venv/bin/python -B scripts/candidate_discovery.py --data-dir data/raw/re_docred/data --manifest /tmp/girer-phase2-missing-manifest.json --output-dir results/phase2 --review-dir data/private_gold/phase2
```

Exit 1. Actual stderr:

```text
Phase 2 failed at verify_baselines_and_sources: [Errno 2] No such file or directory: '/tmp/girer-phase2-missing-manifest.json'
```

latest_run.json became FAILED with stage `verify_baselines_and_sources`, type FileNotFoundError, a meaningful missing-path reason and run_directory=null. Every file in the prior public and private packages stayed byte-identical. The subsequent successful repeat restored latest PASS and produced the second complete run. Earlier directories were never deleted or overwritten.

## Preservation and leakage checks

All 28 protected baseline files remain byte-identical: raw data/README, Phase 0 outputs, both completed Phase 1 output sets/status/validation record, original audit/builder code/tests and project configuration/authority files. The current staging index SHA-256 and `git diff --cached --raw` both match the pre-install snapshot. `git diff --check` exited 0.

| Raw source | Before/after SHA-256 |
|---|---|
| train | `c40a137a1c57f3e2daaf5ebf511eaa1518f9305ffaa3052d46271921a91826f2` |
| dev | `051ee1d057204a5d08ef5502beacdadf191245b5eaf0e29ec2c607cf002c016f` |
| test | `ea673b7ef91e16510d7eb88863d3903e47318dc5653ef361266f27ae3b84723c` |

Candidate export schema checks passed. Nested private-field injection tests reject forbidden data; no arbitrary auxiliary mention metadata enters runtime exports. A read guard confirms candidate generation does not read private-gold files. Verification of the newly generated blank outputs is separate from inference. Private files are Git-ignored (`git check-ignore --quiet` exit 0) and absent from Git status/tracked exports. No existing private annotations were accessed. No controlled mapping was produced.

## Exact files changed or created

Modified existing files: README.md, docs/data_dictionary.md, docs/decision_log.md.

New implementation/documentation files:

- scripts/candidate_discovery.py
- scripts/prepare_annotation_worklist.py
- tests/test_candidate_discovery.py
- tests/test_annotation_worklist.py
- docs/phase2_candidate_methodology.md
- docs/annotation_guide.md

New non-private result files:

- results/phase2/latest_run.json
- results/phase2/validation_record.md
- results/phase2/runs/837f55d310a64db5b1618d554b3f375d/candidates_train.json
- results/phase2/runs/837f55d310a64db5b1618d554b3f375d/candidate_inventory.json
- results/phase2/runs/837f55d310a64db5b1618d554b3f375d/candidate_feasibility_report.md
- results/phase2/runs/837f55d310a64db5b1618d554b3f375d/phase2_report.md
- results/phase2/runs/837f55d310a64db5b1618d554b3f375d/run_manifest.json
- results/phase2/runs/4f974b4911804c1db29777c7e6d1177f/candidates_train.json
- results/phase2/runs/4f974b4911804c1db29777c7e6d1177f/candidate_inventory.json
- results/phase2/runs/4f974b4911804c1db29777c7e6d1177f/candidate_feasibility_report.md
- results/phase2/runs/4f974b4911804c1db29777c7e6d1177f/phase2_report.md
- results/phase2/runs/4f974b4911804c1db29777c7e6d1177f/run_manifest.json

New ignored private files (initial blank snapshots, not for commit):

- data/private_gold/phase2/runs/837f55d310a64db5b1618d554b3f375d/review_dossier.json
- data/private_gold/phase2/runs/837f55d310a64db5b1618d554b3f375d/review_worklist.csv
- data/private_gold/phase2/runs/4f974b4911804c1db29777c7e6d1177f/review_dossier.json
- data/private_gold/phase2/runs/4f974b4911804c1db29777c7e6d1177f/review_worklist.csv

## Independent-review readiness and open decisions

Technically ready for independent Phase 2 review: real source-grounded candidates/worklists exist, provenance/source preservation checks pass, the latest-attempt contract is verified and all 113 tests pass. Technical PASS does not close the scientific feasibility gate. The student still needs to inspect/adjudicate identities (retaining UNKNOWN), assess actual annotation effort, decide whether natural cases support useful query-impact tests and approve any future controlled attribution or QA/evidence protocol.

The selected sample is location-heavy and source-linked; blocking recall and truth balance are unknown. Source licence/authenticity, relation semantics and unavailable standalone research documents remain unresolved. Unwritten future inference modules need their own leakage checks. Exact name/initialism rules miss semantic aliases and may propose spurious abbreviation matches. Large exact blocks grow quadratically. Single-writer output publication is not a cross-directory atomic transaction or power-loss guarantee.

No ER classifier/baseline, labelled QA workload, graph merge/fragmentation, counterfactual delta, risk score, API, frontend or improvement claim was implemented. LACE/ASPEN/ASPEN+ novelty boundaries and the future B3+same-evidence control remain governing. Code/tests/docs were AI-assisted; student ownership and independent methodological review remain required.

**STOP after Phase 2. No Phase 3 or actual fragmentation without explicit approval.**
