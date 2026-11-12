"""Search keywords derived from the CV and the masters degree.

This table is the *filter* half of the scraper: the registry says where to
look, this says what to keep. It is organised by theme so a run can be
weighted ("environmental compliance in BE and LU" is a different query from
"carbon accounting everywhere").

Sources for each entry, so nothing here is invented:

  thesis      M.Sc. thesis: lateral root development of an Arabidopsis
              population from a sand dune environment, molecular and
              eco-physiological characterisation
  degree      M.Sc. Environmental Bioengineering, B.Sc. Engineering Sciences
  role        a job title actually held (see data/experience_master.json)
  skill       listed in the skills block of the master file
  tool        listed in skills.it

`weight` is 3 for a core match, 2 for a likely fit, 1 for adjacent work that
is worth seeing but will mostly be noise.
"""

from .model import Row

# (theme, keyword, lang, weight, source)
KEYWORDS = [
    # ---------------------------------------------------------------- core
    ("sustainability", "sustainability consultant", "en", 3, "role"),
    ("sustainability", "durabilite", "fr", 3, "role"),
    ("sustainability", "sustainability analyst", "en", 3, "role"),
    ("sustainability", "analyste ESG", "fr", 3, "role"),
    ("sustainability", "ESG analyst", "en", 3, "role"),
    ("sustainability", "ESG", "en", 3, "skill"),
    ("sustainability", "RSE", "fr", 3, "skill"),
    ("sustainability", "CSR", "en", 3, "skill"),
    ("sustainability", "sustainability manager", "en", 2, "skill"),
    ("sustainability", "responsable RSE", "fr", 2, "skill"),
    ("sustainability", "sustainability officer", "en", 2, "role"),
    ("sustainability", "charge de mission RSE", "fr", 2, "role"),
    ("sustainability", "sustainability reporting", "en", 3, "skill"),
    ("sustainability", "reporting extra-financier", "fr", 3, "skill"),
    ("sustainability", "sustainability data", "en", 3, "skill"),
    ("sustainability", "donnees RSE", "fr", 2, "skill"),

    # ------------------------------------------------------------- climate
    ("carbon", "carbon footprint", "en", 3, "skill"),
    ("carbon", "empreinte carbone", "fr", 3, "skill"),
    ("carbon", "bilan carbone", "fr", 3, "skill"),
    ("carbon", "carbon accounting", "en", 3, "skill"),
    ("carbon", "GHG Protocol", "en", 3, "skill"),
    ("carbon", "scope 3", "en", 3, "skill"),
    ("carbon", "net zero", "en", 2, "skill"),
    ("carbon", "neutralite carbone", "fr", 2, "skill"),
    ("carbon", "decarbonisation", "en", 2, "skill"),
    ("carbon", "decarbonation", "fr", 2, "skill"),
    ("carbon", "climate risk", "en", 3, "skill"),
    ("carbon", "risques climatiques", "fr", 3, "skill"),
    ("carbon", "TCFD", "en", 2, "skill"),
    ("carbon", "SBTi", "en", 2, "skill"),
    ("carbon", "science based targets", "en", 2, "skill"),
    ("carbon", "ISO 14067", "en", 3, "skill"),
    ("carbon", "product carbon footprint", "en", 3, "skill"),
    ("carbon", "carbon analyst", "en", 3, "skill"),

    # ------------------------------------------------ ESG reporting regimes
    ("reporting", "CSRD", "en", 3, "skill"),
    ("reporting", "ESRS", "en", 3, "skill"),
    ("reporting", "EU Taxonomy", "en", 3, "skill"),
    ("reporting", "taxonomie europeenne", "fr", 3, "skill"),
    ("reporting", "double materiality", "en", 3, "skill"),
    ("reporting", "double materialite", "fr", 3, "skill"),
    ("reporting", "GRI", "en", 2, "skill"),
    ("reporting", "extra-financial reporting", "en", 3, "skill"),
    ("reporting", "sustainability report", "en", 2, "skill"),
    ("reporting", "rapport de durabilite", "fr", 2, "skill"),
    ("reporting", "B Corp", "en", 3, "skill"),
    ("reporting", "certification B Corp", "fr", 3, "skill"),
    ("reporting", "EcoVadis", "en", 3, "skill"),
    ("reporting", "sustainability certification", "en", 2, "skill"),
    ("reporting", "assurance", "en", 1, "skill"),

    # -------------------------------------------------- environment and ISO
    ("environment", "environmental consultant", "en", 3, "role"),
    ("environment", "consultant environnement", "fr", 3, "role"),
    ("environment", "environmental engineer", "en", 3, "degree"),
    ("environment", "ingenieur environnement", "fr", 3, "degree"),
    ("environment", "bioengineer", "en", 3, "degree"),
    ("environment", "bioingenieur", "fr", 3, "degree"),
    ("environment", "environmental scientist", "en", 3, "degree"),
    ("environment", "environmental compliance", "en", 3, "skill"),
    ("environment", "conformite environnementale", "fr", 3, "skill"),
    ("environment", "environmental impact assessment", "en", 2, "skill"),
    ("environment", "etude d'incidence", "fr", 2, "skill"),
    ("environment", "permit", "en", 2, "skill"),
    ("environment", "permis d'environnement", "fr", 2, "skill"),
    ("environment", "ISO 14001", "en", 3, "skill"),
    ("environment", "ISO 14067", "en", 3, "skill"),
    ("environment", "ISO 50001", "en", 2, "skill"),
    ("environment", "environmental management system", "en", 3, "skill"),
    ("environment", "systeme de management environnemental", "fr", 3, "skill"),
    ("environment", "audit environnemental", "fr", 2, "skill"),
    ("environment", "environmental audit", "en", 2, "skill"),
    ("environment", "due diligence", "en", 2, "skill"),
    ("environment", "remediation", "en", 2, "skill"),
    ("environment", "pollution", "en", 2, "skill"),
    ("environment", "air quality", "en", 2, "skill"),
    ("environment", "qualite de l'air", "fr", 2, "skill"),
    ("environment", "soil", "en", 2, "thesis"),
    ("environment", "sols", "fr", 2, "thesis"),
    ("environment", "biodiversity", "en", 2, "thesis"),
    ("environment", "biodiversite", "fr", 2, "thesis"),
    ("environment", "nature", "en", 1, "thesis"),
    ("environment", "ecotoxicology", "en", 2, "degree"),
    ("environment", "ecotoxicologie", "fr", 2, "degree"),
    ("environment", "QHSE", "fr", 3, "role"),
    ("environment", "HSE", "en", 2, "role"),
    ("environment", "EHS", "en", 2, "role"),

    # ------------------------------------------------------------- energy
    ("energy", "energy transition", "en", 3, "role"),
    ("energy", "transition energetique", "fr", 3, "role"),
    ("energy", "energy consultant", "en", 3, "role"),
    ("energy", "consultant energie", "fr", 3, "role"),
    ("energy", "energy efficiency", "en", 3, "skill"),
    ("energy", "efficacite energetique", "fr", 3, "skill"),
    ("energy", "renewable energy", "en", 2, "skill"),
    ("energy", "energies renouvelables", "fr", 2, "skill"),
    ("energy", "geothermal", "en", 3, "skill"),
    ("energy", "geothermie", "fr", 3, "skill"),
    ("energy", "building energy", "en", 3, "skill"),
    ("energy", "performance energetique du batiment", "fr", 3, "skill"),
    ("energy", "PEB", "fr", 3, "skill"),
    ("energy", "EPC", "en", 2, "skill"),
    ("energy", "energy modelling", "en", 3, "skill"),
    ("energy", "techno-economic", "en", 3, "skill"),
    ("energy", "technico-economique", "fr", 3, "skill"),
    ("energy", "feasibility study", "en", 3, "skill"),
    ("energy", "etude de faisabilite", "fr", 3, "skill"),
    ("energy", "CAPEX", "en", 2, "skill"),
    ("energy", "ROI", "en", 2, "skill"),
    ("energy", "energy data", "en", 3, "skill"),
    ("energy", "donnees energetiques", "fr", 3, "skill"),
    ("energy", "utilities", "en", 2, "role"),

    # ------------------------------------------------------- water and waste
    ("water", "water management", "en", 2, "skill"),
    ("water", "gestion de l'eau", "fr", 2, "skill"),
    ("water", "wastewater", "en", 2, "skill"),
    ("water", "eaux usees", "fr", 2, "skill"),
    ("water", "water quality", "en", 2, "skill"),
    ("water", "qualite de l'eau", "fr", 2, "skill"),
    ("water", "hydrology", "en", 2, "degree"),
    ("water", "hydrologie", "fr", 2, "degree"),
    ("waste", "waste management", "en", 2, "skill"),
    ("waste", "gestion des dechets", "fr", 2, "skill"),
    ("waste", "circular economy", "en", 2, "skill"),
    ("waste", "economie circulaire", "fr", 2, "skill"),
    ("waste", "recycling", "en", 2, "skill"),
    ("waste", "recyclage", "fr", 2, "skill"),
    ("waste", "life cycle assessment", "en", 3, "skill"),
    ("waste", "analyse de cycle de vie", "fr", 3, "skill"),
    ("waste", "LCA", "en", 3, "skill"),

    # ------------------------------------------------------ data and tools
    ("data", "sustainability data analyst", "en", 3, "role"),
    ("data", "data analyst", "en", 2, "role"),
    ("data", "analyste de donnees", "fr", 2, "role"),
    ("data", "data scientist", "en", 2, "role"),
    ("data", "business intelligence", "en", 2, "tool"),
    ("data", "Power BI", "en", 3, "tool"),
    ("data", "Power Query", "en", 3, "tool"),
    ("data", "Power Automate", "en", 3, "tool"),
    ("data", "dashboard", "en", 2, "tool"),
    ("data", "tableau de bord", "fr", 2, "tool"),
    ("data", "reporting analyst", "en", 2, "tool"),
    ("data", "SQL", "en", 2, "tool"),
    ("data", "Python", "en", 2, "tool"),
    ("data", "data quality", "en", 3, "skill"),
    ("data", "qualite des donnees", "fr", 3, "skill"),
    ("data", "KPI", "en", 3, "skill"),
    ("data", "indicateurs", "fr", 3, "skill"),
    ("data", "GIS", "en", 2, "skill"),
    ("data", "remote sensing", "en", 3, "skill"),
    ("data", "teledetection", "fr", 3, "skill"),
    ("data", "Copernicus", "en", 3, "skill"),

    # ------------------------------------------------------------- agri/food
    ("agri", "agronomy", "en", 2, "thesis"),
    ("agri", "agronomie", "fr", 2, "thesis"),
    ("agri", "agriculture", "en", 2, "degree"),
    ("agri", "hydroponics", "en", 3, "role"),
    ("agri", "plant science", "en", 2, "thesis"),
    ("agri", "sciences vegetales", "fr", 2, "thesis"),
    ("agri", "food sustainability", "en", 2, "skill"),
    ("agri", "agriculture durable", "fr", 2, "skill"),
    ("agri", "supply chain sustainability", "en", 3, "skill"),
    ("agri", "chaine d'approvisionnement durable", "fr", 3, "skill"),
    ("agri", "traceability", "en", 2, "skill"),
    ("agri", "tracabilite", "fr", 2, "skill"),
    ("agri", "EUDR", "en", 3, "skill"),
    ("agri", "deforestation", "en", 2, "skill"),

    # ------------------------------------------------ adjacent but adjacent
    ("adjacent", "environmental policy", "en", 2, "skill"),
    ("adjacent", "politique environnementale", "fr", 2, "skill"),
    ("adjacent", "regulatory watch", "en", 2, "skill"),
    ("adjacent", "veille reglementaire", "fr", 2, "skill"),
    ("adjacent", "public affairs", "en", 1, "skill"),
    ("adjacent", "research assistant", "en", 1, "thesis"),
    ("adjacent", "PhD", "en", 1, "thesis"),
    ("adjacent", "postdoc", "en", 1, "thesis"),
    ("adjacent", "internship", "en", 1, "role"),
    ("adjacent", "stage", "fr", 1, "role"),
    ("adjacent", "graduate programme", "en", 2, "role"),
    ("adjacent", "young graduate", "en", 2, "role"),
    ("adjacent", "jeune diplome", "fr", 2, "role"),
]


def rows():
    """Keyword rows in the same schema as the registry, so one CSV holds both
    halves of the pipeline."""
    out = []
    for theme, kw, lang, weight, source in KEYWORDS:
        slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in kw)
        while "--" in slug:
            slug = slug.replace("--", "-")
        out.append(Row(
            category="keyword", country="ANY", name=kw, url="https://",
            language=lang, sector="", size="",
            what_it_lists=f"theme: {theme}",
            access="open", fit="high" if weight == 3 else "medium" if weight == 2 else "low",
            priority=1 if weight == 3 else 2 if weight == 2 else 3,
            notes=f"theme={theme}; weight={weight}; source={source}",
            id=f"keyword-{theme}-{slug.strip('-')}",
        ))
    return out
