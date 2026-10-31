"""Authored graph fixtures test software, not empirical identity/QA outcomes."""

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path

import networkx as nx
import pytest

from scripts.audit_dataset import digest, encoded
from scripts.build_graph import (SourceSplit, build_document_graph, build_split_graph,
                                 check_output_dir, load_split, main, make_demo,
                                 reconstruct_edge_source, validate_graph_provenance)


def document():
    return {"title": "authored fixture", "sents": [["Alpha", "Beta", "."], ["Gamma"]],
            "vertexSet": [[{"name": name, "type": "ORG", "sent_id": 0, "pos": [i, i + 1],
                            "global_pos": [0, 0], "index": str(i), "extra": {"values": [i]}}]
                          for i, name in enumerate(["Alpha", "Beta"])],
            "labels": [{"h": 0, "t": 1, "r": "P1", "evidence": [1, 0, 1], "extra": {"x": [1]}}]}


def source(documents=None, split="train"):
    docs = [document()] if documents is None else documents
    return SourceSplit(split, docs, digest(encoded(docs).encode()), [])


def file_source(tmp_path, docs=None):
    s = source(docs)
    folder = tmp_path / "data" / "raw" / "re_docred" / "data"
    folder.mkdir(parents=True)
    path = folder / "train_revised.json"
    raw = encoded(s.documents).encode()
    path.write_bytes(raw)
    manifest = {"files": [{"split": "train", "bytes": len(raw), "sha256": digest(raw), "sha256_after": digest(raw)}]}
    return folder, manifest


def test_directed_multigraph_occurrences_isolates_and_self_loops():
    doc = document()
    doc["vertexSet"].append([{"name": "Gamma", "type": "ORG", "sent_id": 1, "pos": [0, 1]}])
    doc["labels"] += [deepcopy(doc["labels"][0]), {"h": 0, "t": 1, "r": "P2", "evidence": []},
                      {"h": 1, "t": 1, "r": "P3", "evidence": []}]
    s = source([doc])
    g = build_split_graph(s)
    assert isinstance(g, nx.MultiDiGraph)
    assert (g.number_of_nodes(), g.number_of_edges()) == (3, 4)
    assert g.degree("train:0:2") == 0
    assert not g.has_edge("train:0:1", "train:0:0")
    assert set(g["train:0:0"]["train:0:1"]) == {"train:0:0", "train:0:1", "train:0:2"}
    assert g.has_edge("train:0:1", "train:0:1", "train:0:3")
    assert g.edges["train:0:0", "train:0:1", "train:0:2"]["relation"] == "P2"
    counts = validate_graph_provenance(g, s)
    assert counts["nodes_validated"] == 3 and counts["edges_validated"] == 4


def test_document_split_interfaces_deterministic_and_names_do_not_join():
    s = source([document(), document()])
    g = build_split_graph(s)
    assert set(g) == {"train:0:0", "train:0:1", "train:1:0", "train:1:1"}
    again = build_split_graph(s)
    assert list(g.nodes(data=True)) == list(again.nodes(data=True))
    assert list(g.edges(keys=True, data=True)) == list(again.edges(keys=True, data=True))
    doc = build_document_graph(s.documents[1], "train", 1, s.sha256)
    assert set(doc) == {"train:1:0", "train:1:1"}
    assert validate_graph_provenance(doc, s)["documents_validated"] == 1
    dev = build_split_graph(source(split="dev"))
    assert set(g).isdisjoint(dev)


def test_lossless_reconstruction_and_defensive_copy():
    s = source()
    original = deepcopy(s.documents)
    g = build_split_graph(s)
    trace = reconstruct_edge_source(g, "train:0:0", "train:0:1", "train:0:0", s)
    assert trace["source_relation"] == original[0]["labels"][0]
    assert trace["endpoints"]["h"]["mentions"][0]["span_tokens"] == ["Alpha"]
    assert trace["endpoints"]["t"]["mentions"][0]["sentence_tokens"] == ["Alpha", "Beta", "."]
    assert trace["endpoints"]["h"]["mentions"][0]["source_mention"] == original[0]["vertexSet"][0][0]
    assert [x["sentence_index"] for x in trace["evidence_sentences"]] == [1, 0, 1]
    assert trace["evidence_sentences"][0]["tokens"] == ["Gamma"]
    trace["evidence_sentences"][0]["tokens"].append("changed")
    g.nodes["train:0:0"]["source_mentions"][0]["extra"]["values"].append(99)
    g.edges["train:0:0", "train:0:1", "train:0:0"]["source_relation"]["extra"]["x"].append(99)
    g.graph["validation_warnings"].append({"custom": True})
    assert s.documents == original


@pytest.mark.parametrize("mode", ["absent", "empty", "nonempty"])
def test_evidence_policy_preserves_absence_and_values(mode):
    doc = document()
    if mode == "absent":
        del doc["labels"][0]["evidence"]
    elif mode == "empty":
        doc["labels"][0]["evidence"] = []
    s = source([doc])
    g = build_split_graph(s)
    edge = g.edges["train:0:0", "train:0:1", "train:0:0"]
    assert edge["evidence_availability"] == mode
    assert ("evidence" in edge["source_relation"]) == (mode != "absent")
    assert validate_graph_provenance(g, s)[mode] == 1
    if mode == "absent":
        assert g.graph["validation_warnings"][0]["code"] == "absent_evidence"


@pytest.mark.parametrize("change", [
    lambda d: d["labels"][0].update(h=99),
    lambda d: d["labels"][0].update(t=-1),
    lambda d: d["labels"][0].update(h=True),
    lambda d: d["labels"][0].update(evidence=None),
    lambda d: d["labels"][0].update(evidence="0"),
    lambda d: d["labels"][0].update(evidence=[9]),
    lambda d: d["vertexSet"][0][0].update(pos=[0, 99]),
])
def test_invalid_input_rejected_before_any_nodes_are_created(change, monkeypatch):
    doc = document()
    change(doc)
    def forbidden(*args, **kwargs):
        pytest.fail("Graph mutation happened before source validation")
    monkeypatch.setattr(nx.MultiDiGraph, "add_node", forbidden)
    with pytest.raises(ValueError, match="Schema validation failed"):
        build_split_graph(source([document(), doc]))


@pytest.mark.parametrize("change", [
    lambda g: g.nodes["train:0:0"]["source_mentions"][0].update(name="wrong"),
    lambda g: g.edges["train:0:0", "train:0:1", "train:0:0"].update(relation="wrong"),
    lambda g: g.edges["train:0:0", "train:0:1", "train:0:0"]["source_relation"].update(h=False),
    lambda g: g.edges["train:0:0", "train:0:1", "train:0:0"]["provenance"].update(label_index=True),
])
def test_tampered_values_detected_even_when_counts_match(change):
    s = source()
    g = build_split_graph(s)
    change(g)
    with pytest.raises(ValueError, match="provenance mismatch"):
        validate_graph_provenance(g, s)


def test_missing_extra_and_wrong_topology_fail_reconciliation():
    s = source()
    for mode in ("extra_node", "extra_edge", "missing_node", "reverse"):
        g = build_split_graph(s)
        if mode == "extra_node":
            g.add_node("unintended")
        elif mode == "extra_edge":
            g.add_edge("train:0:0", "train:0:1", key="unintended")
        elif mode == "missing_node":
            g.remove_node("train:0:0")
        else:
            attrs = deepcopy(g.edges["train:0:0", "train:0:1", "train:0:0"])
            g.remove_edge("train:0:0", "train:0:1", "train:0:0")
            g.add_edge("train:0:1", "train:0:0", key="train:0:0", **attrs)
        with pytest.raises(ValueError):
            validate_graph_provenance(g, s)


def test_wrong_source_and_tampered_reconstruction():
    s = source()
    g = build_split_graph(s)
    args = g, "train:0:0", "train:0:1", "train:0:0"
    with pytest.raises(ValueError, match="fingerprint"):
        reconstruct_edge_source(*args, replace(s, sha256="0" * 64))
    with pytest.raises(ValueError, match="split"):
        reconstruct_edge_source(*args, replace(s, split="dev"))
    changed = deepcopy(s.documents)
    changed[0]["sents"][0][0] = "wrong source"
    with pytest.raises(ValueError, match="Wrong source document"):
        reconstruct_edge_source(*args, replace(s, documents=changed))
    g.edges[args[1:]]["provenance"]["label_index"] = 999
    with pytest.raises(ValueError, match="Malformed label"):
        reconstruct_edge_source(*args, s)


def test_file_loading_hashes_and_no_private_gold_reads(tmp_path, monkeypatch):
    folder, manifest = file_source(tmp_path)
    original = (folder / "train_revised.json").read_bytes()
    sentinel = tmp_path / "private_gold" / "gold.json"
    sentinel.parent.mkdir()
    sentinel.write_text("forbidden sentinel, not actual labels")
    read = Path.read_bytes
    def safe_read(path):
        assert "private_gold" not in path.resolve().parts
        return read(path)
    monkeypatch.setattr(Path, "read_bytes", safe_read)
    s = load_split(folder, "train", manifest)
    validate_graph_provenance(build_split_graph(s), s)
    assert (folder / "train_revised.json").read_bytes() == original
    bad = deepcopy(manifest)
    bad["files"][0]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="fingerprint mismatch"):
        load_split(folder, "train", bad)
    with pytest.raises(ValueError, match="evaluation-only"):
        load_split(sentinel.parent, "train", manifest)


def test_demo_train_only_deterministic_and_bounded():
    doc = document()
    doc["labels"] *= 5
    doc["vertexSet"][0] *= 4
    s = source([doc])
    g = build_split_graph(s)
    demo = make_demo(g, s)
    assert demo == make_demo(g, s)
    assert len(demo["examples"]) == 3 and demo["omitted_relations"] == 2
    assert demo["examples"][0]["endpoints"]["h"]["omitted_mentions"] == 2
    assert demo["examples"][0]["evidence_sentences"][0]["rendered_view"] == "Gamma"
    with pytest.raises(ValueError, match="train only"):
        make_demo(g, replace(s, split="test"))


def test_output_guards_and_cli_failures(tmp_path, capsys):
    folder, manifest = file_source(tmp_path)
    for target in (folder, folder.parent / "out", Path("results/phase0/new"), tmp_path / "private_gold"):
        with pytest.raises(ValueError):
            check_output_dir(folder, tmp_path / "manifest.json", target)
    out = tmp_path / "out"
    out.mkdir()
    (out / "graph_summary.json").symlink_to(folder / "train_revised.json")
    with pytest.raises(ValueError, match="symlink"):
        check_output_dir(folder, tmp_path / "manifest.json", out)
    assert main(["--manifest", str(tmp_path / "missing.json"), "--output-dir", str(tmp_path / "other")]) == 1
    assert "Phase 1 failed" in capsys.readouterr().err


def test_document_identifiers_reject_boolean_indices():
    with pytest.raises(ValueError, match="document index"):
        build_document_graph(document(), "train", True, "0" * 64)


def test_malformed_provenance_has_informative_errors():
    s = source()
    g = build_split_graph(s)
    g.edges["train:0:0", "train:0:1", "train:0:0"]["provenance"] = None
    with pytest.raises(ValueError, match="Malformed edge provenance"):
        reconstruct_edge_source(g, "train:0:0", "train:0:1", "train:0:0", s)
    g.graph["document_indices"] = ([0],)
    with pytest.raises(ValueError, match="Malformed document scope"):
        validate_graph_provenance(g, s)


def test_cli_reconciles_and_fails_without_outputs_on_count_mismatch(tmp_path, monkeypatch):
    from scripts import build_graph as module
    folder = tmp_path / "data" / "raw" / "re_docred" / "data"
    folder.mkdir(parents=True)
    entries, split_stats, fingerprints = [], {}, {}
    for split in ("train", "dev", "test"):
        raw = encoded([document()]).encode()
        (folder / f"{split}_revised.json").write_bytes(raw)
        sha = digest(raw)
        entries.append({"split": split, "bytes": len(raw), "sha256": sha, "sha256_after": sha})
        fingerprints[split] = sha
        split_stats[split] = {"counts": {"entity_groups": 2, "relations": 1},
                              "evidence_all_relation_objects": {"nonempty": 1}}
    phase0 = tmp_path / "phase0"
    phase0.mkdir()
    manifest = phase0 / "input_manifest.json"
    manifest.write_text(json.dumps({"files": entries}))
    (phase0 / "dataset_audit.json").write_text(json.dumps({"status": "VALID", "input_fingerprints": fingerprints,
                                                         "splits": split_stats}))
    expected = {s: {"nodes": 2, "edges": 1, "nonempty": 1, "empty": 0, "absent": 0} for s in fingerprints}
    monkeypatch.setattr(module, "EXPECTED", expected)
    out = tmp_path / "out"
    args = ["--data-dir", str(folder), "--manifest", str(manifest), "--output-dir", str(out)]
    assert main(args) == 0
    deterministic = ("graph_summary.json", "provenance_demo.json", "phase1_report.md")
    before = {n: (out / n).read_bytes() for n in deterministic}
    assert main(args) == 0
    assert {n: (out / n).read_bytes() for n in deterministic} == before
    expected["train"]["nodes"] = 99
    args[-1] = str(tmp_path / "failed")
    assert main(args) == 1
    assert not (tmp_path / "failed").exists()
