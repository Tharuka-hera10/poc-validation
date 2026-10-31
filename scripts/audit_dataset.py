"""Phase 0 only: immutable Re-DocRED audit; no identity or answer judgements."""

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys


SPLITS = ("train", "dev", "test")
FORMAT_VERSION = 1


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_json(raw):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON object key: {key}")
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError(f"non-JSON constant: {value}")

    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                      parse_constant=invalid_constant)


def validate(docs):
    """Return located diagnostics and indices of structurally usable documents."""
    issues, valid = [], []

    def issue(location, code, severity="ERROR"):
        issues.append({"location": location, "code": code, "severity": severity})

    def fields(obj, required, location):
        if not isinstance(obj, dict):
            issue(location, "expected_object")
            return False
        for key, kind in required.items():
            if key not in obj:
                issue(f"{location}.{key}", "missing_field")
            elif type(obj[key]) is not kind:
                issue(f"{location}.{key}", "wrong_type")
        return all(key in obj and type(obj[key]) is kind for key, kind in required.items())

    def index(value, size):
        return type(value) is int and 0 <= value < size

    if type(docs) is not list:
        issue("$", "expected_document_list")
        return issues, valid
    if not docs:
        issue("$", "empty_document_list")
    for di, doc in enumerate(docs):
        loc = f"$[{di}]"
        start = len(issues)
        if not fields(doc, {"title": str, "sents": list, "vertexSet": list, "labels": list}, loc):
            continue
        sents, groups = doc["sents"], doc["vertexSet"]
        if not sents:
            issue(loc + ".sents", "empty_sentences")
        for si, sent in enumerate(sents):
            if type(sent) is not list or not sent or any(type(t) is not str for t in sent):
                issue(f"{loc}.sents[{si}]", "invalid_token_sentence")
        for gi, group in enumerate(groups):
            gloc = f"{loc}.vertexSet[{gi}]"
            if type(group) is not list or not group:
                issue(gloc, "invalid_or_empty_group")
                continue
            for mi, mention in enumerate(group):
                mloc = f"{gloc}[{mi}]"
                if not fields(mention, {"name": str, "type": str, "sent_id": int, "pos": list}, mloc):
                    continue
                if not mention["name"] or not mention["type"]:
                    issue(mloc, "empty_name_or_type")
                sid, pos = mention["sent_id"], mention["pos"]
                if not index(sid, len(sents)):
                    issue(mloc + ".sent_id", "sentence_out_of_bounds")
                elif type(sents[sid]) is list:
                    if not (len(pos) == 2 and all(type(v) is int for v in pos)
                            and 0 <= pos[0] < pos[1] <= len(sents[sid])):
                        issue(mloc + ".pos", "invalid_half_open_span")
                    elif all(type(t) is str for t in sents[sid]) and mention["name"] != " ".join(sents[sid][pos[0]:pos[1]]):
                        issue(mloc, "name_span_text_difference", "WARNING")
                if "global_pos" in mention:
                    gp = mention["global_pos"]
                    if not (type(gp) is list and len(gp) == 2 and all(type(v) is int for v in gp)):
                        issue(mloc + ".global_pos", "invalid_auxiliary_position")
                if "index" in mention and type(mention["index"]) is not str:
                    issue(mloc + ".index", "invalid_auxiliary_index")
        for li, label in enumerate(doc["labels"]):
            lloc = f"{loc}.labels[{li}]"
            if not fields(label, {"h": int, "t": int, "r": str}, lloc):
                continue
            for endpoint in ("h", "t"):
                if not index(label[endpoint], len(groups)):
                    issue(lloc + "." + endpoint, "entity_out_of_bounds")
            if not label["r"]:
                issue(lloc + ".r", "empty_relation_code")
            if "evidence" not in label:
                issue(lloc + ".evidence", "absent_evidence", "WARNING")
            elif type(label["evidence"]) is not list:
                issue(lloc + ".evidence", "null_or_malformed_evidence")
            else:
                for ei, sid in enumerate(label["evidence"]):
                    if not index(sid, len(sents)):
                        issue(f"{lloc}.evidence[{ei}]", "evidence_out_of_bounds")
        if not any(i["severity"] == "ERROR" for i in issues[start:]):
            valid.append(di)
    return issues, valid


def evidence_kind(label, sentence_count):
    if "evidence" not in label:
        return "absent"
    value = label["evidence"]
    if value is None:
        return "null"
    if type(value) is not list or any(type(s) is not int or not 0 <= s < sentence_count for s in value):
        return "malformed"
    return "nonempty" if value else "empty"


def schema_variants(docs):
    variants = {kind: Counter() for kind in ("document", "mention", "relation")}
    for doc in docs if type(docs) is list else []:
        if type(doc) is not dict:
            continue
        variants["document"][encoded({k: type(v).__name__ for k, v in doc.items()})] += 1
        for group in doc.get("vertexSet", []) if type(doc.get("vertexSet")) is list else []:
            for mention in group if type(group) is list else []:
                if type(mention) is dict:
                    variants["mention"][encoded({k: type(v).__name__ for k, v in mention.items()})] += 1
        for label in doc.get("labels", []) if type(doc.get("labels")) is list else []:
            if type(label) is dict:
                variants["relation"][encoded({k: type(v).__name__ for k, v in label.items()})] += 1
    return {kind: [{"fields": json.loads(k), "count": n} for k, n in sorted(values.items())]
            for kind, values in variants.items()}


def describe(docs, valid_indices, exploratory):
    counts = Counter(documents=len(docs) if type(docs) is list else 0,
                     valid_documents=len(valid_indices))
    hist = {key: Counter() for key in ("entity_types", "relation_codes", "group_mention_counts",
                                       "document_evidence_nonempty_counts", "evidence")}
    relation_evidence, type_evidence = defaultdict(Counter), defaultdict(Counter)
    names = defaultdict(set)
    normalized = lambda name: " ".join(name.casefold().split())
    for di in valid_indices:
        d = docs[di]
        groups, labels = d["vertexSet"], d["labels"]
        counts.update(sentences=len(d["sents"]), tokens=sum(map(len, d["sents"])),
                      entity_groups=len(groups), relations=len(labels))
        for gi, group in enumerate(groups):
            counts["mentions"] += len(group)
            counts["multi_mention_groups"] += len(group) > 1
            hist["group_mention_counts"][str(len(group))] += 1
            types = {m["type"] for m in group}
            counts["mixed_type_groups"] += len(types) > 1
            if exploratory:
                counts["groups_with_distinct_normalized_aliases"] += len({normalized(m["name"]) for m in group}) > 1
            for m in group:
                hist["entity_types"][m["type"]] += 1
                counts["global_pos_zero_pair"] += m.get("global_pos") == [0, 0]
                if exploratory:
                    names[normalized(m["name"])].add((di, gi))
        triples, records = Counter(), Counter()
        nonempty = 0
        for label in labels:
            kind = evidence_kind(label, len(d["sents"]))
            nonempty += kind == "nonempty"
            hist["evidence"][kind] += 1
            hist["relation_codes"][label["r"]] += 1
            relation_evidence[label["r"]][kind] += 1
            pair = [sorted({m["type"] for m in groups[label[k]]}) for k in ("h", "t")]
            type_evidence[encoded(pair)][kind] += 1
            counts["self_relations"] += label["h"] == label["t"]
            triples[(label["h"], label["r"], label["t"])] += 1
            records[encoded(label)] += 1
        counts["duplicate_typed_triple_occurrences"] += sum(n - 1 for n in triples.values())
        counts["duplicate_relation_records"] += sum(n - 1 for n in records.values())
        hist["document_evidence_nonempty_counts"][str(nonempty)] += 1
    suitability = {"status": "DESCRIPTIVE_ONLY" if exploratory else "NOT_INSPECTED_RESERVED_TEST"}
    if exploratory:
        suitability.update(normalized_names_in_multiple_groups=sum(len(v) > 1 for v in names.values()),
                           normalized_names_across_documents=sum(len({di for di, _ in v}) > 1 for v in names.values()),
                           identity_labels_generated=False,
                           caveat="Name collisions and separate groups establish neither identity nor nonidentity.")
    return {"counts": counts, **hist, "evidence_by_relation": dict(relation_evidence),
            "evidence_by_endpoint_types": dict(type_evidence), "suitability": suitability,
            "statistics_scope": "structurally_valid_documents_only"}


def inspect_patterns(doc, split, di, source_hash, max_extensions):
    """Bound edge extensions, not wall time; deduplicate typed edges, retain occurrences."""
    edges = defaultdict(list)
    for li, label in enumerate(doc["labels"]):
        edges[(label["h"], label["r"], label["t"])].append(li)
    adjacency = defaultdict(list)
    for edge in sorted(edges):
        adjacency[edge[0]].append(edge)
    patterns, stats = {}, Counter()

    def visit(nodes, path):
        for edge in adjacency[nodes[-1]]:
            if stats["extensions"] >= max_extensions:
                return False
            stats["extensions"] += 1
            if edge[2] in nodes:
                stats["excluded_repeated_vertex_extensions"] += 1
                continue
            next_nodes, next_path = nodes + [edge[2]], path + [edge]
            if len(next_path) >= 2:
                relations = tuple(e[1] for e in next_path)
                types = tuple(tuple(sorted({m["type"] for m in doc["vertexSet"][n]})) for n in next_nodes)
                key = (relations, types)
                weight = pointer_weight = 1
                chosen = []
                for e in next_path:
                    ids = edges[e]
                    pointed = [i for i in ids if doc["labels"][i].get("evidence")]
                    weight *= len(ids)
                    pointer_weight *= len(pointed)
                    chosen.append((pointed or ids)[0])
                if key not in patterns:
                    patterns[key] = {"structural_paths": 0, "relation_occurrence_paths": 0,
                                     "all_edges_pointed_occurrence_paths": 0,
                                     "example": {"split": split, "document_index": di,
                                                 "file_sha256": source_hash, "entity_indices": next_nodes,
                                                 "relation_label_indices": chosen,
                                                 "evidence_sentence_ids": [doc["labels"][i].get("evidence", []) for i in chosen]}}
                item = patterns[key]
                item["structural_paths"] += 1
                item["relation_occurrence_paths"] += weight
                item["all_edges_pointed_occurrence_paths"] += pointer_weight
            if len(next_path) < 3 and not visit(next_nodes, next_path):
                return False
        return True

    complete = True
    for node in sorted(adjacency):
        if not visit([node], []):
            complete = False
            break
    return patterns, {"split": split, "document_index": di, **stats,
                      "status": "COMPLETE" if complete else "INCOMPLETE"}


def overlaps(entries):
    return [locations for _, locations in sorted(entries.items()) if len(locations) > 1]


def audit(data_dir, max_extensions=100_000):
    if max_extensions < 1:
        raise ValueError("max_extensions must be positive")
    data_dir = Path(data_dir)
    if "private_gold" in data_dir.resolve().parts:
        raise ValueError("private_gold is evaluation-only")
    if any((data_dir / f"{split}_revised.json").is_symlink() for split in SPLITS):
        raise ValueError("source symlinks are not accepted")
    result = {"format_version": FORMAT_VERSION, "splits": {}, "diagnostics": []}
    manifest = {"format_version": FORMAT_VERSION, "files": []}
    patterns, document_runs = {}, []
    duplicates = {k: defaultdict(list) for k in ("title", "sentence_content", "full_document")}
    for split in SPLITS:
        path = data_dir / f"{split}_revised.json"
        entry = {"split": split, "path": path.as_posix()}
        manifest["files"].append(entry)
        try:
            raw = path.read_bytes()
            entry.update(bytes=len(raw), sha256=digest(raw))
            docs = load_json(raw)
        except (OSError, ValueError) as exc:
            result["diagnostics"].append({"split": split, "location": "$", "severity": "ERROR",
                                           "code": "input_load_failure", "detail": str(exc)})
            continue
        issues, valid = validate(docs)
        result["diagnostics"].extend({"split": split, **i} for i in issues)
        summary = describe(docs, valid, split != "test")
        summary["schema_variants"] = schema_variants(docs)
        # Include evidence states even in invalid documents; never hide malformed evidence.
        all_evidence = Counter()
        for d in docs if type(docs) is list else []:
            if type(d) is dict and type(d.get("labels")) is list and type(d.get("sents")) is list:
                for label in d["labels"]:
                    if type(label) is dict:
                        all_evidence[evidence_kind(label, len(d["sents"]))] += 1
        summary["evidence_all_relation_objects"] = all_evidence
        result["splits"][split] = summary
        for di in valid:
            d = docs[di]
            location = {"split": split, "document_index": di}
            duplicates["title"][d["title"]].append(location)
            duplicates["sentence_content"][digest(encoded(d["sents"]).encode())].append(location)
            duplicates["full_document"][digest(encoded(d).encode())].append(location)
            if split == "test":
                continue
            found, status = inspect_patterns(d, split, di, entry["sha256"], max_extensions)
            document_runs.append(status)
            for key, value in found.items():
                if key not in patterns:
                    patterns[key] = {**value, "documents": 0}
                    for count in ("structural_paths", "relation_occurrence_paths", "all_edges_pointed_occurrence_paths"):
                        patterns[key][count] = 0
                item = patterns[key]
                item["documents"] += 1
                for count in ("structural_paths", "relation_occurrence_paths", "all_edges_pointed_occurrence_paths"):
                    item[count] += value[count]
    for entry in manifest["files"]:
        if "sha256" in entry:
            try:
                entry["sha256_after"] = digest(Path(entry["path"]).read_bytes())
            except OSError:
                entry["sha256_after"] = None
            if entry["sha256_after"] != entry["sha256"]:
                result["diagnostics"].append({"split": entry["split"], "location": "$", "severity": "ERROR",
                                               "code": "source_changed_during_audit"})
    result["duplicates"] = {key: overlaps(values) for key, values in duplicates.items()}
    result["diagnostic_counts"] = dict(sorted(Counter(i["code"] for i in result["diagnostics"]).items()))
    result["status"] = "INVALID" if any(i["severity"] == "ERROR" for i in result["diagnostics"]) else "VALID"
    inventory = {"format_version": FORMAT_VERSION, "max_extensions_per_document": max_extensions,
                 "scope": ["train", "dev"], "document_runs": document_runs,
                 "status": "INCOMPLETE" if any(s["status"] == "INCOMPLETE" for s in document_runs) or result["status"] != "VALID" else "COMPLETE",
                 "patterns": [{"relations": list(rel), "entity_types": [list(t) for t in types], **value}
                              for (rel, types), value in sorted(patterns.items())]}
    result["input_fingerprints"] = {e["split"]: e.get("sha256") for e in manifest["files"]}
    inventory["input_fingerprints"] = result["input_fingerprints"]
    manifest["audit_script_sha256"] = digest(Path(__file__).read_bytes())
    return manifest, result, inventory


def guard_paths(data_dir, output_dir):
    data, out = Path(data_dir).resolve(), Path(output_dir).resolve()
    if "private_gold" in data.parts or "private_gold" in out.parts:
        raise ValueError("private_gold is evaluation-only")
    raw_roots = [data, *(p for p in data.parents if p.name in ("raw", "re_docred"))]
    if any(out == root or out.is_relative_to(root) for root in raw_roots):
        raise ValueError("output directory must be outside raw source data")
    for name in ("input_manifest.json", "dataset_audit.json", "pattern_inventory.json", "environment.json", "audit_report.md"):
        path = out / name
        if path.is_symlink():
            raise ValueError(f"output symlinks are not accepted: {path}")


def environment():
    root = Path(__file__).resolve().parents[1]
    def git(*args):
        run = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
        return {"exit_code": run.returncode, "output": run.stdout.strip()}
    return {"python": sys.version, "executable": sys.executable, "platform": platform.platform(),
            "packages": sorted([{"name": d.metadata["Name"], "version": d.version}
                                for d in importlib.metadata.distributions()], key=lambda d: d["name"].casefold()),
            "command": [sys.executable, *sys.argv],
            "script_sha256": digest(Path(__file__).read_bytes()),
            "git_head": git("rev-parse", "HEAD"),
            "git_status": git("status", "--short"),
            "private_gold_ignore_check": git("check-ignore", "data/private_gold/example.json"),
            "raw_tracked_files": git("ls-files", "data/raw"),
            "gitignore_sha256": digest((root / ".gitignore").read_bytes()) if (root / ".gitignore").exists() else None}


def report(result, inventory):
    lines = ["# Phase 0 dataset audit", "", f"Schema status: **{result['status']}**. Pattern inspection: **{inventory['status']}**.", "",
             "| Split | Documents | Groups | Mentions | Relations | Nonempty evidence | Empty evidence |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for split, s in result["splits"].items():
        c, e = s["counts"], s["evidence_all_relation_objects"]
        lines.append(f"| {split} | {c['documents']} | {c['entity_groups']} | {c['mentions']} | {c['relations']} | {e['nonempty']} | {e['empty']} |")
    lines += ["", f"Diagnostic counts: `{encoded(result['diagnostic_counts'])}`.", "",
              f"Distinct typed patterns observed: {len(inventory['patterns'])}.",
              f"Incomplete documents: {sum(d['status'] == 'INCOMPLETE' for d in inventory['document_runs'])}.", ""]
    for hop in (2, 3):
        items = [p for p in inventory["patterns"] if len(p["relations"]) == hop]
        lines.append(f"- {hop}-hop: {len(items)} typed patterns; {sum(p['structural_paths'] for p in items)} structural paths; "
                     f"{sum(p['all_edges_pointed_occurrence_paths'] for p in items)} relation-occurrence paths with all edges pointed.")
    lines += ["", "Duplicate/overlap locations (zero-based):", ""]
    for kind, locations in result["duplicates"].items():
        lines.append(f"- {kind}: `{encoded(locations)}`")
    lines += ["", "## Entity and relationship suitability", "",
              "| Split | Relation codes | Multi-mention groups | Mixed-type groups | Name/span differences |",
              "|---|---:|---:|---:|---:|"]
    for split, s in result["splits"].items():
        c = s["counts"]
        differences = sum(i["split"] == split and i["code"] == "name_span_text_difference" for i in result["diagnostics"])
        lines.append(f"| {split} | {len(s['relation_codes'])} | {c['multi_mention_groups']} | {c['mixed_type_groups']} | {differences} |")
    lines += ["", "Train/dev descriptive normalized-name collision counts (not candidate labels):", ""]
    for split in ("train", "dev"):
        if split in result["splits"]:
            s = result["splits"][split]["suitability"]
            lines.append(f"- {split}: {s['normalized_names_in_multiple_groups']} name strings occur in multiple groups; "
                         f"{s['normalized_names_across_documents']} occur across documents within that split.")
    lines += ["", "## Interpretation and limits", "",
              "Counts describe annotation structure, not source truth. A nonempty evidence list is a sentence pointer, not verified support. "
              "Empty or absent pointers are missing information, never contradiction.", "",
              "Paths are directed, document-local, exactly 2/3 hops and have distinct vertices. Duplicate typed edges are collapsed for structural counts; "
              "relation-occurrence counts retain multiplicity. Pattern counts are lower bounds if INCOMPLETE. Test is excluded from pattern and name-collision discovery.", "",
              "Different groups/documents are not negative identity labels. Multi-mention groups offer potential controlled-fragmentation material, not natural positive pairs. "
              "No identities, verified answers, semantic path validity, merge harm, risk or performance were inferred.", "",
              "See docs/pilot_feasibility_contract.md for unresolved source, identity, literature and partition decisions. "
              "Phase 1 requires separate student approval. STOP.", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data/raw/re_docred/data"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/phase0"))
    parser.add_argument("--max-extensions-per-document", type=int, default=100_000,
                        help="deterministic computational cap; not a risk threshold")
    args = parser.parse_args(argv)
    try:
        guard_paths(args.data_dir, args.output_dir)
        manifest, result, inventory = audit(args.data_dir, args.max_extensions_per_document)
        # Inventory filenames only; read only the three explicitly permitted JSON files.
        manifest["raw_directory_inventory"] = sorted(p.relative_to(args.data_dir.parent).as_posix()
                                                     for p in args.data_dir.parent.rglob("*") if p.is_file())
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, value in (("input_manifest", manifest), ("dataset_audit", result),
                            ("pattern_inventory", inventory), ("environment", environment())):
            (args.output_dir / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        (args.output_dir / "audit_report.md").write_text(report(result, inventory), encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"Audit failed: {exc}", file=sys.stderr)
        return 1
    print(f"Schema: {result['status']}; patterns: {inventory['status']}; outputs: {args.output_dir}")
    print(f"Diagnostics: {encoded(result['diagnostic_counts'])}")
    return 0 if result["status"] == "VALID" and inventory["status"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
