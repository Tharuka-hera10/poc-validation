# GIR-ER Phase 3 structural workload

Technical execution: PASS. Semantic verification: NOT PERFORMED.

Version: `phase3-structural-v1`. Selected queries: 12. Source-only selection rules were declared before answer evaluation.

| Role | Hops | Target | Selected | Shortfall |
|---|---:|---:|---:|---:|
| candidate_endpoint | 2 | 1 | 1 | 0 |
| candidate_endpoint | 3 | 1 | 1 | 0 |
| general | 2 | 4 | 4 | 0 |
| general | 3 | 4 | 4 | 0 |
| zero_diagnostic | 2 | 1 | 1 | 0 |
| zero_diagnostic | 3 | 1 | 1 | 0 |

| Query | Hops | Structural answers | Occurrence paths | Status |
|---|---:|---:|---:|---|
| query_42ee3a5a8d5e59619ee11566b99a04e924f958c1820d3192e272bfe607485dea | 2 | 1 | 1 | COMPLETE |
| query_d20f97547e868436c2a64a30835a16834c5cbdceeadb50b9221ee685cdc513c4 | 3 | 1 | 1 | COMPLETE |
| query_4e4c25ca12e274c383ade25455bfb299221b777c73c8de169a96922ce6b53e8a | 2 | 4 | 9 | COMPLETE |
| query_1afc700695ea8968a15fd050bf98dafc7b1a6e9280c31b15c8a1c51abc284a1c | 2 | 1 | 1 | COMPLETE |
| query_2706aa66ea34e37e8c50f5179213f2171ff582a5e7080fba516dc8c5ef4e795e | 2 | 4 | 4 | COMPLETE |
| query_e2920d59887f32a60662ff184e2f2631583bcfbb1b77a118e413c9d15e4092c0 | 2 | 1 | 2 | COMPLETE |
| query_4f3131f0b9821bd937988b964798044fc807ebded8aa9d569b64b85bcc5c6709 | 3 | 1 | 1 | COMPLETE |
| query_cfad92ace3b2ebc36709c3da576155237509650fd058d32909cf05ea6c81d866 | 3 | 1 | 1 | COMPLETE |
| query_2494ff09561e7b641c9609884673613b0a852111873e4f028b68488d8fdc0531 | 3 | 1 | 1 | COMPLETE |
| query_b68ef9f2f3ab92510a5616759327ce8ba4adaa7d129db8c29af0d6e26a3f31bd | 3 | 1 | 2 | COMPLETE |
| query_42e0fd76479fde01f724cd92906bdf001801550f3a27593d4fbc82c94d7d01c3 | 2 | 0 | 0 | COMPLETE |
| query_e3f529a9d91bb14c64d2a9e8a50cf3763c9767a0be83c1e3f3e2956860b0e714 | 3 | 0 | 0 | COMPLETE |

Train graph FULL_SPLIT reconciliation: `{"absent":0,"documents_available":3053,"documents_validated":3053,"edges":85932,"edges_validated":85932,"empty":38672,"full_split":true,"nodes":59359,"nodes_validated":59359,"nonempty":47260,"provenance_status":"PASS","validation_scope":"FULL_SPLIT"}`.
General train occurrence-chain counts by hop: `{"2":184983,"3":320579}`.
Candidate endpoint coverage: `{"endpoint_count":48,"selected_queries_anchored_at_endpoint":2,"with_three_hop_chains":26,"with_two_hop_chains":31}`. Coverage is anchored structural reachability, not usefulness for ER.
Source self-loops: 0. Repeated-vertex exclusions are recorded per document and query.

Every returned occurrence is reconstructed against original labels and tokens. Answer IDs are deduplicated while all supporting occurrence paths remain. Simple paths exclude self-loops and repeated vertices; the original graph retains them. Type constraints use nonempty intersection with original type sets. Queries follow outgoing edges and never invent reverse relations.

## Research and evidence limits

Structural reachability is not independently verified QA. Relation codes remain uninterpreted; no natural-language questions or semantic support labels are generated. Pointers describe annotation availability, not support. Structural zero does not establish semantic absence. All reviewer judgements are blank.

The pilot uses source order and document/anchor/relation diversity, with candidate reservations first. This biases the workload. Zero diagnostics deliberately use zero-outdegree anchors and are reported separately. A shortage is retained without substitution. Queries were not screened by answer size, identity outcomes or future merge effects.

Phase 2 has 35 LOC, 11 ORG and 2 PER endpoints in eight source-linked components. Natural cross-document candidates may lack useful within-document compositions; even existing anchored paths do not establish an informative merge experiment. No merges were simulated.

Train 3052/dev 469 exact text overlap remains excluded from later independent dev evaluation; no raw document changed. Exact text grouping does not establish entity/paraphrase independence. Dev/test did not influence pattern selection.

Source licence/release authenticity and relation definitions remain unresolved. Only the master research context is available; separate supervisor feedback, proposal/literature drafts and primary papers are unavailable. No authenticated supervisor decision or new literature verification is asserted.

LACE/ASPEN/LACE+/ASPEN+ already cover collective ER/query reasoning. Traversal infrastructure is not a novelty claim. GIR-ER's incremental benefit over an equally informed matcher remains unvalidated, including possible zero or negative results.

## Reproduce

```bash
.venv/bin/python -B scripts/query_workload.py --data-dir data/raw/re_docred/data --manifest results/phase0/input_manifest.json --output-dir results/phase3 --review-dir data/private_gold/phase3
.venv/bin/python -B -m pytest -q -p no:cacheprovider
```

Read ../../latest_run.json first. Only PASS plus complete referenced artifacts establishes latest success. Partial/orphan directories do not. Compare all deterministic artifacts except run_manifest.json; IDs/timing metadata may vary. See ../../validation_record.md for actual tests and failure checks.

Student review of identities, query interpretation, individual triple support, composition and answer evidence remains required. No verified workload freeze, QA accuracy, ER classifier, fragmentation, counterfactual delta or risk score exists. STOP before Phase 4.
