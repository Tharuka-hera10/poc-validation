"""Preparation-only QA dossier; no human judgement is inferred or read."""

from copy import deepcopy
import csv
import io

from scripts.build_graph import reconstruct_edge_source, require, validate_graph_provenance


REVIEW_FIELDS = ("reviewer_identifier", "review_date", "query_semantic_interpretation",
                 "interpretation_validity_decision", "supporting_source_references",
                 "source_relation_support_assessment", "path_composition_validity",
                 "candidate_answer_correctness", "answer_evidence_references",
                 "additional_answer_references", "reviewer_rationale", "reviewer_confidence", "adjudication_status")


def make_qa_dossier(graph, source, queries, results, selection):
    """Reconcile every returned occurrence to original tokens; retain blank decisions."""
    from scripts.query_workload import indices, node_reference, validate_result
    require(source.split == "train", "QA reviewer preparation accepts train only")
    validate_graph_provenance(graph, source, require_full_split=True)
    require(len(queries) == len(results) == len(selection["selections"]), "Query/result/selection reconciliation failed")
    nodes, edges, entries = {}, {}, []

    def add_node(nid):
        if nid not in nodes:
            di, ei = indices(nid)
            doc = source.documents[di]
            mentions = []
            for mi, mention in enumerate(doc["vertexSet"][ei]):
                sentence = doc["sents"][mention["sent_id"]]
                start, end = mention["pos"]
                mentions.append({"mention_index": mi, "source_mention": deepcopy(mention),
                                 "sentence_tokens": deepcopy(sentence), "span_tokens": deepcopy(sentence[start:end]),
                                 "rendered_view": " ".join(sentence),
                                 "name_span_difference": mention["name"] != " ".join(sentence[start:end])})
            nodes[nid] = {"provenance": node_reference(graph, nid), "mentions": mentions}

    def add_edge(u, v, key):
        if key not in edges:
            trace = reconstruct_edge_source(graph, u, v, key, source)
            for sentence in trace["evidence_sentences"]:
                sentence["rendered_view"] = " ".join(sentence["tokens"])
            edges[key] = trace
            add_node(u); add_node(v)

    for query, result, selected in zip(queries, results, selection["selections"]):
        validate_result(result, query)
        require(result["status"] == "COMPLETE" and selected["query_id"] == query["query_id"], "Incomplete or mismatched reviewer query")
        add_node(query["anchor_entity_id"])
        paths = []
        for path in result["paths"]:
            for occurrence in path["edge_occurrences"]:
                add_edge(occurrence["head_entity_id"], occurrence["tail_entity_id"], occurrence["edge_key"])
                actual = edges[occurrence["edge_key"]]
                require(actual["source_relation"]["r"] == occurrence["relation"]
                        and actual["evidence_availability"] == occurrence["evidence_availability"]
                        and ("evidence" in actual["source_relation"]) == ("evidence" in occurrence)
                        and actual["source_relation"].get("evidence") == occurrence.get("evidence"), "Path/source occurrence mismatch")
            paths.append({"node_ids": path["node_ids"], "edge_keys": [e["edge_key"] for e in path["edge_occurrences"]]})
        template_keys = []
        for key in selected["template_origin_edge_keys"]:
            di, li = indices(key)
            label = source.documents[di]["labels"][li]
            add_edge(f"train:{di}:{label['h']}", f"train:{di}:{label['t']}", key)
            template_keys.append(key)
        entries.append({"query": deepcopy(query), "role": selected["role"], "preparation_status": "NOT_ASSESSED",
                        "structural_answer_ids": list(result["answer_ids"]), "supporting_paths": paths,
                        "template_example_edge_keys": template_keys,
                        "template_interpretation": "Template examples show observed relation sequences; they are not evidence for this query's answers.",
                        "answer_reviews": [{"answer_entity_id": n, **{f: "" for f in REVIEW_FIELDS}} for n in result["answer_ids"]],
                        **{f: "" for f in REVIEW_FIELDS}})
    return {"format_version": 1, "source_sha256": source.sha256, "queries": entries,
            "node_evidence": nodes, "edge_evidence": edges,
            "interpretation": "Structural answers only; token joins are rendered views; all human review fields are blank."}


def qa_worklist_csv(dossier):
    """Keep query-level and answer-level review distinct, including empty answer sets."""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=("query_id", "row_scope", "structural_answer_id", "dossier_reference", *REVIEW_FIELDS), lineterminator="\n")
    writer.writeheader()
    for entry in dossier["queries"]:
        qid = entry["query"]["query_id"]
        for scope, answer in [("QUERY", ""), *(("ANSWER", a) for a in entry["structural_answer_ids"])]:
            writer.writerow({"query_id": qid, "row_scope": scope, "structural_answer_id": answer,
                             "dossier_reference": "qa_review_dossier.json#" + qid, **{f: "" for f in REVIEW_FIELDS}})
    return output.getvalue()
