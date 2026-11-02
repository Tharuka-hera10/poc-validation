"""Evaluation-only manual identity workspace; never imported by inference tools."""
import argparse
from collections import Counter
import csv
from datetime import date
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from uuid import uuid4

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.audit_dataset import digest, load_json
from scripts.build_graph import build_split_graph, load_split, require
from scripts.candidate_discovery import json_text, validate_candidate_export, verify_sources
from scripts.prepare_annotation_worklist import ANNOTATION_FIELDS, make_review_worklist, worklist_csv

ROOT = Path(__file__).resolve().parents[1]
WORKING = ROOT / 'data/private_gold/phase2/annotations/working'
DECISIONS = ('SAME ENTITY', 'DIFFERENT ENTITY', 'UNKNOWN / INSUFFICIENT EVIDENCE')


def workspace_path(path):
    """Constrain all writes and review reads to ignored working workspaces."""
    path = Path(path).absolute()
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'Workspace symlinks forbidden')
    require(path.resolve().is_relative_to(WORKING.resolve()) and path.resolve() != WORKING.resolve(),
            'Workspace must be below data/private_gold/phase2/annotations/working')
    result = subprocess.run(['git', 'check-ignore', '-q', '--', str(path)], cwd=ROOT)
    require(result.returncode == 0, 'Workspace must be Git-ignored')
    return path


def evidence_view(dossier, source):
    """Render source values without identity recommendations or predicate guesses."""
    lines = ['# Phase 2 manual identity evidence', '',
             'AI-assisted preparation only. No identity judgement has been made.',
             'Sentence pointers and original annotations are not verified truth.',
             'Rendered sentences join tokens with spaces; token arrays preserve source values.', '',
             '## Candidate index']
    for entry in dossier['candidates']:
        cid = entry['candidate_id']
        lines.append(f'- [{cid}](#{cid})')
    for entry in dossier['candidates']:
        cid = entry['candidate_id']
        lines += ['', f'<a id="{cid}"></a>', f'## {cid}']
        for side, endpoint in entry['endpoints'].items():
            di = endpoint['provenance']['document_index']
            lines += ['', f'### {side}: {endpoint["entity_id"]}', '',
                      'Provenance:', '```json', json_text(endpoint['provenance']).rstrip(), '```',
                      'Original mentions, half-open spans, span tokens and name/span flags:',
                      '```json', json_text(endpoint['mentions']).rstrip(), '```',
                      'Original incident relationships (codes retained without interpretation):',
                      '```json', json_text(endpoint['original_incident_relations']).rstrip(), '```',
                      'Pointer availability:', '```json', json_text(endpoint['evidence_pointer_availability']).rstrip(), '```',
                      'Complete document context; sentence indices are zero-based:']
            for si, tokens in enumerate(source.documents[di]['sents']):
                lines += ['', f'**train:{di}:sentence:{si}**', '```json',
                          json.dumps(tokens, ensure_ascii=False), '```', 'Rendered view:',
                          '```text', ' '.join(tokens), '```']
    return '\n'.join(lines) + '\n'


def prepare(destination, phase2, data_dir, manifest_path):
    destination = workspace_path(destination)
    require(not destination.exists(), 'Refusing to overwrite existing workspace')
    phase2 = Path(phase2)
    require('private_gold' not in phase2.resolve().parts, 'Preparation requires public Phase 2 inputs')
    run = load_json((phase2 / 'latest_run.json').read_bytes())
    require(run['status'] == 'PASS', 'Latest Phase 2 attempt is not PASS')
    package = (phase2 / run['run_directory']).resolve()
    require(package.is_relative_to((phase2 / 'runs').resolve()), 'Invalid public run directory')
    for name, sha in run['artifact_sha256'].items():
        require(Path(name).name == name and digest((package / name).read_bytes()) == sha,
                f'Phase 2 artifact fingerprint mismatch: {name}')
    payload = load_json((package / 'candidates_train.json').read_bytes())
    validate_candidate_export(payload)
    require(len(payload['candidates']) == 24, 'Expected fixed 24-pair pilot')
    manifest = load_json(Path(manifest_path).read_bytes())
    before = verify_sources(Path(data_dir), manifest)
    source = load_split(data_dir, 'train', manifest)
    require(payload['source_sha256'] == source.sha256, 'Candidate/source mismatch')
    dossier = make_review_worklist(payload['candidates'], source, build_split_graph(source))
    blank = worklist_csv(dossier)
    require(digest(blank.encode()) == run['review_artifact_sha256']['review_worklist.csv'],
            'Reconstructed blank worklist differs from original package')
    require(digest(json_text(dossier).encode()) == run['review_artifact_sha256']['review_dossier.json'],
            'Reconstructed source evidence differs from original package')
    rows = list(csv.DictReader(io.StringIO(blank)))
    for row in rows:
        row['dossier_reference'] = 'evidence.md#' + row['candidate_id']
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
    log = ('# Phase 2 Human Identity Annotation Log\n\n'
           '- Dataset: Re-DocRED train\n- Task: Cross-document identity review\n- Candidate count: 24\n'
           '- Reviewer:\n- Annotation start date:\n- Annotation status: NOT STARTED\n'
           '- Version: v1\n- Frozen: NO\n- Frozen date:\n- AI assistance: software and evidence-view preparation only\n\n'
           'Use SAME ENTITY, DIFFERENT ENTITY, UNKNOWN / INSUFFICIENT EVIDENCE. Blank means unreviewed.\n'
           'Inspect exact source references; pointer availability is not truth. External evidence needs a separately approved protocol.\n\n'
           '| Date | Candidate ID | Evidence examined | Time spent (minutes) | Notes |\n'
           '|---|---|---|---|---|\n\n'
           '## Limitations and disagreements\n\nRecord only actual ambiguities and disagreements.\n\n'
           '## Final summary — complete manually after review\n\n'
           '- SAME ENTITY:\n- DIFFERENT ENTITY:\n- UNKNOWN / INSUFFICIENT EVIDENCE:\n'
           '- Unreviewed:\n- Total actual annotation time:\n- Cases independently checked:\n'
           '- Unresolved disagreements:\n- Annotation manifest: annotation_manifest.json\n- Review limitations:\n')
    files = {'annotations.csv': output.getvalue(), 'evidence.md': evidence_view(dossier, source),
             'identity_annotation_log.md': log}
    metadata = {'format_version': 1, 'status': 'PREPARED_UNLABELLED', 'frozen': False,
                'source_run_id': run['run_id'], 'source_fingerprints': before,
                'original_public_hashes': run['artifact_sha256'],
                'original_review_hashes': run['review_artifact_sha256'],
                'guide_sha256': digest((ROOT / 'docs/annotation_guide.md').read_bytes()),
                'implementation_sha256': digest(Path(__file__).read_bytes()),
                'columns': list(rows[0]), 'candidates': [{k: r[k] for k in rows[0] if k not in ANNOTATION_FIELDS} for r in rows],
                'initial_sha256': {k: digest(v.encode()) for k, v in files.items()},
                'human_annotation_performed': False}
    files['annotation_manifest.json'] = json_text(metadata)
    require(verify_sources(Path(data_dir), manifest) == before, 'Source changed during preparation')
    destination.parent.mkdir(parents=True, exist_ok=True)
    pending = Path(tempfile.mkdtemp(prefix='.pending-', dir=destination.parent))
    for name, content in files.items():
        (pending / name).write_text(content, encoding='utf-8')
    require(not destination.exists(), 'Workspace appeared during preparation')
    pending.rename(destination)
    return destination


def read_workspace(path):
    path = workspace_path(path)
    for name in ('annotation_manifest.json', 'annotations.csv', 'identity_annotation_log.md', 'evidence.md'):
        require(not (path / name).is_symlink(), f'Symlink forbidden: {name}')
    meta = load_json((path / 'annotation_manifest.json').read_bytes())
    with (path / 'annotations.csv').open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        require(reader.fieldnames == meta['columns'], 'Annotation columns changed')
        rows = list(reader)
    return path, meta, rows


def check_rows(rows, expected, documents):
    """Validate human-entered records, never their semantic correctness."""
    errors, counts = [], Counter()
    refs = {r['candidate_id']: r for r in expected}
    if len(rows) != len(refs) or Counter(r.get('candidate_id') for r in rows) != Counter(refs.keys()):
        errors.append('Candidate IDs missing, duplicated or unexpected')
    for row in rows:
        cid = row.get('candidate_id')
        if any(not isinstance(v, str) for v in row.values()):
            errors.append(f'{cid}: malformed CSV row')
            continue
        if cid not in refs:
            continue
        if any(row.get(k) != v for k, v in refs[cid].items()) or None in row:
            errors.append(f'{cid}: source metadata/endpoints changed or malformed CSV')
        decision = row.get('reviewer_decision', '')
        counts[decision or 'UNREVIEWED'] += 1
        if not decision:
            if any(row.get(k) for k in ANNOTATION_FIELDS):
                errors.append(f'{cid}: partial review, decision blank')
            continue
        if decision not in DECISIONS:
            errors.append(f'{cid}: invalid decision')
        if any(not row.get(k, '').strip() for k in ANNOTATION_FIELDS):
            errors.append(f'{cid}: incomplete human review fields')
        if row.get('confidence') not in ('low', 'medium', 'high'):
            errors.append(f'{cid}: confidence must be low/medium/high; explain it in rationale')
        try:
            date.fromisoformat(row.get('review_date', ''))
        except ValueError:
            errors.append(f'{cid}: review_date must be actual ISO date YYYY-MM-DD')
        references = row.get('evidence_references', '').split(';')
        try:
            require(bool(references), 'Missing references')
            for ref in references:
                match = re.fullmatch(r'train:(\d+):(sentence:(\d+)|entity:(\d+):mention:(\d+)|label:(\d+))', ref.strip())
                require(match is not None, 'Invalid reference format')
                di = int(match[1]); doc = documents[di]
                if match[3] is not None: doc['sents'][int(match[3])]
                elif match[4] is not None: doc['vertexSet'][int(match[4])][int(match[5])]
                else: doc['labels'][int(match[6])]
        except (ValueError, IndexError, KeyError):
            errors.append(f'{cid}: invalid source reference')
    return {'status': 'CHANGES_REQUIRED' if errors else 'RECORDS_VALID', 'counts': dict(counts),
            'errors': errors, 'semantic_correctness': 'NOT_ASSESSED', 'frozen': False}


def append_log(path, candidate, review_date, evidence, minutes, notes):
    path, meta, _ = read_workspace(path)
    require(candidate in {r['candidate_id'] for r in meta['candidates']}, 'Unknown candidate ID')
    date.fromisoformat(review_date)
    require(minutes >= 0, 'Duration must be nonnegative')
    def cell(x):
        return str(x).replace('|', '\\|').replace('\n', ' ').replace('\r', ' ')
    with (path / 'identity_annotation_log.md').open('a', encoding='utf-8') as f:
        f.write('\nActivity entry (student supplied):\n\n| Date | Candidate ID | Evidence examined | Minutes | Notes |\n|---|---|---|---|---|\n')
        f.write('| ' + ' | '.join(map(cell, (review_date, candidate, evidence, minutes, notes))) + ' |\n')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--workspace', type=Path, default=WORKING / uuid4().hex)
    p.add_argument('--phase2-dir', type=Path, default=ROOT / 'results/phase2')
    for name in ('validate', 'log'):
        p = sub.add_parser(name); p.add_argument('--workspace', type=Path, required=True)
    p.add_argument('--candidate-id', required=True); p.add_argument('--date', required=True)
    p.add_argument('--evidence', required=True); p.add_argument('--minutes', type=int, required=True)
    p.add_argument('--notes', required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == 'prepare':
            print(prepare(args.workspace, args.phase2_dir, ROOT / 'data/raw/re_docred/data', ROOT / 'results/phase0/input_manifest.json'))
        elif args.action == 'log':
            append_log(args.workspace, args.candidate_id, args.date, args.evidence, args.minutes, args.notes)
        else:
            path, meta, rows = read_workspace(args.workspace)
            require(re.fullmatch(r'[a-f0-9]{32}', meta['source_run_id']) is not None, 'Invalid source run ID')
            public = ROOT / 'results/phase2/runs' / meta['source_run_id'] / 'candidates_train.json'
            raw = public.read_bytes()
            require(digest(raw) == meta['original_public_hashes']['candidates_train.json'], 'Original candidates changed')
            payload = load_json(raw)
            validate_candidate_export(payload)
            original = {r['candidate_id']: r for r in payload['candidates']}
            require(len(meta['candidates']) == 24 and len({r['candidate_id'] for r in meta['candidates']}) == 24, 'Invalid workspace candidate inventory')
            for row in meta['candidates']:
                require(row['candidate_id'] in original and all(row[k] == original[row['candidate_id']][k] for k in ('left_entity_id', 'right_entity_id')), 'Workspace identity metadata changed')
            manifest = load_json((ROOT / 'results/phase0/input_manifest.json').read_bytes())
            require(verify_sources(ROOT / 'data/raw/re_docred/data', manifest) == meta['source_fingerprints'], 'Source fingerprints changed')
            require(digest((path / 'evidence.md').read_bytes()) == meta['initial_sha256']['evidence.md'], 'Evidence view changed')
            source = load_split(ROOT / 'data/raw/re_docred/data', 'train', manifest)
            result = check_rows(rows, meta['candidates'], source.documents)
            print(json_text(result), end='')
            return int(bool(result['errors']))
        return 0
    except (ValueError, OSError, KeyError, TypeError, csv.Error) as exc:
        print(f'Identity annotation failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
