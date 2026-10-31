# Independent QA review guide

The generated workload contains structural questions and reachable entity IDs, not independently verified QA. Every human field starts blank. NOT_ASSESSED describes preparation and is not a human UNKNOWN decision. Keep the generated snapshot intact and save completed annotations separately under ignored private_gold/phase3.

Match query IDs between qa_review_worklist.csv and qa_review_dossier.json. Inspect the exact query and follow node/edge registries for original mentions, half-open spans, token arrays, relation-label indices and evidence pointers. Rendered views join tokens; they are not original whitespace. Preserve name/span warnings. Source references must identify split, document/entity/mention/sentence/label indices and dataset SHA-256.

Review four levels separately:

1. Query interpretation: obtain authoritative relation meanings and write a defensible interpretation of the ordered chain. Use UNKNOWN when unavailable; never invent predicate meanings.
2. Original triple support: assess each original occurrence against source context. Pointers alone prove no proposition. Empty/absent pointers are not contradiction.
3. Composition validity: assess whether joining those relations licenses the interpretation. Two supported edges do not establish that their composition means the proposed question.
4. Answer correctness: independently check each structural answer against the interpretation and source evidence. Record additional/missing answer references at query level. Reachability is not correctness, and complete traversal is not real-world answer completeness.

The sheet has a QUERY row for every case and an ANSWER row for each structural answer. Zero cases have a QUERY row only and are not verified negatives. Zero-outdegree diagnostics deliberately test graph mechanics. Observed template examples may come from another document and must never be treated as support for this anchor's answers.

Use VALID / INVALID / UNKNOWN for interpretation and SUPPORTED / CONTRADICTED / UNRESOLVED for explicit evidence propositions. State which proposition and level each decision concerns. CONTRADICTED requires positive conflicting evidence; failure to find support remains UNRESOLVED. These are human record choices, not an automated classifier or approval of a later runtime evidence protocol.

Blank fields: reviewer_identifier, review_date, query_semantic_interpretation, interpretation_validity_decision, supporting_source_references, source_relation_support_assessment, path_composition_validity, candidate_answer_correctness, answer_evidence_references, additional_answer_references, reviewer_rationale, reviewer_confidence and adjudication_status. Enter actual reviewer/date only after review. Confidence may be reviewer-reported low/medium/high with rationale; it is not calibrated. Do not invent reviewers, independent verification or agreement. Preserve disagreements before actual adjudication.

Read the full original local document when needed. External sources or relation dictionaries require provenance/access dates under a reviewed source-use protocol; no external retrieval is implemented here. Keep identity evidence distinct from query/answer evidence. Never use future merge/risk predictions to choose references, force target outcomes or remove difficult cases. Preserve unknowns.

Keep decisions, confidence, verified answers and source excerpts private and evaluation-only. Future inference must not read this directory; comparators must use equally permitted source interfaces. Redistribution is unresolved. Technical Phase 3 success does not establish a semantically verified workload. Human identity/QA review, source-linked partitioning and explicit student approval remain required before Phase 4. STOP; no merge/counterfactual work is authorized.

## Post-review triple and composition supplements

The existing QUERY and ANSWER rows remain unchanged. A separate preparation tool creates edge_review_worklist.csv and path_composition_worklist.csv under data/private_gold/phase3/annotation_supplements/runs/<id>/. It uses original train JSON plus frozen public Phase 3 results, never previous private annotations. Use the existing QA dossier and exact source coordinates for text inspection; generation does not copy reviewer decisions from that dossier.

Each edge row identifies one original occurrence used in actual supporting paths. Each composition row identifies one selected query/occurrence path and its structural answer. Stable edge-review/path IDs link the two sheets; query_path_references includes zero-based edge_position. Arrays and source references are canonical JSON inside CSV cells. An occurrence shared by several paths has one edge record and all usage references. Distinct duplicate source labels retain distinct edge records. Zero-answer diagnostics generate no artificial path or edge records.

IMPORTANT: supporting_paths are actual returned graph paths. template_example_edge_keys merely show where the relation pattern occurred, potentially under a different anchor/document. Template-only edges must never be used as answer evidence or inserted into the supporting-occurrence review sheet. An edge used both as an example and as an actual supporting occurrence is reviewed because of its actual path use. The frozen snapshot has 42 supporting occurrences and 23 paths; the dossier's larger 55-edge registry includes 13 template-only occurrences.

For each edge, review triple_support_decision separately, with supporting_sentence_references and contradictory_source_references, reviewer_rationale, reviewer_confidence, reviewer_identifier, review_date and adjudication_status. Every field starts blank. A nonempty pointer is metadata, not a supporting decision; an empty/absent pointer is not contradictory evidence. Use SUPPORTED/CONTRADICTED/UNRESOLVED only after assessing an explicit proposition under this human-review guide.

For each path, separately record relation_chain_interpretation, path_composition_validity, source_evidence_references, unresolved_ambiguity, reviewer_rationale, reviewer_confidence, reviewer_identifier, review_date and adjudication_status. All start blank. Supported triples do not establish composition validity, and valid composition does not independently establish answer correctness. Preserve the original query/answer judgements as separate reviews. Record unknown/UNRESOLVED after review rather than automatically filling them.

Run `.venv/bin/python -B scripts/prepare_qa_annotation_supplement.py`. The printed immutable package is new on every success. supplement_manifest.json records input fingerprints and CSV hashes; only a fully published runs/<id>/ package is complete. There is no replacement of Phase 3 latest_run.json or global latest-supplement pointer. Failures print an error/exit 1 and establish no new completed package; hidden staging leftovers are not completed runs. Keep the blank snapshot and save completed reviews separately. Never publish these private sheets. See phase3_review_findings.md for independently reviewed limitations and actual correction checks.
