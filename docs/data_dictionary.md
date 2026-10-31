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

## Phase 1 graph and execution contract, version 2

The Phase 0 schema and findings above remain unchanged. Phase 1 reuses its strict loader and validator without pattern discovery. A validation error aborts construction of the split; warnings remain visible. Absent evidence is a warning and stays absent, empty lists stay empty, and malformed/null/out-of-range evidence is rejected.

Graph nodes represent original document-scoped entity groups; IDs are `split:document_index:entity_index`. Each node stores `source_mentions` (deep-copied original mention dictionaries) and separate `provenance` containing split, original indices, document ID/title, raw-file fingerprint and canonical parsed-document fingerprint.

Edges represent original relation occurrences. Keys are `split:document_index:label_index`; `(u,v,key)` identifies the directed occurrence. Attributes are `source_relation` (deep-copied complete relation dictionary), `relation` (original code), `evidence_availability` (absent/empty/nonempty), and `provenance` (document context plus original label/head/tail indices). Edge keys may resemble node IDs but occupy a separate NetworkX namespace. No source field is overwritten by derived metadata.

Graph metadata records split, source fingerprint, document scope, per-document fingerprints and copied warnings. Loaded source documents remain outside the graph. `SourceSplit` is the external lookup returned by the verified file loader; it is a frozen record containing mutable original documents. Callers should not modify them. Graph attribute and reconstruction-result mutations cannot change them. Direct document construction trusts its caller-supplied fingerprint; only file loading verifies raw bytes against the manifest.

Validation visits every node and edge in the graph's declared document scope, compares exact JSON values/types and provenance, then rejects unexpected nodes/edges. It detects wrong topology even when totals match. `validate_graph_provenance(graph, source, *, require_full_split=False)` preserves subset support but returns `validation_scope` (FULL_SPLIT or SUBSET), `full_split`, `documents_available` and `documents_validated`. FULL_SPLIT requires nonempty source data and exact coverage of all source document indices, irrespective of order. Empty scope is SUBSET. Malformed, duplicate, boolean and out-of-range indices are rejected. With `require_full_split=True`, partial coverage raises an error even when internally consistent. The full-data CLI always enables that stricter condition. Canonical JSON comparison distinguishes booleans from numbers. Original dictionary field order is not a semantic acceptance condition; list ordering and original values are preserved.

`reconstruct_edge_source` verifies graph/source split, raw-file fingerprint, document scope/hash, edge identifiers, relation and endpoint records. It returns the original relation, original mention dictionaries, sentence tokens, mention-span tokens and evidence sentence arrays in original pointer order. It does not infer sentence whitespace or identity truth.

The bounded demonstration uses the first train document containing a relation and its first at most three labels. It displays up to two mentions per endpoint and three evidence references per relation with omission counts. A `rendered_view` is a token-joined display only. Other splits undergo integrity verification without example or workload selection.

Phase 1 outputs are graph_summary.json, provenance_demo.json, run_manifest.json and phase1_report.md under immutable results/phase1/runs/<run-id>/ directories. A separate top-level validation_record.md records actual tests/repeated-run checks. Graphs are reconstructed in memory, not exported in full. Existing top-level artifacts are preserved historical snapshots, not the current attempt.

`latest_run.json` is the authoritative latest recorded attempt. Fields include format_version=2, run_id, command, status (RUNNING/PASS/FAILED), run_directory (relative completed directory on PASS, otherwise null) and error (null or stage/type/reason). PASS additionally includes SHA-256 hashes for all four artifacts. A successful summary alone is not proof of latest-attempt success. Users must check latest status and its references/hashes.

The CLI checks protected output paths before writing, atomically publishes RUNNING before loading the manifest, writes artifacts to a hidden same-filesystem staging directory, renames it into runs/ after all writes complete, and finally atomically publishes PASS. A handled failure publishes FAILED; an interruption can leave RUNNING. Partial directories and completed directories without a committed latest PASS are not authoritative for the latest attempt. Existing results are never deleted or overwritten. Hidden incomplete files may remain for diagnosis. Failure before safe status initialization is reported on stderr and establishes no new recorded attempt. Output paths and new control paths receive the source/private-gold/Phase 0 protection and symlink checks. Single writer per output directory is required; this is process-visible atomic publication, not a guarantee against all power/storage failures.

The deterministic summary (format version 2), demonstration and report exclude unique run IDs and machine metadata. New output paths and scope fields do not change node/edge IDs, source copies, evidence semantics or graph normalization. Phase 0 formats and files are unchanged.

## Phase 2 candidate/preparation contract, version 1

Generation version is phase2-candidates-v1. Natural endpoint IDs retain Phase 1 split/document/entity IDs; candidate IDs hash the generation version, raw source SHA-256 and canonically ordered endpoints. No controlled IDs or mappings are created.

The inference-safe envelope contains format_version, candidate_generation_version, source_sha256 and candidates. Each candidate has candidate_id, left_entity_id, right_entity_id, creation_mode=naturally_observed, selection_rule_ids, dataset_split=train, candidate_generation_version, review_status=UNREVIEWED, permitted_name_features, permitted_type_features, permitted_context_features and provenance_reference. Nested objects are allowlisted. Original/normalized aliases remain separate. Context signatures record IN/OUT, original relation codes and neighbour type sets; incident/evidence counts retain occurrence multiplicity. IDs, review status and provenance are administrative, not intended identity features.

candidate_inventory.json records the frozen policy, complete discovered pair counts, type exclusions, category availability, selected IDs/categories, diversity skips before quota, shortfalls, natural/controlled separation, pointer availability and train/dev exact-text exclusions. Selection categories never appear as verified identity labels. Identity sufficiency remains NOT_ASSESSED until human review. Unique pointer/mention location counts in controlled feasibility are not allocated edges or semantic support.

The two private reviewer artifacts preserve original mentions, half-open spans, sentence tokens, original incident labels and exact evidence arrays. Rendered views join tokens. reviewer_decision, evidence_references, rationale, confidence, reviewer_identifier, review_date and adjudication_status are all blank initially. UNKNOWN requires an actual review decision; it is not generated as a label.

Public preparation artifacts live in results/phase2/runs/<run-id>/; private reviewer artifacts live in data/private_gold/phase2/runs/<run-id>/. latest_run.json records RUNNING/PASS/FAILED, run ID, successful public/private paths and buffer SHA-256 hashes when complete. A failure contains stage/type/reason and no successful run reference. Both packages must be completed before final PASS. This is not a cross-directory atomic transaction; orphan packages and interrupted RUNNING states do not establish latest success. Existing records are never overwritten. Private files are never read by candidate generation; hashing their initial output buffers does not require reading annotations.

Four public artifacts and the initial two private artifacts are deterministic. run_manifest.json records source/implementation/policy/Phase 0/Phase 1 fingerprints, invocation, available research context and actual preparation time; its machine/run metadata may differ. Human annotations must be kept separately from the initial blank snapshot and never become runtime fields. Source redistribution remains unresolved.

## Phase 3 structural query contract, version 1

Generation version: phase3-structural-v1. queries_train.json has exactly format_version, query_version, source_sha256 and queries; structural_query_results.json has the same metadata and results. Validators enforce both envelopes and all nested inference records. These are structural inputs/results, never verified QA references.

Query fields: query_id, query_version, dataset_split, anchor_entity_id, relations, hop_count, type_constraints, path_policy=simple, source_sha256, anchor_provenance and max_extensions. Anchor provenance contains split, document_index, entity_index, source_sha256 and document_sha256. Query ID hashes the complete canonical specification excluding query_id itself. Allowed hop counts are integer 2/3; optional constraints have hop_count+1 null or sorted unique nonempty allowed-type lists, matched by intersection.

Result fields: query_id, query_version, source_sha256, status=COMPLETE/INCOMPLETE, answer_ids, paths and diagnostics. Answer IDs are sorted/deduplicated; INCOMPLETE answers are partial, including when empty. Each path has node_ids, relations and edge_occurrences. Occurrences contain head_entity_id, tail_entity_id, edge_key, relation, provenance, evidence_availability and optional exact evidence array. Occurrence provenance contains split, document_index, label_index, head_index, tail_index, source_sha256 and document_sha256. Absent evidence is omitted; empty/nonempty lists retain their original order/duplicates. Arbitrary source fields are excluded from inference structures and preserved in private reconstruction.

Diagnostics contain limit, extensions, excluded_repeated_vertex_extensions, excluded_self_loop_extensions and status. Discovery uses a shared per-document budget and records document_runs, ordered relation/type patterns and occurrence/document/pointed-path counts, source self-loops and candidate_endpoint_coverage. query_inventory.json adds policy, source hashes, train_graph_validation, selection seed provenance/quotas/shortfalls, candidate_summary and overlap_policy. It is an audit artifact, not a runtime identity feature input. Reports summarize that inventory without source quotations or semantic truth claims.

Private qa_review_dossier.json contains format_version, source_sha256, queries, node_evidence, edge_evidence and interpretation. Query entries reference original nodes/edges, distinguish actual structural paths from template examples and retain NOT_ASSESSED preparation state. qa_review_worklist.csv has query_id, row_scope=QUERY/ANSWER, structural_answer_id, dossier_reference and the blank human fields defined in docs/qa_annotation_guide.md. All query-level/answer-level reviewer judgements are blank initially. Every query has a QUERY row, including zero-answer cases.

Public/private packages use new immutable run directories. latest_run.json retains RUNNING/PASS/FAILED and completed package paths/hashes on PASS; failed status has stage/type/reason and no successful-run reference. Both packages must be complete before PASS. Five public artifacts and the initial two private files are deterministic; run_manifest.json contains source/code/policy/Phase 0/1/2 fingerprints, invocation, Python and runtime metadata. Partial/orphan packages are not latest success. Single-writer and process-visible atomic-publication limits remain. Human annotations must be separately versioned and never read as inference features.
