"""Command line: mva check | intake | levers | ideas | run"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mva import ideas, intake, levers


def _save(out: Path, name: str, obj) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    p = out / name
    p.write_text(obj if isinstance(obj, str) else json.dumps(obj, indent=1))
    return p


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="mva", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_data(p):
        p.add_argument("--vcf", required=True, help="VEP-annotated VCF (bgzipped, indexed)")
        p.add_argument("--phenotype", help="phenotype document with HPO terms (.docx/.txt)")
        p.add_argument("--exomiser-genes", help="Exomiser *.genes.tsv (optional)")
        p.add_argument("--out", default="out", help="output directory (git-ignored)")

    c = sub.add_parser("check", help="what does the dataset contain?")
    c.add_argument("--vcf", required=True); c.add_argument("--phenotype"); c.add_argument("--fastq-dir")
    add_data(sub.add_parser("intake", help="build the variant card"))
    lv = sub.add_parser("levers", help="LLM: propose mechanistic levers from a variant card")
    lv.add_argument("--card", default="out/variant_card.json"); lv.add_argument("--out", default="out")
    idp = sub.add_parser("ideas", help="LLM + databases: candidate drugs per lever")
    idp.add_argument("--levers", default="out/levers.json"); idp.add_argument("--disease", required=True)
    idp.add_argument("--gene", required=True); idp.add_argument("--out", default="out")
    run = sub.add_parser("run", help="intake -> levers -> ideas")
    add_data(run)
    run.add_argument("--disease", default="mosaic variegated aneuploidy")
    run.add_argument("--gene", default="BUB1B")

    a = ap.parse_args(argv)
    if a.cmd == "check":
        print(json.dumps(intake.check_dataset(a.vcf, a.phenotype, a.fastq_dir), indent=1))
        return
    out = Path(a.out)
    if a.cmd in ("intake", "run"):
        card = intake.variant_card(a.vcf, a.phenotype, a.exomiser_genes)
        print("wrote", _save(out, "variant_card.json", card))
    if a.cmd == "levers":
        card = json.loads(Path(a.card).read_text())
    if a.cmd in ("levers", "run"):
        lv_list = levers.propose(card)
        print("wrote", _save(out, "levers.json", lv_list))
    if a.cmd == "ideas":
        lv_list = json.loads(Path(a.levers).read_text())
    if a.cmd in ("ideas", "run"):
        rows = ideas.propose(lv_list, a.disease, a.gene)
        _save(out, "ideas.json", rows)
        print("wrote", _save(out, "ideas.md", ideas.to_markdown(rows)))


if __name__ == "__main__":
    main()
