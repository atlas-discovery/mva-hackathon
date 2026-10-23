"""Step 3: for each lever, propose candidate drugs, then check them against public databases.

The model proposes; the databases verify. The output is a plain table of ideas, not a ranking.
"""

from __future__ import annotations

import json

from mva import agent, tools

SYSTEM = """You propose candidate drugs for a mechanistic lever in a rare disease.
Given one lever and the patient's disease and gene, list up to 5 candidate drugs that act on it.
Prefer drugs approved for any indication. You may use the database tools to look for candidates.
Keep any text outside the JSON to two sentences. Return a single ```json block: a list of {"drug": generic name, "why": one sentence, "caveat": one sentence}.
Do not claim efficacy; say what would need to be shown."""


def check_drug(drug: str, disease: str, gene: str) -> dict:
    """Deterministic facts about a drug, from public databases."""
    chembl = tools.call("chembl_drug", {"name": drug})
    fda = tools.call("drugsfda", {"name": drug})
    trials = tools.call("clinical_trials", {"query": f"{drug} AND {disease}", "max_results": 3})
    pm_gene = tools.call("pubmed_search", {"query": f"{drug} AND {gene}", "max_results": 1})
    return {
        "chembl_max_phase": chembl.get("max_phase"),
        "mechanisms": chembl.get("mechanisms", []),
        "fda_applications": fda.get("n_applications"),
        "trials_with_disease": trials.get("total"),
        "pubmed_drug_and_gene": pm_gene.get("total"),
    }


def propose(levers: list[dict], disease: str, gene: str, client=None) -> list[dict]:
    rows = []
    for lever in levers:
        reply = agent.run(SYSTEM, f"Disease: {disease}\nGene: {gene}\nLever:\n" + json.dumps(lever, indent=1),
                          client=client)
        for c in agent.extract_json(reply):
            rows.append({"lever": lever["name"], **c, "checks": check_drug(c["drug"], disease, gene)})
    return rows


def to_markdown(rows: list[dict]) -> str:
    out = ["| Lever | Drug | Approved? | FDA apps | Trials (disease) | PubMed (drug+gene) | Why | Caveat |",
           "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        c = r["checks"]
        approved = "yes" if c["chembl_max_phase"] == 4 else ("no" if c["chembl_max_phase"] is not None else "?")
        out.append(f"| {r['lever']} | {r['drug']} | {approved} | {c['fda_applications']} | {c['trials_with_disease']} "
                   f"| {c['pubmed_drug_and_gene']} | {r.get('why','')} | {r.get('caveat','')} |")
    return "\n".join(out)
