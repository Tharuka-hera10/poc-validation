"""Phase 2: unlabelled train candidates and preparation-only reviewer packages."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from uuid import uuid4

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.audit_dataset import SPLITS, digest, encoded, load_json
from scripts.build_graph import (build_split_graph, load_split, require, source_path,
                                 validate_graph_provenance, write_latest)
from scripts.prepare_annotation_worklist import make_review_worklist, worklist_csv


VERSION = "phase2-candidates-v1"
ROOT = Path(__file__).resolve().parents[1]
TARGETS = {"sparse_context": 4, "different_name_abbreviation": 4,
           "challenging_name_collision": 8, "compatible_name_context": 8}
RULES = {1: "exact_normalized_alias_v1", 2: "exact_initialism_v1"}
POLICY = {"version": VERSION, "discovery_split": "train", "selection_types": ["LOC", "ORG", "PER"],
          "targets_in_priority_order": list(TARGETS.items()),
          "normalization": "casefold then collapse whitespace; preserve originals",
          "initialism": "Unicode \\w+ tokens; single token equals first characters of at least two tokens; no stopword removal",
          "ordering": "ascending numeric document/entity pair indices within category",
          "diversity": "no reused endpoint or matching name/initialism key",
          "controlled_fragmentation": "FEASIBILITY_ONLY; no fragments, parent maps or edge allocation"}


def name_forms(group):
    """Derive auditable blocking keys without rewriting any source mention."""
    aliases = {" ".join(m["name"].casefold().split()) for m in group} - {""}
    shorts, initials = set(), set()
    for alias in aliases:
        tokens = re.findall(r"\w+", alias)
        if len(tokens) == 1:
            shorts.add(tokens[0])
        elif len(tokens) > 1:
            initials.add("".join(t[0] for t in tokens))
    return aliases, shorts, initials


def entity_records(source, graph):
    """Index permitted names, types and occurrence-aware context for discovery."""
    require(source.split == "train", "Candidate discovery accepts train only; dev/test are forbidden")
    validate_graph_provenance(graph, source, require_full_split=True)
    records = {}
    for di, doc in enumerate(source.documents):
        for ei, group in enumerate(doc["vertexSet"]):
            aliases, shorts, initials = name_forms(group)
            nid = f"train:{di}:{ei}"
            records[di, ei] = {"entity_id": nid, "aliases": aliases, "shorts": shorts,
                               "initials": initials, "original_names": sorted({m["name"] for m in group}),
                               "types": tuple(sorted({m["type"] for m in group})),
                               "signature": set(), "incident_relations": 0,
                               "evidence_pointer_counts": {"nonempty": 0, "empty": 0, "absent": 0},
                               "provenance": {k: graph.nodes[nid]["provenance"][k] for k in
                                              ("split", "document_index", "entity_index", "source_sha256", "document_sha256")}}
        for label in doc["labels"]:
            h, t = (records[di, label[k]] for k in ("h", "t"))
            h["signature"].add(("OUT", label["r"], t["types"]))
            t["signature"].add(("IN", label["r"], h["types"]))
            kind = "absent" if "evidence" not in label else "nonempty" if label["evidence"] else "empty"
            for ei in set((label["h"], label["t"])):
                records[di, ei]["incident_relations"] += 1
                records[di, ei]["evidence_pointer_counts"][kind] += 1
    return records


def discover_candidates(records):
    """Enumerate exact blocks; bit flags retain all reasons without exporting the pool."""
    names, shorts, initials = (defaultdict(set) for _ in range(3))
    for ref, record in records.items():
        require(record["entity_id"].startswith("train:"), "Non-train record in discovery")
        for key, index in (("aliases", names), ("shorts", shorts), ("initials", initials)):
            for value in record[key]:
                index[value].add(ref)
    pairs = {}
    for key in sorted(names):
        for pair in combinations(sorted(names[key]), 2):
            pairs[pair] = pairs.get(pair, 0) | 1
    for key in sorted(shorts.keys() & initials.keys()):
        for left in sorted(shorts[key]):
            for right in sorted(initials[key]):
                if left != right:
                    pair = tuple(sorted((left, right)))
                    pairs[pair] = pairs.get(pair, 0) | 2
    return pairs


def matching_keys(left, right):
    """Share one namespace for aliases and initialisms to avoid repeated hubs."""
    return (left["aliases"] & right["aliases"]) | (left["shorts"] & right["initials"]) | (right["shorts"] & left["initials"])


def select_review_candidates(pairs, records):
    """Apply the approved categories and diversity rules without outcome-based tuning."""
    buckets = {category: [] for category in TARGETS}
    excluded = 0
    for pair in sorted(pairs):
        left, right = (records[ref] for ref in pair)
        if any(len(r["types"]) != 1 or r["types"][0] not in POLICY["selection_types"] for r in (left, right)):
            excluded += 1
            continue
        if not left["incident_relations"] or not right["incident_relations"]:
            category = "sparse_context"
        elif pairs[pair] & 1:
            category = ("compatible_name_context" if left["types"] == right["types"]
                        and left["signature"] == right["signature"] else "challenging_name_collision")
        else:
            category = "different_name_abbreviation"
        buckets[category].append(pair)
    selected, used_entities, used_keys = [], set(), set()
    stats = {}
    for category, target in TARGETS.items():
        count = skipped = 0
        for pair in buckets[category]:
            keys = matching_keys(*(records[r] for r in pair))
            if used_entities.intersection(pair) or used_keys.intersection(keys):
                skipped += 1
                continue
            selected.append((pair, category, pairs[pair]))
            used_entities.update(pair)
            used_keys.update(keys)
            count += 1
            if count == target:
                break
        stats[category] = {"available": len(buckets[category]), "target": target, "selected": count,
                           "diversity_skipped_before_quota": skipped, "shortfall": target - count}
    return selected, {"categories": stats, "selection_type_exclusions": excluded}


def candidate_id(fingerprint, left, right):
    """Bind identity of a proposed pair to its source snapshot and frozen generator."""
    return "cand_" + digest(encoded([VERSION, fingerprint, left, right]).encode("utf-8"))


def make_candidate_export(selected, records, fingerprint):
    """Allowlist inference inputs; never copy arbitrary annotation metadata."""
    rows = []
    for pair, _, mask in selected:
        left, right = (records[ref] for ref in pair)
        row = {"candidate_id": candidate_id(fingerprint, left["entity_id"], right["entity_id"]),
               "left_entity_id": left["entity_id"], "right_entity_id": right["entity_id"],
               "creation_mode": "naturally_observed", "selection_rule_ids": [v for bit, v in RULES.items() if mask & bit],
               "dataset_split": "train", "candidate_generation_version": VERSION,
               "review_status": "UNREVIEWED", "permitted_name_features": {}, "permitted_type_features": {},
               "permitted_context_features": {}, "provenance_reference": {}}
        for side, record in (("left", left), ("right", right)):
            row["permitted_name_features"][side] = {"original_names": record["original_names"],
                                                    "normalized_aliases": sorted(record["aliases"])}
            row["permitted_type_features"][side] = list(record["types"])
            row["permitted_context_features"][side] = {
                "relation_signatures": [{"direction": d, "relation": r, "neighbour_types": list(t)}
                                        for d, r, t in sorted(record["signature"])],
                "incident_relations": record["incident_relations"],
                "evidence_pointer_counts": dict(record["evidence_pointer_counts"])}
            row["provenance_reference"][side] = dict(record["provenance"])
        rows.append(row)
    result = {"format_version": 1, "candidate_generation_version": VERSION,
              "source_sha256": fingerprint, "candidates": rows}
    validate_candidate_export(result)
    return result


def validate_candidate_export(payload):
    """Reject unknown fields at every level, including planted private metadata."""
    def fields(value, keys):
        require(type(value) is dict and set(value) == set(keys), f"Candidate export fields must be exactly {sorted(keys)}")

    def strings(value):
        require(type(value) is list and all(type(v) is str for v in value), "Expected string list")

    fields(payload, ("format_version", "candidate_generation_version", "source_sha256", "candidates"))
    require(type(payload["format_version"]) is int and payload["format_version"] == 1
            and payload["candidate_generation_version"] == VERSION, "Unsupported candidate export version")
    require(type(payload["source_sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", payload["source_sha256"]), "Invalid source hash")
    require(type(payload["candidates"]) is list, "Expected candidate list")
    seen = set()
    for row in payload["candidates"]:
        fields(row, ("candidate_id", "left_entity_id", "right_entity_id", "creation_mode", "selection_rule_ids",
                     "dataset_split", "candidate_generation_version", "review_status", "permitted_name_features",
                     "permitted_type_features", "permitted_context_features", "provenance_reference"))
        require(row["creation_mode"] == "naturally_observed" and row["dataset_split"] == "train"
                and row["candidate_generation_version"] == VERSION and row["review_status"] == "UNREVIEWED", "Invalid candidate metadata")
        refs = []
        for side in ("left", "right"):
            nid = row[f"{side}_entity_id"]
            require(type(nid) is str and re.fullmatch(r"train:\d+:\d+", nid), "Invalid train endpoint")
            refs.append(tuple(map(int, nid.split(":")[1:])))
        require(refs[0] < refs[1], "Pair endpoints must be distinct and canonically ordered")
        cid = candidate_id(payload["source_sha256"], row["left_entity_id"], row["right_entity_id"])
        require(row["candidate_id"] == cid and cid not in seen, "Duplicate or invalid candidate ID")
        seen.add(cid)
        strings(row["selection_rule_ids"])
        require(bool(row["selection_rule_ids"]) and len(set(row["selection_rule_ids"])) == len(row["selection_rule_ids"])
                and set(row["selection_rule_ids"]) <= set(RULES.values()), "Unknown or duplicate selection rule")
        for key in ("permitted_name_features", "permitted_type_features", "permitted_context_features", "provenance_reference"):
            fields(row[key], ("left", "right"))
        for side, ref in zip(("left", "right"), refs):
            names = row["permitted_name_features"][side]
            fields(names, ("original_names", "normalized_aliases"))
            for value in names.values():
                strings(value)
            strings(row["permitted_type_features"][side])
            context = row["permitted_context_features"][side]
            fields(context, ("relation_signatures", "incident_relations", "evidence_pointer_counts"))
            require(type(context["incident_relations"]) is int and context["incident_relations"] >= 0, "Invalid incident count")
            fields(context["evidence_pointer_counts"], ("absent", "empty", "nonempty"))
            require(all(type(v) is int and v >= 0 for v in context["evidence_pointer_counts"].values())
                    and sum(context["evidence_pointer_counts"].values()) == context["incident_relations"], "Invalid pointer counts")
            require(type(context["relation_signatures"]) is list, "Expected signature list")
            for sig in context["relation_signatures"]:
                fields(sig, ("direction", "relation", "neighbour_types"))
                require(sig["direction"] in ("IN", "OUT") and type(sig["relation"]) is str, "Invalid relation signature")
                strings(sig["neighbour_types"])
            provenance = row["provenance_reference"][side]
            fields(provenance, ("split", "document_index", "entity_index", "source_sha256", "document_sha256"))
            require(provenance["split"] == "train" and provenance["source_sha256"] == payload["source_sha256"]
                    and all(type(provenance[k]) is int for k in ("document_index", "entity_index"))
                    and (provenance["document_index"], provenance["entity_index"]) == ref
                    and type(provenance["document_sha256"]) is str
                    and re.fullmatch(r"[0-9a-f]{64}", provenance["document_sha256"]), "Invalid candidate provenance")


def controlled_feasibility(source, records):
    """Count resources and pointer ambiguities without creating or allocating fragments."""
    require(source.split == "train", "Controlled feasibility accepts train only")
    groups, locations = Counter(), Counter()
    for di, document in enumerate(source.documents):
        eligible = {}
        for ei, group in enumerate(document["vertexSet"]):
            if len(group) < 2:
                continue
            eligible[ei] = {m["sent_id"] for m in group}
            groups["multi_mention"] += 1
            groups["distinct_normalized_aliases"] += len(records[di, ei]["aliases"]) > 1
            groups["multiple_mention_sentences"] += len(eligible[ei]) > 1
            groups["no_incident_relations"] += records[di, ei]["incident_relations"] == 0
        for label in document["labels"]:
            for ei in set((label["h"], label["t"])) & eligible.keys():
                if "evidence" not in label:
                    state = "absent_pointers"
                elif not label["evidence"]:
                    state = "empty_pointers"
                else:
                    n = len(eligible[ei].intersection(label["evidence"]))
                    state = "unique_sentence_location_only" if n == 1 else "multiple_sentence_locations" if n > 1 else "no_matching_mention_sentence"
                locations[state] += 1
    return {"status": "FEASIBILITY_ONLY", "groups": dict(sorted(groups.items())),
            "incident_entity_relation_location_counts": dict(sorted(locations.items())),
            "fragments_created": 0, "controlled_candidate_pairs": 0, "edge_allocations": 0,
            "interpretation": "Counts concern original entity/relation incidences, not assigned edges. Unique pointer location is not verified attribution."}


def overlap_policy(train, dev, selected_rows):
    """Group exact source tokens without using dev for candidate design."""
    require(train.split == "train" and dev.split == "dev", "Overlap check requires train and dev")
    by_text = defaultdict(list)
    for source in (train, dev):
        for di, doc in enumerate(source.documents):
            by_text[digest(encoded(doc["sents"]).encode("utf-8"))].append({"split": source.split, "document_index": di})
    groups = [{"sentence_content_sha256": h, "locations": refs} for h, refs in sorted(by_text.items()) if len(refs) > 1]
    cross = [g for g in groups if {r["split"] for r in g["locations"]} == {"train", "dev"}]
    train_indices = {r["document_index"] for g in cross for r in g["locations"] if r["split"] == "train"}
    excluded = sorted({r["document_index"] for g in cross for r in g["locations"] if r["split"] == "dev"})
    return {"exact_text_groups": groups, "dev_evaluation_excluded_document_indices": excluded,
            "affected_selected_candidate_ids": [r["candidate_id"] for r in selected_rows
                if any(p["document_index"] in train_indices for p in r["provenance_reference"].values())],
            "policy": "Train development only; exclude train-duplicate dev documents from later dev evaluation; keep exact-text groups and shared selected source documents together in later partitions. Raw splits unchanged.",
            "limitation": "No paraphrase detection or verified real-world identity-disjoint partition guarantee."}


def verify_sources(data_dir, manifest):
    """Hash all splits for integrity; test bytes are never parsed for discovery."""
    require(type(manifest) is dict and type(manifest.get("files")) is list, "Malformed Phase 0 manifest")
    hashes = {}
    for split in SPLITS:
        entries = [e for e in manifest["files"] if type(e) is dict and e.get("split") == split]
        require(len(entries) == 1, f"Manifest must contain exactly one {split} entry")
        entry = entries[0]
        raw = source_path(Path(data_dir) / f"{split}_revised.json").read_bytes()
        sha = digest(raw)
        require(sha == entry["sha256"] == entry["sha256_after"] and len(raw) == entry["bytes"], f"Source fingerprint mismatch: {split}")
        hashes[split] = sha
    return hashes


def phase1_baseline():
    """Verify the completed Phase 1 reference instead of trusting a stale summary."""
    root = ROOT / "results" / "phase1"
    latest = load_json(source_path(root / "latest_run.json").read_bytes())
    require(latest["status"] == "PASS", "Phase 1 latest attempt is not PASS")
    directory = (root / latest["run_directory"]).resolve()
    require(directory.is_relative_to((root / "runs").resolve()), "Invalid Phase 1 run reference")
    names = {"graph_summary.json", "provenance_demo.json", "run_manifest.json", "phase1_report.md"}
    require(set(latest["artifact_sha256"]) == names, "Incomplete Phase 1 artifact references")
    for name, sha in latest["artifact_sha256"].items():
        require(digest(source_path(directory / name).read_bytes()) == sha, f"Phase 1 artifact mismatch: {name}")
    run = load_json(source_path(directory / "run_manifest.json").read_bytes())
    for name in ("audit_dataset.py", "build_graph.py"):
        require(digest((ROOT / "scripts" / name).read_bytes()) == run["implementation_sha256"][name], f"Phase 1 implementation mismatch: {name}")
    return {"latest_status_sha256": digest((root / "latest_run.json").read_bytes()),
            "artifact_sha256": latest["artifact_sha256"]}


def check_destinations(data_dir, manifest, output_dir, review_dir):
    """Allow only new result packages and ignored reviewer writes, never source writes."""
    out, review = output_dir.resolve(), review_dir.resolve()
    protected = [ROOT / "data" / "raw", ROOT / "results" / "phase0", ROOT / "results" / "phase1",
                 ROOT / "scripts", ROOT / "tests", ROOT / "docs", ROOT / ".git",
                 Path(data_dir).resolve(), Path(manifest).resolve().parent]
    protected += [p for p in Path(data_dir).resolve().parents if p.name in ("raw", "re_docred")]
    require(out != ROOT and "private_gold" not in out.parts
            and not any(out == p or out.is_relative_to(p) for p in protected), "Protected public output location")
    private_root = ROOT / "data" / "private_gold"
    require(private_root.resolve() == private_root and not private_root.is_symlink() and review.is_relative_to(private_root.resolve())
            and review != private_root.resolve(), "Reviewer output must be below data/private_gold")
    for directory in (output_dir, review_dir):
        require(not directory.is_symlink(), f"Output symlink is forbidden: {directory}")
        for name in ("latest_run.json", "runs"):
            require(not (directory / name).is_symlink(), f"Output control symlink is forbidden: {name}")
    for parent in review_dir.parents:
        if parent == private_root:
            break
        require(not parent.is_symlink(), "Reviewer parent symlink is forbidden")
    ignored = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "--quiet", str(review / "probe.json")],
                             capture_output=True, check=False)
    require(ignored.returncode == 0, "Private reviewer directory is not Git-ignored; no output written")


def publish_package(root, run_id, files):
    """Publish new files together; hash write buffers so private files are never read."""
    root.mkdir(parents=True, exist_ok=True)
    pending = Path(tempfile.mkdtemp(prefix=f".pending-{run_id}-", dir=root))
    hashes = {}
    for name, content in files.items():
        (pending / name).write_text(content, encoding="utf-8")
        hashes[name] = digest(content.encode("utf-8"))
    runs = root / "runs"
    require(not runs.is_symlink(), "Run directory symlink is forbidden")
    runs.mkdir(exist_ok=True)
    destination = runs / run_id
    require(not destination.exists(), "Refusing to replace an earlier run")
    pending.rename(destination)
    return destination, hashes


def json_text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def reports(inventory):
    """Render actual preparation counts without source excerpts or identity claims."""
    counts = inventory["discovery"]
    lines = ["# GIR-ER Phase 2 execution report", "", "Technical status: PASS; identity annotation NOT PERFORMED.", "",
             f"Generation version: `{VERSION}`. Train only; dev used only for overlap/schema checking. Test hashed only.", "",
             f"Discovered unordered pairs: {counts['unique_pairs']:,}; selected unlabelled review pairs: {inventory['selected_count']}.",
             f"Exact-name pairs: {counts['exact_name_pairs']:,}; initialism pairs: {counts['initialism_pairs']:,}; pairs satisfying both: {counts['both_rules']:,}.", "",
             "| Selection category | Available | Target | Selected | Diversity skips before quota | Shortfall |",
             "|---|---:|---:|---:|---:|---:|"]
    for name, c in inventory["selection"]["categories"].items():
        lines.append(f"| {name} | {c['available']} | {c['target']} | {c['selected']} | {c['diversity_skipped_before_quota']} | {c['shortfall']} |")
    lines += ["", f"Pairs excluded from selection by type policy: {inventory['selection']['selection_type_exclusions']:,} (retained in discovery counts).",
              f"Train graph reconciliation: `{encoded(inventory['train_graph_validation'])}`.",
              f"Selected evidence availability: `{encoded(inventory['review_evidence'])}`.",
              f"Selected pair source scopes: `{encoded(inventory['selected_pair_scopes'])}`.",
              f"Dev evaluation exclusions: `{inventory['partition_policy']['dev_evaluation_excluded_document_indices']}`. Raw splits unchanged.", "",
              "## Interpretation and limitations", "",
              "Every selected pair is naturally observed and UNREVIEWED. Categories describe selection signals, not positive or negative labels. "
              "Mention sentences are inspectable; identity-evidence sufficiency remains NOT_ASSESSED. Missing relation pointers do not mean contradiction.", "",
              "Controlled cases are feasibility-only: no fragments, parent maps, controlled candidate pairs or edge allocations were produced. "
              "Unique pointer/mention sentence intersection is not verified relation attribution. An actual fragmentation policy needs separate student approval.", "",
              "This exact-block pilot has unknown candidate recall and identity balance. Source-order, type and diversity restrictions bias the sample; "
              "shared documents and real-world entities can create dependencies. Exact-text grouping does not detect paraphrases or establish entity-disjoint evaluation.", "",
              "Corpus acquisition/licence, release authenticity and relation meanings remain unverified. Reviewer text and blank annotations stay private. "
              "Generated candidate names are local source-derived inputs, not cleared for redistribution. Separate supervisor feedback/proposal/literature files are unavailable; "
              "the master context is a summary, not authenticated supervisor approval.", "",
              "LACE/ASPEN/ASPEN+ boundaries remain governing. Candidate preparation is infrastructure. GIR-ER's incremental value over an equally informed matcher is unvalidated; "
              "zero or negative future benefit remains possible. No identity metrics, QA answers, merge effects or risk scores were computed.", "",
              "## Reproduce and review", "", "```bash",
              ".venv/bin/python -B scripts/candidate_discovery.py --data-dir data/raw/re_docred/data --manifest results/phase0/input_manifest.json --output-dir results/phase2 --review-dir data/private_gold/phase2",
              ".venv/bin/python -B -m pytest -q -p no:cacheprovider", "```", "",
              "Check ../../latest_run.json and artifact hashes. Earlier completed runs are historical. RUNNING/FAILED is not latest success. "
              "The manifest records actual timing, input/code/rule hashes and invocation; deterministic outputs omit run IDs and timing.", "",
              "AI-assisted code and tests require student understanding and independent review. Human decisions require the annotation guide. "
              "STOP: no Phase 3, fragmentation, merges, counterfactual analysis, scoring, baselines or effectiveness claims.", ""]
    feasibility = ["# Phase 2 candidate feasibility", "",
                   f"Natural discovery pool: {counts['unique_pairs']:,} unique unlabelled train pairs. Selected for review: {inventory['selected_count']}.", "",
                   f"Controlled resources and pointer ambiguities: `{encoded(inventory['controlled_feasibility'])}`.", "",
                   "Proposed future policy: bundle original mentions by sentence; require separately approved, source-checked endpoint attribution. "
                   "Empty/absent pointers, zero or multiple compatible sentence bundles, and unclear semantic links remain unresolved. "
                   "Never copy every original relation to every fragment. No proposed allocation is executed here.", "",
                   "The worklist supports identity review and exposes relation context. It does not yet establish beneficial/harmful merge cases, "
                   "interpretable multi-hop workloads or verified answers. Natural cross-document merges may have no compositional effect. "
                   "Those limitations can lead to an inadequate pilot or negative GIR-ER result and must be reported.", "",
                   "Next student decisions: perform/review identity annotation, retain UNKNOWN where needed, decide whether controlled cases are necessary, "
                   "approve any actual fragmentation policy, and approve separate QA/evaluation methodology before later phases. "
                   "No private annotation may become a runtime feature; all future comparisons require equal permitted evidence.", ""]
    return "\n".join(lines), "\n".join(feasibility)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data/raw/re_docred/data"))
    parser.add_argument("--manifest", type=Path, default=Path("results/phase0/input_manifest.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/phase2"))
    parser.add_argument("--review-dir", type=Path, default=Path("data/private_gold/phase2"))
    args = parser.parse_args(argv)
    attempt = None
    stage = "output_preflight"
    started = time.perf_counter()
    try:
        check_destinations(args.data_dir, args.manifest, args.output_dir, args.review_dir)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        attempt = {"format_version": 1, "run_id": uuid4().hex, "status": "RUNNING", "run_directory": None, "error": None}
        stage = "status_initialization"
        write_latest(args.output_dir, attempt)
        stage = "verify_baselines_and_sources"
        manifest = load_json(source_path(args.manifest).read_bytes())
        fingerprints = verify_sources(args.data_dir, manifest)
        baseline = phase1_baseline()
        audit = load_json(source_path(args.manifest.parent / "dataset_audit.json").read_bytes())
        require(audit["status"] == "VALID" and audit["input_fingerprints"] == fingerprints, "Phase 0 audit does not match sources")
        stage = "construct_train_graph"
        train = load_split(args.data_dir, "train", manifest)
        graph = build_split_graph(train)
        counts = validate_graph_provenance(graph, train, require_full_split=True)
        require(counts["nodes"] == audit["splits"]["train"]["counts"]["entity_groups"]
                and counts["edges"] == audit["splits"]["train"]["counts"]["relations"], "Phase 0 train reconciliation failed")
        stage = "discover_and_select"
        records = entity_records(train, graph)
        pairs = discover_candidates(records)
        selected, selection = select_review_candidates(pairs, records)
        export = make_candidate_export(selected, records, train.sha256)
        controlled = controlled_feasibility(train, records)
        stage = "overlap_check"
        dev = load_split(args.data_dir, "dev", manifest)
        partition = overlap_policy(train, dev, export["candidates"])
        observed = sorted(encoded(g["locations"]) for g in partition["exact_text_groups"])
        expected = sorted(encoded(refs) for group in audit["duplicates"]["sentence_content"]
                          if len(refs := [r for r in group if r["split"] in ("train", "dev")]) > 1)
        require(observed == expected, "Train/dev overlap reconciliation with Phase 0 failed")
        stage = "prepare_reviewer_evidence"
        dossier = make_review_worklist(export["candidates"], train, graph)
        selected_meta = [{"candidate_id": row["candidate_id"], "selection_category": category,
                          "left_entity_id": row["left_entity_id"], "right_entity_id": row["right_entity_id"]}
                         for row, (_, category, _) in zip(export["candidates"], selected)]
        endpoints = [e for c in dossier["candidates"] for e in c["endpoints"].values()]
        inventory = {"format_version": 1, "status": "PASS", "policy": POLICY,
                     "input_fingerprints": fingerprints, "train_graph_validation": counts,
                     "discovery": {"unique_pairs": len(pairs), "exact_name_pairs": sum(bool(m & 1) for m in pairs.values()),
                                   "initialism_pairs": sum(bool(m & 2) for m in pairs.values()), "both_rules": sum(m == 3 for m in pairs.values()),
                                   "within_document_pairs": sum(a[0] == b[0] for a, b in pairs)},
                     "selection": selection, "selected_count": len(selected), "selected_candidates": selected_meta,
                     "selected_pair_scopes": dict(Counter("within_document" if a[0] == b[0] else "cross_document" for (a, b), _, _ in selected)),
                     "controlled_feasibility": controlled, "partition_policy": partition,
                     "review_evidence": {"candidates_with_inspectable_mention_tokens": len(selected),
                         "identity_sufficiency_not_assessed": len(selected),
                         "endpoints_without_incident_relations": sum(e["context_flags"]["no_incident_relations"] for e in endpoints),
                         "endpoints_without_nonempty_incident_pointers": sum(e["context_flags"]["no_nonempty_incident_pointers"] for e in endpoints),
                         "incident_pointer_counts": {k: sum(e["evidence_pointer_availability"][k] for e in endpoints) for k in ("nonempty", "empty", "absent")}}}
        stage = "final_source_and_graph_integrity"
        validate_graph_provenance(graph, train, require_full_split=True)
        require(verify_sources(args.data_dir, manifest) == fingerprints, "Source changed during Phase 2")
        report, feasibility = reports(inventory)
        runtime = time.perf_counter() - started
        versions = {"format_version": 1, "generation_version": VERSION, "policy_sha256": digest(encoded(POLICY).encode()),
                    "command": sys.orig_argv if argv is None else [sys.executable, str(Path(__file__)), *map(str, argv)],
                    "python": sys.version, "runtime_seconds_before_publication": runtime,
                    "source_sha256_before": fingerprints, "source_sha256_after": verify_sources(args.data_dir, manifest),
                    "phase0_manifest_sha256": digest(args.manifest.read_bytes()),
                    "phase0_audit_sha256": digest((args.manifest.parent / "dataset_audit.json").read_bytes()),
                    "phase1_reference": baseline,
                    "implementation_sha256": {n: digest((ROOT / "scripts" / n).read_bytes()) for n in
                        ("candidate_discovery.py", "prepare_annotation_worklist.py", "audit_dataset.py", "build_graph.py")},
                    "research_context_available": [p.name for p in sorted((ROOT / "docs" / "research_context").glob("*.md"))],
                    "private_annotations_read": False, "annotation_performed": False}
        stage = "publish_private_package"
        private_dir, private_hashes = publish_package(args.review_dir, attempt["run_id"],
                    {"review_dossier.json": json_text(dossier), "review_worklist.csv": worklist_csv(dossier)})
        stage = "publish_candidate_package"
        destination, hashes = publish_package(args.output_dir, attempt["run_id"], {
            "candidates_train.json": json_text(export), "candidate_inventory.json": json_text(inventory),
            "candidate_feasibility_report.md": feasibility, "phase2_report.md": report, "run_manifest.json": json_text(versions)})
        stage = "success_status_publication"
        write_latest(args.output_dir, {**attempt, "status": "PASS", "run_directory": destination.relative_to(args.output_dir).as_posix(),
                                     "artifact_sha256": hashes, "review_directory": str(private_dir), "review_artifact_sha256": private_hashes})
    except (ValueError, OSError, KeyError, TypeError, IndexError) as exc:
        if attempt is not None and stage != "status_initialization":
            try:
                write_latest(args.output_dir, {**attempt, "status": "FAILED", "error": {"stage": stage, "type": type(exc).__name__, "reason": str(exc)}})
            except OSError as status_exc:
                print(f"Could not record failed attempt: {status_exc}; no new PASS established", file=sys.stderr)
        else:
            print("No new attempt recorded; output preflight/status initialization failed", file=sys.stderr)
        print(f"Phase 2 failed at {stage}: {exc}", file=sys.stderr)
        return 1
    print(f"Phase 2 PASS: {len(pairs)} discovered pairs; {len(selected)} unlabelled natural review cases; controlled pairs 0")
    print(f"Train graph: {counts['nodes']} nodes / {counts['edges']} edges individually reconciled; all source hashes unchanged")
    print(f"Outputs: {destination}; private reviewer package: {private_dir}; preparation seconds: {runtime:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
