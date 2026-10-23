"""Parse Exomiser TSV output (optional input; Exomiser is run separately)."""

from __future__ import annotations

import csv
from pathlib import Path


def top_genes(genes_tsv: str, n: int = 5) -> list[dict]:
    """Top-ranked rows of an Exomiser `.genes.tsv`, best combined score first."""
    with Path(genes_tsv).open() as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    score = lambda r: float(r.get("COMBINED_SCORE") or r.get("EXOMISER_GENE_COMBINED_SCORE") or 0)
    rows.sort(key=score, reverse=True)
    return [{"gene": r.get("#GENE_SYMBOL") or r.get("GENE_SYMBOL"), "combined_score": round(score(r), 4),
             "model": r.get("MOI") or r.get("MODE_OF_INHERITANCE") or "", "rank_in_file": i + 1}
            for i, r in enumerate(rows[:n])]
