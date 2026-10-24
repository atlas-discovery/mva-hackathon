"""Step 2: from the variant card to a short list of mechanistic levers (LLM + database tools)."""

from __future__ import annotations

import json

from mva import agent

SYSTEM = """You help a rare-disease research team think about one patient.
You are given a variant card (variants, phenotype terms, gene ranking) from a whole-genome analysis.
Task: propose 2 to 4 mechanistic levers, meaning distinct biological ways a drug might compensate for
this patient's specific genetic defect. Use the database tools to check each lever against the biology
(protein domains, pathways, interaction partners, literature). Be honest about uncertainty.
Rules:
- Ground every lever in a specific finding on the card (a variant, its type, a phenotype term).
- State what is NOT known (for example variant phase, protein level) rather than assuming it.
- Consider each of these generic lever types and include the ones the card supports (skip those it does not):
  restore expression or function of the affected gene; read through a premature stop codon (only if a
  truncating variant is present); stabilise a mutant protein (including by changing its post-translational
  regulation, such as acetylation or ubiquitination); compensate downstream in the same pathway; and a
  context-specific lever if the phenotype includes a tumour.
- Do not name drugs here; levers only.
Keep any text outside the JSON to two sentences. Return a single ```json block: a list of objects with keys
"name", "type" (e.g. "restore function", "stabilise protein", "bypass pathway"), "rationale",
"grounding" (list of card findings used), "evidence" (list of short strings naming tool results you used),
"unknowns" (list of strings), "search_terms" (list of 2-4 words for finding drugs)."""


def propose(card: dict, client=None) -> list[dict]:
    reply = agent.run(SYSTEM, "Variant card:\n" + json.dumps(card, indent=1), client=client)
    levers = agent.extract_json(reply)
    if not isinstance(levers, list):
        raise ValueError("the model did not return a list of levers")
    return levers
