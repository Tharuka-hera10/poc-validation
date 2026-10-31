# Phase 2 candidate preparation methodology

## Authority and limits

The student approved Phase 2 and then approved the explicit implementation plan: train-only discovery, exact alias/initialism blocks, a provisional 24-case natural review sample, PER/ORG/LOC selection, endpoint/key diversity and controlled feasibility only. This is not approval of labels, fragmentation, thresholds, query workloads or risk design. Phase 0/1 code, results and raw data remain unchanged.

The available master research context summarizes historical feedback. Separate supervisor feedback, proposal draft, literature draft, critical literature review and primary papers are unavailable locally. No direct supervisor decision or new literature verification is asserted. LACE/ASPEN/ASPEN+ boundaries in AGENTS.md remain authoritative project instructions.

GIR-ER's unvalidated question is whether source-grounded, candidate-specific counterfactual multi-hop answer changes add value beyond an equally informed strong matcher. Candidate preparation is infrastructure. It cannot establish novelty, identity correctness or effectiveness.

## Discovery version phase2-candidates-v1

The verified Phase 1 loader checks schema, indices, bytes and Phase 0 fingerprints. Train's MultiDiGraph is reconstructed and every node/edge reconciled under strict FULL_SPLIT validation. No graph mutation or cross-document consolidation occurs.

Each original train entity group is a discovery unit. All mention names/types remain original source values. Derived exact-name keys use casefold and whitespace collapse; punctuation is retained. Empty normalized keys do not block pairs. A Unicode `\w+` tokenization derives single-token short forms and initials of names containing at least two tokens. Match a short form exactly to those initials. No stopword list, fuzzy threshold, embedding, semantic judgement or API is used. Dotted abbreviations and aliases requiring linguistic knowledge can be missed; accidental initialism matches are expected.

Enumerate every distinct unordered pair in exact alias blocks and short-form/initialism cross-blocks. Exclude self-pairs. A pair can retain both rule reasons, but appears once. Within-document and cross-document pairs remain distinct source groups with UNKNOWN identity until review. In particular, separate groups are never negative labels.

The full pair pool is held as compact source-index pairs with rule flags and counted; it is not exported as hundreds of thousands of feature rows. There is no hidden truncation cap. Exact blocks can still grow quadratically; this pilot has no general scalability claim. Changing blocks or introducing caps requires a new documented generation version and explicit completeness reporting.

Context signatures are sets of `(direction, relation code, neighbour type set)`. Incident relation counts retain original occurrence multiplicity; a self-loop is counted once as an incident occurrence and contributes both direction signatures. Pointer counts retain absent/empty/nonempty states. Signature sets do not deduplicate the underlying graph. Relation codes remain uninterpreted.

## Approved sample and frozen selection

Discovery retains all types. Sampling permits only groups whose complete type set is exactly one of PER, ORG or LOC. Mixed, TIME, NUM and MISC groups remain in discovery counts but cannot enter this sample. This restriction is student-approved and is a selection bias, not a claim that other types cannot have identity.

| Priority | Category | Observable condition | Target |
|---|---|---|---:|
| 1 | sparse_context | Either endpoint has zero incident relations | 4 |
| 2 | different_name_abbreviation | No exact alias match; initialism match; both endpoints have relations | 4 |
| 3 | challenging_name_collision | Exact alias match; both have relations; singleton types or signature sets differ | 8 |
| 4 | compatible_name_context | Exact alias match; same singleton type; equal nonempty signature sets | 8 |

These mutually exclusive buckets are evaluated in that order. Within a bucket, sort by numeric `(left document, left entity, right document, right entity)` indices. Never select an already used endpoint or any already used matching alias/initialism string. Alias and initialism keys share one diversity namespace. Reserve no cases using labels, answer changes or risk outcomes. Report shortfalls; do not loosen rules or fill them with synthetic pairs. Diversity-skip counts describe examined rows before quota, not every excluded pair in the full pool.

The source fingerprint, version, endpoint IDs and canonical ordering determine a full SHA-256 candidate ID. All rule reasons are retained. The inference export excludes sample categories; the inventory records them for audit. Administrative IDs, provenance and constant UNREVIEWED status are not intended to be identity prediction features. Future methods must not exploit selection order or administrative fields as hidden supervision.

Selecting contextual agreement/difference is deliberate case stratification and can bias later comparison. This is not a prevalence sample or a labelled test set. Candidate recall, true label balance and independent evidence sufficiency are unknown. The rules must be versioned/frozen before outcome-based evaluation; changes need a new inventory and rationale rather than silent retuning.

## Permitted inputs and reviewer separation

`candidates_train.json` contains only allowlisted candidate metadata, original/derived names, source types, derived context signatures/counts and natural source references. Every nested object has an explicit permitted field set. No arbitrary mention metadata is copied into runtime features. No identity decisions, hidden maps, verified answers or annotation confidence are exported.

`review_dossier.json` and `review_worklist.csv` are preparation/evaluation-only and stay beneath Git-ignored `data/private_gold/phase2/runs/<id>/`. The generator verifies Git exclusion before output. It reads only source/verification inputs, never any existing private file; private output hashes are computed from write buffers. Unique directories prevent overwriting previous annotations.

Each dossier endpoint contains all original mention dictionaries and span tokens; all incident original relation occurrences with label indices; and the exact token arrays for mention/evidence sentences. Original evidence lists retain ordering and duplicates. Rendered views are labelled token joins, not original whitespace. No pointer becomes a support or contradiction judgement. Existing name/span differences are shown rather than corrected. All reviewer decision/confidence/adjudication fields are blank; evidence sufficiency is NOT_ASSESSED.

Future inference must not read reviewer packages, human decisions or private maps. If original text is permitted as runtime evidence later, both GIR-ER and the same-evidence baseline must obtain it through an approved source interface, not by reading review outcomes. Code/tests verify the current generator's boundaries; no claim is made about unwritten future components.

## Controlled-fragmentation feasibility gate

Only original train-group aggregates are produced: multiple mentions, distinct aliases, distinct mention sentences, incident-edge absence and evidence/mention sentence intersections. The unit of the pointer analysis is an original eligible entity/relation incidence; it is not an allocated fragment edge.

An intersection with one mention sentence is called `unique_sentence_location_only`, never supported attribution. An empty intersection, several compatible sentences, absent or empty evidence remain explicit limitations. Dataset pointers do not necessarily identify the mention responsible for an occurrence. Coreference groups remain noisy annotations rather than independent truth.

A possible future design bundles mentions by sentence, creates opaque observable IDs and keeps parent maps private. Alternative policies include mention-level splits or human-attributed occurrences. Sentence bundles avoid splitting same-sentence aliases arbitrarily but can still reveal original grouping through auxiliary metadata and fail to identify relation roles. Mention-level splitting has additional ambiguity; human attribution costs effort and must remain separate from runtime evidence.

No policy is executed. No fragment IDs, parent maps, controlled pairs or reassigned/copied edges are produced. Actual fragmentation requires student review of attribution, ambiguity handling, leakage and consequences. Never create attractive answer effects by arbitrary edge allocation or copying all edges to all fragments.

## Train/dev overlap and future evaluation

Dev is loaded only for schema and exact sentence-array overlap checking. Test is hashed for integrity and never parsed by candidate discovery. The computed overlap inventory must reconcile with Phase 0's train/dev sentence-content groups.

Train 3052 and dev 469 have identical sentence arrays for Lark Force but different annotations. Keep train for development; record dev 469 as excluded from later dev evaluation. Do not delete or relabel either document. Record selected candidate IDs touching overlapping train content, including an empty list when none do.

Future partitioning must keep exact-text groups together, and selected candidates sharing source documents must not straddle purported independent partitions. No partition assignment or evaluation occurs in Phase 2. Exact token equality misses paraphrases and does not ensure real-world entity-disjoint evaluation. Repeated entities and source-linked cases can reduce independent sample size substantially.

## Output-state contract and reproduction

Run `scripts/candidate_discovery.py` with the README command. Only `results/phase2/latest_run.json` with PASS and complete referenced package hashes establishes latest recorded success. RUNNING, FAILED, missing/unreadable status or an unreferenced completed directory does not. The status is initialized before source loading. Failure before safe initialization is reported on stderr and cannot create a new recorded attempt.

Each new reviewer package is staged/renamed into its unique private run directory, followed by a complete public candidate package. Only then is latest PASS published atomically. There is no cross-directory atomic filesystem transaction: a failure can leave an orphaned private/public package, which must not be used as latest success. Earlier runs and annotations are never deleted. One writer per output directory is required; power-loss durability is not guaranteed.

Compare the four deterministic public artifacts (everything except run_manifest.json) and the two initially blank reviewer artifacts across repeated runs. Status IDs, invocation paths, Python details and measured runtime may differ. Once humans annotate, do not require that private worklist to match its initial blank-template hash or overwrite it; keep the original generation snapshot and separately version the human annotation.

The run manifest records source, Phase 0, Phase 1 reference, implementation and policy fingerprints plus actual invocation/timing. Source-rich outputs remain local; redistribution permissions are unresolved. No stage/commit/push or Git configuration change is authorized.

## Acceptance and research ownership

All existing and new tests must pass. Actual train graph provenance must reconcile, all raw hashes must remain unchanged, repetitions must match deterministic artifacts, and success/failure publication tests must preserve earlier results. Report actual shortages, runtime, evidence gaps and failures rather than interpreting technical PASS as scientific success.

The student must understand the AI-assisted implementation and annotate/check identities independently. A technically complete worklist may still fail to yield useful positives, hard negatives or future answer-impact cases. Positive, zero and negative research outcomes remain possible. Candidate labels, QA semantics, evidence protocol, baseline parity and any fragmentation are unresolved later gates. STOP after Phase 2 for independent review.
