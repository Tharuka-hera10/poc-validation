# Phase 3 methodology — phase3-structural-v1

## Authority and scope

The student approved Phase 3, the 12-case mix and source-index/diversity selection. These rules are declared before inspecting any real Phase 3 selected answers. Start on phase-three from merged Phase 2 main commit 9c2fb77. Preserve raw JSON, configuration, staging and Phase 0–2 code/results. No stage/commit/push/merge is authorized.

Only the master research context is locally available; separate supervisor feedback, proposal/literature drafts and primary papers remain unavailable. Summaries are not authenticated supervisor decisions. LACE/ASPEN/LACE+/ASPEN+ already cover collective ER/logical querying. This infrastructure does not establish novelty or GIR-ER benefit over an equally informed matcher.

## Contract and evaluator

`make_query(graph, anchor, relations, type_constraints=None, max_extensions=100000)` creates a source-bound specification. `evaluate_query(graph, query)` uses the previously source-validated original MultiDiGraph. Query/result/package validators enforce nested allowlists. The CLI validates every original node/edge before discovery and after source reconstruction. Callers must not mutate source/graph between validation and evaluation. Separate reviewer preparation reconstructs returned occurrences against actual JSON before publication.

Follow exactly two or three outgoing original relation occurrences in the specified order. All vertices must be distinct: simple paths only. Keep loops/cycles in the graph and count excluded repeated-vertex/self-loop extensions. Unsupported walk policies are rejected. No reverse predicates or natural-language meanings are invented.

Optional type constraints have one position per vertex, including anchor. A position is null or a sorted unique nonempty list of allowed type strings. Match by nonempty intersection with the original annotated type set. Mixed types remain intact; unknown types match nothing. Pilot queries have no type restrictions; observed type combinations are descriptive, not tuned constraints.

Query IDs hash the complete canonical specification: version, split, source SHA-256, anchor provenance, ordered codes, hop count, constraints, path policy and extension limit. Numeric document/entity/label order determines traversal, independent of insertion order. Answer IDs are unique and sorted; all supporting occurrence paths remain, including the Cartesian combinations of repeated typed relations. No graph/source mutation occurs.

Discovery shares a 100,000 examined outgoing-occurrence extension budget across anchors in each source document, to depth three. Each query has a separate 100,000 budget. Examined mismatched/rejected occurrences count. If more work remains beyond the budget, return INCOMPLETE with partial paths/answers; exact-budget natural completion is COMPLETE. An empty incomplete answer list is not a complete zero. CLI discovery/evaluation incompleteness fails explicitly, records FAILED and does not publish a complete workload or substitute easy cases. API discovery diagnostics retain per-document status/lower-bound counts.

## Frozen train-only selection

Discover observed simple chains from train. Aggregate relation/type sequences, occurrence counts, document coverage and all-edges-pointed availability. Original self-loops and excluded extensions are explicit diagnostics. These describe structure, not support. Pattern counts do not rank queries.

Read only Phase 2's verified public candidate export; use its original endpoint IDs for anchored coverage. Never read existing private material. Report coverage for every endpoint separately from general graph feasibility. Anchored reachability is not evidence of ER experiment utility.

Priority and targets are fixed:

1. One endpoint-anchored 2-hop case, then one endpoint-anchored 3-hop case.
2. Four general 2-hop cases, then four general 3-hop cases.
3. One real zero-answer diagnostic per hop length, 2 hops before 3.

Within observed-path roles, order numeric document/anchor indices, relation sequences, then numeric edge-label sequences. Store the first seed per anchor/sequence. Enforce globally unique selected documents/anchors and unique relation sequences within each hop length. General cases may incidentally use remaining candidate endpoints; count overlap without double-counting queries or implying utility. An endpoint role must start at an actual candidate endpoint.

Zero diagnostics use the earliest unused zero-outdegree anchor and earliest unused relation sequence actually observed in train for that hop length. Their template examples are separately referenced and cannot support this anchor's answers. These are deliberate structural diagnostics, not verified natural questions.

Do not filter selected cases by answer size, semantic support or expected merge effects. Record pointer/type/frequency statistics descriptively. Retain role-specific shortages with no relaxation, quota transfer or fabricated cases. No semantic sufficiency has been assessed merely because tokens are inspectable.

## Provenance, review and privacy

Public paths retain ordered node IDs, relation codes, edge keys, original endpoint/label indices, source/document fingerprints and exact optional evidence arrays. Preserve absent versus empty/nonempty evidence, order and duplicates. Public fields are allowlisted; arbitrary source auxiliary metadata is excluded. Private reconstruction retains complete original relations and mentions.

The private dossier uses node/edge evidence registries plus query/path references. Nodes include original mention dictionaries, sentence tokens, half-open spans and name/span warnings. Edges reconstruct original records and evidence sentences using Phase 1. Rendered views are labelled token joins. Zero queries retain anchor evidence. Template examples remain distinct from actual supporting paths.

The CSV has one QUERY row per case and one ANSWER row per structural answer. A zero case still has a QUERY row. All human fields are blank; NOT_ASSESSED is preparation only. Distinguish query interpretation, original triple support, path composition validity and answer correctness. Additional/missing answer evidence can be recorded at query level. Reachability is not semantic correctness or real-world answer completeness.

Write new immutable packages only beneath ignored data/private_gold/phase3/runs/<id>/. Never read previous private identity/QA judgements. Hash private output buffers rather than rereading files. A separate post-generation verification may inspect newly generated blank snapshots; that is evaluation-side checking, not inference. Later methods must receive equal permitted source information and never reviewer outcomes.

## Artifacts and failure contract

Public results/phase3/runs/<id>/ contains query_inventory.json, queries_train.json, structural_query_results.json, query_feasibility_report.md, phase3_report.md and run_manifest.json. Queries/results have strict versioned envelopes. Inventory documents frozen policy, source hashes, graph validation, discovery diagnostics/patterns/endpoint coverage, selection provenance/quotas and overlap policy. Reports interpret those observations. The manifest records code/policy/baseline/source fingerprints, invocation, Python and measured preparation time. These are audit outputs, not runtime identity features.

Private files are qa_review_dossier.json and qa_review_worklist.csv. Compare all five public artifacts excluding run_manifest.json, and both initially blank private artifacts, across repeated runs. Runtime, unique IDs and invocation metadata can vary. Completed human reviews must be separately versioned and never overwritten by generation.

Reuse atomic latest RUNNING/PASS/FAILED status and staged/renamed immutable packages. Final PASS requires both packages complete. Earlier results survive. Missing/unreadable/non-PASS latest or orphan packages do not establish success. Preflight failures before status initialization establish no new attempt; stderr/exit code identify that invocation. One writer per output location; no cross-directory atomic transaction or power-loss guarantee.

Verify only public Phase 0/1/2 references. Protect earlier outputs and private annotation directories. Hash all raw files before/after; test is not parsed. Dev 469 remains excluded from later independent dev evaluation because it duplicates train 3052. No dev/test information influences query design. Exact text equality does not establish entity/paraphrase independence.

## Verification and limitations

Test traversal, types, occurrence multiplicity, direction, zero/invalid cases, loops, exact budgets, insertion ordering, source reconstruction, allowlists, privacy and publication. Run every existing test unchanged. Execute on real train twice, compare deterministic outputs, and reproduce success followed by failure in a safe separate output location. Record actual results/shortages/failures.

Source-order/diversity selection is biased. Phase 2 contains 35 LOC, 11 ORG and 2 PER endpoints linked into eight source-document components. Natural candidates may lack useful compositional effects; anchored paths alone cannot establish usefulness. Relation semantics, human evidence sufficiency/effort, licence/release authenticity and meaningful QA remain unresolved. No private source excerpts are cleared for publication.

Code/tests/docs are AI-assisted. Student review must precede any scientifically verified workload freeze. Technical PASS establishes infrastructure only. No actual fragmentation, merging, counterfactual delta, baseline, evidence classifier, risk or effectiveness claim exists. STOP before Phase 4.
