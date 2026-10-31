# GIR-ER Phase 2 execution report

Technical status: PASS; identity annotation NOT PERFORMED.

Generation version: `phase2-candidates-v1`. Train only; dev used only for overlap/schema checking. Test hashed only.

Discovered unordered pairs: 856,836; selected unlabelled review pairs: 24.
Exact-name pairs: 790,659; initialism pairs: 74,989; pairs satisfying both: 8,812.

| Selection category | Available | Target | Selected | Diversity skips before quota | Shortfall |
|---|---:|---:|---:|---:|---:|
| sparse_context | 139052 | 4 | 4 | 4 | 0 |
| different_name_abbreviation | 39512 | 4 | 4 | 1 | 0 |
| challenging_name_collision | 248057 | 8 | 8 | 124 | 0 |
| compatible_name_context | 12647 | 8 | 8 | 40 | 0 |

Pairs excluded from selection by type policy: 417,568 (retained in discovery counts).
Train graph reconciliation: `{"absent":0,"documents_available":3053,"documents_validated":3053,"edges":85932,"edges_validated":85932,"empty":38672,"full_split":true,"nodes":59359,"nodes_validated":59359,"nonempty":47260,"provenance_status":"PASS","validation_scope":"FULL_SPLIT"}`.
Selected evidence availability: `{"candidates_with_inspectable_mention_tokens":24,"endpoints_without_incident_relations":5,"endpoints_without_nonempty_incident_pointers":17,"identity_sufficiency_not_assessed":24,"incident_pointer_counts":{"absent":0,"empty":134,"nonempty":206}}`.
Selected pair source scopes: `{"cross_document":24}`.
Dev evaluation exclusions: `[469]`. Raw splits unchanged.

## Interpretation and limitations

Every selected pair is naturally observed and UNREVIEWED. Categories describe selection signals, not positive or negative labels. Mention sentences are inspectable; identity-evidence sufficiency remains NOT_ASSESSED. Missing relation pointers do not mean contradiction.

Controlled cases are feasibility-only: no fragments, parent maps, controlled candidate pairs or edge allocations were produced. Unique pointer/mention sentence intersection is not verified relation attribution. An actual fragmentation policy needs separate student approval.

This exact-block pilot has unknown candidate recall and identity balance. Source-order, type and diversity restrictions bias the sample; shared documents and real-world entities can create dependencies. Exact-text grouping does not detect paraphrases or establish entity-disjoint evaluation.

Corpus acquisition/licence, release authenticity and relation meanings remain unverified. Reviewer text and blank annotations stay private. Generated candidate names are local source-derived inputs, not cleared for redistribution. Separate supervisor feedback/proposal/literature files are unavailable; the master context is a summary, not authenticated supervisor approval.

LACE/ASPEN/ASPEN+ boundaries remain governing. Candidate preparation is infrastructure. GIR-ER's incremental value over an equally informed matcher is unvalidated; zero or negative future benefit remains possible. No identity metrics, QA answers, merge effects or risk scores were computed.

## Reproduce and review

```bash
.venv/bin/python -B scripts/candidate_discovery.py --data-dir data/raw/re_docred/data --manifest results/phase0/input_manifest.json --output-dir results/phase2 --review-dir data/private_gold/phase2
.venv/bin/python -B -m pytest -q -p no:cacheprovider
```

Check ../../latest_run.json and artifact hashes. Earlier completed runs are historical. RUNNING/FAILED is not latest success. The manifest records actual timing, input/code/rule hashes and invocation; deterministic outputs omit run IDs and timing.

AI-assisted code and tests require student understanding and independent review. Human decisions require the annotation guide. STOP: no Phase 3, fragmentation, merges, counterfactual analysis, scoring, baselines or effectiveness claims.
