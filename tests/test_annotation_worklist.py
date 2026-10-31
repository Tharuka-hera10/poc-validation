"""Synthetic reviewer-package checks; no identity annotations are asserted."""

from copy import deepcopy
import csv
import io

import pytest

from scripts.prepare_annotation_worklist import ANNOTATION_FIELDS, make_review_worklist, worklist_csv
from scripts.build_graph import SourceSplit, build_split_graph
from scripts.audit_dataset import digest, encoded
from scripts.candidate_discovery import entity_records, discover_candidates, select_review_candidates, make_candidate_export


def setup_case():
    docs = []
    for _ in range(2):
        docs.append({"title": "AUTHORED FIXTURE", "sents": [["Alias", "One", "."], ["A1", "Other", "."]],
                     "vertexSet": [[{"name": "Alias One", "type": "ORG", "sent_id": 0, "pos": [0, 2], "extra": {"x": [1]}},
                                    {"name": "A1", "type": "ORG", "sent_id": 1, "pos": [0, 1]}],
                                   [{"name": "Other", "type": "LOC", "sent_id": 1, "pos": [1, 2]}]],
                     "labels": [{"h": 0, "t": 1, "r": "P1", "evidence": [1, 0, 1], "extra": ["original"]}]})
    source = SourceSplit("train", docs, digest(encoded(docs).encode()), [])
    graph = build_split_graph(source)
    records = entity_records(source, graph)
    selected, _ = select_review_candidates(discover_candidates(records), records)
    export = make_candidate_export(selected, records, source.sha256)
    return source, graph, export


def test_exact_mentions_spans_sentence_tokens_relation_occurrences_and_blank_fields():
    source, graph, export = setup_case()
    before = deepcopy(source.documents)
    dossier = make_review_worklist(export["candidates"], source, graph)
    endpoint = dossier["candidates"][0]["endpoints"]["left"]
    assert endpoint["mentions"][0]["span_tokens"] == ["Alias", "One"]
    assert endpoint["mentions"][0]["source_mention"] == before[0]["vertexSet"][0][0]
    assert endpoint["sentences"][0]["tokens"] == before[0]["sents"][0]
    relation = endpoint["original_incident_relations"][0]
    assert relation["source_relation"] == before[0]["labels"][0]
    assert relation["source_relation"]["evidence"] == [1, 0, 1]
    assert relation["provenance"]["label_index"] == 0
    assert all(entry[f] == "" for entry in dossier["candidates"] for f in ANNOTATION_FIELDS)
    rows = list(csv.DictReader(io.StringIO(worklist_csv(dossier))))
    assert rows and all(row[f] == "" for row in rows for f in ANNOTATION_FIELDS)
    assert source.documents == before
    endpoint["mentions"][0]["source_mention"]["extra"]["x"].append(99)
    relation["source_relation"]["extra"].append("mutation")
    assert source.documents == before


def test_empty_and_absent_pointers_remain_distinct_without_invented_judgements():
    source, _, _ = setup_case()
    source.documents[0]["labels"][0]["evidence"] = []
    del source.documents[1]["labels"][0]["evidence"]
    graph = build_split_graph(source)
    records = entity_records(source, graph)
    selected, _ = select_review_candidates(discover_candidates(records), records)
    export = make_candidate_export(selected, records, source.sha256)
    dossier = make_review_worklist(export["candidates"], source, graph)
    entry = dossier["candidates"][0]
    assert entry["endpoints"]["left"]["evidence_pointer_availability"]["empty"] == 1
    assert entry["endpoints"]["right"]["evidence_pointer_availability"]["absent"] == 1
    assert entry["identity_evidence_sufficiency"] == "NOT_ASSESSED" and entry["reviewer_decision"] == ""


def test_isolated_mentions_are_reviewable_and_dossier_reconstruction_is_deterministic():
    source, _, _ = setup_case()
    for doc in source.documents:
        doc["labels"] = []
    graph = build_split_graph(source)
    records = entity_records(source, graph)
    selected, _ = select_review_candidates(discover_candidates(records), records)
    export = make_candidate_export(selected, records, source.sha256)
    a = make_review_worklist(export["candidates"], source, graph)
    b = make_review_worklist(export["candidates"], source, graph)
    assert a == b and worklist_csv(a) == worklist_csv(b)
    assert all(e["context_flags"]["no_incident_relations"] for r in a["candidates"] for e in r["endpoints"].values())


def test_empty_worklist_has_header_no_labels_and_nontrain_is_rejected():
    source, graph, _ = setup_case()
    dossier = make_review_worklist([], source, graph)
    assert dossier["candidates"] == [] and len(worklist_csv(dossier).splitlines()) == 1
    other = SourceSplit("test", source.documents, source.sha256, [])
    with pytest.raises(ValueError, match="train only"):
        make_review_worklist([], other, graph)


def test_wrong_source_for_relationship_is_rejected():
    source, graph, export = setup_case()
    source.documents[0]["sents"][0][0] = "changed"
    with pytest.raises(ValueError, match="changed source"):
        make_review_worklist(export["candidates"], source, graph)


def test_isolated_node_mutation_is_rejected_too():
    source, _, _ = setup_case()
    for doc in source.documents:
        doc["labels"] = []
    graph = build_split_graph(source)
    graph.nodes["train:0:0"]["source_mentions"][0]["name"] = "tampered"
    with pytest.raises(ValueError, match="Node provenance"):
        make_review_worklist([], source, graph)
