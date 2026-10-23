"""Tool registry: function + JSON schema for each database client."""

from __future__ import annotations

from mva.tools import databases as d


def _s(props: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": props, "required": required}


_STR = {"type": "string"}
_INT = {"type": "integer"}

TOOLS = {
    "pubmed_search": (d.pubmed_search, "Search PubMed; returns total hit count and the top papers.",
                      _s({"query": _STR, "max_results": _INT}, ["query"])),
    "opentargets_gene": (d.opentargets_gene, "Open Targets: diseases most associated with a gene symbol.",
                         _s({"gene_symbol": _STR}, ["gene_symbol"])),
    "uniprot_domains": (d.uniprot_domains, "UniProt: protein length, accession, domains and regions for a gene symbol.",
                        _s({"gene_symbol": _STR}, ["gene_symbol"])),
    "string_partners": (d.string_partners, "STRING: high-confidence interaction partners of a gene.",
                        _s({"gene_symbol": _STR}, ["gene_symbol"])),
    "reactome_pathways": (d.reactome_pathways, "Reactome: pathways containing a protein (UniProt accession).",
                          _s({"uniprot_accession": _STR}, ["uniprot_accession"])),
    "gtex_expression": (d.gtex_expression, "GTEx: tissues with the highest median expression of a gene.",
                        _s({"gene_symbol": _STR}, ["gene_symbol"])),
    "chembl_drug": (d.chembl_drug, "ChEMBL: drug identity, highest clinical phase (4 = approved) and mechanisms.",
                    _s({"name": _STR}, ["name"])),
    "drugsfda": (d.drugsfda, "openFDA Drugs@FDA: US marketing applications for a drug name.",
                 _s({"name": _STR}, ["name"])),
    "clinical_trials": (d.clinical_trials, "ClinicalTrials.gov: trials matching a free-text query.",
                        _s({"query": _STR, "max_results": _INT}, ["query"])),
}


def schemas() -> list[dict]:
    return [{"name": n, "description": desc, "input_schema": sch} for n, (_, desc, sch) in TOOLS.items()]


def call(name: str, args: dict) -> dict:
    if name not in TOOLS:
        return {"error": f"unknown tool {name}"}
    try:
        return TOOLS[name][0](**args)
    except Exception as e:  # tool errors go back to the model, not up the stack
        return {"error": f"{type(e).__name__}: {e}"}
