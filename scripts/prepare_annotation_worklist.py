"""Preparation-only reviewer evidence; never an inference or private-label reader."""

from copy import deepcopy
import csv
import io

from scripts.build_graph import edge_key, reconstruct_edge_source, require, validate_graph_provenance


ANNOTATION_FIELDS = ("reviewer_decision", "evidence_references", "rationale", "confidence",
                     "reviewer_identifier", "review_date", "adjudication_status")


def make_review_worklist(candidates, source, graph):
    """Reconstruct selected original evidence and leave every judgement blank."""
    require(source.split == "train", "Reviewer preparation accepts train only")
    validate_graph_provenance(graph, source, require_full_split=True)
    entries = []
    for candidate in candidates:
        endpoints = {}
        for side in ("left", "right"):
            nid = candidate[f"{side}_entity_id"]
            require(nid in graph, f"Unknown candidate endpoint: {nid}")
            ref = graph.nodes[nid]["provenance"]
            di, ei = ref["document_index"], ref["entity_index"]
            document = source.documents[di]
            group = document["vertexSet"][ei]
            mentions = []
            sentence_ids = set()
            for mi, mention in enumerate(group):
                sid = mention["sent_id"]
                start, end = mention["pos"]
                tokens = document["sents"][sid]
                sentence_ids.add(sid)
                mentions.append({"mention_index": mi, "source_mention": deepcopy(mention),
                                 "span_tokens": deepcopy(tokens[start:end]),
                                 "name_span_difference": mention["name"] != " ".join(tokens[start:end])})
            relations = []
            availability = {"nonempty": 0, "empty": 0, "absent": 0}
            for li, label in enumerate(document["labels"]):
                if ei not in (label["h"], label["t"]):
                    continue
                u, v = (f"train:{di}:{label[k]}" for k in ("h", "t"))
                trace = reconstruct_edge_source(graph, u, v, edge_key("train", di, li), source)
                availability[trace["evidence_availability"]] += 1
                sentence_ids.update(label.get("evidence", []))
                relations.append({"edge_key": trace["edge_key"], "provenance": trace["provenance"],
                                  "source_relation": trace["source_relation"],
                                  "evidence_availability": trace["evidence_availability"]})
            endpoints[side] = {
                "entity_id": nid, "provenance": deepcopy(ref), "mentions": mentions,
                "sentences": [{"sentence_index": sid, "tokens": deepcopy(document["sents"][sid]),
                               "rendered_view": " ".join(document["sents"][sid])}
                              for sid in sorted(sentence_ids)],
                "original_incident_relations": relations, "evidence_pointer_availability": availability,
                "context_flags": {"no_incident_relations": not relations,
                                  "no_nonempty_incident_pointers": availability["nonempty"] == 0},
            }
        entries.append({"candidate_id": candidate["candidate_id"],
                        "generation_reason": deepcopy(candidate["selection_rule_ids"]),
                        "endpoints": endpoints,
                        "identity_evidence_sufficiency": "NOT_ASSESSED",
                        **{field: "" for field in ANNOTATION_FIELDS}})
    return {"format_version": 1, "dataset_split": "train", "source_sha256": source.sha256,
            "interpretation": "Unlabelled reviewer evidence. Pointers are not truth; rendered views join original tokens.",
            "candidates": entries}


def worklist_csv(dossier):
    """Make a practical annotation sheet; source-rich evidence stays in its dossier."""
    output = io.StringIO(newline="")
    fields = ("candidate_id", "generation_reason", "left_entity_id", "right_entity_id",
              "left_document", "right_document", "dossier_reference", *ANNOTATION_FIELDS)
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for entry in dossier["candidates"]:
        row = {"candidate_id": entry["candidate_id"],
               "generation_reason": ";".join(entry["generation_reason"]),
               "dossier_reference": "review_dossier.json#" + entry["candidate_id"],
               **{field: "" for field in ANNOTATION_FIELDS}}
        for side, endpoint in entry["endpoints"].items():
            row[f"{side}_entity_id"] = endpoint["entity_id"]
            row[f"{side}_document"] = endpoint["provenance"]["document_id"]
        writer.writerow(row)
    return output.getvalue()
