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
