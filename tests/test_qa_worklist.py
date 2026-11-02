"""Blank reviewer records verify preparation mechanics, not source truth."""

from copy import deepcopy
import csv
import io

import pytest

from test_query_workload import fixture
from scripts import query_workload as q
from scripts.prepare_qa_worklist import REVIEW_FIELDS, make_qa_dossier, qa_worklist_csv


def prepared():
    source,graph=fixture();queries=[q.make_query(graph,"train:0:0",["R1","R2","R3"]),q.make_query(graph,"train:0:5",["R1","R2"])]
    selection={"selections":[{"query_id":query["query_id"],"role":"general" if i==0 else "zero_diagnostic",
                               "template_origin_edge_keys":["train:0:0","train:0:1"]} for i,query in enumerate(queries)]}
    results=[q.evaluate_query(graph,query) for query in queries]
    return source,graph,queries,results,selection


def test_lossless_source_registry_blank_fields_and_zero_query_context():
    source,graph,queries,results,selection=prepared();before=deepcopy(source.documents)
    dossier=make_qa_dossier(graph,source,queries,results,selection)
    assert dossier["edge_evidence"]["train:0:0"]["source_relation"]["evidence"]==[0,0]
    assert dossier["edge_evidence"]["train:0:1"]["source_relation"]["evidence"]==[]
    assert "evidence" not in dossier["edge_evidence"]["train:0:2"]["source_relation"]
    mention=dossier["node_evidence"]["train:0:0"]["mentions"][0]
    assert mention["source_mention"]==before[0]["vertexSet"][0][0] and mention["span_tokens"]==["A"]
    assert "train:0:5" in dossier["node_evidence"] and dossier["queries"][1]["supporting_paths"]==[]
    rows=list(csv.DictReader(io.StringIO(qa_worklist_csv(dossier))))
    assert [r["row_scope"] for r in rows]==["QUERY","ANSWER","QUERY"]
    assert all(r[f]=="" for r in rows for f in REVIEW_FIELDS)
    assert all(r[f]=="" for r in dossier["queries"] for f in REVIEW_FIELDS)
    assert all(r[f]=="" for query in dossier["queries"] for r in query["answer_reviews"] for f in REVIEW_FIELDS)
    assert all(r["preparation_status"]=="NOT_ASSESSED" for r in dossier["queries"])
    assert dossier==make_qa_dossier(graph,source,queries,results,selection)
    mention["source_mention"]["name"]="changed"
    dossier["edge_evidence"]["train:0:0"]["source_relation"]["evidence"].append(0)
    assert source.documents==before


def test_tampered_source_provenance_or_results_cannot_be_published_for_review():
    source,graph,queries,results,selection=prepared()
    results[0]["paths"][0]["edge_occurrences"][0]["evidence"]=[0]
    with pytest.raises(ValueError,match="occurrence mismatch"):make_qa_dossier(graph,source,queries,results,selection)
    source,graph,queries,results,selection=prepared();source.documents[0]["sents"][0][0]="changed"
    with pytest.raises(ValueError,match="changed source"):make_qa_dossier(graph,source,queries,results,selection)


def test_incomplete_result_and_nontrain_review_are_rejected():
    source,graph,queries,results,selection=prepared();results[0]["status"]="INCOMPLETE";results[0]["diagnostics"]["status"]="INCOMPLETE"
    with pytest.raises(ValueError,match="Incomplete"):make_qa_dossier(graph,source,queries,results,selection)
    other=type(source)("dev",source.documents,source.sha256,[])
    with pytest.raises(ValueError,match="train only"):make_qa_dossier(graph,other,queries,results,selection)


def test_empty_review_package_has_csv_header():
    source,graph=fixture();dossier=make_qa_dossier(graph,source,[],[],{"selections":[]})
    assert dossier["queries"]==[] and len(qa_worklist_csv(dossier).splitlines())==1
