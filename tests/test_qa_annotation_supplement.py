"""Supplement mechanics only; authored fixtures are not verified QA evidence."""

from copy import deepcopy
import csv
import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from test_query_workload import fixture
from scripts import prepare_qa_annotation_supplement as s
from scripts import query_workload as q
from scripts.build_graph import SourceSplit, build_split_graph


def prepared():
    source,_=fixture()
    docs=deepcopy(source.documents)
    docs[0]["labels"].append({"h":4,"t":5,"r":"TEMPLATE_ONLY","evidence":[]})
    docs[0]["labels"].append(deepcopy(docs[0]["labels"][0]))
    source=SourceSplit("train",docs,s.digest(s.encoded(docs).encode()),[])
    graph=build_split_graph(source)
    queries=[q.make_query(graph,"train:0:0",["R1","R2"]),q.make_query(graph,"train:0:0",["R1","R2","R3"]),
             q.make_query(graph,"train:0:5",["R1","R2"])]
    results=[q.evaluate_query(graph,query) for query in queries]
    envelope={"format_version":1,"query_version":q.VERSION,"source_sha256":source.sha256}
    return source,{**envelope,"queries":queries},{**envelope,"results":results}


def test_unique_occurrences_paths_and_all_cross_references():
    source,queries,results=prepared();before=deepcopy(source.documents)
    edges,paths=s.prepare_records(source,queries,results)
    assert len(edges)==4 and len(paths)==4
    assert {r["edge_key"] for r in edges}=={"train:0:0","train:0:1","train:0:2","train:0:4"}
    assert "train:0:3" not in {r["edge_key"] for r in edges}
    edge_map={e["edge_review_id"]:e for e in edges};path_map={p["path_id"]:p for p in paths}
    assert len(path_map)==4
    for path in paths:
        assert path["ordered_node_ids"][-1]==path["structural_answer_id"]
        assert [edge_map[r]["edge_key"] for r in path["edge_review_ids"]]==path["ordered_edge_keys"]
    for edge in edges:
        for ref in edge["query_path_references"]:
            path=path_map[ref["path_id"]]
            assert path["query_id"]==ref["query_id"]
            assert path["edge_review_ids"][ref["edge_position"]]==edge["edge_review_id"]
    shared=next(e for e in edges if e["edge_key"]=="train:0:1")
    assert len(shared["query_path_references"])==4
    assert all(p["query_id"]!=queries["queries"][2]["query_id"] for p in paths)
    assert source.documents==before


def test_human_fields_blank_and_absent_empty_nonempty_pointers_preserved():
    source,queries,results=prepared();edges,paths=s.prepare_records(source,queries,results)
    by_key={e["edge_key"]:e for e in edges}
    assert by_key["train:0:0"]["evidence_sentence_indices"]==[0,0]
    assert by_key["train:0:1"]["evidence_sentence_indices"]==[]
    assert by_key["train:0:2"]["evidence_sentence_indices"] is None
    assert by_key["train:0:2"]["evidence_field_present"] is False
    for rows,meta,human in ((edges,s.EDGE_METADATA,s.EDGE_FIELDS),(paths,s.PATH_METADATA,s.PATH_FIELDS)):
        parsed=list(csv.DictReader(io.StringIO(s.csv_text(rows,meta,human))))
        assert all(row[f]=="" for row in parsed for f in human)
    altered=deepcopy(edges);altered[0][s.EDGE_FIELDS[0]]="SYNTHETIC_LABEL"
    with pytest.raises(ValueError,match="populated"):s.csv_text(altered,s.EDGE_METADATA,s.EDGE_FIELDS)


def test_stable_ids_and_determinism_under_reordered_input():
    source,queries,results=prepared();edges,paths=s.prepare_records(source,queries,results)
    queries["queries"].reverse();results["results"].reverse()
    for result in results["results"]:result["paths"].reverse()
    other_edges,other_paths=s.prepare_records(source,queries,results)
    assert edges==other_edges and paths==other_paths
    assert s.csv_text(edges,s.EDGE_METADATA,s.EDGE_FIELDS)==s.csv_text(other_edges,s.EDGE_METADATA,s.EDGE_FIELDS)


@pytest.mark.parametrize("change",["source","pointers","fingerprint","incomplete","private"])
def test_invalid_source_results_and_private_payloads_are_rejected(change):
    source,queries,results=prepared()
    if change=="source":source.documents[0]["sents"][0][0]="modified"
    elif change=="pointers":results["results"][0]["paths"][0]["edge_occurrences"][0]["evidence"]=[0]
    elif change=="fingerprint":source=SourceSplit("train",source.documents,"0"*64,[])
    elif change=="incomplete":
        results["results"][0]["status"]="INCOMPLETE";results["results"][0]["diagnostics"]["status"]="INCOMPLETE"
    else:results["results"][0]["paths"][0]["gold_answer"]="SYNTHETIC_PRIVATE_SENTINEL"
    with pytest.raises(ValueError):s.prepare_records(source,queries,results)


def test_empty_and_zero_queries_create_header_only_sheets():
    source,queries,results=prepared();queries["queries"]=queries["queries"][-1:];results["results"]=results["results"][-1:]
    edges,paths=s.prepare_records(source,queries,results)
    assert edges==paths==[]
    assert len(s.csv_text(edges,s.EDGE_METADATA,s.EDGE_FIELDS).splitlines())==1
    assert len(s.csv_text(paths,s.PATH_METADATA,s.PATH_FIELDS).splitlines())==1


@pytest.fixture
def cli_case(tmp_path,monkeypatch):
    root=tmp_path/"project";root.mkdir();monkeypatch.setattr(s,"ROOT",root)
    scripts=root/"scripts";scripts.mkdir()
    for name in ("prepare_qa_annotation_supplement.py","query_workload.py","build_graph.py","audit_dataset.py","candidate_discovery.py"):
        (scripts/name).write_bytes(Path(s.__file__).with_name(name).read_bytes())
    source,queries,results=prepared()
    data=root/"data"/"raw";data.mkdir(parents=True)
    manifest={"files":[]}
    for split in ("train","dev","test"):
        raw=s.encoded(source.documents).encode();(data/f"{split}_revised.json").write_bytes(raw)
        manifest["files"].append({"split":split,"sha256":s.digest(raw),"sha256_after":s.digest(raw),"bytes":len(raw)})
    phase0=root/"results"/"phase0";phase0.mkdir(parents=True);(phase0/"input_manifest.json").write_text(json.dumps(manifest))
    public=root/"results"/"phase3";run=public/"runs"/"original";run.mkdir(parents=True)
    files={"queries_train.json":queries,"structural_query_results.json":results,
           "query_inventory.json":{"template_example_edge_keys":["train:0:3"]},
           "query_feasibility_report.md":{},"phase3_report.md":{},"run_manifest.json":{}}
    hashes={}
    for name,payload in files.items():
        content=s.json_text(payload);(run/name).write_text(content);hashes[name]=s.digest(content.encode())
    (public/"latest_run.json").write_text(json.dumps({"status":"PASS","run_directory":"runs/original","artifact_sha256":hashes,
                                                  "review_directory":"data/private_gold/DO_NOT_READ"}))
    original=s.subprocess.run
    monkeypatch.setattr(s.subprocess,"run",lambda args,**kw:SimpleNamespace(returncode=0) if "check-ignore" in args else original(args,**kw))
    out=root/"data"/"private_gold"/"phase3"/"annotation_supplements"
    args=["--data-dir",str(data),"--manifest",str(phase0/"input_manifest.json"),"--phase3-dir",str(public),"--output-dir",str(out)]
    return SimpleNamespace(root=root,out=out,args=args,public=public,run=run,data=data,phase0=phase0)


def test_cli_reads_no_private_data_and_preserves_source_and_public_results(cli_case,monkeypatch):
    before={p:p.read_bytes() for base in (cli_case.public,cli_case.data,cli_case.phase0) for p in base.rglob('*') if p.is_file()}
    original=Path.open
    def guard(path,mode="r",*args,**kw):
        if "private_gold" in path.parts and ("r" in mode or "+" in mode):pytest.fail("Private annotation read")
        return original(path,mode,*args,**kw)
    with monkeypatch.context() as scope:
        scope.setattr(Path,"open",guard)
        assert s.main(cli_case.args)==0
        assert s.main(cli_case.args)==0
    packages=list((cli_case.out/"runs").iterdir());assert len(packages)==2
    assert {p.name:p.read_bytes() for p in packages[0].iterdir()}=={p.name:p.read_bytes() for p in packages[1].iterdir()}
    assert before=={p:p.read_bytes() for p in before}
    edge_rows=list(csv.DictReader((packages[0]/"edge_review_worklist.csv").open()))
    assert len(edge_rows)==4 and "train:0:3" not in {r["edge_key"] for r in edge_rows}


def test_prior_completed_annotations_are_not_overwritten(cli_case):
    assert s.main(cli_case.args)==0;package=next((cli_case.out/"runs").iterdir())
    sheet=package/"edge_review_worklist.csv";sheet.write_text(sheet.read_text()+"SYNTHETIC reviewer note\n");before=sheet.read_bytes()
    assert s.main(cli_case.args)==0 and sheet.read_bytes()==before


@pytest.mark.parametrize("failure",["missing_manifest","corrupt_public","not_pass"])
def test_failure_creates_no_new_package_and_preserves_prior_work(cli_case,failure):
    assert s.main(cli_case.args)==0
    before={p:p.read_bytes() for p in cli_case.out.rglob('*') if p.is_file()};args=list(cli_case.args)
    if failure=="missing_manifest":args[3]=str(cli_case.phase0/"missing.json")
    elif failure=="corrupt_public":(cli_case.run/"queries_train.json").write_text('{}')
    else:
        path=cli_case.public/"latest_run.json";record=json.loads(path.read_text());record["status"]="FAILED";path.write_text(json.dumps(record))
    assert s.main(args)==1 and before=={p:p.read_bytes() for p in cli_case.out.rglob('*') if p.is_file()}


@pytest.mark.parametrize("location",["public","raw","old_private"])
def test_output_cannot_write_outside_supplement_subtree(cli_case,location):
    args=list(cli_case.args);args[-1]=str({"public":cli_case.public,"raw":cli_case.data,"old_private":cli_case.out.parent/"runs"}[location])
    assert s.main(args)==1 and not cli_case.out.exists()


def test_ignore_and_symlink_guards(cli_case,monkeypatch):
    monkeypatch.setattr(s.subprocess,"run",lambda *a,**kw:SimpleNamespace(returncode=1))
    assert s.main(cli_case.args)==1 and not cli_case.out.exists()
    monkeypatch.setattr(s.subprocess,"run",lambda *a,**kw:SimpleNamespace(returncode=0))
    cli_case.out.mkdir(parents=True);(cli_case.out/"runs").symlink_to(cli_case.data,target_is_directory=True)
    assert s.main(cli_case.args)==1


def test_partial_publication_is_never_a_completed_run(cli_case,monkeypatch):
    original=Path.write_text
    def fail_second(path,*args,**kw):
        if path.name=="path_composition_worklist.csv":raise OSError("SYNTHETIC partial write")
        return original(path,*args,**kw)
    monkeypatch.setattr(Path,"write_text",fail_second)
    assert s.main(cli_case.args)==1 and not (cli_case.out/"runs").exists()
