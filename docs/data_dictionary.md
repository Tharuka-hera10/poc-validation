# Phase 0 observed data dictionary

The source is `data/raw/re_docred/data/{train,dev,test}_revised.json`, each a JSON list. The nested README says only `data dir`; acquisition URL, release version, licence and relation-name metadata are not locally documented. All positions below are zero-based.

| Field | Observed form | Interpretation and audit rule |
|---|---|---|
| `title` | string | Display/source title, not a unique document or global entity ID |
| `sents` | list of token-string lists | Original source tokens; keep boundaries and token text |
| `vertexSet` | list of nonempty mention lists | Existing within-document coreference annotations; not cross-document identity gold |
| mention `name`, `type` | strings | Original mention name and coarse annotation type |
| mention `sent_id` | integer | Index into this document's sentences |
| mention `pos` | two integers | Half-open token span `[start,end)` within the sentence |
| mention `global_pos` | two-integer list | Auxiliary original metadata; semantics not established; zero pairs retained |
| mention `index` | string | Auxiliary original metadata; do not interpret as a real-world identity |
| `labels` | list of relation objects | Fixed annotated relations available equally to later methods under the approved input policy |
| relation `h`, `t` | integers | Directed head/tail indices into this document's `vertexSet` |
| relation `r` | string | Original relation code; retain without inventing a name/meaning |
| relation `evidence` | list of sentence indices | Annotation pointers; validity is not semantic support |

All actual mentions contain `global_pos` and `index`. The validator permits their absence for compatibility, validates them if supplied, and reports field/type variants. Additional fields are preserved in the untouched raw records and represented in schema variants. Required document fields and core mention/relation fields are validated. JSON duplicate keys, non-JSON constants, boolean indices, empty root datasets and invalid bounds are errors.

The observed entity types are PER, ORG, LOC, TIME, NUM and MISC. Mixed types within a group are descriptive findings, not identity contradictions. Mention names may differ from token-joined spans due to formatting or other unverified causes; neither field is rewritten.

## Audit output contract, version 1

- `input_manifest.json`: file paths, byte lengths, before/after SHA-256, audit script SHA-256, raw directory filename inventory. Inventory paths are relative to `re_docred/`; input paths retain the supplied path form.
- `dataset_audit.json`: split counts, schema variants, located diagnostics, evidence coverage, relation and mention histograms, train/dev name-collision counts and overlap locations. Statistics use structurally valid documents; evidence states across all relation objects are separately available. All actual documents passed validation.
- `pattern_inventory.json`: train/dev only; computational bound, per-document completion and extension counts, ordered relation/type sequences, structural path and multiplicity counts, document coverage and one deterministic provenance example per pattern.
- `environment.json`: Python executable/version, platform, installed packages, exact invocation, script hash and read-only Git inspection. Package presence does not mean the audit used that package.
- `audit_report.md`: generated human-readable observed counts and limitations. `feasibility_report.md` is a separate Phase 0 interpretation with execution/test evidence.

An example path records split, document index, file hash, original entity indices, relation-label indices and evidence sentence indices. Fetch original `labels[label_index]` and `sents[sentence_index]` from the fingerprinted source to reconstruct it. Sentence display, if needed, is token-joined rendering, not a recovered original whitespace string. Diagnostics use JSON-like locations such as `$[5].vertexSet[0][0]`.

## Structural pattern counting

Edges are directed `(h,r,t)` triples. Identical typed triples collapse only in temporary inspection adjacency; relation occurrence indices stay attached. A structural path has exactly 2 or 3 edges and all vertices distinct. A pattern key includes the ordered relation codes and each vertex's observed type set. Different typed routes over the same vertices remain distinct structural paths.

`structural_paths` counts deduplicated typed paths. `relation_occurrence_paths` weights each path by the product of edge multiplicities. `all_edges_pointed_occurrence_paths` uses the product of the number of nonempty-evidence occurrences per edge. It counts pointer availability only. Examples prefer the first pointed occurrence of each edge, otherwise the first occurrence. Repeated-vertex extensions are counted and excluded; they are not reported as cycle path totals. Self-relations are counted independently in dataset statistics.

Inspection follows ascending entity and `(h,r,t)` order, document order, then train/dev split order. Counts and examples are reproducible. A cap limits attempted extensions per document; a partial inventory is explicitly INCOMPLETE. There is no cross-document adjacency or inverse-edge synthesis. These paths are not semantic entailments, proposed QA templates or verified answers.
