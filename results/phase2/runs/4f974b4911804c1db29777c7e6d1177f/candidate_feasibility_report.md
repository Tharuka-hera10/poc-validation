# Phase 2 candidate feasibility

Natural discovery pool: 856,836 unique unlabelled train pairs. Selected for review: 24.

Controlled resources and pointer ambiguities: `{"controlled_candidate_pairs":0,"edge_allocations":0,"fragments_created":0,"groups":{"distinct_normalized_aliases":4715,"multi_mention":10993,"multiple_mention_sentences":9410,"no_incident_relations":1817},"incident_entity_relation_location_counts":{"empty_pointers":23945,"multiple_sentence_locations":7862,"no_matching_mention_sentence":1543,"unique_sentence_location_only":23778},"interpretation":"Counts concern original entity/relation incidences, not assigned edges. Unique pointer location is not verified attribution.","status":"FEASIBILITY_ONLY"}`.

Proposed future policy: bundle original mentions by sentence; require separately approved, source-checked endpoint attribution. Empty/absent pointers, zero or multiple compatible sentence bundles, and unclear semantic links remain unresolved. Never copy every original relation to every fragment. No proposed allocation is executed here.

The worklist supports identity review and exposes relation context. It does not yet establish beneficial/harmful merge cases, interpretable multi-hop workloads or verified answers. Natural cross-document merges may have no compositional effect. Those limitations can lead to an inadequate pilot or negative GIR-ER result and must be reported.

Next student decisions: perform/review identity annotation, retain UNKNOWN where needed, decide whether controlled cases are necessary, approve any actual fragmentation policy, and approve separate QA/evaluation methodology before later phases. No private annotation may become a runtime feature; all future comparisons require equal permitted evidence.
