# GIR-ER — PyCharm-specific Codex Plan and PoC Checklist

**Status:** Research-feasibility PoC execution plan, updated 31 October 2026 to incorporate primary-paper comparison of LACE (2022), ASPEN (2024), and ASPEN+ (2025). This is an amended implementation contract, not a completed experiment, approved final algorithm, or validated research result. The original comprehensive plan follows below, subject to the updated instructions in Sections A–G.

## A. Verified visible project layout and immediate corrections

From the screenshot, the PyCharm project root is `~/Downloads/KG/risk aware/poc` and contains:

```text
poc/
  data/
    raw/
      re_docred/
        data/                  # visible extra folder; inspect contents; not assumed empty
        train_revised.json
        dev_revised.json
        test_revised.json
  AGENTS.md                    # existing Codex instructions
  GIR_ER_PyCharm_Codex_Plan.md # current governing execution plan
```

The earlier PyCharm screenshot showed **`<No interpreter>`**. Check the *current* setting; this does not prove Python is missing, and Python 3.12.15 was previously confirmed in the terminal. Configure PyCharm to use `poc/.venv/bin/python` via Settings/Preferences → Project: poc → Python Interpreter → Add Interpreter (Existing Environment after virtual environment creation). Do not create an additional nested `gir-er-pilot/` directory; use existing `poc/` as the pilot repository root. The `data/raw/re_docred/data/` folder's content is unknown from the screenshot: inspect, do not delete by assumption. The three JSON files are visibly directly inside `re_docred/` and match the path used in the original plan.

In the project-root terminal:

```bash
pwd
python3.12 --version
git status --short
# If .venv does not exist: python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install networkx pandas rapidfuzz pytest
# Verify existing .gitignore entries instead of reinitialising Git:
git check-ignore .venv data/private_gold 2>/dev/null || true
```

Git and `.gitignore` are already set up: **do not run `git init`, recreate `.gitignore`, or rename an already-correct `AGENTS.md`.** Inspect whether `.venv/`, `__pycache__/`, `.pytest_cache/`, and `data/private_gold/` are ignored; decide separately whether raw data is tracked according to licence and provenance rules. If `.venv` already exists, verify it rather than overwriting it. In PyCharm set interpreter to `.venv/bin/python`. Back up source files and generate SHA-256 checksums; never alter source JSON. `evaluation.py` in the original Re-DocRED repository is not needed for pilot graph-merging experiments.

**Required literature-context access for subsequent phases**: Make `FYP_Master_Research_Context.md`, `supervisor feedabck.md`, `pprs draft 2 tharuka.md`, `lit review draft.md`, and `GIR-ER_SE_Proposal_Critical_Review_lit_review.md` readable to local Codex under `docs/research_context/` or a clearly documented local path. Include the verified LACE/ASPEN/ASPEN+ comparison as a literature note (not as an experimental result). Files available only within this ChatGPT conversation are **not automatically available** to local Codex. A Phase 0 data audit may proceed if some literature files are missing, but record that limitation; do not begin identity-risk method design without the authoritative research context.

## B. Checklist coverage: previous plan versus six requested research tasks

| Requested checklist item | Covered by existing full plan | Actual status visible now | Phase gate |
|---|---|---|---|
| 1. Dataset inspection | Phase 0 (audit) and Phase 1 (provenance graph) | JSON files present; no audit output shown | Audit and document dataset suitability |
| 2. Candidate preparation | Phase 2 | No candidate/independent gold files shown | Human-check genuine/synthetic identity cases separately |
| 3. Question and reference annotation | Phase 3 | No fixed queries/answer references shown | Verified two/three-hop QA; gold isolated |
| 4. Graph simulation | Phase 4 | No code or test results shown | Temporary merges, answer-delta and nonmutation tests |
| 5. Evidence and baseline comparison | Phases 5 and 6 | No checked evidence/compared baselines shown | Evidence definitions, same-source baselines and approved risk-v0 rule |
| 6. Feasibility decision | Phase 7 | No empirical report shown | Reproducible honest GO/CONDITIONAL/NO-GO report |

These tasks are **planned, not completed**. Prior checking of uploaded JSON file structure in ChatGPT is a useful preliminary audit, but it is not evidence that a local reproducible Phase 0 or any later phase has been run.

## C. Is this a proof of concept?

- **Phase 0–3**: PoC preparation (audited data, cases and gold labels, typed graph and queries).
- **Phase 4**: Demonstrates the core mechanics of a reversible merge affecting query answers (a limited technical PoC).
- **Phases 5–7**: Makes it a meaningful **research-oriented GIR-ER feasibility PoC**, by assessing support/contradiction/unresolved and testing against same-evidence baselines.
- **Not the full FYP**, and not proof of global novelty, statistical superiority, or a generalisable method; larger held-out experiments, multi-merge testing and deeper comparisons are follow-on work.

## D. Mandatory human review/approval gates

1. **Phase 0:** confirm schema audit, evidence coverage and whether Re-DocRED supports real candidate cases.
2. **Phase 2:** independently annotate/correct identities; Codex must not invent gold negatives, treat separate vertexSet groups as necessarily different, or use private fragmentation mapping as prediction inputs.
3. **Phase 3:** confirm source-consistent typed multi-hop query semantics, freeze queries before testing outcomes.
4. **Phase 5:** approve written definitions of SUPPORTED / CONTRADICTED / UNRESOLVED, operational evidence constraints and any human review role.
5. **Phase 6:** approve a transparent risk-v0 policy and fixed review thresholds before testing. B3+same-evidence comparison is required.
6. **Phase 7:** personally inspect failures and costs. Keep unknown gold labels out of definitive identity metrics; no invented benchmark results.

## E. First Codex prompt (Plan mode; NO modifications yet)

> You are working inside an existing PyCharm project rooted at `~/Downloads/KG/risk aware/poc` on macOS with Python 3.12.15. This is a research feasibility PoC for GIR-ER: Graph Impact Risk-Aware Entity Resolution for Reliable Knowledge Graph Construction. Read `AGENTS.md`, `GIR_ER_PyCharm_Codex_Plan.md`, and available files in `docs/research_context/` before planning. Inspect the files `data/raw/re_docred/{train_revised,dev_revised,test_revised}.json`. Note that `data/raw/re_docred/data/` is an extra visible folder; inspect its contents and do not remove it without permission. Verify that PyCharm has a valid interpreter at `.venv/bin/python` or report how to set it. **Only plan Phase 0**: read-only audit of JSON integrity, source schema, entity mentions, relation labels, missing evidence pointers, duplicate-document risks, provenance, and suitability for legitimate positive/negative pairs and typed 2/3-hop queries. The research hypothesis — source-grounded counterfactual answer-impact improving ER beyond a same-evidence baseline — is unvalidated. Explicitly list any scientific assumptions, leakage risks, exact output files and acceptance tests. Do not implement Phase 1–7; do not change raw datasets; do not fabricate identity/QA labels or choose final risk weights. Present the Phase 0 plan and stop for student approval.

## F. After Phase 0 is approved

Use the integrated plan below one phase at a time. Every Codex phase must end with files changed, exact commands run and outcomes, tests, unresolved issues, and a **STOP** for the student's review. Avoid polished UI, LLM API calls, knowledge-graph novelty claims and automatic ground-truth generation during this PoC.

## G. Literature-review amendments — LACE, ASPEN, ASPEN+ (31 October 2026)

The review of the actual papers establishes that **LACE (Bienvenu et al., 2022)** already formalises recursive collective ER, hard/soft merge rules, denial constraints, merge justifications and possible/certain query answers. **ASPEN (Xiang et al., 2024)** implements LACE with ASP, explanations, solution approximations and empirical ER evaluation. **ASPEN+ (Xiang et al., 2025)** implements extensions supporting local value merges and alternative solution optimality criteria, with measured accuracy–runtime trade-offs. The underlying local-merge framework **LACE+ (Bienvenu et al., 2023)** also predates ASPEN+. **Do not claim that constraint-aware ER, recursive merging, query reasoning, merge justification or local value merging is new to GIR-ER.**

**Research distinction to test, not assume:** Does a candidate-specific, before-commit *change in a selected two-/three-hop QA workload*, assessed using independently permitted source evidence, add discriminative information compared with an equally informed strong identity/constraint-aware method? This is not a proof of global novelty. A suitably expressive logical rule system may represent related safeguards.

**Minimal amendments to existing phases (no restart):**

- **Phase 0:** Continue reproducible data auditing. Count *structural paths* only; do not label them semantically valid inference, source-verified QA or beneficial/harmful merges.
- **Phase 1–2:** Preserve entity identity, source provenance, and original vs induced graph facts. Do not confuse local textual aliases with global real-world IDs.
- **Phase 3:** Distinguish four levels: structural path → semantically interpretable relation pattern → proposed QA template → independently verified QA answer. Freeze workload before checking risk-method outcomes.
- **Phase 4:** Keep immutable temporary merges and stable answer-identity mapping; report new/removed answers but not truth without separate evidence.
- **Phase 5:** Before implementation, specify distinct evidence targets: **identity equivalence**, **source triple**, **compositional path meaning**, and **resulting answer**. Record which premise each source supports; source pointer validity alone is not evidence of truth. Unknown must remain UNRESOLVED, not contradicted.
- **Phase 6:** Separate matcher confidence, answer-change severity, evidence-conditioned assessment, and final ACCEPT/REJECT/REVIEW rule. Keep B3+same-source primary control, count-only ablation, and full GIR-ER. **Consider** a constraint-aware comparable control inspired by LACE/ASPEN where compatible, but do not claim an unimplemented imitation is an exact ASPEN reproduction. Do not mandate an ASP solver for the PoC.
- **Phase 7:** Include a **bounded, labelled sequential-merge A–B–C test with at least two merge orders** as a separate diagnostic outcome, not only isolated pairwise tests. Report cluster consequences and extra cost separately. Broad sequential/scale experiments remain optional post-PoC work.

**Decision checkpoints:** No final risk weights or thresholds chosen now. Any source-evidence runtime verification (automatic or human-assisted), optional constraint comparator, and sequential merge evaluation protocol require transparent rationale and student review before implementation. These amendments refine the existing research direction and do not affect already validated Phase 0 artefacts.


---

# GIR-ER — Codex Execution Plan for the Re-DocRED Feasibility Pilot

**Status:** Proposed execution contract for student review; not an implemented research system or an approved final methodology.  
**Project title:** GIR-ER: Graph Impact Risk-Aware Entity Resolution for Reliable Knowledge Graph Construction.  
**Prepared:** 29 October 2026.  
**Recommended Codex model:** GPT-6.1 Sol, High reasoning (use GPT-6 Astra, High, for critical algorithm/experimental design review if available).  
**Scope:** A reproducible, honest *pilot* on the supplied Re-DocRED data, not the full FYP, not a paper, not a deployed service, and not a claim of novelty or improvement.

## 0. Governing research context and status

### Research question

Does an additional **source-evidence-conditioned, candidate-specific counterfactual multi-hop answer-impact signal** improve decisions about whether to consolidate two entities in a text-derived KG, beyond an equally informed semantic+structural matcher?

Preserve the established research direction: entity consolidation **after relation/entity extraction and before committing identity merges**. Do not redesign GIR-ER into generic GraphRAG, a chatbot, neural KGQA, a universal KG framework, or a new LLM architecture. The source documents and revised KG annotations provide an experimental starting point; extraction itself is held fixed to isolate the merge decision. Human/LLM annotation and risk-scoring details remain hypotheses, not confirmed findings.

The research method is Design Science Research with quantitative controlled experiments and case-based error analysis, as proposed in the student's working draft, not a final supervisor-approved specification. Ensure every result distinguishes source finding, experiment, human annotation, algorithmic output, and interpretation.

### Prior art boundaries

- **LACE (Bienvenu et al., PODS 2022):** logical, recursive and constraint-aware collective entity resolution, justified merges and possible/certain query answers.
- **LACE+ (Bienvenu et al., 2023):** formal local value merges alongside global object merges; see the exact publication for technical scope.
- **ASPEN (Xiang et al., KR 2024):** executable ASP-based LACE system for collective ER, explanations and empirical accuracy/runtime evaluation.
- **ASPEN+ (Xiang et al., KR 2025):** local merges, alternative preferred-solution criteria, empirical accuracy/runtime trade-offs; it has already analysed erroneous global conflation scenarios.
- **Fagin et al. (KR 2023):** formal entity equivalence + rule-driven query answering; GIR-ER must NOT claim to be the first ER+QA work.
- **Graphusion (2025):** global KG fusion, entity merging, retrieved source context and conflict handling; GIR-ER must NOT claim novel context/source-informed fusion alone.
- **KGGen (2025):** semantic, LLM-assisted entity/relation deduplication; GIR-ER must NOT treat existing deduplication as merely string matching.
- **Altwaijry (2015):** query-aware ER; GIR-ER must NOT claim first awareness of downstream query consequences.
- **Pavani et al. (2026), and other verified-clustering work:** re-verification of potentially unsafe merges already exists.
- **Cai and O'Connor (2025):** downstream effects of KG extraction errors already studied.

**Open hypothesis:** the proposed **pre-commit counterfactual answer delta with independent source evidence**, under fair same-evidence ablations, adds useful discriminative information. This pilot must also be capable of revealing zero or negative incremental value.

### Available research inputs

- `FYP_Master_Research_Context.md` — master status, confirmed decisions, open methodological questions.
- `supervisor feedabck.md` — draft review/correction guide, particularly data, leakage, reversible merges and same-evidence comparator.
- `pprs draft 2 tharuka.md` — provisional Chapters 1 and 3 through §3.5.3.
- `README.md` — official dataset description; `README(1).md` is only `data dir` and is not scientific context.
- `train_revised.json`, `dev_revised.json`, `test_revised.json` — uploaded Re-DocRED dataset files. Copy to `data/raw/re_docred/`.
- Research PDFs, especially Graphusion, KGGen, Fagin, Altwaijry, Cai and O'Connor. They are optional *runtime inputs* to code; retain as readable research references, with citations checked separately.

### Verified uploaded data facts (from JSON parsing, not independent semantic annotation)

| Split | Documents | Relations | Entity groups | Relations with non-empty `evidence` | Relations with empty `evidence` |
|---|---:|---:|---:|---:|---:|
| Train | 3053 | 85932 | 59359 | 47260 | 38672 |
| Dev | 500 | 17284 | 9684 | 7473 | 9811 |
| Test | 500 | 17448 | 9779 | 7547 | 9901 |

The files parse as JSON, with `title`, `sents`, `vertexSet` and `labels`; mention objects include `name`, `type`, `sent_id`, `pos` (sometimes additional positions/index fields). Relation objects contain `h`, `t`, `r`, and `evidence`. Re-DocRED `vertexSet` groups are **within-document coreference groups**, not ready-made cross-document identity labels. `r` uses Wikidata-style property codes (`P17`, `P131`, etc.). Empty evidence is **missing explicit sentence annotation**, not contradiction and not necessarily an incorrect relation.

These checks do NOT establish cross-document identity, source-truth completeness, verified multi-hop answers, or GIR-ER effectiveness.

## 1. Before any code: human preparation and Codex preflight

**Required from student:**

1. Use the **existing** PyCharm `poc/` Git repository (already initialised); do not create a nested `gir-er-pilot/` repository or run `git init` again.
2. Copy the three uploaded JSONs to `data/raw/re_docred/`; preserve original bytes and record SHA256 hashes. Git-ignore raw dataset if redistribution/license is uncertain; record original dataset license and provenance/URL. Do not upload private gold labels to a public Git repository.
3. Make these research files locally accessible: `FYP_Master_Research_Context.md`, `supervisor feedabck.md`, `pprs draft 2 tharuka.md` (optional research PDFs). Codex cannot read documents only present in a different ChatGPT conversation unless separately mounted/copied into its workspace.
4. Use Python 3.11+ (3.12 is fine), Git, a virtual environment, and local disk/memory suitable for ~25 MB raw JSON (plus in-memory data structures); no GPU needed for deterministic stages.
5. Confirm this pilot is strictly exploratory; selected primary dataset, evidence rules, risks, final thresholds and final study sizes are not adopted by this plan.
6. Student retains ownership of gold annotation, scientific judgements, baseline decisions, acceptance criteria and the final report. The coding assistant must not fabricate labels or claim to have completed manual independent verification.

**Existing macOS project root (do not recreate):**

    cd ~/Downloads/KG/'risk aware'/poc
    git status --short
    # If .venv does not exist: python3.12 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip

**Environment note:** This pilot currently runs in the existing macOS PyCharm `poc/` repository. Do not create or initialise a separate repository. **Do not** assume Codex CLI or ChatGPT has implicit file access.

**Model selection:** GPT-6.1 Sol High for plan+implementation; GPT-6 Astra High for review if available. Do not use a generative LLM to manufacture authoritative identity labels. No OpenAI API key is required for the initial deterministic pilot. A local pretrained embedding model may be added later for semantic baseline, and its name/version must be recorded.

**Codex must start read-only:** inspect files, hashes, schemas, environment, requirements, and this plan; report discrepancies and propose phase-0 artefacts. **Do not start the entire project in one unreviewed pass.** Finish one phase, run tests, report outputs and wait for the student to select the next phase. Never modify `data/raw/`.

## 2. Scope and explicit non-goals

**In scope:**

- Dataset schema/stats audit; extract source-bearing mentions and relation triples.
- Structured candidate discovery without pretending automatically generated pairs are ground truth.
- Candidate source/annotation worklist for 20–30 pairs, including positive, hard-negative, uncertain and no-change cases where evidence exists.
- Structured 2-hop and 3-hop query templates (initial target about 10–15 or 12–18, subject to evidence availability) with fixed typed direction and evidence-path tracking.
- Temporary merge simulation; exact baseline-vs-merge query answer differences; immutable raw graph and auditable provenance.
- Operational evidence *protocol* for `SUPPORTED`, `CONTRADICTED`, `UNRESOLVED`; when automation is unjustified, leave review-required and expose limits.
- B1 name, B2 semantic where feasible, B3 semantic+structural, B3+same-source, B3+same-source+count-only, full GIR-ER (once a risk-v0 rule is agreed).
- Pilot-level correctness, QA, review-rate, runtime, and reproducibility reports; small sample **not** significance claims.

**Not in scope until explicitly approved:**

- Full KGGen/Graphusion reconstruction, API calls/paid LLM pipelines, fine-tuning, GNNs, full web app/Neo4j, LLM-as-oracle labels, automatic cross-document gold alignment, full research-paper claims, releasing raw data or annotation files, modifying Chapters 1–4 as if experimental results were confirmed.

## 3. Dependency recommendations

Keep dependencies minimal and pin reproducible versions in `pyproject.toml`/lockfile or `requirements*.txt`:

- Python standard library (`json`, `csv`, `hashlib`, `pathlib`, `dataclasses`, `collections`, `logging`, `time`).
- `networkx`: bounded typed directed multigraph and temporary contraction mechanics (or a deliberate custom representation with unit tests).
- `pandas`: audit outputs / CSV handling, optional.
- `rapidfuzz`: simple name-based matcher.
- `pytest`: tests; `pytest-cov` optional.
- `sentence-transformers` and a small **version-pinned** pretrained embedding model only after base pilot mechanics; CPU execution first.
- `psutil`: optional memory profiling. No generative LLM API and no need for original repository `evaluation.py` to evaluate GIR-ER merges.

Explain each dependency. Avoid package version invention; determine a working compatible set in the actual environment and freeze it.

## 4. Repository layout and data boundary

    gir-er-pilot/
      AGENTS.md
      README.md
      PLANS.md                      # copy of this plan or link, preserved as project contract
      pyproject.toml
      .gitignore
      docs/
        research_context/          # user-provided reference texts; not runtime features
        data_dictionary.md
        annotation_guide.md
        decision_log.md
        pilot_feasibility_contract.md
      data/
        raw/re_docred/             # immutable train/dev/test JSON; do not commit by default
        prepared/                  # normalized source-derived data; never contain gold labels
        private_gold/              # human-validated identities, QA answers, split map; Git-ignored
        worklists/                 # annotation tasks, empty label slots and evidence pointers
      src/girer/
        __init__.py
        schemas.py
        io_re_docred.py
        audit.py
        graph.py
        candidate_discovery.py
        query.py
        merge_simulation.py
        evidence.py
        matchers.py
        experiment.py
        evaluation.py
        cli.py
      tests/
        fixtures/
        test_loader.py
        test_graph.py
        test_queries.py
        test_merge.py
        test_evidence.py
        test_splits.py
        test_no_gold_leakage.py
        test_metrics.py
      experiments/
        pilot_config.yaml
      results/                     # reproducible outputs, metadata, per-case errors
      scripts/
        audit_dataset.py
        export_worklist.py
        run_toy_sanity.py
        run_pilot.py
        score_predictions.py

Only add files as each phase warrants them. `private_gold` is never passed to a production inference function. `score_predictions.py` is the only program allowed to read it. No mention/cluster gold identity map may be smuggled into feature generation, filenames, obvious IDs, prompt context, outputs or logs.

### Proposed data contracts

**Source document:** `doc_id` (stable split+index, not title alone), `split`, `title`, `sentences` (list token lists), `source_hash`.

**Mention:** `mention_id` (`split:doc-index:entity-index:mention-index`), `name`, `type`, `sent_id`, `pos`, `doc_id`; do NOT expose raw `vertexSet` gold-group index as an identity feature in controlled-fragmentation experiments.

**Original entity-group annotation:** held in preparation/evaluation layer; within-document `vertexSet` indices signal existing coreference and must NOT be used as model-side gold feature for positives created by splitting that group.

**Triple:** `triple_id`, `subject_node_id`, `relation_code`, `object_node_id`, `doc_id`, `evidence_sentence_ids` (possibly empty), `evidence_status` (ANNOTATED_WITH_EVIDENCE / ANNOTATED_NO_EVIDENCE), `source_triple_label_index`, `derived_or_original`.

**Candidate:** `candidate_id`, `left_node_id`, `right_node_id`, `creation_mode` (`naturally_observed`, `controlled_fragmentation`, `adjudication_required`), `selection_rule_id`, `split`, and **no gold identity label** in inference file.

**Private gold:** `candidate_id`, `same_entity` (`true/false/unknown`), independent support references, verifier ID/method, confidence/notes, `positive_fragmentation_parent` if applicable. A gold `unknown` is excluded from definitive identity metrics and counted in feasibility/coverage.

**Query:** `query_id`, `hop_count` (2 or 3), `anchor_node_id`, ordered relation codes and directions, output-variable semantics, workload/template-selection rule and provenance. Preselect templates by an outcome-blind rule; freeze them before candidate evaluation. Do not generate a tailored 'gotcha' query for each wrongly merged candidate after seeing its gold label and treat it as an independent performance test.

**Private QA gold:** `query_id`, verified answer IDs/sets, supporting source references and adjudication; do not give this to matchers/risk scoring.

**Prediction:** candidate ID, before/after answers and paths, added/removed/unchanged answers, source provenance, B1/B2/B3/same-evidence/count-only/full predictions, evidence states, decision explanation, review reason, runtime, config/version fingerprint.

## 5. Implementation phases — stop at every gate

### Phase 0 — Read-only preflight, experimental contract and scaffolding

**Actions:** Read research context/feedback/draft. Verify Python version and file paths. Hash original files. Parse each JSON. Count documents, entity groups, mentions, triples, missing `evidence`, distinct relation codes, and document-level source IDs; inspect randomly selected records from dev/train without using test for feature choices. Inspect license, relation-name metadata availability. Verify that original `evaluation.py` is not necessary for this study. Draft `docs/pilot_feasibility_contract.md` and `docs/decision_log.md` with unresolved topics. Create initial skeleton, `.gitignore`, README and unit test runner only after preflight approval.

**Must not:** Modify raw JSON, silently pick final dataset/thresholds, manufacture gold, include test labels in development, download huge models, initiate API charges.

**Acceptance:** All three datasets load and are schema-consistent; results explicitly show missing evidence counts; accurate split hashes and source file lineage; run is repeatable; unresolved method questions enumerated. Stop and show student the audit.

### Phase 1 — Normalized source graph with provenance

**Actions:** Create loader; build a *directed typed multigraph* from subject (`h`), relation (`r`) and object (`t`). Preserve parallel predicate types, repeated triple occurrences and original evidence pointers. Use source-scoped IDs so entities from different documents do not collapse through identical strings. Keep repeated triples either as parallel edges or unique provenance bundles with explicit documented semantics. Identify self-loops, duplicate labels and cross-document matches separately, without deleting them silently. Provide a relation-code dictionary; if mapping (`P###` -> readable relation) is unavailable, retain codes and note limitations. Annotated triples with no evidence remain traceable but must not be promoted to independent verified support.

**Acceptance:** 1:1 traceability from each extracted relation record to original `doc_id` and label index; graph counts reconcile; no unintended cross-document joins; sampled source sentences reconstruct correctly; tests include multirelations, empty provenance and self loops.

### Phase 2 — Candidate discovery and student annotation worklist

**Actions:** Generate potential within-document positive scenarios from multi-mention `vertexSet` groups, but do NOT label them as real-world deployment positives without qualification. For controlled fragmentation, retain a private original group-to-mention mapping and carefully allocate relations to fragments using sentence evidence; if attribution is ambiguous, flag it and skip or send to human review. Crucially, do NOT copy every original incident edge to both aliases: that can eliminate the desired graph-fragmentation mechanism or fabricate evidence. For natural hard negatives, look for similar names/abbreviations/types *without treating 'different group' or 'different document' as automatic evidence of nonidentity*. Produce human-reviewed worklists and blank gold-label templates with source excerpts/links. Seek a balanced *target* around 20–30 verified cases (e.g., 8 positives, 8 hard negatives, 4 other negatives, 4 sparse/uncertain); reduce counts if verification is not possible. Track naturally observed vs induced/split cases separately.

**Acceptance:** Every candidate has reproducible source provenance, generation method and a reviewable evidence dossier. No 'known different' labels are automatically manufactured. Unknown/ambiguous remain unknown; annotator can inspect original sentences. Human reviews and freezes pilot reference labels before scoring.

### Phase 3 — Fixed directed 2-hop and 3-hop QA workload

**Actions:** Select relation patterns using development graph statistics plus predeclared rules (e.g., typed 2-/3-edge directed chains with meaningful anchors). Return *sets of answer entity IDs* and path provenance; do not invent natural-language text for semantic truth. Avoid treating relation-code combinations as logically valid entailments without checking their semantics. Build 10–15 (or 12–18 if feasible) source-checkable query cases and annotation worklists. Retain direction, anchor remapping, self loops, parallel edges, repeated answers, zero-answer cases, and stable IDs. Gold answer verification must be independent of GIR-ER's prediction and use source text/identity facts. Keep experiment query inputs (templates) separate from private correct-answer lists.

**Acceptance:** Deterministic correct outputs on hand-constructed toy cases; human-verifiable pilot queries; no selected query relies only on private gold identity features; query set frozen before performance comparison.

### Phase 4 — Temporary merge / counterfactual answer delta

**Actions:** For each candidate, run the exact same queries before and after a *copy-based* hypothetical merge. Preserve node origin IDs, edge directions, relation types, source evidence; assign a temporary canonical ID and explicit projection `original_id -> temporary_id`. Compare answers after mapping canonical representations back to stable entity-reference semantics; a mere renamed ID is not an added answer. Track `added`, `removed`, `unchanged`, affected query count, 2-hop and 3-hop separately; include all changed source paths. Unaffected queries are recorded, not assumed to prove safety. No permanent modifications; catch exceptions/timeouts/bounded-query truncation and return INCOMPLETE or REVIEW rather than SAFE. Provide an explicit cluster policy for multiple sequential merges in a later phase, not during isolated pilot case checks.

**Tests:** harmful 2-hop false connection, beneficial correct 2-hop, correct 3-hop, false/no-change case, identifier-only renaming, two relation types between same nodes, duplicate edges, loop, rollback on exception, timeout/truncated search. Compare graph hash before/after, ensure byte-identical source and unchanged input graph.

**Acceptance:** Deterministic before/after query deltas on fixtures; rollback tests pass; ID projection does not produce phantom answers; source evidence remains traceable; code is independently understandable by the student.

### Phase 5 — Evidence annotation protocol and conservative operational checker

**Actions:** Before writing code, define which proposition is being assessed separately at four levels: (i) candidate entity identity, (ii) underlying original relationship triple, (iii) semantic validity of joining the path, (iv) resulting answer truth/support. Keep this decomposition auditable and do not infer (iv) merely from source support for (ii). Then write `docs/annotation_guide.md` with definitions and examples:

- `SUPPORTED`: permitted independent original evidence supports the identity proposition or resulting inference, including any identity premise essential to the new path.
- `CONTRADICTED`: permitted independent evidence or a justified domain constraint establishes incompatibility; never treat multiple affiliations or absence from a source as contradiction automatically.
- `UNRESOLVED`: neither sufficient support nor contradiction; includes missing sentence indices, ambiguous identity, absent documents, conflicting/low-quality evidence, or inability to complete the check.

Store citation-like `doc_id`, sentence ID(s), and a machine-readable rationale. Separate *gold* human adjudication from *operational* source evidence. If evidence cannot be automatically classified without human labels/LLM, implement a conservative rule-based/provenance checker returning UNRESOLVED and a review worklist; do not claim automated evidence understanding. Optional human-assisted operational evidence is allowed **only if reported as human-assisted**, with measured time and identical assistance budget for comparable baselines. Under no circumstances use a private `same_entity`, `correct_answer`, or positive-fragmentation-parent map in evidence classification.

**Acceptance:** Every changed answer gets a defined evidence status or explicit incomplete; sample disagreements and unknowns are retained; prompt/data leakage tests pass; false certainty is not rewarded.

### Phase 6 — Baselines and provisional risk-v0 policy

**Actions:** Implement:

- B1 normalized/fuzzy names.
- B2 semantic text embeddings (may be postponed until baseline resources installed; report exact model/version).
- B3 semantic + structural/contextual features, transparently tuned on development only.
- B3+source: **identical permitted source material**, without graph-change evaluation.
- B3+source+count-only: same source and counterfactual answer change *counts* without states.
- Full GIR-ER: same source + changed-answer evidence states (and count features), with a versioned, deterministic decision rule.
- Optional, conditional control: a transparent constraint-aware ER variant inspired by LACE/ASPEN, **only** when justified constraints exist for the selected text-derived cases; document coverage, fair evidence access and compatibility. Do not call this 'ASPEN' unless the original published system is actually run faithfully on compatible inputs.

Before phase 6 actual classifier, propose **at least two** candidate risk-v0 policies, their cost, and boundary behaviours; explain design trade-offs and request the student's explicit adoption of one. Do NOT silently choose weights, thresholds, class labels, LLM oracle or a supposedly proven scoring formula. Use development data only for settings, and lock before any genuine held-out final test. Include ACCEPT/REJECT/REVIEW; REVIEW does not count as accepted and the graph is not updated. A merge with zero changed selected answers is **not automatically accepted**. Different permissible evidence available across baselines is forbidden for the primary attribution comparison.

**Acceptance:** Side-by-side feature vectors demonstrate B3+source and full GIR-ER have exactly the same source documents; features and thresholds are versioned, code paths separated; review/no-change/tie cases defined.

### Phase 7 — Pilot run, failure analysis and feasibility report

**Actions:** Run isolated candidate-pair experiments with exactly the same initial graph and candidate order as applicable. Do not infer complete incremental clustering outcomes from pairwise-only experiments. Additionally conduct a **small predeclared A–B–C sequential-merge diagnostic**, applying at least two candidate orders on separately reset graphs; report resulting cluster equivalences, changed answer sets, correctness against the appropriate private reference, and runtime. Keep this bounded diagnostic distinct from the larger final-study collective ER evaluation. Record candidate confusion counts (with unknown separately), accepted-merge precision, true-merge recall, false accepted counts and denominators, review coverage, downstream QA precision/recall separately for 2-hop and 3-hop, new false answers (only against independently verified answer sets), run time including evidence checking, peak memory and annotation effort. If a query has no gold answers, define denominator convention and report counts, not silent NaN/zero substitutions. Maintain separate results by `natural` vs `controlled_fragmentation`, and source-evidence coverage.

Perform qualitative error audit: harmful/beneficial/new-answer and no-change cases, false rejection, false acceptance, unresolved evidence, query selection bias, and whether same-evidence matcher already solved the case. Summarize **observed** result, small sample limitations, confounders, missing evidence and a recommended next study gate. Do NOT claim formal statistical superiority from 20–30 pairs, or novelty proof, or 90+ marks.

**Acceptance:** Full rerunnable pilot with logs/config/hash, exact comparable denominators, failures included, no private labels consumed during inference, an honest `results/feasibility_report.md` with GO / CONDITIONAL / NO-GO judgement and requirements for expansion.

### Phase 8 — Optional extensions; require separate student authorization

Only after the pilot is scientifically defensible: held-out source-family and query-template tests, **larger-scale** sequence-of-merges/transitive closure and merge-order sensitivity, larger dataset, efficient incremental query evaluation, controlled alternative extraction pipelines, Graphusion/KGGen compatibility analysis, interactive small graph display, full Chapter 3 evaluation results, ethics/LESP documentation. Do not auto-start.

## 6. Core graph/query semantics (must be documented before Phase 4)

1. Graph is directed and relation-typed; same pair may have several relation types. Keep parallel provenance.
2. Query is a **fixed ordered relation sequence** of length exactly 2 or 3, with an anchor and direction per hop. Return answer ID set and supporting path ID sequences.
3. Avoid generic unlabeled path counting as a substitute for meaningful typed queries.
4. Map candidate-affected anchor IDs and answer IDs under merges; distinguish result changes from string/ID renames.
5. Contraction preserves underlying asserted edge provenance; do not infer source verification from edges created solely by the hypothesis.
6. Empty source evidence is missing annotation; missing truth is NOT falsehood. `UNRESOLVED` is legitimate, not a classifier failure to hide.
7. If bounded search is incomplete, output INCOMPLETE/REVIEW. Do not interpret absence of observed change as proof of merge safety.
8. Repeated runs are deterministic given frozen code/data/seed/config.
9. Under isolated assessments, each candidate starts from identical unmerged graph; do not accidentally carry earlier hypothetical merges into later candidates.
10. Query composition from source triples is a *graph-path answer*; do not claim every relational composition is a justified real-world entailment without verifying relation semantics.

## 7. Required tests and negative controls

- Schema invalid fields, bad entity index, out-of-bounds evidence sentence, duplicate IDs: diagnostic errors without corrupting state.
- `vertexSet` multi-mention coreference group: identity parent confined to private preparation/gold; operational pair file cannot reveal original group ID.
- Cross-document same name: remains two different nodes until separately verified; never auto-label as different.
- Positive split case with distributed, sentence-supported edges: new useful answer, no edge fabrication.
- Negative candidate with similar names and different facts: false cross-context answer can be demonstrated, but judge harmful only with independent gold/evidence.
- Incorrect merge changing zero selected answers: impact feature no evidence of safety.
- Correct merge with added answers: counts-only risk must not necessarily reject.
- No gold leakage: block attempts to call evaluation data from inference modules; assert no `gold_`/`parent_entity_group` in model-facing features.
- Same-evidence audit: assert exact permitted source IDs/text/versions equal for same-evidence and full GIR-ER.
- Metamorphic test: change only display node IDs, answer meaning unchanged.
- Bounded query exceeded: explicit incomplete state; no ACCEPT solely for 'zero observed delta'.
- Source evidence disagreement: cannot treat all differences as contradiction.
- Test data never used to tune risk weights, thresholds or semantic model choice.
- Analysis checks: denominators, abstentions, zero denominators, mixed natural/synthetic records, 2/3-hop scores, cluster-vs-pair metric labels.

## 8. Suggested precise commands once repo is prepared

After Codex creates executable modules and locks dependencies, document commands in README such as:

    python -m pip install -e '.[dev]'
    pytest -q
    python scripts/audit_dataset.py --data-dir data/raw/re_docred --output results/dataset_audit.json
    python scripts/run_toy_sanity.py --out results/toy_sanity.json
    python scripts/export_worklist.py --split dev --out data/worklists/candidates_dev.csv
    python scripts/run_pilot.py --config experiments/pilot_config.yaml --out results/pilot_predictions.jsonl
    python scripts/score_predictions.py --predictions results/pilot_predictions.jsonl --gold-dir data/private_gold --out results/pilot_metrics.json

These are **target commands**; Codex must implement their actual CLIs and test them rather than falsely claim these scripts exist now. `score_predictions.py` should not share its gold loader with `run_pilot.py`. The evaluator must run only **after** predictions have been saved. If annotation worklists are incomplete, pilot prediction/metrics stages should report BLOCKED rather than fabricate ground truth.

## 9. Required output artefacts and gate review checklist

**Phase 0 outputs**: file audit, exact hashes, split summary, environment versions, unresolved decisions, contract for a pilot and proposal of dataset selection.  
**Phase 1 outputs**: normalized typed provenance graph with unit tests and sample triple traceability.  
**Phase 2 outputs**: candidates/worklist with no fabricated negatives; an explicit student annotation task, private gold schema.  
**Phase 3 outputs**: reproducible query templates, answer/path runner and gold-QA annotation worklist.  
**Phase 4 outputs**: tested reversible merge/delta computation.  
**Phase 5 outputs**: documented evidence protocol, conservative checker and unresolved-case reporting.  
**Phase 6 outputs**: feature-matched baselines, explicitly selected provisional risk-v0 policy, clear review semantics.  
**Phase 7 outputs**: predictions, metrics, human annotation costs, **small sequential-merge diagnostic**, failure analysis, feasibility verdict (possibly NO-GO).

At the end of EACH phase, Codex shall report:

- Changed files (only that phase).
- Commands executed and exact observed outcomes, not invented logs.
- Tests run and passed/failed.
- Any methodological deviation requiring student approval.
- Open scientific ambiguities, leak risks and unavailable labels.
- Next phase entry criteria; stop and await student review.

## 10. Initial prompt to paste into Codex — PLAN MODE ONLY (only if Phase 0 has not already been planned)

> You are working on my research-driven Computer Science FYP, GIR-ER (Graph Impact Risk-Aware Entity Resolution for Reliable Knowledge Graph Construction). Read `GIR_ER_PyCharm_Codex_Plan.md`, `AGENTS.md` if present, `FYP_Master_Research_Context.md`, `supervisor feedabck.md`, `pprs draft 2 tharuka.md` if present, and inspect the three raw Re-DocRED JSON files in `data/raw/re_docred/`. This is a dataset-and-method FEASIBILITY PILOT, not the entire FYP. My proposed novelty is an UNVALIDATED additional pre-commit counterfactual 2-/3-hop answer-impact signal assessed with independent source evidence. Preserve this scope; do not replace it with GraphRAG or LLM generation. Start in read-only PLAN MODE. Report exact available files, schema, missing evidence, limitations, proposed phases, dependencies, experimental risks, gold-data leakage protections, test gates, and any conflicts with the plan. Do NOT execute all phases or modify source data. Present a Phase 0 implementation proposal with acceptance criteria and wait for my approval before creating code. No fabricated identity or QA labels, no paid API calls, no external uploads, no claims of improvement.

## 11. First execution prompt AFTER approving Phase 0 (continue existing project; do not re-plan or restart)

> I approve Phase 0 only. Implement the minimal repository scaffold and **read-only** Re-DocRED schema audit specified in the plan. Keep source JSON immutable and outside inference outputs. Provide CLI commands, tests, data lineage/hashes, true observed split statistics and an unresolved-research-decisions list. Do not generate final gold labels, do not use `test_revised.json` for setting selection, do not implement risk scoring or expand into later phases. Run the tests and report exact outputs; then stop.

## 12. Suggested commands/prompts for subsequent review gates

- **Phase 1:** "I approve Phase 1 only. Build the provenance-preserving directed typed graph from revised DocRED data; demonstrate reconstructing exact source evidence and handle empty evidence safely. Write tests, run them, and stop."
- **Phase 2:** "I approve Phase 2 only. Generate a *review worklist* for genuine/constructed candidate pairs, keep within-document gold coreference hidden, do not auto-mark negatives, and produce blank human annotation templates. Stop before treating worklist as gold."
- **Phase 3:** "I approve Phase 3 only. Build deterministic fixed 2/3-hop typed query execution and traceable answer paths. Export human-verifiable questions without making up truth labels. Tests then stop."
- **Phase 4:** "I approve Phase 4 only. Implement immutable candidate merge simulations and identity-stable before/after answer delta, with fixtures for wrong/helpful/no-change cases, rollback and provenance. Tests then stop."
- **Phase 5:** "I approve Phase 5 only. Implement the source-evidence contract and conservative supported/contradicted/unresolved statuses. If verification requires human judgement, export a worklist; do not hallucinate source proof. Tests then stop."
- **Phase 6:** "Plan two deterministic risk-v0 rules and matching baselines using the same evidence. Do not select a final formula, thresholds or tune on test data until I choose the policy and review the validation protocol."
- **Phase 7:** "Run the pilot on frozen reviewed annotations and approved development configuration; include an explicitly bounded A–B–C two-order sequential diagnostic, separately report candidate metrics, cluster outcomes, reviewer workload, baseline fairness, limitations and failures. Do not claim novelty or significance. Stop."

## 13. Scientific integrity and responsible GenAI use

The student's responsibility is to understand and explain the actual code, algorithm, graph query, data selection, reference labels, metric definitions, ablation and failure cases. Each Codex-generated function should be accompanied by a small student-inspectable test. Record whether AI wrote code, proposed categories or drafted text. Do not submit Codex-generated explanatory text or synthetic labels as independently verified research evidence. Keep uncertain cases uncertain and report negative findings.

**Pilot scientific decision:** advance only if the evidence protocol is practicable and full GIR-ER *can be fairly compared* with B3+same-evidence. A positive research benefit requires observed incremental differences in appropriately controlled experiments; functionality alone is insufficient.
