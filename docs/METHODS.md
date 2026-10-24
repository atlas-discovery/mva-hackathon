# Methods and limits

## Flow

```
VEP-annotated VCF ──┐
phenotype (HPO) ────┼─► intake ─► variant card ─► levers (LLM + tools) ─► ideas (LLM) ─► checks (databases) ─► table
Exomiser genes.tsv ─┘
```

## Intake

- `bcftools` reads PASS records; the VEP `CSQ` field is parsed per transcript. One record is kept per
  variant and gene, preferring the MANE Select transcript.
- Only HIGH and MODERATE impact variants in a small gene panel (`src/mva/data/mva_genes.txt`: the three
  established MVA genes plus core spindle-checkpoint genes) go into the card. Edit the file to widen it.
- Each variant is typed as loss-of-function, missense or other from its consequence terms.
- HPO IDs are taken from the phenotype document by pattern match (`HP:#######`).
- If given, the top rows of an Exomiser genes file are added as a phenotype-driven ranking.
- The card states plainly that variant phase is unknown unless separately established.

## Levers

One system prompt and one user message (the card). The model may call the database tools for up to
ten turns, then must return levers as JSON. Each lever must cite a finding on the card and list what is
not known. Levers do not name drugs.

## Ideas

For each lever the model proposes up to five drugs. For every drug the code then queries: ChEMBL
(highest phase; 4 means approved for some indication), openFDA Drugs@FDA (number of US applications),
ClinicalTrials.gov (trials matching drug and disease) and PubMed (papers mentioning drug and gene).
These are facts about the drug, not a score and not evidence that it works for this patient.

## Limits

- No ranking, no scoring, no adversarial review and no systematic literature review. The table is a
  list of ideas to investigate.
- ChEMBL phase 4 means "approved somewhere for something". It includes drugs approved only outside the US
  (for example ataluren) and drugs no longer marketed. The FDA column is the check for a US application;
  read it next to the phase.
- Zero FDA applications means none were found by name. Brand or salt-form names can be missed.
- The model can propose drugs that are wrong for the mechanism. The databases confirm identity and
  status, not suitability.
- A genome shows what the DNA encodes, not whether protein is made or stable. The card does not infer
  that, and the prompts tell the model not to.
- Single-sample data cannot establish whether two variants are on the same chromosome copy.
