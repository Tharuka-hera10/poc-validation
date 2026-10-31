# Phase 2 identity annotation guide

## What you are reviewing

Each row proposes a pair of original train document-scoped entity groups. Names, types and relation contexts triggered selection; none proves identity. Re-DocRED's within-document coreference is already represented within each group. Two groups or two documents are not automatically different entities. All rows start unlabelled; no human annotation or adjudication has been performed by the generator.

Read the private `review_worklist.csv` and locate its candidate ID in the adjacent `review_dossier.json`. The dossier contains both endpoints, original mention names/types, document and sentence indices, exact token arrays, half-open mention spans and incident relation-label records. A rendered view joins tokens; it is not original whitespace. Source fingerprints identify the supplied files, not their authenticity or truth.

## Decision definitions

| Decision | Required interpretation |
|---|---|
| SAME ENTITY | Source context gives a defensible reason that both groups denote the same particular real-world referent, including compatible scope/time where relevant. |
| DIFFERENT ENTITY | Source context gives a defensible distinction between the referents. A different group/document ID, type mismatch or different relationships alone is insufficient. |
| UNKNOWN / INSUFFICIENT EVIDENCE | Available source context cannot responsibly establish either conclusion, or ambiguity/noise remains unresolved. |

For people, distinguish namesakes and contextual roles. For organizations, consider branches, subsidiaries and changes over time; do not equate related organizations automatically. For places, inspect administrative/geographical scope rather than name alone. These are review considerations, not automated truth rules. Mixed/other types are inventoried but outside the approved sample.

## Review procedure

1. Inspect both groups' original mentions and sentence tokens. Check name/span warnings and the complete original document locally when the provided sentences omit needed context.
2. Inspect relevant original relation records. Relation codes are uninterpreted unless authoritative definitions are independently obtained. A nonempty evidence list is an annotation pointer, not verified support. Empty/absent pointers are not contradictions.
3. Distinguish explicit identity evidence from similarity, shared attributes or a lack of differences. Do not use the sample category, filename, candidate order or original group separation as a reference label.
4. Record a decision only after review. Give exact supporting references and a reason; use UNKNOWN when evidence is inadequate. Do not force target positive/negative counts.
5. Record confidence as reviewer-reported low/medium/high with an explanation; it is not a calibrated probability. Record reviewer identifier, actual review date and adjudication status. Do not backfill invented reviewers, dates or independent review.

Use source references such as `train:<document-index>:entity:<group-index>:mention:<mention-index>` and `train:<document-index>:sentence:<sentence-index>`, with the dataset SHA-256. Relationship references include the original label index or Phase 1 edge key. These are reference formats, not additional empirical examples. Preserve exact sentence-token quotations only in private annotations. If external sources are later permitted, record their provenance and access date under a separately reviewed source-use protocol; no external retrieval is implemented here.

## Annotation fields

- `candidate_id`: retain the generated value.
- `reviewer_decision`: one decision above; blank until review.
- `evidence_references`: exact source references supporting the decision or documenting the unresolved gap.
- `rationale`: explain why the references support the conclusion and any ambiguity.
- `confidence`: reviewer-reported confidence, blank until review.
- `reviewer_identifier`, `review_date`: actual reviewer and review date.
- `adjudication_status`: actual status, for example single review, disagreement pending, or independently adjudicated. Never imply a second reviewer exists when none does.

All seven judgement/administrative fields are generated blank. NOT_ASSESSED in the dossier concerns evidence sufficiency before human review; it is not a reviewer UNKNOWN decision.

Keep the generated package intact. Save completed annotations separately under `data/private_gold/` with a genuine version/date. A second reviewer should decide without seeing a first review where independence is intended; preserve disagreements before adjudication. Do not claim inter-annotator agreement without actual multiple annotations.

## Privacy and research limits

Reviewer packages, confidence, decisions and future parent mappings remain evaluation-only and Git-ignored. Never copy them into matcher, risk or candidate features. Candidate source inputs may later be shared equally with comparators through an approved source interface; reviewer conclusions remain private.

Do not publish source excerpts or private annotations while redistribution/ethics permissions remain unresolved. Source evidence can be incomplete or wrong. This worklist is not a finished gold benchmark and provides no ER or QA accuracy result. Stop after Phase 2 review; graph fragmentation and Phase 3 require separate approval.
