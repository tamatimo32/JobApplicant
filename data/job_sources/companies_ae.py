"""United Arab Emirates. The bosses are Masdar, DEWA, ADNOC, TAQA and the
environment authorities; the useful SME layer is the specialist ESG and
green-building consultancies, which hire junior analysts directly.
"""

from .model import company as C

ROWS = []
_add = ROWS.append


def c(name, url, sector, size, fit="medium", priority=2, note=""):
    _add(C("AE", name, url, sector, size, fit, priority, note))


# --- energy and utilities
c("Masdar", "https://www.masdar.ae", "energy", "large", "high", 1,
  "Abu Dhabi renewable-energy company; the highest-profile clean-energy employer.")
c("DEWA", "https://www.dewa.gov.ae", "utilities", "large", "high", 1,
  "Dubai Electricity and Water Authority.")
c("TAQA", "https://www.taqa.com", "energy", "large", "high", 1)
c("ADNOC", "https://www.adnoc.ae", "energy", "large", "medium", 2)
c("EWEC (Emirates Water and Electricity Company)", "https://www.ewec.ae", "energy",
  "mid", "high", 2, "Runs the emirate's power and water procurement.")
c("Emirates Global Aluminium", "https://www.ega.ae", "industry", "large", "medium", 2)
c("SNOC (Sharjah National Oil Corporation)", "https://www.snoc.ae", "energy", "mid",
  "medium", 3)
c("Dubai Municipality", "https://www.dm.gov.ae", "public_body", "large", "high", 2)
c("Sharjah Electricity and Water Authority", "https://www.sewa.gov.ae", "utilities",
  "mid", "medium", 3)
c("ADDC (Abu Dhabi Distribution Company)", "https://www.addc.ae", "utilities",
  "mid", "medium", 3)
c("AADC (Al Ain Distribution Company)", "https://www.aadc.ae", "utilities", "mid",
  "medium", 3)

# --- environment and sustainability bodies
c("Environment Agency Abu Dhabi", "https://www.ead.gov.ae", "public_body", "mid",
  "high", 1, "The emirate's environmental regulator.")
c("Ministry of Climate Change and Environment", "https://www.moccae.gov.ae",
  "public_body", "mid", "high", 1)
c("Emirates Nature-WWF", "https://www.emiratesnaturewwf.ae", "ngo", "sme", "high", 2)
c("Abu Dhabi Department of Energy", "https://www.doe.gov.ae", "public_body", "mid",
  "high", 2)
c("Sharjah Environment and Protected Areas Authority", "https://www.epaah.ae",
  "public_body", "sme", "medium", 3)

# --- waste and circular economy
c("Bee'ah", "https://www.beeah.ae", "waste", "large", "high", 1)
c("Tadweer (Abu Dhabi Waste Management)", "https://www.tadweer.ae", "waste", "mid",
  "high", 1)
c("Veolia UAE", "https://www.veolia.com", "waste", "large", "high", 2)
c("Imdaad", "https://www.imdaad.ae", "services", "large", "medium", 2)
c("Enviro Services", "https://www.enviroservices.ae", "waste", "sme", "high", 3)
c("Dulsco", "https://www.dulsco.com", "waste", "large", "medium", 3)

# --- ESG, environmental and green-building consultancies (the SME layer)
c("AESG", "https://www.aesg.com", "env_consulting", "mid", "high", 1,
  "Sustainability, environmental and commissioning consultancy; hires juniors.")
c("WKC Group", "https://www.wkcgroup.com", "env_consulting", "sme", "high", 2,
  "Environmental impact assessment and acoustics.")
c("Accuracy", "https://www.proaccuracy.com", "env_consulting", "sme", "high", 3)
c("Uniqus", "https://www.uniqus.com", "env_consulting", "mid", "high", 3)
c("Planet First", "https://www.planetfirst.ae", "env_consulting", "sme", "high", 2,
  "ESG reporting, LCA, EcoVadis and ISO support for SMEs.")
c("Smart Sustain Transformation Consultancies", "https://www.sstc.ae", "env_consulting",
  "sme", "high", 3)
c("Environmental International Consultants", "https://www.eic.ae", "env_consulting",
  "sme", "high", 2)
c("EHS Consultants", "https://www.ehsconsultants.ae", "env_consulting", "sme",
  "high", 3)
c("Outlook Industrial Consultants", "https://www.outlookic.com", "env_consulting",
  "sme", "medium", 3)
c("Buro Happold UAE", "https://www.burohappold.com", "buildings", "large", "high", 2)
c("AtkinsRealis Middle East", "https://www.atkinsrealis.com", "engineering", "large",
  "high", 2)
c("Khatib & Alami", "https://www.khatibalami.com", "engineering", "large", "medium", 3)
c("Dar Al-Handasah", "https://www.dar.com", "engineering", "large", "medium", 3)
c("Bureau Veritas UAE", "https://www.bureauveritas.ae", "services", "large", "high", 3)
# --- real estate, transport, finance, industry
c("Emaar", "https://www.emaar.com", "buildings", "large", "medium", 3)
c("Aldar Properties", "https://www.aldar.com", "buildings", "large", "high", 2,
  "Large sustainability and green-finance programme.")
c("Majid Al Futtaim", "https://www.majidalfuttaim.com", "retail", "large", "high", 2,
  "Net-positive commitments across malls and retail.")
c("DP World", "https://www.dpworld.com", "transport", "large", "high", 2)
c("AD Ports Group", "https://www.adportsgroup.com", "transport", "large", "medium", 3)
c("Emirates Group", "https://www.emiratesgroupcareers.com", "transport", "large",
  "medium", 3)
c("Etihad Airways", "https://www.etihad.com", "transport", "large", "medium", 3)
c("Mubadala", "https://www.mubadala.com", "finance", "large", "high", 2)
c("Abu Dhabi Investment Authority", "https://www.adia.ae", "finance", "large",
  "medium", 3)
c("Emirates NBD", "https://www.emiratesnbd.com", "finance", "large", "high", 2)
c("First Abu Dhabi Bank", "https://www.bankfab.com", "finance", "large", "high", 2)
c("Mashreq", "https://www.mashreqbank.com", "finance", "large", "medium", 3)
c("Dubai Islamic Bank", "https://www.dib.ae", "finance", "large", "medium", 3)
c("Borouge", "https://www.borouge.com", "chemicals", "large", "medium", 2)
c("Strata Manufacturing", "https://www.strata.ae", "industry", "mid", "medium", 3)
c("Unilever MENA", "https://www.unilever.com", "agri_food", "large", "medium", 3)
c("Agthia Group", "https://www.agthia.com", "agri_food", "large", "medium", 3)
c("Al Ain Farms", "https://www.alainfarms.com", "agri_food", "mid", "medium", 3)
