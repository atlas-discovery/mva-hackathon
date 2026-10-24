# Methods from the team's report

This is the Methods section of the team's hackathon report, reproduced as submitted, with the
references it cites. The report's candidates came from the full agentic harness described here. This
repository contains the data-analysis and lever-identification layer and a candidate lookup; see
[METHODS.md](METHODS.md) for what the code in this repository does and its limits.

## Methods

### Workflows

We used an agentic research harness to perform this analysis. In the first stage, the supplied data were converted into evidence claims using the toolset provided to the agents. These findings were then available to use at later stages of the analysis pipeline as supporting evidence to guide candidate selection. In the discovery stage, parallel research threads search for mechanistic levers involved in the disease pathway. These findings are then used to begin independent searches along those mechanistic hypotheses for potential candidates, using extended literature searches, gene-expression signature databases, and more. A merge step collapsed about 920 raw candidate mentions into 304 unique compounds, then filtered these to the 218 that are approved for some indication according to ChEMBL.

Each remaining candidate gets six independent evidence reviews: target engagement, human genetics, tissue context, clinical landscape, safety, and practicality. The agents use more than 200 biomedical tools and publicly available resources, including Open Targets, ChEMBL, IBM RXN, STRING, PubMed, ClinicalTrials.gov, and FAERS, and every claim is cited and checked against the evidence record.

Finally, a team of judge agents with no prior context perform a thorough analysis of the evidence for each candidate based on their mechanistic coherence, translational feasibility, resolution of conflicting evidence, and biological plausibility. The remaining drug-disease hypotheses are then vetted individually with the supporting evidence provided to find those that are most promising.

### Tools & Datasets

All data sources used for this analysis were publicly available (Table 1). To our knowledge no proprietary data were used at any point.

**Table 1.** Data sources used in this drug repurposing analysis.

| Purpose | Sources |
|---|---|
| Drug identity and regulatory status | ChEMBL (Zdrazil et al., 2024); Drugs@FDA (U.S. Food and Drug Administration, n.d.); DailyMed (National Library of Medicine, n.d.-b); European Medicines Agency (n.d.) |
| Safety and clinical trials | openFDA (Kass-Hout et al., 2016); ClinicalTrials.gov (National Library of Medicine, n.d.-a) |
| Variant interpretation and genetic associations | ClinVar (Landrum et al., 2025); gnomAD (Karczewski et al., 2020); MyVariant.info (Xin et al., 2016; Lelong et al., 2022); Open Targets (Buniello et al., 2025) |
| Protein function, pathways, and tissue expression | UniProt (The UniProt Consortium, 2025); STRING (Szklarczyk et al., 2025); Reactome (Ragueneau et al., 2026); GTEx (GTEx Consortium, 2020) |
| Gene essentiality, drug sensitivity, and perturbation signatures | DepMap; PRISM (Corsello et al., 2020); LINCS/L1000 (Subramanian et al., 2017) |

### AI Disclosure and Runtime

The pipeline's research threads used Anthropic's Claude Opus model through the Anthropic API. Patient-derived variant and phenotype data was never used for any model training. A full run of the agentic harness takes roughly four to four and a half hours with more than 120 evidence-review threads and an adversarial review of 1,888 claims. Additionally, more than 10 human hours were applied to review the results, verify with the existing tools, and surface other literature that the harness might have missed.

## References cited in the Methods

Buniello, A., Suveges, D., Cruz-Castillo, C., Llinares, M. B., Cornu, H., Lopez, I., Tsukanov, K., Roldán-Romero, J. M., Mehta, C., Fumis, L., McNeill, G., Hayhurst, J. D., Martinez Osorio, R. E., Barkhordari, E., Ferrer, J., Carmona, M., Uniyal, P., Falaguera, M. J., Rusina, P., . . . Ochoa, D. (2025). Open Targets Platform: Facilitating therapeutic hypotheses building in drug discovery. *Nucleic Acids Research*, *53*(D1), D1467–D1475. https://doi.org/10.1093/nar/gkae1128

Corsello, S. M., Nagari, R. T., Spangler, R. D., Rossen, J., Kocak, M., Bryan, J. G., Humeidi, R., Peck, D., Wu, X., Tang, A. A., Wang, V. M., Bender, S. A., Lemire, E., Narayan, R., Montgomery, P., Ben-David, U., Garvie, C. W., Chen, Y., Rees, M. G., . . . Golub, T. R. (2020). Discovering the anti-cancer potential of non-oncology drugs by systematic viability profiling. *Nature Cancer*, *1*(2), 235–248. https://doi.org/10.1038/s43018-019-0018-6

European Medicines Agency. (n.d.). *Medicines*. Retrieved October 22, 2026, from https://www.ema.europa.eu/en/medicines

GTEx Consortium. (2020). The GTEx Consortium atlas of genetic regulatory effects across human tissues. *Science*, *369*(6509), 1318–1330. https://doi.org/10.1126/science.aaz1776

Karczewski, K. J., Francioli, L. C., Tiao, G., Cummings, B. B., Alföldi, J., Wang, Q., Collins, R. L., Laricchia, K. M., Ganna, A., Birnbaum, D. P., Gauthier, L. D., Brand, H., Solomonson, M., Watts, N. A., Rhodes, D., Singer-Berk, M., England, E. M., Seaby, E. G., Kosmicki, J. A., . . . MacArthur, D. G. (2020). The mutational constraint spectrum quantified from variation in 141,456 humans. *Nature*, *581*(7809), 434–443. https://doi.org/10.1038/s41586-020-2308-7

Kass-Hout, T. A., Xu, Z., Mohebbi, M., Nelsen, H., Baker, A., Levine, J., Johanson, E., & Bright, R. A. (2016). OpenFDA: An innovative platform providing access to a wealth of FDA's publicly available data. *Journal of the American Medical Informatics Association*, *23*(3), 596–600. https://doi.org/10.1093/jamia/ocv153

Landrum, M. J., Chitipiralla, S., Kaur, K., Brown, G., Chen, C., Hart, J., Hoffman, D., Jang, W., Liu, C., Maddipatla, Z., Maiti, R., Mitchell, J., Rezaie, T., Riley, G., Song, G., Yang, J., Ziyabari, L., Russette, A., & Kattman, B. L. (2025). ClinVar: Updates to support classifications of both germline and somatic variants. *Nucleic Acids Research*, *53*(D1), D1313–D1321. https://doi.org/10.1093/nar/gkae1090

Lelong, S., Zhou, X., Afrasiabi, C., Qian, Z., Cano, M. A., Tsueng, G., Xin, J., Mullen, J., Yao, Y., Avila, R., Taylor, G., Su, A. I., & Wu, C. (2022). BioThings SDK: A toolkit for building high-performance data APIs in biomedical research. *Bioinformatics*, *38*(7), 2077–2079. https://doi.org/10.1093/bioinformatics/btac017

National Library of Medicine. (n.d.-a). *ClinicalTrials.gov*. Retrieved October 22, 2026, from https://clinicaltrials.gov/

National Library of Medicine. (n.d.-b). *DailyMed*. Retrieved October 22, 2026, from https://dailymed.nlm.nih.gov/dailymed/

Ragueneau, E., Gong, C., Sinquin, P., Sevilla, C., Beavers, D., Grentner, A., Griss, J., Hogue, G. F. J., Li, N. T., Matthews, L., May, B., Milacic, M., Mohammadi, H., Petryszak, R., Rothfels, K., Shamovsky, V., Stephan, R., Tiwari, K., Weiser, J., . . . D'Eustachio, P. (2026). The Reactome Knowledgebase 2026. *Nucleic Acids Research*, *54*(D1), D673–D681. https://doi.org/10.1093/nar/gkaf1223

Subramanian, A., Narayan, R., Corsello, S. M., Peck, D. D., Natoli, T. E., Lu, X., Gould, J., Davis, J. F., Tubelli, A. A., Asiedu, J. K., Lahr, D. L., Hirschman, J. E., Liu, Z., Donahue, M., Julian, B., Khan, M., Wadden, D., Smith, I. C., Lam, D., . . . Golub, T. R. (2017). A next generation connectivity map: L1000 platform and the first 1,000,000 profiles. *Cell*, *171*(6), 1437–1452.e17. https://doi.org/10.1016/j.cell.2017.10.049

Szklarczyk, D., Nastou, K., Koutrouli, M., Kirsch, R., Mehryary, F., Hachilif, R., Hu, D., Peluso, M. E., Huang, Q., Fang, T., Doncheva, N. T., Pyysalo, S., Bork, P., Jensen, L. J., & von Mering, C. (2025). The STRING database in 2025: Protein networks with directionality of regulation. *Nucleic Acids Research*, *53*(D1), D730–D737. https://doi.org/10.1093/nar/gkae1113

The UniProt Consortium. (2025). UniProt: The Universal Protein Knowledgebase in 2025. *Nucleic Acids Research*, *53*(D1), D609–D617. https://doi.org/10.1093/nar/gkae1010

U.S. Food and Drug Administration. (n.d.). *Drugs@FDA: FDA-approved drugs*. Retrieved October 22, 2026, from https://www.accessdata.fda.gov/scripts/cder/daf/

Xin, J., Mark, A., Afrasiabi, C., Tsueng, G., Juchler, M., Gopal, N., Stupp, G. S., Putman, T. E., Ainscough, B. J., Griffith, O. L., Torkamani, A., Whetzel, P. L., Mungall, C. J., Mooney, S. D., Su, A. I., & Wu, C. (2016). High-performance web services for querying gene and variant annotation. *Genome Biology*, *17*, Article 91. https://doi.org/10.1186/s13059-016-0953-9

Zdrazil, B., Felix, E., Hunter, F., Manners, E. J., Blackshaw, J., Corbett, S., de Veij, M., Ioannidis, H., Lopez, D. M., Mosquera, J. F., Magarinos, M. P., Bosc, N., Arcila, R., Kizilören, T., Gaulton, A., Bento, A. P., Adasme, M. F., Monecke, P., Landrum, G. A., & Leach, A. R. (2024). The ChEMBL Database in 2023: A drug discovery platform spanning multiple bioactivity data types and time periods. *Nucleic Acids Research*, *52*(D1), D1180–D1192. https://doi.org/10.1093/nar/gkad1004
