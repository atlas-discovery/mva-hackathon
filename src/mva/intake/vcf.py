"""Read a VEP-annotated VCF with bcftools and build per-variant records."""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from importlib import resources

LOF = {"stop_gained", "frameshift_variant", "splice_donor_variant", "splice_acceptor_variant",
       "start_lost", "stop_lost"}
IMPACTS = {"HIGH", "MODERATE"}


@dataclass
class Variant:
    chrom: str
    pos: int
    ref: str
    alt: str
    genotype: str
    allele_depth: str
    gene: str
    transcript: str
    hgvsc: str
    hgvsp: str
    consequence: str
    impact: str
    exon: str
    mane_select: str
    kind: str  # "lof" | "missense" | "other"
    max_af: str = ""
    clin_sig: str = ""
    sift: str = ""
    polyphen: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


def default_panel() -> set[str]:
    txt = resources.files("mva").joinpath("data/mva_genes.txt").read_text()
    return {g.strip() for g in txt.splitlines() if g.strip() and not g.startswith("#")}


def _csq_fields(vcf: str) -> list[str]:
    out = subprocess.run(["bcftools", "view", "-h", vcf], capture_output=True, text=True, check=True).stdout
    m = re.search(r'ID=CSQ.*?Format: ([^">]+)', out)
    if not m:
        raise ValueError("no CSQ field in the VCF header; annotate it with Ensembl VEP first")
    return m.group(1).strip().split("|")


def _kind(consequence: str) -> str:
    terms = set(consequence.split("&"))
    if terms & LOF:
        return "lof"
    if "missense_variant" in terms:
        return "missense"
    return "other"


def read_variants(vcf: str, panel: set[str] | None = None, pass_only: bool = True) -> list[Variant]:
    """Return HIGH/MODERATE variants in `panel` genes (all genes if panel is None)."""
    if not shutil.which("bcftools"):
        raise RuntimeError("bcftools is required (brew install bcftools)")
    fields = _csq_fields(vcf)
    idx = {f: i for i, f in enumerate(fields)}
    cmd = ["bcftools", "query", "-f", "%CHROM\t%POS\t%REF\t%ALT\t[%GT]\t[%AD]\t%INFO/CSQ\n"]
    if pass_only:
        cmd[2:2] = ["-i", 'FILTER="PASS" || FILTER="."']
    rows = subprocess.run(cmd + [vcf], capture_output=True, text=True, check=True).stdout.splitlines()
    out: list[Variant] = []
    for row in rows:
        chrom, pos, ref, alt, gt, ad, csq = row.split("\t")
        for entry in csq.split(","):
            f = entry.split("|")
            get = lambda k: f[idx[k]] if k in idx and idx[k] < len(f) else ""
            gene, impact = get("SYMBOL"), get("IMPACT")
            if impact not in IMPACTS or (panel is not None and gene not in panel):
                continue
            out.append(Variant(chrom, int(pos), ref, alt, gt, ad, gene, get("Feature"), get("HGVSc"),
                               get("HGVSp"), get("Consequence"), impact, get("EXON"), get("MANE_SELECT"),
                               _kind(get("Consequence")), get("MAX_AF"), get("CLIN_SIG"), get("SIFT"),
                               get("PolyPhen")))
    # keep one record per variant/gene, preferring the MANE Select transcript
    best: dict[tuple, Variant] = {}
    for v in out:
        k = (v.chrom, v.pos, v.ref, v.alt, v.gene)
        if k not in best or (v.mane_select and not best[k].mane_select):
            best[k] = v
    return sorted(best.values(), key=lambda v: (v.gene, v.pos))
