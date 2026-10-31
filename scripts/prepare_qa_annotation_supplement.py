"""Evaluation-only blank triple/path sheets from public Phase 3 and original source.

Never imported by query generation; never reads existing private annotations.
"""

import argparse
import csv
import io
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.audit_dataset import digest, encoded, load_json
from scripts.build_graph import check_schema, load_split, require, same_record, source_path
from scripts.candidate_discovery import json_text, publish_package, verify_sources
from scripts.query_workload import indices, validate_packages


ROOT = Path(__file__).resolve().parents[1]
VERSION = "phase3-annotation-supplement-v1"
EDGE_FIELDS = ("triple_support_decision", "supporting_sentence_references", "contradictory_source_references",
               "reviewer_rationale", "reviewer_confidence", "reviewer_identifier", "review_date", "adjudication_status")
PATH_FIELDS = ("relation_chain_interpretation", "path_composition_validity", "source_evidence_references",
               "unresolved_ambiguity", "reviewer_rationale", "reviewer_confidence", "reviewer_identifier", "review_date", "adjudication_status")
EDGE_METADATA = ("edge_review_id", "edge_key", "dataset_split", "document_index", "label_index",
                 "head_entity_id", "tail_entity_id", "relation_code", "source_reference",
                 "evidence_pointer_availability", "evidence_field_present", "evidence_sentence_indices", "query_path_references")
PATH_METADATA = ("query_id", "path_id", "ordered_node_ids", "ordered_edge_keys", "structural_answer_id", "edge_review_ids")


def stable_id(prefix, values):
    return prefix + digest(encoded([VERSION, *values]).encode("utf-8"))


def prepare_records(source, query_package, result_package):
    """Reconcile supporting occurrences only; no discovery, templates or human labels."""
    require(source.split == "train", "Annotation supplement accepts train only")
    check_schema(source.documents)
    validate_packages(query_package, result_package)
    require(query_package["source_sha256"] == source.sha256, "Wrong source fingerprint")
    document_hashes = {}
    edges, paths = {}, []
    for query, result in zip(query_package["queries"], result_package["results"]):
        require(query["dataset_split"] == "train" and result["status"] == "COMPLETE", "Require complete train queries")
        di, ei = indices(query["anchor_entity_id"])
        require(di < len(source.documents) and ei < len(source.documents[di]["vertexSet"]), "Anchor outside source")
        document_hashes.setdefault(di, digest(encoded(source.documents[di]).encode("utf-8")))
        require(query["anchor_provenance"]["document_sha256"] == document_hashes[di], "Source document fingerprint mismatch")
        for path in result["paths"]:
            keys = [edge["edge_key"] for edge in path["edge_occurrences"]]
            pid = stable_id("path_", [source.sha256, query["query_id"], path["node_ids"], keys])
            reviews = []
            for position, occurrence in enumerate(path["edge_occurrences"]):
                key = occurrence["edge_key"]
                edi, li = indices(key)
                require(edi == di and li < len(source.documents[di]["labels"]), "Occurrence outside source")
                label = source.documents[di]["labels"][li]
                p = occurrence["provenance"]
                require(same_record([label["h"], label["t"], label["r"]], [p["head_index"], p["tail_index"], occurrence["relation"]])
                        and ("evidence" in label) == ("evidence" in occurrence)
                        and same_record(label.get("evidence"), occurrence.get("evidence")), "Original relationship occurrence mismatch")
                rid = stable_id("edge_review_", [source.sha256, key])
                reference = {"file": "train_revised.json", "source_sha256": source.sha256,
                             "document_index": di, "label_index": li, "document_sha256": document_hashes[di]}
                if key not in edges:
                    edges[key] = {"edge_review_id": rid, "edge_key": key, "dataset_split": "train",
                                  "document_index": di, "label_index": li,
                                  "head_entity_id": occurrence["head_entity_id"], "tail_entity_id": occurrence["tail_entity_id"],
                                  "relation_code": label["r"], "source_reference": reference,
                                  "evidence_pointer_availability": occurrence["evidence_availability"],
                                  "evidence_field_present": "evidence" in label,
                                  "evidence_sentence_indices": list(label["evidence"]) if "evidence" in label else None,
                                  "query_path_references": [], **{f: "" for f in EDGE_FIELDS}}
                edges[key]["query_path_references"].append({"query_id": query["query_id"], "path_id": pid, "edge_position": position})
                reviews.append(rid)
            paths.append({"query_id": query["query_id"], "path_id": pid, "ordered_node_ids": list(path["node_ids"]),
                          "ordered_edge_keys": keys, "structural_answer_id": path["node_ids"][-1],
                          "edge_review_ids": reviews, **{f: "" for f in PATH_FIELDS}})
    ordered_edges = [edges[k] for k in sorted(edges, key=indices)]
    for edge in ordered_edges:
        edge["query_path_references"].sort(key=lambda r: (r["query_id"], r["path_id"], r["edge_position"]))
    paths.sort(key=lambda p: (p["query_id"], tuple(indices(n) for n in p["ordered_node_ids"]),
                              tuple(indices(k) for k in p["ordered_edge_keys"])))
    return ordered_edges, paths


def csv_text(rows, metadata, human_fields):
    """Serialize reference arrays as canonical JSON; keep all human decisions blank."""
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=(*metadata, *human_fields), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        require(set(row) == set(metadata) | set(human_fields), "Unexpected supplement fields")
        require(all(row[f] == "" for f in human_fields), "Refuse to generate populated human decisions")
        writer.writerow({k: encoded(v) if isinstance(v, (dict, list)) or v is None or type(v) is bool else v for k, v in row.items()})
    return stream.getvalue()


def read_public_run(root):
    """Verify all six public artifacts; ignore private-path/status metadata entirely."""
    latest = load_json(source_path(root / "latest_run.json").read_bytes())
    require(latest["status"] == "PASS", "Phase 3 latest attempt is not PASS")
    relative = Path(latest["run_directory"])
    require(not relative.is_absolute(), "Expected relative public run path")
    run = (root / relative).resolve()
    require(run.is_relative_to((root / "runs").resolve()) and run != (root / "runs").resolve(), "Invalid public run path")
    names = {"query_inventory.json", "queries_train.json", "structural_query_results.json", "query_feasibility_report.md", "phase3_report.md", "run_manifest.json"}
    require(set(latest["artifact_sha256"]) == names, "Incomplete public artifact references")
    for name, sha in latest["artifact_sha256"].items():
        require(digest(source_path(run / name).read_bytes()) == sha, f"Public artifact fingerprint mismatch: {name}")
    return (load_json(source_path(run / "queries_train.json").read_bytes()),
            load_json(source_path(run / "structural_query_results.json").read_bytes()),
            {"latest_sha256": digest(source_path(root / "latest_run.json").read_bytes()),
             "run_directory": relative.as_posix(), "artifact_sha256": latest["artifact_sha256"]})


def check_output(path):
    """Restrict writes to a new ignored supplement subtree, never prior QA packages."""
    allowed = ROOT / "data" / "private_gold" / "phase3" / "annotation_supplements"
    require(allowed.resolve() == allowed and (path.resolve() == allowed or path.resolve().is_relative_to(allowed)), "Output must be below private_gold/phase3/annotation_supplements")
    for current in (path.absolute(), *path.absolute().parents):
        require(not current.is_symlink(), "Supplement symlink redirect is forbidden")
        if current == ROOT:
            break
    require(not (path / "runs").is_symlink(), "Supplement runs symlink is forbidden")
    ignored = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "--quiet", str(path.resolve() / "probe.json")], capture_output=True, check=False)
    require(ignored.returncode == 0, "Supplement output is not Git-ignored")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data/raw/re_docred/data"))
    parser.add_argument("--manifest", type=Path, default=Path("results/phase0/input_manifest.json"))
    parser.add_argument("--phase3-dir", type=Path, default=Path("results/phase3"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/private_gold/phase3/annotation_supplements"))
    args = parser.parse_args(argv)
    try:
        check_output(args.output_dir)
        manifest = load_json(source_path(args.manifest).read_bytes())
        fingerprints = verify_sources(args.data_dir, manifest)
        queries, results, public_reference = read_public_run(args.phase3_dir)
        source = load_split(args.data_dir, "train", manifest)
        edges, paths = prepare_records(source, queries, results)
        files = {"edge_review_worklist.csv": csv_text(edges, EDGE_METADATA, EDGE_FIELDS),
                 "path_composition_worklist.csv": csv_text(paths, PATH_METADATA, PATH_FIELDS)}
        require(verify_sources(args.data_dir, manifest) == fingerprints, "Source changed during supplement preparation")
        # Recheck the public snapshot before publishing; no annotations are inputs.
        require(read_public_run(args.phase3_dir)[2] == public_reference, "Public Phase 3 reference changed")
        record = {"format_version": 1, "version": VERSION, "status": "COMPLETE_BLANK_PREPARATION",
                  "edge_review_records": len(edges), "path_review_records": len(paths),
                  "source_sha256_before": fingerprints, "source_sha256_after": verify_sources(args.data_dir, manifest),
                  "phase0_manifest_sha256": digest(source_path(args.manifest).read_bytes()),
                  "public_phase3_reference": public_reference,
                  "implementation_sha256": {name: digest((ROOT / "scripts" / name).read_bytes()) for name in
                      ("prepare_qa_annotation_supplement.py", "query_workload.py", "build_graph.py", "audit_dataset.py", "candidate_discovery.py")},
                  "artifact_sha256": {name: digest(value.encode("utf-8")) for name, value in files.items()},
                  "private_annotations_read": False, "human_review_performed": False,
                  "interpretation": "Supporting occurrences only. Templates are not answer evidence; metadata pointer availability is not support."}
        files["supplement_manifest.json"] = json_text(record)
        destination, _ = publish_package(args.output_dir, uuid4().hex, files)
    except (ValueError, OSError, KeyError, TypeError, IndexError) as exc:
        print(f"QA annotation supplement failed; no new complete package established: {exc}", file=sys.stderr)
        return 1
    print(f"QA supplement: {len(edges)} original-occurrence rows; {len(paths)} path rows; human fields blank")
    print(f"Immutable private package: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
