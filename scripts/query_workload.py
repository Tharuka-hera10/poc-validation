"""Phase 3 structural queries over original annotations; no verified QA or merges."""

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import time
from uuid import uuid4

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.audit_dataset import SPLITS, digest, encoded, load_json
from scripts.build_graph import (build_split_graph, load_split, require, same_record, source_path,
                                 validate_graph_provenance, write_latest)
from scripts.candidate_discovery import (check_destinations, json_text, phase1_baseline,
                                         publish_package, validate_candidate_export, verify_sources)


ROOT = Path(__file__).resolve().parents[1]
VERSION = "phase3-structural-v1"
LIMIT = 100_000
POLICY = {"version": VERSION, "path_policy": "simple", "discovery_split": "train",
          "extension_limit_per_document_and_query": LIMIT,
          "role_order": ["candidate_endpoint", "general", "zero_diagnostic"],
          "targets_per_hop": {"candidate_endpoint": 1, "general": 4, "zero_diagnostic": 1},
          "hop_order": [2, 3], "ordering": "numeric document/anchor, relation sequence, numeric label sequence",
          "diversity": "unique document and anchor globally; unique relation sequence within hop",
          "selection": "no answer-count, semantic, private-label or merge-outcome ranking"}


def fields(value, keys):
    """Enforce nested allowlists at public input/output boundaries."""
    require(type(value) is dict and set(value) == set(keys), f"Expected exactly fields: {sorted(keys)}")


def indices(value):
    """Sort source identifiers numerically and reject malformed identifiers."""
    require(type(value) is str and re.fullmatch(r"(?:train|dev|test):(?:0|[1-9]\d*):(?:0|[1-9]\d*)", value), "Invalid source identifier")
    return tuple(map(int, value.split(":")[1:]))


def node_reference(graph, nid):
    """Export only source coordinates, never arbitrary source attributes."""
    di, ei = indices(nid)
    require(nid in graph, f"Missing anchor/node: {nid}")
    p = graph.nodes[nid].get("provenance", {})
    expected = {"split": graph.graph["split"], "document_index": di, "entity_index": ei,
                "source_sha256": graph.graph["source_sha256"], "document_sha256": graph.graph["document_hashes"].get(di)}
    require(nid.split(":")[0] == expected["split"] and all(same_record(p.get(k), v) for k, v in expected.items()), "Node provenance mismatch")
    return expected


def make_query(graph, anchor, relations, type_constraints=None, max_extensions=LIMIT):
    """Bind a structural query to fixed source bytes and explicit semantics."""
    query = {"query_version": VERSION, "dataset_split": graph.graph["split"],
             "anchor_entity_id": anchor, "relations": list(relations), "hop_count": len(relations),
             "type_constraints": deepcopy(type_constraints) if type_constraints is not None else [None] * (len(relations) + 1),
             "path_policy": "simple", "source_sha256": graph.graph["source_sha256"],
             "anchor_provenance": node_reference(graph, anchor), "max_extensions": max_extensions}
    query["query_id"] = "query_" + digest(encoded(query).encode())
    validate_query(query)
    return query


def validate_query(query):
    """Reject private fields, unsupported semantics and ambiguous query shapes."""
    fields(query, ("query_id", "query_version", "dataset_split", "anchor_entity_id", "relations", "hop_count",
                   "type_constraints", "path_policy", "source_sha256", "anchor_provenance", "max_extensions"))
    require(query["query_version"] == VERSION and query["path_policy"] == "simple", "Unsupported query semantics")
    require(query["dataset_split"] in SPLITS and type(query["hop_count"]) is int and query["hop_count"] in (2, 3), "Invalid split or hop count")
    require(type(query["relations"]) is list and len(query["relations"]) == query["hop_count"]
            and all(type(r) is str and bool(r) for r in query["relations"]), "Invalid relation sequence")
    require(type(query["source_sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", query["source_sha256"]), "Invalid fingerprint")
    require(type(query["max_extensions"]) is int and query["max_extensions"] > 0, "Invalid computational limit")
    constraints = query["type_constraints"]
    require(type(constraints) is list and len(constraints) == query["hop_count"] + 1, "Invalid type constraint positions")
    for allowed in constraints:
        require(allowed is None or (type(allowed) is list and bool(allowed)
                and all(type(t) is str and bool(t) for t in allowed) and allowed == sorted(set(allowed))), "Invalid type constraint")
    di, ei = indices(query["anchor_entity_id"])
    p = query["anchor_provenance"]
    fields(p, ("split", "document_index", "entity_index", "source_sha256", "document_sha256"))
    require(query["anchor_entity_id"].split(":")[0] == query["dataset_split"] == p["split"]
            and type(p["document_index"]) is int and type(p["entity_index"]) is int
            and (p["document_index"], p["entity_index"]) == (di, ei)
            and p["source_sha256"] == query["source_sha256"]
            and type(p["document_sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", p["document_sha256"]), "Invalid anchor provenance")
    core = {k: v for k, v in query.items() if k != "query_id"}
    require(query["query_id"] == "query_" + digest(encoded(core).encode()), "Query ID does not match specification")


def traverse(graph, anchor, budget, relations=None, constraints=None):
    """Yield occurrence paths; a shared deterministic budget also bounds discovery."""
    depth = len(relations) if relations is not None else 3

    def matches(nid, position):
        allowed = constraints[position] if constraints is not None else None
        return allowed is None or bool(set(allowed) & {m["type"] for m in graph.nodes[nid]["source_mentions"]})

    def visit(nodes, edges):
        outgoing = sorted(graph.out_edges(nodes[-1], keys=True), key=lambda e: (indices(e[1]), indices(e[2])))
        for u, v, key in outgoing:
            if budget["extensions"] == budget["limit"]:
                budget["status"] = "INCOMPLETE"
                return
            budget["extensions"] += 1
            if relations is not None and graph.edges[u, v, key]["relation"] != relations[len(edges)]:
                continue
            if v in nodes:
                budget["excluded_repeated_vertex_extensions"] += 1
                budget["excluded_self_loop_extensions"] += u == v
                continue
            if not matches(v, len(nodes)):
                continue
            next_nodes, next_edges = nodes + [v], edges + [(u, v, key)]
            if len(next_edges) == depth or (relations is None and len(next_edges) == 2):
                yield next_nodes, next_edges
            if len(next_edges) < depth:
                yield from visit(next_nodes, next_edges)
            if budget["status"] == "INCOMPLETE":
                return
    if matches(anchor, 0):
        yield from visit([anchor], [])


def new_budget(limit):
    return {"limit": limit, "extensions": 0, "excluded_repeated_vertex_extensions": 0,
            "excluded_self_loop_extensions": 0, "status": "COMPLETE"}


def edge_view(graph, u, v, key):
    """Retain occurrence provenance with exact optional evidence and no extra fields."""
    ref = node_reference(graph, u)
    target = node_reference(graph, v)
    di, li = indices(key)
    edge = graph.edges[u, v, key]
    p, label = edge.get("provenance", {}), edge.get("source_relation", {})
    require(di == ref["document_index"] == target["document_index"] and key.split(":")[0] == ref["split"], "Wrong edge document")
    required = {"split": ref["split"], "document_index": di, "label_index": li,
                "head_index": indices(u)[1], "tail_index": indices(v)[1],
                "source_sha256": ref["source_sha256"], "document_sha256": ref["document_sha256"]}
    require(all(same_record(p.get(k), val) for k, val in required.items()), "Malformed edge provenance")
    require(type(label) is dict and type(label.get("r")) is str and label["r"] == edge.get("relation")
            and same_record(label.get("h"), required["head_index"]) and same_record(label.get("t"), required["tail_index"]), "Source relation mismatch")
    result = {"head_entity_id": u, "tail_entity_id": v, "edge_key": key, "relation": label["r"],
              "provenance": required, "evidence_availability": edge["evidence_availability"]}
    if "evidence" in label:
        result["evidence"] = deepcopy(label["evidence"])
    return result


def evaluate_query(graph, query):
    """Evaluate a previously source-validated graph; reconstruction verifies source rows."""
    import networkx as nx
    require(isinstance(graph, nx.MultiDiGraph), "Expected directed MultiDiGraph")
    validate_query(query)
    require(graph.graph["split"] == query["dataset_split"] and graph.graph["source_sha256"] == query["source_sha256"], "Wrong split/fingerprint")
    require(same_record(node_reference(graph, query["anchor_entity_id"]), query["anchor_provenance"]), "Wrong anchor reference")
    budget, paths = new_budget(query["max_extensions"]), []
    for nodes, edges in traverse(graph, query["anchor_entity_id"], budget, query["relations"], query["type_constraints"]):
        paths.append({"node_ids": nodes, "relations": list(query["relations"]),
                      "edge_occurrences": [edge_view(graph, *edge) for edge in edges]})
    result = {"query_id": query["query_id"], "query_version": VERSION,
              "source_sha256": query["source_sha256"], "status": budget["status"],
              "answer_ids": sorted({p["node_ids"][-1] for p in paths}, key=indices),
              "paths": paths, "diagnostics": budget}
    validate_result(result, query)
    return result


def validate_result(result, query):
    """Validate public answer/path structures, including nested provenance allowlists."""
    validate_query(query)
    fields(result, ("query_id", "query_version", "source_sha256", "status", "answer_ids", "paths", "diagnostics"))
    require(result["query_id"] == query["query_id"] and result["query_version"] == VERSION
            and result["source_sha256"] == query["source_sha256"] and result["status"] in ("COMPLETE", "INCOMPLETE"), "Invalid result identity/status")
    fields(result["diagnostics"], new_budget(1))
    d = result["diagnostics"]
    require(d["status"] == result["status"] and d["limit"] == query["max_extensions"]
            and all(type(d[k]) is int and d[k] >= 0 for k in ("limit", "extensions", "excluded_repeated_vertex_extensions", "excluded_self_loop_extensions"))
            and d["extensions"] <= d["limit"], "Invalid completion diagnostics")
    require(type(result["paths"]) is list and type(result["answer_ids"]) is list, "Invalid answer/path lists")
    seen = set()
    for path in result["paths"]:
        fields(path, ("node_ids", "relations", "edge_occurrences"))
        nodes, edges = path["node_ids"], path["edge_occurrences"]
        require(type(nodes) is list and len(nodes) == query["hop_count"] + 1
                and all(type(n) is str for n in nodes) and len(set(nodes)) == len(nodes)
                and nodes[0] == query["anchor_entity_id"] and path["relations"] == query["relations"]
                and type(edges) is list and len(edges) == query["hop_count"], "Invalid path semantics")
        for nid in nodes:
            indices(nid)
        for i, edge in enumerate(edges):
            required = {"head_entity_id", "tail_entity_id", "edge_key", "relation", "provenance", "evidence_availability"}
            require(type(edge) is dict, "Invalid occurrence")
            fields(edge, required | ({"evidence"} if "evidence" in edge else set()))
            p = edge["provenance"]
            fields(p, ("split", "document_index", "label_index", "head_index", "tail_index", "source_sha256", "document_sha256"))
            require(all(type(p[k]) is int and p[k] >= 0 for k in ("document_index", "label_index", "head_index", "tail_index")), "Invalid occurrence indices")
            require((edge["head_entity_id"], edge["tail_entity_id"], edge["relation"]) == (nodes[i], nodes[i+1], query["relations"][i])
                    and edge["edge_key"] == f"{p['split']}:{p['document_index']}:{p['label_index']}"
                    and nodes[i] == f"{p['split']}:{p['document_index']}:{p['head_index']}"
                    and nodes[i+1] == f"{p['split']}:{p['document_index']}:{p['tail_index']}"
                    and p["split"] == query["dataset_split"] and p["source_sha256"] == query["source_sha256"]
                    and p["document_sha256"] == query["anchor_provenance"]["document_sha256"], "Wrong path provenance")
            if "evidence" in edge:
                require(type(edge["evidence"]) is list and all(type(s) is int and s >= 0 for s in edge["evidence"]), "Invalid evidence pointers")
                kind = "nonempty" if edge["evidence"] else "empty"
            else:
                kind = "absent"
            require(edge["evidence_availability"] == kind, "Wrong pointer availability")
        identity = (tuple(nodes), tuple(e["edge_key"] for e in edges))
        require(identity not in seen, "Duplicate occurrence path")
        seen.add(identity)
    require(result["answer_ids"] == sorted({p["node_ids"][-1] for p in result["paths"]}, key=indices), "Answer-set reconciliation failed")


def discover_workload(graph, candidate_endpoints, limit=LIMIT):
    """Train-only occurrence-chain audit; store one seed per anchor/relation sequence."""
    require(graph.graph["split"] == "train", "Workload discovery accepts train only")
    require(type(limit) is int and limit > 0, "Invalid discovery limit")
    require(all(n in graph and n.startswith("train:") for n in candidate_endpoints), "Invalid candidate endpoint")
    documents = defaultdict(list)
    for nid in graph:
        documents[indices(nid)[0]].append(nid)
    seeds, patterns, runs, endpoint_coverage = {}, {}, [], {n: {2: 0, 3: 0} for n in sorted(candidate_endpoints, key=indices)}
    for di, anchors in sorted(documents.items()):
        budget = new_budget(limit)
        for anchor in sorted(anchors, key=indices):
            for nodes, edges in traverse(graph, anchor, budget):
                relations = tuple(graph.edges[e]["relation"] for e in edges)
                types = tuple(tuple(sorted({m["type"] for m in graph.nodes[n]["source_mentions"]})) for n in nodes)
                key = (relations, types)
                if key not in patterns:
                    patterns[key] = {"occurrence_paths": 0, "documents": set(), "all_edges_pointed_paths": 0}
                p = patterns[key]
                p["occurrence_paths"] += 1
                p["documents"].add(di)
                p["all_edges_pointed_paths"] += all(graph.edges[e]["evidence_availability"] == "nonempty" for e in edges)
                seeds.setdefault((anchor, relations), tuple(e[2] for e in edges))
                if anchor in endpoint_coverage:
                    endpoint_coverage[anchor][len(edges)] += 1
            if budget["status"] == "INCOMPLETE":
                break
        runs.append({"document_index": di, **budget})
    inventory = {"status": "COMPLETE" if all(r["status"] == "COMPLETE" for r in runs) else "INCOMPLETE",
                 "document_runs": runs,
                 "patterns": [{"relations": list(rel), "type_sets": [list(t) for t in types],
                               "occurrence_paths": p["occurrence_paths"], "document_count": len(p["documents"]),
                               "all_edges_pointed_paths": p["all_edges_pointed_paths"]}
                              for (rel, types), p in sorted(patterns.items())],
                 "candidate_endpoint_coverage": [{"entity_id": n, "two_hop_occurrence_paths": counts[2],
                                                  "three_hop_occurrence_paths": counts[3]} for n, counts in endpoint_coverage.items()],
                 "source_self_loops": sum(u == v for u, v in graph.edges()),
                 "interpretation": "Occurrence chains and pointer availability only; endpoint proximity is not candidate utility."}
    return seeds, inventory


def validate_packages(query_package, result_package):
    """Validate exported envelopes as well as each nested query and result."""
    for payload, content in ((query_package, "queries"), (result_package, "results")):
        fields(payload, ("format_version", "query_version", "source_sha256", content))
        require(type(payload["format_version"]) is int and payload["format_version"] == 1
                and payload["query_version"] == VERSION and type(payload[content]) is list, "Invalid package version/content")
    require(query_package["source_sha256"] == result_package["source_sha256"]
            and type(query_package["source_sha256"]) is str
            and re.fullmatch(r"[0-9a-f]{64}", query_package["source_sha256"]), "Wrong package fingerprint")
    queries, results = query_package["queries"], result_package["results"]
    require(len(queries) == len(results), "Query/result count mismatch")
    seen = set()
    for query, result in zip(queries, results):
        validate_result(result, query)
        require(query["source_sha256"] == query_package["source_sha256"] and query["query_id"] not in seen, "Duplicate/wrong-source query")
        seen.add(query["query_id"])


def select_queries(graph, seeds, endpoints):
    """Freeze the approved role/hop priority, without inspecting selected answer sets."""
    require(graph.graph["split"] == "train", "Workload selection accepts train only")
    queries, selections, used_docs, used_anchors, used_patterns = [], [], set(), set(), set()
    ordered = sorted(seeds, key=lambda item: (indices(item[0]), item[1], tuple(indices(k) for k in seeds[item])))
    quotas = []
    for role in POLICY["role_order"]:
        for hop in (2, 3):
            count, target = 0, POLICY["targets_per_hop"][role]
            if role == "zero_diagnostic":
                available_relations = sorted({rel for _, rel in seeds if len(rel) == hop and rel not in used_patterns})
                options = ((n, rel) for n in sorted(graph, key=indices) if graph.out_degree(n) == 0 for rel in available_relations)
            else:
                options = ((n, rel) for n, rel in ordered if len(rel) == hop and (role != "candidate_endpoint" or n in endpoints))
            for anchor, relations in options:
                di = indices(anchor)[0]
                if di in used_docs or anchor in used_anchors or relations in used_patterns:
                    continue
                query = make_query(graph, anchor, relations)
                template_seed = next((n, rel) for n, rel in ordered if rel == relations)
                queries.append(query)
                selections.append({"query_id": query["query_id"], "role": role, "hop_count": hop,
                                   "anchor_entity_id": anchor, "template_origin_anchor": template_seed[0],
                                   "template_origin_edge_keys": list(seeds[template_seed])})
                used_docs.add(di); used_anchors.add(anchor); used_patterns.add(relations)
                count += 1
                if count == target:
                    break
            quotas.append({"role": role, "hop_count": hop, "target": target, "selected": count, "shortfall": target-count})
    return queries, {"selections": selections, "quotas": quotas}


def phase2_inputs():
    """Read only verified public preparation artifacts, never the private review paths."""
    root = ROOT / "results" / "phase2"
    latest = load_json(source_path(root / "latest_run.json").read_bytes())
    require(latest["status"] == "PASS", "Phase 2 latest attempt is not PASS")
    run = (root / latest["run_directory"]).resolve()
    require(run.is_relative_to((root / "runs").resolve()), "Invalid Phase 2 run reference")
    names = {"candidates_train.json", "candidate_inventory.json", "candidate_feasibility_report.md", "phase2_report.md", "run_manifest.json"}
    require(set(latest["artifact_sha256"]) == names, "Incomplete Phase 2 public reference")
    for name in sorted(names):
        require(digest(source_path(run / name).read_bytes()) == latest["artifact_sha256"][name], f"Phase 2 artifact mismatch: {name}")
    manifest = load_json(source_path(run / "run_manifest.json").read_bytes())
    for name, sha in manifest["implementation_sha256"].items():
        require(name in ("audit_dataset.py", "build_graph.py", "candidate_discovery.py", "prepare_annotation_worklist.py"), "Unexpected implementation reference")
        require(digest((ROOT / "scripts" / name).read_bytes()) == sha, f"Phase 2 implementation mismatch: {name}")
    candidates = load_json(source_path(run / "candidates_train.json").read_bytes())
    validate_candidate_export(candidates)
    return candidates, {"latest_sha256": digest((root / "latest_run.json").read_bytes()), "public_artifact_sha256": latest["artifact_sha256"]}


def check_phase3_destinations(args):
    """Extend previous guards without altering historical Phase 2 behaviour."""
    check_destinations(args.data_dir, args.manifest, args.output_dir, args.review_dir)
    out, private = args.output_dir.resolve(), args.review_dir.resolve()
    old = (ROOT / "results" / "phase2").resolve()
    require(not (out == old or out.is_relative_to(old)), "Phase 2 outputs are protected")
    private_root = (ROOT / "data" / "private_gold" / "phase3").resolve()
    require(private == private_root or private.is_relative_to(private_root), "Reviewer output must be under private_gold/phase3")


def render_reports(inventory, queries, results):
    """Report observed structural feasibility without assigning semantic truth."""
    totals = Counter()
    for pattern in inventory["discovery"]["patterns"]:
        totals[len(pattern["relations"]) ] += pattern["occurrence_paths"]
    report = ["# GIR-ER Phase 3 structural workload", "", "Technical execution: PASS. Semantic verification: NOT PERFORMED.", "",
              f"Version: `{VERSION}`. Selected queries: {len(queries)}. Source-only selection rules were declared before answer evaluation.", "",
              "| Role | Hops | Target | Selected | Shortfall |", "|---|---:|---:|---:|---:|"]
    for row in inventory["selection"]["quotas"]:
        report.append(f"| {row['role']} | {row['hop_count']} | {row['target']} | {row['selected']} | {row['shortfall']} |")
    report += ["", "| Query | Hops | Structural answers | Occurrence paths | Status |", "|---|---:|---:|---:|---|"]
    for query, result in zip(queries, results):
        report.append(f"| {query['query_id']} | {query['hop_count']} | {len(result['answer_ids'])} | {len(result['paths'])} | {result['status']} |")
    report += ["", f"Train graph FULL_SPLIT reconciliation: `{encoded(inventory['train_graph_validation'])}`.",
               f"General train occurrence-chain counts by hop: `{encoded(dict(totals))}`.",
               f"Candidate endpoint coverage: `{encoded(inventory['candidate_summary'])}`. Coverage is anchored structural reachability, not usefulness for ER.",
               f"Source self-loops: {inventory['discovery']['source_self_loops']}. Repeated-vertex exclusions are recorded per document and query.", "",
               "Every returned occurrence is reconstructed against original labels and tokens. Answer IDs are deduplicated while all supporting occurrence paths remain. "
               "Simple paths exclude self-loops and repeated vertices; the original graph retains them. Type constraints use nonempty intersection with original type sets. "
               "Queries follow outgoing edges and never invent reverse relations.", "",
               "## Research and evidence limits", "",
               "Structural reachability is not independently verified QA. Relation codes remain uninterpreted; no natural-language questions or semantic support labels are generated. "
               "Pointers describe annotation availability, not support. Structural zero does not establish semantic absence. All reviewer judgements are blank.", "",
               "The pilot uses source order and document/anchor/relation diversity, with candidate reservations first. This biases the workload. "
               "Zero diagnostics deliberately use zero-outdegree anchors and are reported separately. A shortage is retained without substitution. "
               "Queries were not screened by answer size, identity outcomes or future merge effects.", "",
               "Phase 2 has 35 LOC, 11 ORG and 2 PER endpoints in eight source-linked components. Natural cross-document candidates may lack useful "
               "within-document compositions; even existing anchored paths do not establish an informative merge experiment. No merges were simulated.", "",
               "Train 3052/dev 469 exact text overlap remains excluded from later independent dev evaluation; no raw document changed. "
               "Exact text grouping does not establish entity/paraphrase independence. Dev/test did not influence pattern selection.", "",
               "Source licence/release authenticity and relation definitions remain unresolved. Only the master research context is available; separate supervisor feedback, "
               "proposal/literature drafts and primary papers are unavailable. No authenticated supervisor decision or new literature verification is asserted.", "",
               "LACE/ASPEN/LACE+/ASPEN+ already cover collective ER/query reasoning. Traversal infrastructure is not a novelty claim. "
               "GIR-ER's incremental benefit over an equally informed matcher remains unvalidated, including possible zero or negative results.", "",
               "## Reproduce", "", "```bash",
               ".venv/bin/python -B scripts/query_workload.py --data-dir data/raw/re_docred/data --manifest results/phase0/input_manifest.json --output-dir results/phase3 --review-dir data/private_gold/phase3",
               ".venv/bin/python -B -m pytest -q -p no:cacheprovider", "```", "",
               "Read ../../latest_run.json first. Only PASS plus complete referenced artifacts establishes latest success. Partial/orphan directories do not. "
               "Compare all deterministic artifacts except run_manifest.json; IDs/timing metadata may vary. See ../../validation_record.md for actual tests and failure checks.", "",
               "Student review of identities, query interpretation, individual triple support, composition and answer evidence remains required. "
               "No verified workload freeze, QA accuracy, ER classifier, fragmentation, counterfactual delta or risk score exists. STOP before Phase 4.", ""]
    feasibility = ["# Phase 3 feasibility", "", f"Selected structural cases: {len(queries)}; queries by hop: `{encoded(dict(Counter(q['hop_count'] for q in queries)))}`.",
                   f"General train occurrence chains: `{encoded(dict(totals))}`.",
                   f"Phase 2 endpoint coverage: `{encoded(inventory['candidate_summary'])}`.", "",
                   "This establishes source-traceable structural query mechanics and preparation material. It does not establish interpretable semantic compositions, "
                   "correct real-world answers or useful answer impacts for the natural ER pilot. Missing and ambiguous source evidence requires human review; "
                   "empty/absent pointers cannot establish contradiction. Complete graph enumeration cannot establish real-world answer completeness.", "",
                   "Inspect role-specific shortages in query_inventory.json. Keep general feasibility distinct from candidate coverage. "
                   "Do not change selection to produce favourable future outcomes. Publication rights, independent QA/identity review, source-linked partitioning "
                   "and any Phase 4 authorization remain open. No fragmentation or merge behaviour was implemented.", ""]
    return "\n".join(report), "\n".join(feasibility)


def main(argv=None):
    from scripts.prepare_qa_worklist import make_qa_dossier, qa_worklist_csv
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data/raw/re_docred/data"))
    parser.add_argument("--manifest", type=Path, default=Path("results/phase0/input_manifest.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/phase3"))
    parser.add_argument("--review-dir", type=Path, default=Path("data/private_gold/phase3"))
    args = parser.parse_args(argv)
    attempt, stage = None, "output_preflight"
    started = time.perf_counter()
    try:
        check_phase3_destinations(args)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        attempt = {"format_version": 1, "run_id": uuid4().hex, "status": "RUNNING", "run_directory": None, "error": None}
        stage = "status_initialization"
        write_latest(args.output_dir, attempt)
        stage = "baselines_and_sources"
        manifest = load_json(source_path(args.manifest).read_bytes())
        fingerprints = verify_sources(args.data_dir, manifest)
        phase1 = phase1_baseline()
        candidates, phase2 = phase2_inputs()
        require(candidates["source_sha256"] == fingerprints["train"], "Wrong Phase 2 source")
        audit = load_json(source_path(args.manifest.parent / "dataset_audit.json").read_bytes())
        require(audit["status"] == "VALID" and audit["input_fingerprints"] == fingerprints, "Invalid Phase 0 reference")
        stage = "train_validation"
        source = load_split(args.data_dir, "train", manifest)
        graph = build_split_graph(source)
        counts = validate_graph_provenance(graph, source, require_full_split=True)
        require(counts["nodes"] == audit["splits"]["train"]["counts"]["entity_groups"]
                and counts["edges"] == audit["splits"]["train"]["counts"]["relations"], "Phase 0 count mismatch")
        endpoints = {r[k] for r in candidates["candidates"] for k in ("left_entity_id", "right_entity_id")}
        stage = "discovery_and_selection"
        seeds, discovery = discover_workload(graph, endpoints)
        require(discovery["status"] == "COMPLETE", "INCOMPLETE discovery; document budgets in diagnostic stderr: " + encoded([r for r in discovery["document_runs"] if r["status"] != "COMPLETE"]))
        queries, selection = select_queries(graph, seeds, endpoints)
        stage = "evaluation"
        results = [evaluate_query(graph, query) for query in queries]
        require(all(r["status"] == "COMPLETE" for r in results), "INCOMPLETE selected-query enumeration; no complete workload published")
        stage = "source_reconstruction"
        dossier = make_qa_dossier(graph, source, queries, results, selection)
        validate_graph_provenance(graph, source, require_full_split=True)
        require(verify_sources(args.data_dir, manifest) == fingerprints, "Raw source changed")
        coverage = discovery["candidate_endpoint_coverage"]
        inventory = {"format_version": 1, "policy": POLICY, "source_sha256": fingerprints,
                     "train_graph_validation": counts, "discovery": discovery, "selection": selection,
                     "candidate_summary": {"endpoint_count": len(endpoints),
                         "with_two_hop_chains": sum(r["two_hop_occurrence_paths"] > 0 for r in coverage),
                         "with_three_hop_chains": sum(r["three_hop_occurrence_paths"] > 0 for r in coverage),
                         "selected_queries_anchored_at_endpoint": sum(q["anchor_entity_id"] in endpoints for q in queries)},
                     "overlap_policy": "Retain train 3052; exclude dev 469 from later independent dev evaluation. No dev/test discovery."}
        report, feasibility = render_reports(inventory, queries, results)
        query_package = {"format_version": 1, "query_version": VERSION, "source_sha256": source.sha256, "queries": queries}
        result_package = {"format_version": 1, "query_version": VERSION, "source_sha256": source.sha256, "results": results}
        validate_packages(query_package, result_package)
        runtime = time.perf_counter() - started
        versions = {"format_version": 1, "query_version": VERSION, "python": sys.version,
                    "command": sys.orig_argv if argv is None else [sys.executable, str(Path(__file__)), *map(str, argv)],
                    "runtime_seconds_before_publication": runtime, "source_sha256_before": fingerprints,
                    "source_sha256_after": verify_sources(args.data_dir, manifest),
                    "policy_sha256": digest(encoded(POLICY).encode()), "phase1_reference": phase1, "phase2_public_reference": phase2,
                    "phase0_manifest_sha256": digest(args.manifest.read_bytes()),
                    "phase0_audit_sha256": digest((args.manifest.parent / "dataset_audit.json").read_bytes()),
                    "implementation_sha256": {n: digest((ROOT / "scripts" / n).read_bytes()) for n in
                        ("query_workload.py", "prepare_qa_worklist.py", "audit_dataset.py", "build_graph.py", "candidate_discovery.py", "prepare_annotation_worklist.py")},
                    "private_inputs_read": False, "human_verification_performed": False}
        stage = "private_publication"
        private, private_hashes = publish_package(args.review_dir, attempt["run_id"],
                    {"qa_review_dossier.json": json_text(dossier), "qa_review_worklist.csv": qa_worklist_csv(dossier)})
        stage = "public_publication"
        public, hashes = publish_package(args.output_dir, attempt["run_id"], {
            "queries_train.json": json_text(query_package),
            "structural_query_results.json": json_text(result_package),
            "query_inventory.json": json_text(inventory), "phase3_report.md": report,
            "query_feasibility_report.md": feasibility, "run_manifest.json": json_text(versions)})
        stage = "success_status_publication"
        write_latest(args.output_dir, {**attempt, "status": "PASS", "run_directory": public.relative_to(args.output_dir).as_posix(),
                                      "artifact_sha256": hashes, "review_directory": str(private), "review_artifact_sha256": private_hashes})
    except (ValueError, OSError, KeyError, TypeError, IndexError) as exc:
        if attempt is not None and stage != "status_initialization":
            try:
                write_latest(args.output_dir, {**attempt, "status": "FAILED", "error": {"stage": stage, "type": type(exc).__name__, "reason": str(exc)}})
            except OSError as status_exc:
                print(f"Could not record failure: {status_exc}; no new PASS established", file=sys.stderr)
        else:
            print("Output/status preflight failed; no new attempt recorded", file=sys.stderr)
        print(f"Phase 3 failed at {stage}: {exc}", file=sys.stderr)
        return 1
    print(f"Phase 3 PASS: {len(queries)} structural queries; hops {dict(Counter(q['hop_count'] for q in queries))}; {sum(len(r['answer_ids']) for r in results)} query/answer pairs; {sum(len(r['paths']) for r in results)} occurrence paths")
    print(f"Train: {counts['nodes']} nodes / {counts['edges']} edges individually validated; hashes unchanged")
    print(f"Outputs: {public}; private blank QA package: {private}; preparation seconds: {runtime:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
