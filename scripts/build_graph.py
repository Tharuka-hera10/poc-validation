"""Phase 1: document-scoped annotated graphs, not verified factual knowledge."""

import argparse
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
import json
import os
from pathlib import Path
import platform
import sys
import tempfile
from uuid import uuid4

import networkx as nx

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.audit_dataset import SPLITS, digest, encoded, evidence_kind, load_json, validate


FORMAT_VERSION = 2
EXPECTED = {
    "train": {"nodes": 59359, "edges": 85932, "nonempty": 47260, "empty": 38672, "absent": 0},
    "dev": {"nodes": 9684, "edges": 17284, "nonempty": 7473, "empty": 9811, "absent": 0},
    "test": {"nodes": 9779, "edges": 17448, "nonempty": 7547, "empty": 9901, "absent": 0},
}


@dataclass(frozen=True)
class SourceSplit:
    """Loaded source owned separately from graph attributes; fixtures may use path=None."""
    split: str
    documents: list
    sha256: str
    diagnostics: list
    path: Path | None = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def same_record(actual, expected):
    # JSON distinguishes bool/int and int/float where Python container equality does not.
    return encoded(actual) == encoded(expected)


def source_path(path):
    path = Path(path)
    require("private_gold" not in path.resolve().parts, "private_gold is evaluation-only")
    require(not path.is_symlink(), f"Source symlinks are not accepted: {path}")
    return path


def check_schema(documents):
    issues, valid = validate(documents)
    errors = [i for i in issues if i["severity"] == "ERROR"]
    require(not errors, f"Schema validation failed: {encoded(errors[:5])}; total errors={len(errors)}")
    require(len(valid) == len(documents), "Schema validation excluded source documents")
    return issues


def load_split(data_dir, split, manifest):
    require(split in SPLITS, f"Unknown split: {split}")
    entries = [e for e in manifest["files"] if e["split"] == split]
    require(len(entries) == 1, f"Manifest must contain exactly one entry for {split}")
    entry = entries[0]
    path = source_path(Path(data_dir) / f"{split}_revised.json")
    raw = path.read_bytes()
    fingerprint = digest(raw)
    require(fingerprint == entry["sha256"], f"Source fingerprint mismatch: {split}")
    require(fingerprint == entry["sha256_after"], f"Phase 0 before/after fingerprint mismatch: {split}")
    require(len(raw) == entry["bytes"], f"Source byte count mismatch: {split}")
    documents = load_json(raw)
    issues = check_schema(documents)
    return SourceSplit(split, documents, fingerprint, issues, path)


def node_id(split, document_index, entity_index):
    return f"{split}:{document_index}:{entity_index}"


def edge_key(split, document_index, label_index):
    return f"{split}:{document_index}:{label_index}"


def provenance(document, split, document_index, source_sha256):
    return {"split": split, "document_index": document_index,
            "document_id": f"{split}:{document_index}", "title": document["title"],
            "source_sha256": source_sha256,
            "document_sha256": digest(encoded(document).encode("utf-8"))}


def node_record(group, base, entity_index):
    return {"source_mentions": deepcopy(group), "provenance": {**base, "entity_index": entity_index}}


def edge_record(label, base, label_index, sentence_count):
    return {"source_relation": deepcopy(label), "relation": label["r"],
            "evidence_availability": evidence_kind(label, sentence_count),
            "provenance": {**base, "label_index": label_index,
                           "head_index": label["h"], "tail_index": label["t"]}}


def append_document(graph, document, split, document_index, fingerprint):
    base = provenance(document, split, document_index, fingerprint)
    for ei, group in enumerate(document["vertexSet"]):
        nid = node_id(split, document_index, ei)
        require(nid not in graph, f"Duplicate node identifier: {nid}")
        graph.add_node(nid, **node_record(group, base, ei))
    for li, label in enumerate(document["labels"]):
        u, v = (node_id(split, document_index, label[k]) for k in ("h", "t"))
        require(u in graph and v in graph, f"Invalid endpoints: {split}:{document_index}:{li}")
        key = edge_key(split, document_index, li)
        graph.add_edge(u, v, key=key, **edge_record(label, base, li, len(document["sents"])))


def build_document_graph(document, split, document_index, source_sha256):
    require(split in SPLITS, f"Unknown split: {split}")
    require(type(document_index) is int and document_index >= 0, "Invalid document index")
    require(type(source_sha256) is str and len(source_sha256) == 64
            and all(c in "0123456789abcdef" for c in source_sha256), "Invalid source fingerprint")
    issues = check_schema([document])
    graph = nx.MultiDiGraph(split=split, source_sha256=source_sha256,
                            document_indices=(document_index,), validation_warnings=deepcopy(issues),
                            document_hashes={document_index: digest(encoded(document).encode("utf-8"))})
    append_document(graph, document, split, document_index, source_sha256)
    return graph


def build_split_graph(source):
    require(source.split in SPLITS, f"Unknown split: {source.split}")
    issues = check_schema(source.documents)
    graph = nx.MultiDiGraph(split=source.split, source_sha256=source.sha256,
                            document_indices=tuple(range(len(source.documents))),
                            validation_warnings=deepcopy(issues),
                            document_hashes={i: digest(encoded(d).encode("utf-8")) for i, d in enumerate(source.documents)})
    for di, document in enumerate(source.documents):
        append_document(graph, document, source.split, di, source.sha256)
    return graph


def check_context(graph, source):
    require(isinstance(graph, nx.MultiDiGraph), "Expected a directed MultiDiGraph")
    require(graph.graph.get("split") == source.split, "Wrong source split")
    require(graph.graph.get("source_sha256") == source.sha256, "Source fingerprint mismatch")
    indices = graph.graph.get("document_indices")
    require(type(indices) is tuple and all(type(i) is int for i in indices), "Malformed document scope")
    require(len(indices) == len(set(indices)), "Malformed document scope")
    require(all(type(i) is int and 0 <= i < len(source.documents) for i in indices),
            "Document scope outside supplied source")
    require(type(graph.graph.get("document_hashes")) is dict, "Malformed document hash lookup")
    return indices


def validate_graph_provenance(graph, source, *, require_full_split=False):
    indices = check_context(graph, source)
    full_split = bool(source.documents) and set(indices) == set(range(len(source.documents)))
    require(not require_full_split or full_split,
            f"Full-split validation requires all {len(source.documents)} source documents; declared {len(indices)}")
    expected_nodes, expected_edges = 0, 0
    evidence = Counter(nonempty=0, empty=0, absent=0)
    for di in indices:
        document = source.documents[di]
        base = provenance(document, source.split, di, source.sha256)
        require(graph.graph.get("document_hashes", {}).get(di) == base["document_sha256"],
                f"Wrong source document or changed source: {di}")
        for ei, group in enumerate(document["vertexSet"]):
            nid = node_id(source.split, di, ei)
            require(nid in graph, f"Missing source node: {nid}")
            require(same_record(graph.nodes[nid], node_record(group, base, ei)), f"Node provenance mismatch: {nid}")
            expected_nodes += 1
        for li, label in enumerate(document["labels"]):
            u, v = (node_id(source.split, di, label[k]) for k in ("h", "t"))
            key = edge_key(source.split, di, li)
            require(graph.has_edge(u, v, key), f"Missing source edge: {key}")
            require(same_record(graph.edges[u, v, key], edge_record(label, base, li, len(document["sents"]))),
                    f"Edge provenance mismatch: {key}")
            evidence[evidence_kind(label, len(document["sents"]))] += 1
            expected_edges += 1
    require(graph.number_of_nodes() == expected_nodes, "Node reconciliation failed: unexpected nodes")
    require(graph.number_of_edges() == expected_edges, "Edge reconciliation failed: unexpected edges")
    return {"nodes": expected_nodes, "edges": expected_edges, **evidence,
            "nodes_validated": expected_nodes, "edges_validated": expected_edges,
            "documents_validated": len(indices), "documents_available": len(source.documents),
            "full_split": full_split, "validation_scope": "FULL_SPLIT" if full_split else "SUBSET",
            "provenance_status": "PASS"}


def reconstruct_edge_source(graph, u, v, key, source):
    indices = check_context(graph, source)
    require(graph.has_edge(u, v, key), f"Unknown edge: {u}, {v}, {key}")
    edge = graph.edges[u, v, key]
    ref = edge.get("provenance", {})
    require(type(ref) is dict, "Malformed edge provenance reference")
    di, li = ref.get("document_index"), ref.get("label_index")
    require(type(di) is int and di in indices, "Malformed document reference")
    document = source.documents[di]
    require(type(li) is int and 0 <= li < len(document["labels"]), "Malformed label reference")
    label = document["labels"][li]
    base = provenance(document, source.split, di, source.sha256)
    require(graph.graph.get("document_hashes", {}).get(di) == base["document_sha256"],
            f"Wrong source document or changed source: {di}")
    require((u, v, key) == (node_id(source.split, di, label["h"]),
                            node_id(source.split, di, label["t"]), edge_key(source.split, di, li)),
            "Edge identifiers do not match source record")
    require(same_record(edge, edge_record(label, base, li, len(document["sents"]))), "Edge provenance mismatch")
    endpoints = {}
    for role in ("h", "t"):
        ei = label[role]
        nid = node_id(source.split, di, ei)
        group = document["vertexSet"][ei]
        require(same_record(graph.nodes[nid], node_record(group, base, ei)), f"Node provenance mismatch: {nid}")
        mentions = []
        for mi, mention in enumerate(group):
            sentence = document["sents"][mention["sent_id"]]
            start, end = mention["pos"]
            mentions.append({"mention_index": mi, "source_mention": deepcopy(mention),
                             "sentence_tokens": deepcopy(sentence), "span_tokens": deepcopy(sentence[start:end])})
        endpoints[role] = {"node_id": nid, "entity_index": ei, "mentions": mentions}
    return {"edge_key": key, "provenance": deepcopy(ref), "source_relation": deepcopy(label),
            "evidence_availability": edge["evidence_availability"], "endpoints": endpoints,
            "evidence_sentences": [{"sentence_index": sid, "tokens": deepcopy(document["sents"][sid])}
                                   for sid in label.get("evidence", [])]}


def make_demo(graph, source):
    require(source.split == "train", "Demonstration must use train only")
    di = next((i for i, d in enumerate(source.documents) if d["labels"]), None)
    require(di is not None, "No train document with relations is available for demonstration")
    doc = source.documents[di]
    examples = []
    for li, label in enumerate(doc["labels"][:3]):
        u, v = (node_id("train", di, label[k]) for k in ("h", "t"))
        example = reconstruct_edge_source(graph, u, v, edge_key("train", di, li), source)
        for endpoint in example["endpoints"].values():
            endpoint["omitted_mentions"] = max(0, len(endpoint["mentions"]) - 2)
            endpoint["mentions"] = endpoint["mentions"][:2]
        example["omitted_evidence_sentences"] = max(0, len(example["evidence_sentences"]) - 3)
        example["evidence_sentences"] = example["evidence_sentences"][:3]
        for sentence in example["evidence_sentences"]:
            sentence["rendered_view"] = " ".join(sentence["tokens"])
        examples.append(example)
    return {"selection_rule": "lowest train document index with a relation; first at most 3 labels",
            "document_index": di, "title": doc["title"], "omitted_relations": max(0, len(doc["labels"]) - 3),
            "examples": examples, "interpretation": "Original annotations and token arrays; rendered views are not original whitespace text."}


def check_output_dir(data_dir, manifest_path, output_dir):
    data, out = Path(data_dir).resolve(), Path(output_dir).resolve()
    root = Path(__file__).resolve().parents[1]
    require("private_gold" not in out.parts, "private_gold is evaluation-only")
    roots = [data, root / "data" / "raw", root / "results" / "phase0",
             *(p for p in data.parents if p.name in ("raw", "re_docred"))]
    if Path(manifest_path).resolve().parent.name == "phase0":
        roots.append(Path(manifest_path).resolve().parent)
    require(not any(out == p or out.is_relative_to(p) for p in roots), "Output must be outside raw data and Phase 0 outputs")
    for name in ("graph_summary.json", "provenance_demo.json", "run_manifest.json", "phase1_report.md", "latest_run.json", "runs"):
        target = out / name
        require(not target.is_symlink(), f"Output symlink is not accepted: {target}")
        require(target.resolve() != Path(manifest_path).resolve(), "Cannot overwrite input manifest")


def write_latest(output_dir, status):
    """Replace the single authoritative attempt record atomically on the same filesystem."""
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output_dir,
                                     prefix=".latest-", suffix=".json", delete=False) as handle:
        json.dump(status, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(handle.name, output_dir / "latest_run.json")


def publish_run(output_dir, run_id, summary, demo, versions):
    """Expose all artifacts together; a separate latest PASS commits the complete run."""
    pending = Path(tempfile.mkdtemp(prefix=f".pending-{run_id}-", dir=output_dir))
    for name, value in (("graph_summary", summary), ("provenance_demo", demo), ("run_manifest", versions)):
        (pending / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    (pending / "phase1_report.md").write_text(report(summary, demo), encoding="utf-8")
    hashes = {p.name: digest(p.read_bytes()) for p in sorted(pending.iterdir())}
    runs = output_dir / "runs"
    require(not runs.is_symlink(), "Output symlink is not accepted: runs")
    runs.mkdir(exist_ok=True)
    destination = runs / run_id
    require(not destination.exists(), f"Run directory already exists: {destination}")
    pending.rename(destination)
    return destination, hashes


def report(summary, demo):
    lines = ["# GIR-ER Phase 1 execution report", "", f"Status: **{summary['status']}**.", "",
             "| Split | Nodes validated | Edges validated | Nonempty pointers | Empty pointers | Absent pointers |",
             "|---|---:|---:|---:|---:|---:|"]
    for split, s in summary["splits"].items():
        lines.append(f"| {split} | {s['nodes_validated']} | {s['edges_validated']} | {s['nonempty']} | {s['empty']} | {s['absent']} |")
    lines += ["", "Every node and edge was compared with its original annotation, including nested source values and provenance. "
              "Strict FULL_SPLIT validation covered every source document. Counts matched both Phase 0 expectations and source-derived mappings. "
              "Input hashes matched before and after construction.", "",
              f"Warnings by split: `{encoded({k: v['warning_counts'] for k, v in summary['splits'].items()})}`.", "",
              f"Train demonstration: document {demo['document_index']} ({demo['title']}), {len(demo['examples'])} original relation records. "
              "See provenance_demo.json for node identifiers, source labels, mentions and sentence tokens.", "",
              "## Design and limits", "",
              "A NetworkX MultiDiGraph preserves one node per document-scoped group and one edge per source label, including isolates, "
              "duplicates, parallel predicates and loops. Explicit IDs use split and original indices. Mutable source dictionaries are deep-copied "
              "into node/edge attributes; verified source documents remain external to the graph. No full graph dump is generated.", "",
              "Missing evidence is retained as absent, empty or nonempty; malformed evidence fails validation. These are pointer-availability "
              "states, not truth classifications. Sentence arrays are lossless; joined text is labelled rendered_view.", "",
              "The source loader and validator are reused without modifying Phase 0. Test is used only for integrity verification. "
              "No candidates, fragmentation, merges, counterfactual analysis, risk scores or verified QA were implemented.", "",
              "The independent PASS WITH CONDITIONS review is student-reported; its detailed conditions are unavailable locally. "
              "No claim is made that unseen conditions were satisfied. Known deferred limitations include source licence/release authenticity, "
              "relation semantics, independent identity/QA annotation, and train/dev text overlap. Source hashes identify bytes, not truth.", "",
              "LACE/ASPEN/ASPEN+ boundaries remain governing; graph construction is not claimed as a novel contribution. "
              "GIR-ER's incremental benefit over an equally informed matcher is untested.", "",
              "## Reproduce", "", "```bash",
              ".venv/bin/python -B scripts/build_graph.py --data-dir data/raw/re_docred/data --manifest results/phase0/input_manifest.json --output-dir results/phase1",
              ".venv/bin/python -B -m pytest -q -p no:cacheprovider", "```", "",
              "See ../../validation_record.md for actual test output, repeated-run comparison and final repository integrity checks. "
              "run_manifest.json records the invocation, input hashes and implementation versions. Machine-specific metadata is not required to be byte-identical.", "",
              "## Execution status contract", "",
              "This is an immutable completed-run artifact. Check ../../latest_run.json for the latest recorded attempt: "
              "only PASS with a completed run_directory and matching artifact hashes establishes latest-attempt success. "
              "RUNNING, FAILED, a missing record or an unreadable record does not. Earlier top-level Phase 1 files are historical. "
              "Publication stages all four artifacts in a hidden directory, renames it into runs/, then atomically publishes PASS. "
              "A crash before that final status may leave an uncommitted directory; it is not an authoritative successful attempt. "
              "Use one writer per output directory; concurrent executions require separate output directories.", "",
              "Phase 2 requires student approval plus review of genuine identity evidence, permitted inputs, private-map safeguards, "
              "annotation protocol and partition policy. No candidate work was started. STOP.", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data/raw/re_docred/data"))
    parser.add_argument("--manifest", type=Path, default=Path("results/phase0/input_manifest.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/phase1"))
    args = parser.parse_args(argv)
    attempt = None
    stage = "output_preflight"
    try:
        check_output_dir(args.data_dir, args.manifest, args.output_dir)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        attempt = {"format_version": FORMAT_VERSION, "run_id": uuid4().hex,
                   "status": "RUNNING", "run_directory": None, "error": None,
                   "command": sys.orig_argv if argv is None else [sys.executable, str(Path(__file__)), *argv]}
        stage = "status_initialization"
        write_latest(args.output_dir, attempt)
        stage = "load_manifest"
        manifest = load_json(source_path(args.manifest).read_bytes())
        phase0_path = source_path(args.manifest.parent / "dataset_audit.json")
        phase0 = load_json(phase0_path.read_bytes())
        require(phase0["status"] == "VALID", "Phase 0 dataset audit is not VALID")
        summary = {"format_version": FORMAT_VERSION, "status": "PASS", "splits": {}}
        fingerprints, demo = {}, None
        for split in SPLITS:
            stage = f"construct_and_validate:{split}"
            source = load_split(args.data_dir, split, manifest)
            require(phase0["input_fingerprints"][split] == source.sha256, f"Phase 0 audit fingerprint mismatch: {split}")
            graph = build_split_graph(source)
            counts = validate_graph_provenance(graph, source, require_full_split=True)
            for name, expected in EXPECTED[split].items():
                require(counts[name] == expected, f"Acceptance count mismatch for {split}.{name}: {counts[name]} != {expected}")
            original = phase0["splits"][split]
            require(counts["nodes"] == original["counts"]["entity_groups"] and counts["edges"] == original["counts"]["relations"],
                    f"Phase 0 graph count reconciliation failed: {split}")
            for kind in ("nonempty", "empty", "absent"):
                require(counts[kind] == original["evidence_all_relation_objects"].get(kind, 0), f"Phase 0 evidence reconciliation failed: {split}.{kind}")
            summary["splits"][split] = {**counts, "warning_counts": dict(Counter(i["code"] for i in source.diagnostics)),
                                        "source_sha256": source.sha256}
            fingerprints[split] = {"path": source.path.as_posix(), "sha256_before": source.sha256}
            if split == "train":
                demo = make_demo(graph, source)
            del graph, source
        stage = "source_integrity"
        for split, entry in fingerprints.items():
            entry["sha256_after"] = digest(Path(entry["path"]).read_bytes())
            require(entry["sha256_after"] == entry["sha256_before"], f"Source changed during execution: {split}")
        versions = {"format_version": FORMAT_VERSION, "python": sys.version, "executable": sys.executable,
                    "platform": platform.platform(), "networkx": nx.__version__,
                    "command": sys.orig_argv if argv is None else [sys.executable, str(Path(__file__)), *argv],
                    "inputs": fingerprints, "phase0_manifest_sha256": digest(args.manifest.read_bytes()),
                    "phase0_audit_sha256": digest(phase0_path.read_bytes()),
                    "implementation_sha256": {p.name: digest(p.read_bytes()) for p in (Path(__file__), Path(__file__).with_name("audit_dataset.py"))}}
        stage = "artifact_publication"
        destination, hashes = publish_run(args.output_dir, attempt["run_id"], summary, demo, versions)
        stage = "success_status_publication"
        write_latest(args.output_dir, {**attempt, "status": "PASS",
                                      "run_directory": destination.relative_to(args.output_dir).as_posix(),
                                      "artifact_sha256": hashes})
    except (ValueError, OSError, KeyError, TypeError, IndexError) as exc:
        if attempt is not None and stage != "status_initialization":
            try:
                write_latest(args.output_dir, {**attempt, "status": "FAILED",
                                              "error": {"stage": stage, "type": type(exc).__name__, "reason": str(exc)}})
            except OSError as status_exc:
                print(f"Could not record failed attempt: {status_exc}; no new PASS established", file=sys.stderr)
        elif stage == "status_initialization":
            print("Could not initialize latest-run status; no new attempt recorded", file=sys.stderr)
        print(f"Phase 1 failed: {exc}", file=sys.stderr)
        return 1
    for split, s in summary["splits"].items():
        print(f"{split}: {s['nodes_validated']} nodes, {s['edges_validated']} edges validated; provenance PASS")
    print(f"Phase 1 PASS; all source hashes unchanged; outputs: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
