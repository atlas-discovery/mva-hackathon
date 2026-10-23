"""Thin clients for the public databases used in the analysis.

Each function takes simple arguments and returns a small JSON-serialisable dict.
Only gene-level and drug-level queries are made here; single-variant lookups live in
`variant_scores` and are off by default.
"""

from __future__ import annotations

from mva import config
from mva.tools.http import get_json, post_json

NCBI = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def pubmed_search(query: str, max_results: int = 5) -> dict:
    s = get_json(f"{NCBI}/esearch.fcgi", {"db": "pubmed", "term": query, "retmode": "json",
                                            "retmax": max_results})["esearchresult"]
    ids = s.get("idlist", [])
    papers = []
    if ids:
        r = get_json(f"{NCBI}/esummary.fcgi", {"db": "pubmed", "id": ",".join(ids), "retmode": "json"})["result"]
        for i in ids:
            p = r.get(i, {})
            papers.append({"pmid": i, "year": (p.get("pubdate") or "")[:4], "title": p.get("title"),
                           "journal": p.get("source")})
    return {"query": query, "total": int(s.get("count", 0)), "papers": papers}


def opentargets_gene(gene_symbol: str, n: int = 8) -> dict:
    url = "https://api.platform.opentargets.org/api/v4/graphql"
    hit = post_json(url, {"query": 'query($q:String!){search(queryString:$q,entityNames:["target"],page:{index:0,size:1}){hits{id name}}}',
                          "variables": {"q": gene_symbol}})["data"]["search"]["hits"]
    if not hit:
        return {"gene": gene_symbol, "error": "not found"}
    eid = hit[0]["id"]
    q = ("query($id:String!,$n:Int!){target(ensemblId:$id){approvedSymbol approvedName "
         "associatedDiseases(page:{index:0,size:$n}){count rows{score disease{name}}}}}")
    t = post_json(url, {"query": q, "variables": {"id": eid, "n": n}})["data"]["target"]
    rows = t["associatedDiseases"]["rows"]
    return {"gene": t["approvedSymbol"], "ensembl_id": eid, "name": t["approvedName"],
            "n_diseases": t["associatedDiseases"]["count"],
            "top_diseases": [{"disease": r["disease"]["name"], "score": round(r["score"], 3)} for r in rows]}


def uniprot_domains(gene_symbol: str) -> dict:
    d = get_json("https://rest.uniprot.org/uniprotkb/search", {
        "query": f"gene_exact:{gene_symbol} AND organism_id:9606 AND reviewed:true",
        "fields": "accession,length,ft_domain,ft_region", "format": "json", "size": 1}).get("results", [])
    if not d:
        return {"gene": gene_symbol, "error": "not found"}
    e = d[0]
    feats = [{"type": f["type"], "description": f.get("description", ""),
              "start": f["location"]["start"]["value"], "end": f["location"]["end"]["value"]}
             for f in e.get("features", [])]
    return {"gene": gene_symbol, "accession": e["primaryAccession"], "length": e["sequence"]["length"],
            "features": feats}


def string_partners(gene_symbol: str, min_score: int = 700, limit: int = 10) -> dict:
    r = get_json("https://string-db.org/api/json/interaction_partners", {
        "identifiers": gene_symbol, "species": 9606, "required_score": min_score, "limit": limit})
    return {"gene": gene_symbol, "partners": [{"partner": x["preferredName_B"], "score": x["score"]}
                                               for x in (r or [])]}


def reactome_pathways(uniprot_accession: str) -> dict:
    r = get_json(f"https://reactome.org/ContentService/data/mapping/UniProt/{uniprot_accession}/pathways",
                 {"species": "Homo sapiens"})
    return {"accession": uniprot_accession,
            "pathways": [{"id": p["stId"], "name": p["displayName"]} for p in (r or [])[:15]]}


def gtex_expression(gene_symbol: str, top: int = 8) -> dict:
    g = get_json("https://gtexportal.org/api/v2/reference/gene", {"geneId": gene_symbol}).get("data", [])
    if not g:
        return {"gene": gene_symbol, "error": "not found"}
    gid = g[0]["gencodeId"]
    r = get_json("https://gtexportal.org/api/v2/expression/medianGeneExpression",
                 {"gencodeId": gid, "datasetId": "gtex_v8", "itemsPerPage": 100}).get("data", [])
    rows = sorted(r, key=lambda x: -x["median"])[:top]
    return {"gene": gene_symbol, "top_tissues": [{"tissue": x["tissueSiteDetailId"], "median_tpm": round(x["median"], 1)}
                                                  for x in rows]}


def chembl_drug(name: str) -> dict:
    m = get_json("https://www.ebi.ac.uk/chembl/api/data/molecule/search.json", {"q": name, "limit": 1}).get("molecules", [])
    if not m:
        return {"drug": name, "found": False}
    m = m[0]
    mech = get_json("https://www.ebi.ac.uk/chembl/api/data/mechanism.json",
                    {"molecule_chembl_id": m["molecule_chembl_id"], "limit": 5}).get("mechanisms", [])
    return {"drug": name, "found": True, "chembl_id": m["molecule_chembl_id"], "pref_name": m.get("pref_name"),
            "max_phase": float(m["max_phase"]) if m.get("max_phase") is not None else None, "first_approval": m.get("first_approval"),
            "mechanisms": [x.get("mechanism_of_action") for x in mech]}


def drugsfda(name: str) -> dict:
    """US marketing applications (openFDA drugsfda). Zero results means no FDA application found."""
    r = get_json("https://api.fda.gov/drug/drugsfda.json",
                 {"search": f'openfda.generic_name:"{name}" OR openfda.brand_name:"{name}"', "limit": 20})
    res = r.get("results", []) if isinstance(r, dict) else []
    apps = [{"application": a.get("application_number"), "sponsor": a.get("sponsor_name"),
             "statuses": sorted({p.get("marketing_status") for p in a.get("products", [])})} for a in res]
    return {"drug": name, "n_applications": len(apps), "applications": apps[:8]}


def clinical_trials(query: str, max_results: int = 8) -> dict:
    r = get_json("https://clinicaltrials.gov/api/v2/studies", {"query.term": query, "pageSize": max_results,
                                                                "countTotal": "true"})
    out = []
    for s in r.get("studies", []):
        p = s["protocolSection"]
        out.append({"nct": p["identificationModule"]["nctId"], "title": p["identificationModule"].get("briefTitle"),
                    "status": p["statusModule"].get("overallStatus"),
                    "phase": p.get("designModule", {}).get("phases"),
                    "enrollment": p.get("designModule", {}).get("enrollmentInfo", {}).get("count")})
    return {"query": query, "total": r.get("totalCount", len(out)), "studies": out}


def variant_scores(chrom: str, pos: int, ref: str, alt: str) -> dict:
    """Missense predictor scores for ONE variant from MyVariant.info (dbNSFP).

    This sends genomic coordinates to a public server, so it is disabled unless
    MVA_ALLOW_VARIANT_LOOKUP=1.
    """
    if not config.ALLOW_VARIANT_LOOKUP:
        return {"error": "variant lookups are disabled; set MVA_ALLOW_VARIANT_LOOKUP=1 to allow"}
    hgvs = f"chr{chrom.removeprefix('chr')}:g.{pos}{ref}>{alt}"
    r = get_json(f"https://myvariant.info/v1/variant/{hgvs}",
                 {"assembly": "hg38", "fields": "dbnsfp.alphamissense,dbnsfp.sift,dbnsfp.polyphen2,dbnsfp.cadd,dbnsfp.revel,clinvar.rcv.clinical_significance,gnomad_genome.af"})
    return {"variant": hgvs, "scores": r}
