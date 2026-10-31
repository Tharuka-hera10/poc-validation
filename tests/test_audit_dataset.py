"""Authored structural fixtures, not dataset identity or QA gold."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from scripts.audit_dataset import (audit, describe, digest, evidence_kind, guard_paths,
                                   inspect_patterns, load_json, main, validate)


def document():
    return {"title": "fixture", "sents": [["A", "B", "C", "D"]],
            "vertexSet": [[{"name": name, "type": "PER", "sent_id": 0, "pos": [i, i + 1],
                            "global_pos": [0, 0], "index": str(i)}] for i, name in enumerate("ABCD")],
            "labels": [{"h": i, "t": i + 1, "r": f"P{i + 1}", "evidence": [0]} for i in range(3)]}


def source_dir(tmp_path):
    folder = tmp_path / "data" / "raw" / "re_docred" / "data"
    folder.mkdir(parents=True)
    for split in ("train", "dev", "test"):
        (folder / f"{split}_revised.json").write_text(json.dumps([document()]), encoding="utf-8")
    return folder


@pytest.mark.parametrize("raw", [b"{", b'[{"x":1,"x":2}]', b'[{"x":NaN}]', b'\xff'])
def test_invalid_json(raw):
    with pytest.raises(ValueError):
        load_json(raw)


@pytest.mark.parametrize("change,code", [
    (lambda d: d.pop("title"), "missing_field"),
    (lambda d: d.update(sents="wrong"), "wrong_type"),
    (lambda d: d["vertexSet"].__setitem__(0, []), "invalid_or_empty_group"),
    (lambda d: d["labels"][0].update(h=99), "entity_out_of_bounds"),
    (lambda d: d["labels"][0].update(t=True), "wrong_type"),
    (lambda d: d["vertexSet"][0][0].update(sent_id=-1), "sentence_out_of_bounds"),
    (lambda d: d["vertexSet"][0][0].update(pos=[0, 9]), "invalid_half_open_span"),
    (lambda d: d["vertexSet"][0][0].update(pos=[True, 2]), "invalid_half_open_span"),
    (lambda d: d["labels"][0].update(evidence=[9]), "evidence_out_of_bounds"),
    (lambda d: d["labels"][0].update(evidence=[True]), "evidence_out_of_bounds"),
    (lambda d: d["labels"][0].update(evidence=None), "null_or_malformed_evidence"),
])
def test_schema_errors_located(change, code):
    doc = document()
    change(doc)
    issues, valid = validate([doc])
    assert not valid
    assert any(i["code"] == code and i["location"].startswith("$[0]") for i in issues)


def test_root_type_and_span_difference_preserve_source():
    assert validate({})[0][0]["code"] == "expected_document_list"
    assert validate([])[0][0]["code"] == "empty_document_list"
    doc = document()
    doc["vertexSet"][0][0]["name"] = "A formatted differently"
    doc["vertexSet"][0][0]["extra"] = {"retained": True}
    original = deepcopy(doc)
    issues, valid = validate([doc])
    assert valid == [0]
    assert issues == [{"location": "$[0].vertexSet[0][0]", "code": "name_span_text_difference", "severity": "WARNING"}]
    assert doc == original


def test_evidence_states_are_availability_only():
    assert evidence_kind({}, 1) == "absent"
    for value, kind in [(None, "null"), ("0", "malformed"), ([3], "malformed"),
                        ([False], "malformed"), ([], "empty"), ([0], "nonempty")]:
        assert evidence_kind({"evidence": value}, 1) == kind
    doc = document()
    del doc["labels"][0]["evidence"]
    issues, valid = validate([doc])
    assert valid == [0] and issues[0]["code"] == "absent_evidence"


def test_direction_counts_multiplicity_and_exact_provenance():
    doc = document()
    doc["labels"].append({**doc["labels"][0], "evidence": []})
    original = deepcopy(doc)
    found, status = inspect_patterns(doc, "dev", 7, "hash", 100)
    assert status["status"] == "COMPLETE"
    assert sum(p["structural_paths"] for k, p in found.items() if len(k[0]) == 2) == 2
    three = found[(("P1", "P2", "P3"), (("PER",),) * 4)]
    assert three["structural_paths"] == 1
    assert three["relation_occurrence_paths"] == 2
    assert three["all_edges_pointed_occurrence_paths"] == 1
    example = three["example"]
    assert example["document_index"] == 7 and example["file_sha256"] == "hash"
    for hop, li in enumerate(example["relation_label_indices"]):
        label = doc["labels"][li]
        assert label["h"] == example["entity_indices"][hop]
        assert label["t"] == example["entity_indices"][hop + 1]
        assert label["evidence"] == example["evidence_sentence_ids"][hop]
        assert doc["sents"][label["evidence"][0]] == ["A", "B", "C", "D"]
    assert doc == original
    doc["labels"][1]["h"], doc["labels"][1]["t"] = 2, 1
    assert not inspect_patterns(doc, "dev", 7, "hash", 100)[0]


def test_cycles_loops_and_parallel_relation_types():
    doc = document()
    doc["labels"] += [{"h": 0, "t": 1, "r": "P99", "evidence": []},
                       {"h": 1, "t": 0, "r": "P98", "evidence": []},
                       {"h": 1, "t": 1, "r": "P97", "evidence": []}]
    found, status = inspect_patterns(doc, "train", 0, "hash", 1000)
    assert status["excluded_repeated_vertex_extensions"] > 0
    assert any(k[0] == ("P99", "P2", "P3") for k in found)
    assert all(len(set(p["example"]["entity_indices"])) == len(p["example"]["entity_indices"]) for p in found.values())
    assert all("P97" not in k[0] for k in found)


def test_bound_is_deterministic_and_explicit():
    args = document(), "dev", 0, "hash", 1
    first = inspect_patterns(*args)
    assert first == inspect_patterns(*args)
    assert first[1]["status"] == "INCOMPLETE"
    assert first[1]["extensions"] == 1


def test_full_audit_immutable_deterministic_and_test_reserved(tmp_path, monkeypatch):
    folder = source_dir(tmp_path)
    test_doc = document()
    test_doc["labels"][0]["r"] = "P_TEST_ONLY"
    (folder / "test_revised.json").write_text(json.dumps([test_doc]))
    sentinel = tmp_path / "data" / "private_gold" / "secret.json"
    sentinel.parent.mkdir()
    sentinel.write_text("NEVER READ")
    read = Path.read_bytes
    def permitted_read(path):
        assert "private_gold" not in path.parts
        return read(path)
    monkeypatch.setattr(Path, "read_bytes", permitted_read)
    before = {p: digest(p.read_bytes()) for p in folder.glob("*.json")}
    first = audit(folder)
    assert first == audit(folder)
    manifest, result, inventory = first
    assert result["status"] == "VALID" and inventory["status"] == "COMPLETE"
    assert {p: digest(p.read_bytes()) for p in folder.glob("*.json")} == before
    assert all(e["sha256"] == e["sha256_after"] for e in manifest["files"])
    assert result["duplicates"]["sentence_content"]
    assert all(run["split"] != "test" for run in inventory["document_runs"])
    assert all("P_TEST_ONLY" not in p["relations"] for p in inventory["patterns"])
    assert result["splits"]["test"]["suitability"]["status"] == "NOT_INSPECTED_RESERVED_TEST"
    assert main(["--data-dir", str(folder), "--output-dir", str(tmp_path / "outputs")]) == 0


def test_invalid_documents_and_missing_file_reported(tmp_path):
    folder = source_dir(tmp_path)
    (folder / "dev_revised.json").write_text('{"not":"a list"}')
    doc = document()
    doc["labels"][0]["evidence"] = None
    (folder / "train_revised.json").write_text(json.dumps([doc]))
    manifest, result, inventory = audit(folder)
    assert result["status"] == "INVALID" and inventory["status"] == "INCOMPLETE"
    assert result["splits"]["train"]["evidence_all_relation_objects"]["null"] == 1
    assert main(["--data-dir", str(tmp_path / "missing"), "--output-dir", str(tmp_path / "out")]) == 1


def test_duplicate_records_and_candidate_limits():
    doc = document()
    doc["labels"].append(deepcopy(doc["labels"][0]))
    doc["vertexSet"][1][0]["name"] = " a "
    data = describe([doc], [0], True)
    assert data["counts"]["duplicate_relation_records"] == 1
    assert data["counts"]["duplicate_typed_triple_occurrences"] == 1
    assert data["suitability"]["normalized_names_in_multiple_groups"] == 1
    assert data["suitability"]["identity_labels_generated"] is False


def test_guards_and_invalid_bound(tmp_path):
    folder = source_dir(tmp_path)
    for out in (folder, folder.parent / "out", tmp_path / "data" / "raw" / "out"):
        with pytest.raises(ValueError, match="outside raw"):
            guard_paths(folder, out)
    with pytest.raises(ValueError, match="evaluation-only"):
        guard_paths(tmp_path / "private_gold", tmp_path / "out")
    with pytest.raises(ValueError, match="evaluation-only"):
        audit(tmp_path / "private_gold")
    with pytest.raises(ValueError, match="positive"):
        audit(folder, 0)
    assert main(["--data-dir", str(folder), "--output-dir", str(tmp_path / "out"),
                 "--max-extensions-per-document", "1"]) == 1


def test_source_change_is_detected(tmp_path, monkeypatch):
    folder = source_dir(tmp_path)
    read = Path.read_bytes
    calls = {}
    def changing_read(path):
        calls[path] = calls.get(path, 0) + 1
        return read(path) + (b" " if calls[path] > 1 else b"")
    monkeypatch.setattr(Path, "read_bytes", changing_read)
    result = audit(folder)[1]
    assert result["status"] == "INVALID"
    assert result["diagnostic_counts"]["source_changed_during_audit"] == 3


def test_symlink_boundaries(tmp_path):
    folder = source_dir(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    (out / "dataset_audit.json").symlink_to(folder / "train_revised.json")
    with pytest.raises(ValueError, match="output symlinks"):
        guard_paths(folder, out)
    linked = tmp_path / "linked"
    linked.mkdir()
    (linked / "train_revised.json").symlink_to(folder / "train_revised.json")
    with pytest.raises(ValueError, match="source symlinks"):
        audit(linked)
