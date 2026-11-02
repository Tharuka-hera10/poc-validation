"""Authored graph-theoretic fixtures are not empirical semantic QA references."""

from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

import networkx as nx
import pytest

from scripts import query_workload as q
from scripts.audit_dataset import digest, encoded
from scripts.build_graph import SourceSplit, build_split_graph, validate_graph_provenance


def fixture(labels=None, split="train", names=None):
    names = names or ["A", "B", "C", "D", "E", "Isolate"]
    doc = {"title": "AUTHORED QA FIXTURE", "sents": [names],
           "vertexSet": [[{"name": name, "type": "ORG" if i == 0 else "LOC", "sent_id": 0, "pos": [i, i+1]}]
                         for i, name in enumerate(names)],
           "labels": labels if labels is not None else [
               {"h": 0, "t": 1, "r": "R1", "evidence": [0, 0]},
               {"h": 1, "t": 2, "r": "R2", "evidence": []},
               {"h": 2, "t": 3, "r": "R3"}]}
    source = SourceSplit(split, [doc], digest(encoded([doc]).encode()), [])
    graph = build_split_graph(source)
    validate_graph_provenance(graph, source, require_full_split=True)
    return source, graph


def reidentify(query):
    query["query_id"] = "query_" + digest(encoded({k:v for k,v in query.items() if k != "query_id"}).encode())
    return query


def test_exact_two_and_three_hops_and_zero_answers_preserve_input():
    source, graph = fixture()
    before, docs = deepcopy(graph), deepcopy(source.documents)
    two = q.evaluate_query(graph, q.make_query(graph, "train:0:0", ["R1", "R2"]))
    three = q.evaluate_query(graph, q.make_query(graph, "train:0:0", ["R1", "R2", "R3"]))
    assert two["answer_ids"] == ["train:0:2"] and three["answer_ids"] == ["train:0:3"]
    assert two["paths"][0]["edge_occurrences"][0]["evidence"] == [0, 0]
    assert two["paths"][0]["edge_occurrences"][1]["evidence_availability"] == "empty"
    assert "evidence" not in three["paths"][0]["edge_occurrences"][-1]
    for anchor, rels in [("train:0:2", ["R2", "R1"]), ("train:0:0", ["R2", "R1"]), ("train:0:5", ["R1", "R2"])]:
        result = q.evaluate_query(graph, q.make_query(graph, anchor, rels))
        assert result["status"] == "COMPLETE" and result["answer_ids"] == [] and result["paths"] == []
    assert nx.utils.graphs_equal(graph, before) and source.documents == docs


def test_occurrence_combinations_parallel_relations_and_unique_answer_sets():
    source, graph = fixture()
    labels = source.documents[0]["labels"]
    labels += [deepcopy(labels[0]), deepcopy(labels[1]), {"h": 0,"t": 1,"r":"OTHER","evidence":[]}]
    graph = build_split_graph(source)
    result = q.evaluate_query(graph, q.make_query(graph,"train:0:0",["R1","R2"]))
    assert result["answer_ids"] == ["train:0:2"] and len(result["paths"]) == 4
    assert len({tuple(e["edge_key"] for e in p["edge_occurrences"]) for p in result["paths"]}) == 4
    assert len(q.evaluate_query(graph,q.make_query(graph,"train:0:0",["OTHER","R2"]))["paths"]) == 2


def test_multiple_routes_and_distinct_answers():
    labels=[{"h":h,"t":t,"r":r,"evidence":[]} for h,t,r in [(0,1,"X"),(0,3,"X"),(1,2,"Y"),(3,2,"Y"),(1,4,"Y")]]
    _, graph=fixture(labels)
    result=q.evaluate_query(graph,q.make_query(graph,"train:0:0",["X","Y"]))
    assert result["answer_ids"]==["train:0:2","train:0:4"] and len(result["paths"])==3


def test_type_constraints_intersection_including_mixed_source_types():
    source,graph=fixture()
    extra=deepcopy(source.documents[0]["vertexSet"][1][0]);extra["type"]="ORG"
    source.documents[0]["vertexSet"][1].append(extra)
    graph=build_split_graph(source)
    assert q.evaluate_query(graph,q.make_query(graph,"train:0:0",["R1","R2"],[["ORG"],["ORG"],["LOC"]]))["answer_ids"]==["train:0:2"]
    assert not q.evaluate_query(graph,q.make_query(graph,"train:0:0",["R1","R2"],[["LOC"],None,None]))["answer_ids"]


def test_self_loops_and_repeated_vertices_are_retained_but_excluded_explicitly():
    source,_=fixture()
    source.documents[0]["labels"] += [{"h":0,"t":0,"r":"R1","evidence":[]},{"h":1,"t":0,"r":"R2","evidence":[]}]
    graph=build_split_graph(source)
    result=q.evaluate_query(graph,q.make_query(graph,"train:0:0",["R1","R2"]))
    assert result["answer_ids"]==["train:0:2"]
    assert result["diagnostics"]["excluded_repeated_vertex_extensions"]==2
    assert result["diagnostics"]["excluded_self_loop_extensions"]==1 and graph.has_edge("train:0:0","train:0:0")


def test_limit_and_exact_budget_boundary_are_not_confused():
    _,graph=fixture()
    partial=q.evaluate_query(graph,q.make_query(graph,"train:0:0",["R1","R2"],max_extensions=1))
    assert partial["status"]=="INCOMPLETE" and partial["answer_ids"]==[]
    complete=q.evaluate_query(graph,q.make_query(graph,"train:0:0",["R1","R2"],max_extensions=2))
    assert complete["status"]=="COMPLETE" and complete["answer_ids"]==["train:0:2"]
    _,inv=q.discover_workload(graph,set(),limit=1)
    assert inv["status"]=="INCOMPLETE"


@pytest.mark.parametrize("change",[
    lambda x:x.update(hop_count=True), lambda x:x.update(path_policy="walk"),
    lambda x:x.update(max_extensions=False),lambda x:x.update(type_constraints=[None]),
    lambda x:x.update(type_constraints=[None,{"gold_label":True},None]),
    lambda x:x.update(relations=["R1"]),lambda x:x.update(dataset_split="dev"),
    lambda x:x.update(same_entity=True),lambda x:x["anchor_provenance"].update(gold_answer="hidden"),
])
def test_invalid_query_fields_and_private_injection(change):
    _,g=fixture();query=q.make_query(g,"train:0:0",["R1","R2"]);change(query);reidentify(query)
    with pytest.raises(ValueError):q.evaluate_query(g,query)


def test_missing_anchor_wrong_fingerprint_and_malformed_edge_provenance():
    _,g=fixture()
    with pytest.raises(ValueError,match="Missing"):q.make_query(g,"train:0:99",["R1","R2"])
    query=q.make_query(g,"train:0:0",["R1","R2"]);query["source_sha256"]="0"*64;query["anchor_provenance"]["source_sha256"]="0"*64;reidentify(query)
    with pytest.raises(ValueError,match="fingerprint"):q.evaluate_query(g,query)
    g.edges["train:0:0","train:0:1","train:0:0"]["provenance"]["label_index"]=True
    with pytest.raises(ValueError,match="provenance"):q.evaluate_query(g,q.make_query(g,"train:0:0",["R1","R2"]))


@pytest.mark.parametrize("location",["result","path","occurrence","provenance","diagnostics"])
def test_nested_result_allowlists(location):
    _,g=fixture();query=q.make_query(g,"train:0:0",["R1","R2"]);result=q.evaluate_query(g,query)
    targets={"result":result,"path":result["paths"][0],"occurrence":result["paths"][0]["edge_occurrences"][0],
             "provenance":result["paths"][0]["edge_occurrences"][0]["provenance"],"diagnostics":result["diagnostics"]}
    targets[location]["gold_label"]="SYNTHETIC PRIVATE SENTINEL"
    with pytest.raises(ValueError):q.validate_result(result,query)


def test_shuffled_graph_insertion_does_not_change_results_or_discovery():
    source,g=fixture();other=nx.MultiDiGraph(**deepcopy(g.graph))
    other.add_nodes_from(reversed(list(g.nodes(data=True))))
    other.add_edges_from(reversed(list(g.edges(keys=True,data=True))))
    query=q.make_query(g,"train:0:0",["R1","R2"])
    assert q.evaluate_query(g,query)==q.evaluate_query(other,query)
    assert q.discover_workload(g,{"train:0:0"})==q.discover_workload(other,{"train:0:0"})


@pytest.mark.parametrize("split",["dev","test"])
def test_discovery_rejects_dev_and_test(split):
    _,g=fixture(split=split)
    with pytest.raises(ValueError,match="train only"):q.discover_workload(g,set())
    with pytest.raises(ValueError,match="train only"):q.select_queries(g,{},set())


def test_selection_priority_diversity_and_shortages():
    s,_=fixture();docs=[deepcopy(s.documents[0]) for _ in range(15)]
    s=SourceSplit("train",docs,digest(encoded(docs).encode()),[]);g=build_split_graph(s)
    seeds,inv=q.discover_workload(g,{"train:0:0","train:1:0"})
    queries,selection=q.select_queries(g,seeds,{"train:0:0","train:1:0"})
    assert [r["role"] for r in selection["selections"]][:2]==["candidate_endpoint"]*2
    assert len({q.indices(r["anchor_entity_id"])[0] for r in queries})==len(queries)
    assert len({tuple(r["relations"]) for r in queries})==len(queries)
    assert any(r["shortfall"] for r in selection["quotas"])
    assert inv["candidate_endpoint_coverage"][0]["two_hop_occurrence_paths"]==1


def test_full_role_mix_includes_both_zero_diagnostics_without_generator_variable_aliasing():
    s,_=fixture();docs=[]
    for i in range(15):
        doc=deepcopy(s.documents[0])
        for label in doc["labels"]:label["r"]+=f"_{i}"
        docs.append(doc)
    source=SourceSplit("train",docs,digest(encoded(docs).encode()),[]);graph=build_split_graph(source)
    endpoints={"train:0:0","train:1:0"}
    seeds,_=q.discover_workload(graph,endpoints)
    queries,selection=q.select_queries(graph,seeds,endpoints)
    assert len(queries)==12 and all(r["shortfall"]==0 for r in selection["quotas"])
    assert len({q.indices(query["anchor_entity_id"])[0] for query in queries})==12
    zeros=[query for query,meta in zip(queries,selection["selections"]) if meta["role"]=="zero_diagnostic"]
    assert [query["hop_count"] for query in zeros]==[2,3]
    assert all(q.evaluate_query(graph,query)["answer_ids"]==[] for query in zeros)


def test_no_queries_and_empty_endpoint_population_are_explicit():
    _,g=fixture(labels=[])
    seeds,inventory=q.discover_workload(g,set());queries,selection=q.select_queries(g,seeds,set())
    assert seeds=={} and queries==[] and inventory["status"]=="COMPLETE"
    assert sum(r["shortfall"] for r in selection["quotas"])==12


def test_exported_envelopes_reject_private_fields_and_wrong_sources():
    _,g=fixture();query=q.make_query(g,"train:0:0",["R1","R2"]);result=q.evaluate_query(g,query)
    queries={"format_version":1,"query_version":q.VERSION,"source_sha256":query["source_sha256"],"queries":[query]}
    results={"format_version":1,"query_version":q.VERSION,"source_sha256":query["source_sha256"],"results":[result]}
    q.validate_packages(queries,results)
    for package in (queries,results):
        package["verified_answers"]=[]
        with pytest.raises(ValueError):q.validate_packages(queries,results)
        del package["verified_answers"]
    results["source_sha256"]="0"*64
    with pytest.raises(ValueError,match="fingerprint"):q.validate_packages(queries,results)


@pytest.fixture
def cli_case(tmp_path,monkeypatch):
    from scripts import candidate_discovery as c
    root=tmp_path/"project";root.mkdir();monkeypatch.setattr(q,"ROOT",root);monkeypatch.setattr(c,"ROOT",root)
    scripts=root/"scripts";scripts.mkdir()
    for name in ("query_workload.py","prepare_qa_worklist.py","candidate_discovery.py","prepare_annotation_worklist.py","audit_dataset.py","build_graph.py"):
        (scripts/name).write_bytes(Path(q.__file__).with_name(name).read_bytes())
    data=root/"data"/"raw"/"re_docred"/"data";data.mkdir(parents=True)
    phase0=root/"results"/"phase0";phase0.mkdir(parents=True)
    s,_=fixture();manifest={"files":[]}
    for split in ("train","dev","test"):
        raw=encoded(s.documents).encode();(data/f"{split}_revised.json").write_bytes(raw)
        manifest["files"].append({"split":split,"sha256":digest(raw),"sha256_after":digest(raw),"bytes":len(raw)})
    (phase0/"input_manifest.json").write_text(json.dumps(manifest))
    (phase0/"dataset_audit.json").write_text(json.dumps({"status":"VALID","input_fingerprints":{e["split"]:e["sha256"] for e in manifest["files"]},
        "splits":{"train":{"counts":{"entity_groups":6,"relations":3}}}}))
    monkeypatch.setattr(q,"phase1_baseline",lambda:{"SYNTHETIC_FIXTURE":True})
    monkeypatch.setattr(q,"phase2_inputs",lambda:({"source_sha256":s.sha256,"candidates":[{"left_entity_id":"train:0:0","right_entity_id":"train:0:5"}]},{"SYNTHETIC_FIXTURE":True}))
    original=c.subprocess.run
    monkeypatch.setattr(c.subprocess,"run",lambda args,**kw:SimpleNamespace(returncode=0) if "check-ignore" in args else original(args,**kw))
    out=root/"results"/"phase3";private=root/"data"/"private_gold"/"phase3"
    args=["--data-dir",str(data),"--manifest",str(phase0/"input_manifest.json"),"--output-dir",str(out),"--review-dir",str(private)]
    return SimpleNamespace(root=root,data=data,phase0=phase0,out=out,private=private,args=args)


def latest(case):return json.loads((case.out/"latest_run.json").read_text())


def test_cli_repeatability_without_private_reads_or_test_loading(cli_case,monkeypatch):
    original_open,original_load=Path.open,q.load_split
    with monkeypatch.context() as guard:
        def no_private(path,mode="r",*args,**kw):
            if "private_gold" in path.parts and ("r" in mode or "+" in mode):pytest.fail("Private data read")
            return original_open(path,mode,*args,**kw)
        def train_only(data,split,manifest):
            assert split=="train"
            return original_load(data,split,manifest)
        guard.setattr(Path,"open",no_private);guard.setattr(q,"load_split",train_only)
        assert q.main(cli_case.args)==0;first=latest(cli_case)
        assert q.main(cli_case.args)==0;second=latest(cli_case)
    assert first["run_id"]!=second["run_id"]
    assert all(first["artifact_sha256"][n]==sha for n,sha in second["artifact_sha256"].items() if n!="run_manifest.json")
    assert first["review_artifact_sha256"]==second["review_artifact_sha256"]


@pytest.mark.parametrize("failure",["missing","malformed","after_discovery","incomplete"])
def test_failed_rerun_preserves_previous_packages_and_records_failure(cli_case,monkeypatch,failure):
    assert q.main(cli_case.args)==0;first=latest(cli_case)
    before={p:p.read_bytes() for base in (cli_case.out/first["run_directory"],Path(first["review_directory"])) for p in base.iterdir()}
    args=list(cli_case.args)
    if failure=="missing":args[3]=str(cli_case.phase0/"missing.json")
    elif failure=="malformed":(cli_case.phase0/"input_manifest.json").write_text("{")
    elif failure=="after_discovery":
        def fail(*a):raise ValueError("SYNTHETIC evaluation failure")
        monkeypatch.setattr(q,"evaluate_query",fail)
    else:
        original=q.discover_workload
        monkeypatch.setattr(q,"discover_workload",lambda g,e:original(g,e,limit=1))
    assert q.main(args)==1
    assert latest(cli_case)["status"]=="FAILED" and latest(cli_case)["run_directory"] is None
    assert before=={p:p.read_bytes() for p in before}


@pytest.mark.parametrize("protected",["raw","phase0","phase1","phase2","old_private"])
def test_protected_output_paths_receive_no_writes(cli_case,protected):
    args=list(cli_case.args)
    if protected=="old_private":args[7]=str(cli_case.root/"data"/"private_gold"/"phase2")
    else:args[5]=str(cli_case.data if protected=="raw" else cli_case.root/"results"/protected)
    before={p:p.read_bytes() for p in cli_case.root.rglob("*") if p.is_file()}
    assert q.main(args)==1
    assert before=={p:p.read_bytes() for p in cli_case.root.rglob("*") if p.is_file()}


def test_publication_failure_and_interruption_cannot_publish_success(cli_case,monkeypatch):
    original=q.publish_package
    def fail(root,run_id,files):
        if root==cli_case.out:raise OSError("SYNTHETIC publish failure")
        return original(root,run_id,files)
    with monkeypatch.context() as scope:
        scope.setattr(q,"publish_package",fail);assert q.main(cli_case.args)==1
    assert latest(cli_case)["status"]=="FAILED"
    def interrupt(*args):raise KeyboardInterrupt
    monkeypatch.setattr(q,"discover_workload",interrupt)
    with pytest.raises(KeyboardInterrupt):q.main(cli_case.args)
    assert latest(cli_case)["status"]=="RUNNING"


def test_preexisting_review_notes_are_not_overwritten(cli_case):
    assert q.main(cli_case.args)==0;first=latest(cli_case)
    path=Path(first["review_directory"])/"qa_review_worklist.csv";path.write_text(path.read_text()+"SYNTHETIC note\n");before=path.read_bytes()
    assert q.main(cli_case.args)==0 and path.read_bytes()==before


def test_status_initialization_failure_reads_no_sources(cli_case,monkeypatch):
    def fail(*args):raise OSError("SYNTHETIC unwritable latest status")
    monkeypatch.setattr(q,"write_latest",fail)
    monkeypatch.setattr(q,"verify_sources",lambda *a:pytest.fail("Source read before status initialization"))
    assert q.main(cli_case.args)==1 and not (cli_case.out/"runs").exists()


def test_failed_final_pass_marker_leaves_failed_latest(cli_case,monkeypatch):
    original=q.write_latest
    def fail_pass(root,status):
        if status["status"]=="PASS":raise OSError("SYNTHETIC final PASS failure")
        return original(root,status)
    monkeypatch.setattr(q,"write_latest",fail_pass)
    assert q.main(cli_case.args)==1 and latest(cli_case)["status"]=="FAILED" and latest(cli_case)["run_directory"] is None
