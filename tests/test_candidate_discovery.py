"""Synthetic behaviour checks, never independently verified identity findings."""

from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import candidate_discovery as c
from scripts.audit_dataset import digest, encoded
from scripts.build_graph import SourceSplit, build_split_graph, validate_graph_provenance


def document(names, types=None, relation="P1", edges=True):
    sents, groups = [], []
    for ei, aliases in enumerate(names):
        group = []
        for name in [aliases] if isinstance(aliases, str) else aliases:
            tokens = name.split() or [" "]
            group.append({"name": name, "type": (types or ["ORG"] * len(names))[ei],
                          "sent_id": len(sents), "pos": [0, len(tokens)], "index": f"auxiliary_{ei}"})
            sents.append(tokens + ["."])
        groups.append(group)
    return {"title": "AUTHORED SYNTHETIC FIXTURE", "sents": sents, "vertexSet": groups,
            "labels": [{"h": 0, "t": 1, "r": relation, "evidence": [0]}] if edges else []}


def source(docs, split="train"):
    return SourceSplit(split, docs, digest(encoded(docs).encode()), [])


def prepared(docs):
    s = source(docs)
    g = build_split_graph(s)
    records = c.entity_records(s, g)
    pairs = c.discover_candidates(records)
    selected, stats = c.select_review_candidates(pairs, records)
    export = c.make_candidate_export(selected, records, s.sha256)
    return s, g, records, pairs, selected, stats, export


def cases():
    return [document(["Sparse"], edges=False), document(["Sparse"], edges=False),
            document(["World Trade Organization", "Peer2"]), document(["WTO", "Peer3"]),
            document(["Collision", "Peer4"], ["ORG", "LOC"]),
            document(["Collision", "Peer5"], ["PER", "LOC"]),
            document(["Compatible", "Peer6"]), document(["Compatible", "Peer7"])]


def test_discovery_categories_stable_ids_no_labels_or_reversed_pairs():
    *_, pairs, selected, stats, export = prepared(cases())
    assert len(pairs) == 4
    assert all(a < b for a, b in pairs)
    assert [category for _, category, _ in selected] == list(c.TARGETS)
    assert [v["selected"] for v in stats["categories"].values()] == [1, 1, 1, 1]
    assert export == prepared(cases())[-1]
    assert all(row["review_status"] == "UNREVIEWED" for row in export["candidates"])
    assert all("same_entity" not in row and "gold_label" not in row for row in export["candidates"])


def test_exact_normalization_preserves_originals_and_different_name_initialism():
    assert c.name_forms([{"name": "  Mixed  NAME "}])[0] == {"mixed name"}
    *_, export = prepared(cases())
    row = export["candidates"][1]
    assert row["selection_rule_ids"] == ["exact_initialism_v1"]
    assert row["permitted_name_features"]["left"]["original_names"] == ["World Trade Organization"]
    assert "reviewer_decision" not in row


def test_both_rules_preserve_all_reasons_and_duplicate_aliases_do_not_repeat_pairs():
    docs = [document([["World Trade Organization", "WTO", "WTO"]], edges=False),
            document([["WTO", "World Trade Organization"]], edges=False)]
    _, _, _, pairs, _, _, export = prepared(docs)
    assert list(pairs.values()) == [3]
    assert export["candidates"][0]["selection_rule_ids"] == list(c.RULES.values())


def test_diversity_no_reused_entity_or_matching_key_and_shortfalls_reported():
    docs = [document(["Hub"], edges=False) for _ in range(5)]
    _, _, records, pairs, selected, stats, _ = prepared(docs)
    assert len(pairs) == 10 and len(selected) == 1
    assert stats["categories"]["sparse_context"]["shortfall"] == 3
    refs, keys = set(), set()
    for pair, _, _ in selected:
        matching = c.matching_keys(*(records[r] for r in pair))
        assert not refs.intersection(pair) and not keys.intersection(matching)
        refs.update(pair)
        keys.update(matching)


def test_all_types_discovered_but_mixed_and_numeric_not_selected():
    docs = [document(["Same"], ["NUM"], edges=False), document(["Same"], ["NUM"], edges=False),
            document([["Same", "Alias"]], ["ORG"], edges=False)]
    docs[-1]["vertexSet"][0][1]["type"] = "PER"
    _, _, _, pairs, selected, stats, _ = prepared(docs)
    assert len(pairs) == 3 and not selected
    assert stats["selection_type_exclusions"] == 3


@pytest.mark.parametrize("split", ["dev", "test"])
def test_nontrain_rejected_before_discovery(split):
    s = source([document(["Name"], edges=False)], split)
    with pytest.raises(ValueError, match="train only"):
        c.entity_records(s, build_split_graph(s))
    with pytest.raises(ValueError, match="train only"):
        c.controlled_feasibility(s, {})
    records = {(0, 0): {"entity_id": f"{split}:0:0"}}
    with pytest.raises(ValueError, match="Non-train"):
        c.discover_candidates(records)


def test_empty_discovery_and_whitespace_names_produce_no_fake_cases():
    _, _, _, pairs, selected, stats, export = prepared([document(["   "], edges=False)])
    assert not pairs and not selected and export["candidates"] == []
    assert sum(v["shortfall"] for v in stats["categories"].values()) == 24


def test_no_source_or_graph_mutation_and_context_retains_occurrence_counts():
    docs = cases()
    docs[-1]["labels"] *= 2
    before = deepcopy(docs)
    s, g, records, *_ = prepared(docs)
    assert docs == before
    assert validate_graph_provenance(g, s, require_full_split=True)["edges"] == 7
    record = records[7, 0]
    assert record["incident_relations"] == 2 and len(record["signature"]) == 1
    assert record["evidence_pointer_counts"]["nonempty"] == 2


@pytest.mark.parametrize("mode", ["empty", "absent"])
def test_missing_pointers_are_availability_not_truth(mode):
    docs = cases()
    if mode == "empty":
        docs[2]["labels"][0]["evidence"] = []
    else:
        del docs[2]["labels"][0]["evidence"]
    _, _, records, *_ = prepared(docs)
    assert records[2, 0]["evidence_pointer_counts"][mode] == 1
    assert "supported" not in records[2, 0]


@pytest.mark.parametrize("where", ["top", "row", "name", "context", "signature", "provenance"])
def test_export_rejects_nested_private_fields(where):
    export = prepared(cases())[-1]
    row = export["candidates"][2]
    targets = {"top": export, "row": row, "name": row["permitted_name_features"]["left"],
               "context": row["permitted_context_features"]["left"],
               "signature": row["permitted_context_features"]["left"]["relation_signatures"][0],
               "provenance": row["provenance_reference"]["left"]}
    targets[where]["fragmentation_parent"] = "AUTHORED_LEAK_SENTINEL"
    with pytest.raises(ValueError, match="fields must"):
        c.validate_candidate_export(export)


def test_unknown_source_fields_are_not_copied_to_export():
    docs = cases()
    docs[0]["vertexSet"][0][0]["hidden_parent"] = {"gold_label": "SYNTHETIC_SENTINEL"}
    export = prepared(docs)[-1]
    assert "SYNTHETIC_SENTINEL" not in encoded(export)
    assert "auxiliary_" not in encoded(export)


def test_export_rejects_duplicate_pairs_and_tampered_provenance():
    export = prepared(cases())[-1]
    export["candidates"].append(deepcopy(export["candidates"][0]))
    with pytest.raises(ValueError, match="Duplicate"):
        c.validate_candidate_export(export)
    export = prepared(cases())[-1]
    export["candidates"][0]["provenance_reference"]["left"]["entity_index"] = True
    with pytest.raises(ValueError, match="provenance"):
        c.validate_candidate_export(export)


def test_controlled_feasibility_counts_ambiguities_never_creates_fragments():
    doc = document([["Alias One", "Alias Two"], "Other"])
    doc["labels"] = [{"h": 0, "t": 1, "r": "P1", "evidence": ev} for ev in ([0], [0, 1], [], [2])]
    s, _, records, *_ = prepared([doc])
    before = deepcopy(doc)
    result = c.controlled_feasibility(s, records)
    assert result["groups"]["multi_mention"] == 1
    assert result["incident_entity_relation_location_counts"] == {
        "empty_pointers": 1, "multiple_sentence_locations": 1,
        "no_matching_mention_sentence": 1, "unique_sentence_location_only": 1}
    assert result["fragments_created"] == result["controlled_candidate_pairs"] == result["edge_allocations"] == 0
    assert doc == before and "fragmentation_parent" not in encoded(result)


def test_overlap_uses_tokens_not_titles_or_annotations_and_lists_affected_ids():
    train = source([document(["Same"], edges=False)])
    devdoc = deepcopy(train.documents[0])
    devdoc["title"] = "different title"
    devdoc["vertexSet"][0][0]["type"] = "PER"
    dev = source([devdoc], "dev")
    rows = [{"candidate_id": "unlabelled_id", "provenance_reference": {"left": {"document_index": 0}, "right": {"document_index": 7}}}]
    result = c.overlap_policy(train, dev, rows)
    assert result["dev_evaluation_excluded_document_indices"] == [0]
    assert result["affected_selected_candidate_ids"] == ["unlabelled_id"]
    devdoc["sents"][0][0] = "Different"
    assert not c.overlap_policy(train, dev, rows)["exact_text_groups"]


@pytest.fixture
def cli_case(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    monkeypatch.setattr(c, "ROOT", root)
    monkeypatch.setattr(c, "phase1_baseline", lambda: {"SYNTHETIC_TEST_ONLY": True})
    original_run = c.subprocess.run
    def git_ignore(args, **kwargs):
        if "check-ignore" in args:
            return SimpleNamespace(returncode=0)
        return original_run(args, **kwargs)
    monkeypatch.setattr(c.subprocess, "run", git_ignore)
    scripts = root / "scripts"
    scripts.mkdir()
    for name in ("candidate_discovery.py", "prepare_annotation_worklist.py", "audit_dataset.py", "build_graph.py"):
        src = Path(c.__file__).with_name(name)
        scripts.joinpath(name).write_bytes(src.read_bytes())
    data = root / "data" / "raw" / "re_docred" / "data"
    data.mkdir(parents=True)
    phase0 = root / "results" / "phase0"
    phase0.mkdir(parents=True)
    manifest = {"files": []}
    docs = {"train": cases(), "dev": [document(["Dev only"], edges=False)], "test": [document(["TEST RESERVED"], edges=False)]}
    for split, values in docs.items():
        raw = encoded(values).encode()
        (data / f"{split}_revised.json").write_bytes(raw)
        manifest["files"].append({"split": split, "sha256": digest(raw), "sha256_after": digest(raw), "bytes": len(raw)})
    (phase0 / "input_manifest.json").write_text(json.dumps(manifest))
    text_groups = {}
    for split, values in docs.items():
        for di, doc in enumerate(values):
            text_groups.setdefault(digest(encoded(doc["sents"]).encode()), []).append({"split": split, "document_index": di})
    audit = {"status": "VALID", "input_fingerprints": {e["split"]: e["sha256"] for e in manifest["files"]},
             "splits": {"train": {"counts": {"entity_groups": sum(len(d["vertexSet"]) for d in docs["train"]),
                                             "relations": sum(len(d["labels"]) for d in docs["train"])}}},
             "duplicates": {"sentence_content": [refs for refs in text_groups.values() if len(refs) > 1]}}
    (phase0 / "dataset_audit.json").write_text(json.dumps(audit))
    out, private = root / "results" / "phase2", root / "data" / "private_gold" / "phase2"
    args = ["--data-dir", str(data), "--manifest", str(phase0 / "input_manifest.json"),
            "--output-dir", str(out), "--review-dir", str(private)]
    return SimpleNamespace(root=root, data=data, phase0=phase0, out=out, private=private, args=args)


def latest(case):
    return json.loads((case.out / "latest_run.json").read_text())


def test_cli_deterministic_repeats_and_no_private_reads_or_test_discovery(cli_case, monkeypatch):
    original_open, original_load = Path.open, c.load_split
    with monkeypatch.context() as scope:
        def protected_open(path, mode="r", *args, **kwargs):
            if "private_gold" in path.parts and ("r" in mode or "+" in mode):
                pytest.fail("Private label/dossier read")
            return original_open(path, mode, *args, **kwargs)
        def no_test(data, split, manifest):
            assert split != "test"
            return original_load(data, split, manifest)
        scope.setattr(Path, "open", protected_open)
        scope.setattr(c, "load_split", no_test)
        assert c.main(cli_case.args) == 0
        first = latest(cli_case)
        assert c.main(cli_case.args) == 0
        second = latest(cli_case)
    assert first["run_directory"] != second["run_directory"]
    for name in first["artifact_sha256"]:
        if name != "run_manifest.json":
            assert first["artifact_sha256"][name] == second["artifact_sha256"][name]
    assert first["review_artifact_sha256"] == second["review_artifact_sha256"]
    assert json.loads((cli_case.out / second["run_directory"] / "candidate_inventory.json").read_text())["selected_count"] == 4


@pytest.mark.parametrize("failure", ["missing", "malformed", "changed_source", "after_processing"])
def test_success_then_failure_has_explicit_status_and_preserves_previous(cli_case, monkeypatch, failure):
    assert c.main(cli_case.args) == 0
    first = latest(cli_case)
    previous = {p: p.read_bytes() for p in (cli_case.out / first["run_directory"]).iterdir()}
    args = list(cli_case.args)
    if failure == "missing":
        args[3] = str(cli_case.phase0 / "missing.json")
    elif failure == "malformed":
        (cli_case.phase0 / "input_manifest.json").write_text("{invalid")
    elif failure == "changed_source":
        (cli_case.data / "train_revised.json").write_text("[]")
    else:
        def fail(*args):
            raise ValueError("SYNTHETIC failure after candidate discovery")
        monkeypatch.setattr(c, "make_review_worklist", fail)
    assert c.main(args) == 1
    status = latest(cli_case)
    assert status["status"] == "FAILED" and status["run_directory"] is None and status["error"]["reason"]
    assert previous == {p: p.read_bytes() for p in previous}


def test_partial_private_publication_cannot_be_latest_success(cli_case, monkeypatch):
    original = c.publish_package
    def fail_public(root, run_id, files):
        if root == cli_case.out:
            raise OSError("SYNTHETIC public publication failure")
        return original(root, run_id, files)
    monkeypatch.setattr(c, "publish_package", fail_public)
    assert c.main(cli_case.args) == 1
    assert latest(cli_case)["status"] == "FAILED"
    assert not (cli_case.out / "runs").exists()
    assert len(list((cli_case.private / "runs").iterdir())) == 1


@pytest.mark.parametrize("location", ["raw", "phase0", "phase1", "private", "scripts"])
def test_protected_outputs_receive_no_writes(cli_case, location):
    protected = {"raw": cli_case.data, "phase0": cli_case.phase0,
                 "phase1": cli_case.root / "results" / "phase1", "private": cli_case.private,
                 "scripts": cli_case.root / "scripts"}[location]
    args = list(cli_case.args)
    args[5] = str(protected)
    before = {p: p.read_bytes() for p in cli_case.root.rglob("*") if p.is_file()}
    assert c.main(args) == 1
    assert before == {p: p.read_bytes() for p in cli_case.root.rglob("*") if p.is_file()}


def test_review_git_ignore_required_and_symlinks_rejected(cli_case, monkeypatch):
    monkeypatch.setattr(c.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=1))
    assert c.main(cli_case.args) == 1
    assert not cli_case.out.exists()
    monkeypatch.setattr(c.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=0))
    cli_case.out.mkdir(parents=True)
    (cli_case.out / "runs").symlink_to(cli_case.data, target_is_directory=True)
    assert c.main(cli_case.args) == 1
    assert not (cli_case.out / "latest_run.json").exists()


def test_failure_to_initialize_status_aborts_before_inputs(cli_case, monkeypatch):
    def fail(*args):
        raise OSError("SYNTHETIC unwritable status")
    monkeypatch.setattr(c, "write_latest", fail)
    monkeypatch.setattr(c, "verify_sources", lambda *args: pytest.fail("Input read before status"))
    assert c.main(cli_case.args) == 1
    assert not (cli_case.out / "runs").exists()


def test_manifest_rejects_missing_split_and_changed_test_fingerprint(cli_case):
    manifest = json.loads((cli_case.phase0 / "input_manifest.json").read_text())
    manifest["files"] = manifest["files"][:-1]
    with pytest.raises(ValueError, match="exactly one test"):
        c.verify_sources(cli_case.data, manifest)
    manifest = json.loads((cli_case.phase0 / "input_manifest.json").read_text())
    (cli_case.data / "test_revised.json").write_text("[]")
    with pytest.raises(ValueError, match="test"):
        c.verify_sources(cli_case.data, manifest)


def test_prior_annotation_notes_survive_later_generation(cli_case):
    assert c.main(cli_case.args) == 0
    first = latest(cli_case)
    sheet = Path(first["review_directory"]) / "review_worklist.csv"
    sheet.write_text(sheet.read_text() + "SYNTHETIC preservation sentinel\n")
    previous = sheet.read_bytes()
    assert c.main(cli_case.args) == 0
    assert sheet.read_bytes() == previous


def test_failed_final_status_and_interrupt_cannot_establish_pass(cli_case, monkeypatch):
    original = c.write_latest
    def fail_pass(root, status):
        if status["status"] == "PASS":
            raise OSError("SYNTHETIC final publication failure")
        return original(root, status)
    with monkeypatch.context() as scope:
        scope.setattr(c, "write_latest", fail_pass)
        assert c.main(cli_case.args) == 1
    assert latest(cli_case)["status"] == "FAILED" and latest(cli_case)["run_directory"] is None
    def interrupt(*args):
        raise KeyboardInterrupt
    monkeypatch.setattr(c, "make_review_worklist", interrupt)
    with pytest.raises(KeyboardInterrupt):
        c.main(cli_case.args)
    assert latest(cli_case)["status"] == "RUNNING" and latest(cli_case)["run_directory"] is None
