"""Synthetic software checks only; fixture decisions are not research labels."""
from copy import deepcopy
import csv
import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from scripts import identity_annotation as tool
from scripts.build_graph import SourceSplit, build_split_graph
from scripts.prepare_annotation_worklist import ANNOTATION_FIELDS, make_review_worklist


@pytest.fixture
def records():
    row = {'candidate_id': 'c1', 'left_entity_id': 'train:0:0', 'right_entity_id': 'train:0:1',
           **{k: '' for k in ANNOTATION_FIELDS}}
    expected = [{k: v for k, v in row.items() if k not in ANNOTATION_FIELDS}]
    docs = [{'sents': [['A', 'B']], 'vertexSet': [[{}], [{}]], 'labels': []}]
    return row, expected, docs


def reviewed(row):
    row.update(reviewer_decision='UNKNOWN / INSUFFICIENT EVIDENCE', evidence_references='train:0:sentence:0',
               rationale='Synthetic test rationale; evidence insufficient; low confidence.', confidence='low',
               reviewer_identifier='fixture', review_date='2026-11-02', adjudication_status='single review')
    return row


def test_blank_is_unreviewed_without_mutation(records):
    row, expected, docs = records
    before = deepcopy(row)
    result = tool.check_rows([row], expected, docs)
    assert result['counts'] == {'UNREVIEWED': 1} and not result['errors']
    assert result['semantic_correctness'] == 'NOT_ASSESSED' and row == before


@pytest.mark.parametrize('decision', tool.DECISIONS)
def test_manual_decisions_are_accepted_as_records_only(records, decision):
    row, expected, docs = records
    reviewed(row)['reviewer_decision'] = decision
    assert not tool.check_rows([row], expected, docs)['errors']


@pytest.mark.parametrize('field,value', [('reviewer_decision', 'known_positive'), ('confidence', '0.9'),
    ('review_date', 'yesterday'), ('evidence_references', 'train:999:sentence:0'),
    ('evidence_references', 'train:0:entity:0:mention:99'), ('rationale', ''), ('left_entity_id', 'wrong')])
def test_invalid_manual_records(records, field, value):
    row, expected, docs = records
    reviewed(row)[field] = value
    assert tool.check_rows([row], expected, docs)['errors']


def test_duplicate_missing_partial(records):
    row, expected, docs = records
    assert tool.check_rows([row, row], expected, docs)['errors']
    assert tool.check_rows([], expected, docs)['errors']
    row['rationale'] = 'unfinished'
    assert tool.check_rows([row], expected, docs)['errors']


def test_evidence_exact_mentions_and_context():
    docs = [{'title': 'Example', 'sents': [['A', ',', 'B'], ['Other', 'context']],
             'vertexSet': [[{'name': 'A,', 'type': 'ORG', 'sent_id': 0, 'pos': [0, 2]}],
                           [{'name': 'B', 'type': 'LOC', 'sent_id': 0, 'pos': [2, 3]}]],
             'labels': [{'h': 0, 't': 1, 'r': 'P17', 'evidence': []}]}]
    source = SourceSplit('train', docs, 'fixture', [])
    pair = {'candidate_id': 'c1', 'left_entity_id': 'train:0:0', 'right_entity_id': 'train:0:1', 'selection_rule_ids': ['fixture']}
    before = deepcopy(docs)
    dossier = make_review_worklist([pair], source, build_split_graph(source))
    view = tool.evidence_view(dossier, source)
    assert 'Other context' in view and 'name_span_difference' in view and 'train:0:sentence:1' in view
    assert '"evidence": []' in view and '"pos"' in view and 'P17' in view
    assert view == tool.evidence_view(dossier, source) and docs == before
    assert all(e[k] == '' for e in dossier['candidates'] for k in ANNOTATION_FIELDS)


@pytest.fixture
def workspace(tmp_path, monkeypatch, records):
    monkeypatch.setattr(tool, 'WORKING', tmp_path)
    monkeypatch.setattr(tool.subprocess, 'run', lambda *a, **k: SimpleNamespace(returncode=0))
    p = tmp_path / 'workspace'; p.mkdir()
    row, expected, _ = records
    (p / 'annotation_manifest.json').write_text(json.dumps({'columns': list(row), 'candidates': expected}))
    out = io.StringIO(); w = csv.DictWriter(out, fieldnames=list(row)); w.writeheader(); w.writerow(row)
    (p / 'annotations.csv').write_text(out.getvalue())
    (p / 'identity_annotation_log.md').write_text('initial log\n')
    (p / 'evidence.md').write_text('source')
    return p


def test_logging_preserves_annotations_and_existing_log(workspace):
    before = (workspace / 'annotations.csv').read_bytes()
    tool.append_log(workspace, 'c1', '2026-11-02', 'train:0:sentence:0', 5, 'actual supplied note')
    assert (workspace / 'annotations.csv').read_bytes() == before
    assert (workspace / 'identity_annotation_log.md').read_text().startswith('initial log\n')
    assert '5' in (workspace / 'identity_annotation_log.md').read_text()


def test_logging_rejects_bad_candidate(workspace):
    before = (workspace / 'identity_annotation_log.md').read_bytes()
    with pytest.raises(ValueError): tool.append_log(workspace, 'missing', '2026-11-02', 'ref', 1, 'note')
    assert (workspace / 'identity_annotation_log.md').read_bytes() == before


def test_protected_paths_and_symlinks(workspace, tmp_path):
    with pytest.raises(ValueError): tool.workspace_path(tmp_path.parent / 'raw')
    link = tmp_path / 'link'; link.symlink_to(workspace, target_is_directory=True)
    with pytest.raises(ValueError): tool.workspace_path(link)
    (workspace / 'evidence.md').unlink(); (workspace / 'evidence.md').symlink_to(workspace / 'annotations.csv')
    with pytest.raises(ValueError): tool.read_workspace(workspace)


def test_prepare_never_overwrites(workspace):
    before = {p.name: p.read_bytes() for p in workspace.iterdir()}
    with pytest.raises(ValueError, match='overwrite'):
        tool.prepare(workspace, Path('missing'), Path('missing'), Path('missing'))
    assert before == {p.name: p.read_bytes() for p in workspace.iterdir()}


def test_workspace_reads_do_not_write(workspace):
    before = {p.name: p.read_bytes() for p in workspace.iterdir()}
    tool.read_workspace(workspace)
    assert before == {p.name: p.read_bytes() for p in workspace.iterdir()}


def test_malformed_csv_values_report_errors(records):
    row, expected, docs = records
    row['rationale'] = None
    assert tool.check_rows([row], expected, docs)['errors']


def test_readonly_validation_cli_with_synthetic_reviews(workspace, monkeypatch, records):
    row, _, docs = records
    run = 'a' * 32
    meta = json.loads((workspace / 'annotation_manifest.json').read_text())
    candidates = []
    rows = []
    for i in range(24):
        r = reviewed(dict(row)); r['candidate_id'] = f'c{i}'
        rows.append(r)
        candidates.append({k: r[k] for k in ('candidate_id', 'left_entity_id', 'right_entity_id')})
    data = tool.json_text({'candidates': candidates})
    public = workspace / 'results/phase2/runs' / run
    public.mkdir(parents=True); (public / 'candidates_train.json').write_text(data)
    p0 = workspace / 'results/phase0'; p0.mkdir(parents=True); (p0 / 'input_manifest.json').write_text('{}')
    meta.update(source_run_id=run, original_public_hashes={'candidates_train.json': tool.digest(data.encode())},
                candidates=candidates, source_fingerprints={'train': 'fixture'},
                initial_sha256={'evidence.md': tool.digest(b'source')})
    (workspace / 'annotation_manifest.json').write_text(json.dumps(meta))
    out = io.StringIO(); w = csv.DictWriter(out, fieldnames=list(row)); w.writeheader(); w.writerows(rows)
    (workspace / 'annotations.csv').write_text(out.getvalue())
    monkeypatch.setattr(tool, 'ROOT', workspace)
    monkeypatch.setattr(tool, 'validate_candidate_export', lambda p: None)
    monkeypatch.setattr(tool, 'verify_sources', lambda *a: {'train': 'fixture'})
    monkeypatch.setattr(tool, 'load_split', lambda *a: SimpleNamespace(documents=docs))
    before = {str(p): p.read_bytes() for p in workspace.rglob('*') if p.is_file()}
    assert tool.main(['validate', '--workspace', str(workspace)]) == 0
    assert before == {str(p): p.read_bytes() for p in workspace.rglob('*') if p.is_file()}


def test_no_inference_module_imports_annotation_tool():
    for name in ('candidate_discovery.py', 'query_workload.py', 'build_graph.py'):
        assert 'identity_annotation' not in (Path('scripts') / name).read_text()
