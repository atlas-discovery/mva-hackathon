"""Dataset intake: check files, read variants, parse phenotype, build the variant card."""

from __future__ import annotations

from pathlib import Path

from mva.intake import exomiser, hpo, vcf


def check_dataset(vcf_path: str, phenotype_path: str | None = None, fastq_dir: str | None = None) -> dict:
    """Report what the dataset contains. Nothing is uploaded or copied."""
    p = Path(vcf_path)
    res = {"vcf": {"path": str(p), "exists": p.exists(), "indexed": Path(str(p) + ".tbi").exists()
                   or Path(str(p) + ".csi").exists()},
           "phenotype_document": bool(phenotype_path and Path(phenotype_path).exists())}
    if fastq_dir:
        fq = sorted(x.name for x in Path(fastq_dir).glob("*.f*q*"))
        res["fastq_files"] = len(fq)
    exts = {x.suffix for x in p.parent.iterdir()} if p.parent.exists() else set()
    res["alignment_files_present"] = bool(exts & {".bam", ".cram"})
    return res


def variant_card(vcf_path: str, phenotype_path: str | None = None, exomiser_genes: str | None = None,
                 panel: set[str] | None = None) -> dict:
    """Everything the lever step needs to know about the patient, as one dict."""
    panel = panel if panel is not None else vcf.default_panel()
    variants = vcf.read_variants(vcf_path, panel)
    card = {
        "variants": [v.as_dict() for v in variants],
        "genes_with_findings": sorted({v.gene for v in variants}),
        "notes": [
            "Genotype phase between variants is not known unless read-backed phasing was done.",
            "Only HIGH/MODERATE-impact variants in the scanned gene panel are listed.",
        ],
    }
    if phenotype_path:
        card["hpo_terms"] = hpo.hpo_terms(phenotype_path)
    if exomiser_genes:
        card["exomiser_top_genes"] = exomiser.top_genes(exomiser_genes)
    return card
