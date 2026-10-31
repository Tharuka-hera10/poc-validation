# Phase 0 dataset audit

Schema status: **VALID**. Pattern inspection: **COMPLETE**.

| Split | Documents | Groups | Mentions | Relations | Nonempty evidence | Empty evidence |
|---|---:|---:|---:|---:|---:|---:|
| train | 3053 | 59359 | 79481 | 85932 | 47260 | 38672 |
| dev | 500 | 9684 | 13189 | 17284 | 7473 | 9811 |
| test | 500 | 9779 | 13018 | 17448 | 7547 | 9901 |

Diagnostic counts: `{"name_span_text_difference":2422}`.

Distinct typed patterns observed: 32666.
Incomplete documents: 0.

- 2-hop: 6404 typed patterns; 229812 structural paths; 74683 relation-occurrence paths with all edges pointed.
- 3-hop: 26262 typed patterns; 410929 structural paths; 74145 relation-occurrence paths with all edges pointed.

Duplicate/overlap locations (zero-based):

- title: `[[{"document_index":3052,"split":"train"},{"document_index":469,"split":"dev"}]]`
- sentence_content: `[[{"document_index":3052,"split":"train"},{"document_index":469,"split":"dev"}]]`
- full_document: `[]`

## Entity and relationship suitability

| Split | Relation codes | Multi-mention groups | Mixed-type groups | Name/span differences |
|---|---:|---:|---:|---:|
| train | 96 | 10993 | 29 | 1821 |
| dev | 95 | 1891 | 9 | 284 |
| test | 95 | 1763 | 9 | 317 |

Train/dev descriptive normalized-name collision counts (not candidate labels):

- train: 4542 name strings occur in multiple groups; 4332 occur across documents within that split.
- dev: 750 name strings occur in multiple groups; 739 occur across documents within that split.

## Interpretation and limits

Counts describe annotation structure, not source truth. A nonempty evidence list is a sentence pointer, not verified support. Empty or absent pointers are missing information, never contradiction.

Paths are directed, document-local, exactly 2/3 hops and have distinct vertices. Duplicate typed edges are collapsed for structural counts; relation-occurrence counts retain multiplicity. Pattern counts are lower bounds if INCOMPLETE. Test is excluded from pattern and name-collision discovery.

Different groups/documents are not negative identity labels. Multi-mention groups offer potential controlled-fragmentation material, not natural positive pairs. No identities, verified answers, semantic path validity, merge harm, risk or performance were inferred.

See docs/pilot_feasibility_contract.md for unresolved source, identity, literature and partition decisions. Phase 1 requires separate student approval. STOP.
