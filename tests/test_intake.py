from pathlib import Path

from mva import intake
from mva.intake import hpo, vcf

SYN = str(Path(__file__).parent.parent / "data" / "synthetic.vcf")


def test_reads_only_pass_panel_high_moderate():
    vs = vcf.read_variants(SYN, vcf.default_panel())
    assert [v.hgvsp for v in vs] == ["p.Arg400Ter", "p.Gly900Arg"]
    assert [v.kind for v in vs] == ["lof", "missense"]
    assert vs[0].allele_depth == "12,11" and vs[0].genotype == "0/1"


def test_no_panel_includes_other_genes():
    genes = {v.gene for v in vcf.read_variants(SYN, None)}
    assert genes == {"BUB1B", "SOMEOTHERGENE"}


def test_hpo_terms_from_text(tmp_path):
    f = tmp_path / "pheno.txt"
    f.write_text("Short stature HP:0004322\nRhabdomyosarcoma (HP:0002859)\nrepeat HP:0004322\n")
    assert [t["id"] for t in hpo.hpo_terms(str(f))] == ["HP:0004322", "HP:0002859"]


def test_variant_card_and_check(tmp_path):
    f = tmp_path / "p.txt"; f.write_text("HP:0001511")
    card = intake.variant_card(SYN, str(f))
    assert card["genes_with_findings"] == ["BUB1B"] and card["hpo_terms"][0]["id"] == "HP:0001511"
    assert intake.check_dataset(SYN, str(f))["phenotype_document"] is True
