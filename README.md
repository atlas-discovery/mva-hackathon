# mva-hackathon

A small, reproducible workflow for the Sage Bionetworks *Rare Disease, Real Kid: MVA Hackathon 2026*.
It takes one patient's annotated whole-genome VCF and phenotype document and produces:

1. a **variant card** (what the genome shows in the genes that matter),
2. a short list of **mechanistic levers** (how a drug might compensate for that defect), and
3. a table of **candidate-drug ideas** per lever, each checked against public databases.

The levers and ideas steps are LLM-driven (Claude with database tools). The checks on each drug
(approval, applications, trials, literature counts) come from the databases, not from the model.

> **Scope.** This repository is the data-analysis and lever-identification layer plus a simple
> candidate lookup. It is not the full multi-stage research pipeline used to write the team's
> submission report; that pipeline is not released here. Results from this repo are a starting
> list of ideas, not a ranked or scored evidence review.

## Patient data

No patient data is in this repository, and none should ever be committed. The hackathon terms
require the dataset to be deleted afterwards and prohibit redistribution. `.gitignore` excludes
VCFs, alignments, FASTQs, `.docx` files and the `out/` directory. The only VCF here,
`data/synthetic.vcf`, is invented for tests and uses made-up positions and variants.

Two things leave your machine when you run the LLM steps: the variant card (gene, consequence,
HGVS strings, HPO terms) goes to the Anthropic API, and gene or drug names go to the public
databases below. Single-variant lookups (genomic coordinates) are **off by default**; enable them
only if you are comfortable sending coordinates to a public server (`MVA_ALLOW_VARIANT_LOOKUP=1`).

## Install

```bash
brew install bcftools            # or apt-get install bcftools
python -m venv .venv && . .venv/bin/activate
pip install -e ".[docx]"         # add ",dev" to run the tests
cp .env.example .env             # then set ANTHROPIC_API_KEY
```

## Reproduce

Inputs are a VEP-annotated, bgzipped, indexed VCF, and optionally the phenotype document and an
Exomiser `*.genes.tsv`. Annotate the supplied VCF with [Ensembl VEP](https://www.ensembl.org/vep)
(GRCh38, `--mane_select --symbol --hgvs --canonical`) and, if you want the gene ranking, run
[Exomiser](https://github.com/exomiser/Exomiser) with the patient's HPO terms.

```bash
mva check   --vcf annotated.vcf.gz --phenotype pheno.docx
mva intake  --vcf annotated.vcf.gz --phenotype pheno.docx [--exomiser-genes sample.genes.tsv]
mva levers                                   # reads out/variant_card.json
mva ideas   --disease "mosaic variegated aneuploidy" --gene BUB1B
mva run     --vcf annotated.vcf.gz --phenotype pheno.docx   # all three steps
```

To start from the same three levers as the team's report instead of asking the model to find levers:

```bash
mva ideas --levers configs/report_levers.json --disease "mosaic variegated aneuploidy" --gene BUB1B
```

Outputs go to `out/`: `variant_card.json`, `levers.json`, `ideas.json`, `ideas.md`. Database
responses are cached in `.cache/`, so a rerun against the same cache reproduces the database facts
exactly. The LLM steps are not deterministic; expect the wording and some of the ideas to vary.

## What is in the box

| Step | Code | Uses |
|---|---|---|
| Intake | `src/mva/intake/` | bcftools, VEP annotation, HPO parsing, Exomiser output |
| Levers | `src/mva/levers.py` | Claude + the database tools below |
| Ideas | `src/mva/ideas.py` | Claude proposes; ChEMBL, openFDA, ClinicalTrials.gov, PubMed check |
| Tools | `src/mva/tools/` | PubMed, Open Targets, UniProt, STRING, Reactome, GTEx, ChEMBL, Drugs@FDA, ClinicalTrials.gov, MyVariant.info (opt-in) |

See [docs/METHODS.md](docs/METHODS.md) for the design and its limits.

## Worked example

`docs/example/` holds a complete run on the synthetic VCF (variant card, levers) and a run of the
`ideas` step on `configs/report_levers.json`. The synthetic variants are invented, so the example shows
the shape of the outputs, not findings about any patient.

## AI use

Levers and ideas come from Anthropic's Claude via the Anthropic API (default model `claude-opus-5-5`).
When the API's safety classifier declines a drug-related request, the API retries it on the model it
recommends for that category (server-side fallback, `MVA_FALLBACK=1`); the model that answered is
printed to stderr. Plan or tier and data-handling terms: **TODO (team): fill in before making public.**
Claude Code was also used as a coding assistant while building this repository.

## Tests

```bash
pytest
```

Tests use the synthetic VCF and mocked model and database calls; no network or API key is needed.

## Licence

Code: MIT (see `LICENSE`). Under the hackathon rules, submissions, code and reports are also released
under CC BY 4.0. Public databases are subject to their own terms of use.
