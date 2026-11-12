"""SME layer: specialist employers, plus the sector federations and clusters
whose member directories are how you actually reach Belgian SMEs at scale.

A note on what a federation row is. A federation is not an employer; it is a
rolling list of several hundred member companies, many of them SMEs that never
appear on a job board. For a scraper it is more valuable than any single
career page: fetch the member directory once, then check the members.
"""

from .model import company as C, board

ROWS = []
_add = ROWS.append


def c(country, name, url, sector, size, fit="high", priority=2, note=""):
    _add(C(country, name, url, sector, size, fit, priority, note))


def fed(name, url, sector, what, note="", listing=""):
    _add(board("federation", "BE", name, url, listing, "fr/nl/en",
               what=what, fit="high", priority=2,
               notes=note or "Federation: its member directory is the real target, "
                             "not the site's own vacancies."))


# =========================================================================== #
# Belgian SME-scale employers, by sector
# =========================================================================== #
# --- sustainable building and energy services
c("BE", "Abora", "https://www.abora.be", "buildings", "sme")
c("BE", "Bati-Tech", "https://www.bati-tech.be", "buildings", "sme", "medium", 3)
c("BE", "D-Sight", "https://www.d-sight.be", "buildings", "sme", "medium", 3)
c("BE", "Eco Energie", "https://www.eco-energie.be", "energy", "sme")
c("BE", "Sunrise Energy", "https://www.sunrise-energy.be", "energy", "sme", "medium", 3)
c("BE", "Watt Matters", "https://www.wattmatters.be", "energy", "sme", "medium", 3)
c("BE", "Futech", "https://www.futech.be", "energy", "mid")
c("BE", "Izen", "https://www.izen.be", "energy", "sme", "medium", 3)
c("BE", "Enerdeal", "https://www.enerdeal.com", "energy", "sme")
c("BE", "Volta Energy", "https://www.volta.energy", "energy", "sme", "medium", 3)
c("BE", "Energent", "https://www.energent.be", "energy", "sme", "medium", 3)
c("BE", "Treepower", "https://www.treepower.be", "energy", "sme", "medium", 3)
c("BE", "Chaudfontaine Energie", "https://www.chaudfontaine-energie.be", "energy",
  "sme", "low", 3)

# --- water, soil and remediation specialists
c("BE", "Sorescu", "https://www.sorescu.be", "water", "sme", "high")
c("BE", "Bodemkundige Dienst van Belgie", "https://www.bdb.be", "water", "sme", "medium", 3)
c("BE", "Grondwerken Verheyden", "https://www.grondwerkenverheyden.be", "water", "sme",
  "low", 3)
c("BE", "Aquaplus", "https://www.aquaplus.be", "water", "sme", "medium", 3)
c("BE", "Hydrosoil", "https://www.hydrosoil.be", "water", "sme", "medium", 3)
c("BE", "Sanitas", "https://www.sanitas.be", "water", "sme", "low", 3)
c("BE", "Ecosphere", "https://www.ecosphere.be", "water", "sme", "medium", 3)

# --- soil, air and environmental monitoring labs
c("BE", "SGS Belgium (laboratories)", "https://www.sgs.com", "services", "large", "high", 3)
c("BE", "Eurofins Belgium", "https://www.eurofins.be", "services", "large", "high", 2,
  "Environmental and food testing laboratories; hires scientists at scale.")
c("BE", "ALS Belgium", "https://www.alsglobal.com", "services", "large", "high", 2)
c("BE", "Synlab Belgium", "https://www.synlab.be", "services", "large", "medium", 3)
c("BE", "Laborelec", "https://www.laborelec.com", "research", "mid", "high", 2,
  "Engie's power-technology research centre.")

# --- agri-food and horticulture SMEs
c("BE", "Rijk Zwaan Belgium", "https://www.rijkzwaan.be", "agri_food", "mid")
c("BE", "Nunhems Belgium", "https://www.nunhems.com", "agri_food", "mid", "high", 3)
c("BE", "Vlaams Zaadhuis", "https://www.vlaamszaadhuis.be", "agri_food", "sme", "high", 3)
c("BE", "Greenyard", "https://www.greenyard.group", "agri_food", "large")
c("BE", "Clarebout Potatoes", "https://www.clarebout.be", "agri_food", "mid", "medium", 3)
c("BE", "Agristo", "https://www.agristo.com", "agri_food", "large", "medium", 3)
c("BE", "Ardo", "https://www.ardo.com", "agri_food", "large", "medium", 3)
c("BE", "Hofland", "https://www.hofland.be", "agri_food", "sme", "medium", 3)
c("BE", "Vandepoel", "https://www.vandepoel.be", "agri_food", "sme", "low", 3)
c("BE", "Bioforum", "https://www.bioforum.be", "agri_food", "sme", "high", 2,
  "Organic-sector federation; also recruits project staff.")
c("BE", "Ligrano", "https://www.ligrano.be", "agri_food", "sme", "medium", 3)
c("BE", "Vitakem", "https://www.vitakem.be", "agri_food", "sme", "low", 3)
c("BE", "Agro-Bio Center", "https://www.agrobio.be", "research", "sme", "medium", 3)

# --- packaging and materials SMEs
c("BE", "Verstraete IML", "https://www.verstraete-iml.com", "packaging", "mid")
c("BE", "Dekapack", "https://www.dekapack.be", "packaging", "sme", "medium", 3)
c("BE", "Comart", "https://www.comart.be", "packaging", "sme", "medium", 3)
c("BE", "Pacombi", "https://www.pacombi.be", "packaging", "sme", "medium", 3)
c("BE", "Eco-Oh!", "https://www.eco-oh.be", "waste", "sme", "high", 2,
  "Recycled plastic compounds; a close match to the packaging angle.")
c("BE", "ETAP Lighting", "https://www.etaplighting.com", "industry", "mid", "medium", 2)
c("BE", "Reynaers Aluminium", "https://www.reynaers.be", "buildings", "large", "medium", 2)
c("BE", "Sioen Industries", "https://www.sioen.com", "industry", "large", "medium", 3)
c("BE", "Vandemoortele", "https://www.vandemoortele.com", "agri_food", "large", "medium", 3)

# --- sustainable finance, impact and advisory SMEs
c("BE", "Impact Finance Belgium", "https://www.impactfinance.be", "finance", "sme", "high", 3)
c("BE", "Be Financité", "https://www.financite.be", "finance", "sme", "medium", 3)
c("BE", "SRIB (Societe Regionale d'Investissement de Bruxelles)", "https://www.srib.be",
  "finance", "sme", "medium", 3)
c("BE", "Wallonie Entreprendre", "https://www.wallonie-entreprendre.be", "finance",
  "mid", "medium", 3)
c("BE", "Participatiemaatschappij Vlaanderen (PMV)", "https://www.pmv.eu", "finance",
  "mid", "medium", 3)
c("BE", "B Corp Belgium community", "https://www.bcorporation.net", "services", "sme",
  "medium", 3, "Directory of Belgian B Corps; each is a mission-aligned employer.")
c("BE", "The Beacon", "https://www.thebeacon.eu", "services", "sme", "medium", 3,
  "Sustainability and innovation hub; hosts many small mission-aligned teams.")

# --- environmental labs, consultancies and one-person-plus firms
c("BE", "Idelux Environnement", "https://www.idelux.be", "waste", "mid", "high", 2,
  "Walloon inter-municipal environmental group.")
c("BE", "Ipalle", "https://www.ipalle.be", "waste", "mid", "high", 3)
c("BE", "Tributerre", "https://www.tributerre.be", "env_consulting", "sme", "medium", 3)
c("BE", "Universite de Namur", "https://www.unamur.be", "research", "large", "medium", 3)
c("BE", "Haute Ecole Lucia de Brouckere", "https://www.heldb.be", "research", "sme",
  "medium", 3)
c("BE", "HENALLUX", "https://www.henallux.be", "research", "sme", "medium", 3)
c("BE", "Institut Meurice", "https://www.imeurice.be", "research", "sme", "medium", 3)
c("BE", "Agro Louvain", "https://www.agrolouvain.be", "research", "sme", "medium", 3)

# =========================================================================== #
# Sector federations and clusters: the route into the SME long tail
# =========================================================================== #
fed("Agoria", "https://agoria.be", "services",
    "Technology industry federation, ~1,900 members, most of them SMEs; "
    "member directory plus its own vacancy board.",
    "The single highest-leverage Belgian directory for engineering and tech SMEs.")
fed("Essenscia", "https://www.essenscia.be", "chemicals",
    "Chemicals, plastics and life-sciences federation; member list of large and "
    "mid-sized plants across Belgium.")
fed("FEBEG", "https://www.febeg.be", "energy",
    "Electricity and gas producers and suppliers; member list is the whole "
    "Belgian energy sector in one page.")
fed("FEBELPACK", "https://www.febelpack.be", "packaging",
    "Packaging industry federation; SME-heavy member directory.")
fed("Comeos", "https://www.comeos.be", "retail",
    "Retail federation; sustainability and packaging roles across members.")
fed("Fevia", "https://www.fevia.be", "agri_food",
    "Food industry federation; the food-processing employers, SMEs included.")
fed("FEBELCEM", "https://www.febelcem.be", "buildings",
    "Cement industry association.")
fed("Voka", "https://www.voka.be", "services",
    "Flemish chamber network; publishes a large SME vacancy feed.",
    "Its job board is a better SME source than VDAB for Flanders.")
fed("UCM", "https://www.ucm.be", "services",
    "Union des Classes Moyennes, the Walloon and Brussels SME association. "
    "Publishes ESG, CSRD and carbon guidance for SMEs and runs Camille.be, its "
    "job board for small employers.")
fed("SNI", "https://www.sni.be", "services",
    "Neutral union for the self-employed and SMEs.")
fed("BeCommerce", "https://www.becommerce.be", "services",
    "E-commerce federation.")
fed("VITO (cleantech research and cluster)", "https://vito.be", "energy",
    "Flemish cleantech research centre, 1,300 staff; the former Cleantech "
    "Flanders cluster now resolves here.")
fed("GreenWin", "https://www.greenwin.be", "energy",
    "Walloon cleantech cluster, 220 members (170+ companies) in green chemistry, "
    "construction and environmental technologies; its Jobs Centre relays member "
    "vacancies, which is exactly the SME feed this profile needs.",
    listing="https://www.greenwin.be/fr/news/4")
fed("Tweed / Smart Grids cluster", "https://www.tweed.be", "energy",
    "Walloon sustainable-energy cluster.")
fed("Blue Cluster", "https://www.blueluster.be", "water",
    "Flemish marine and coastal cluster, including offshore energy.")
fed("Catalisti", "https://www.catalisti.be", "chemicals",
    "Flemish chemical and plastics innovation cluster.")
fed("Flanders' Food", "https://www.flandersfood.com", "agri_food",
    "Flemish agri-food innovation cluster; SME-heavy.")
fed("Wagralim", "https://www.wagralim.be", "agri_food",
    "Walloon agri-food innovation cluster.")
fed("Agoria Environnement", "https://www.agoriaenv.be", "env_consulting",
    "Environmental services arm of Agoria.")
fed("BECI", "https://www.beci.be", "services",
    "Brussels chamber of commerce; SME members and a job board.")

