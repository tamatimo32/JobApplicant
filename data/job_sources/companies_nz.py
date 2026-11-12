"""New Zealand. Small market: the electricity gentailers, the water
authorities, the Crown research institutes and the two big engineering
consultancies cover most of the relevant hiring.
"""

from .model import company as C

ROWS = []
_add = ROWS.append


def c(name, url, sector, size, fit="medium", priority=2, note=""):
    _add(C("NZ", name, url, sector, size, fit, priority, note))


# --- electricity and utilities
c("Meridian Energy", "https://www.meridianenergy.co.nz", "energy", "large", "high", 1)
c("Contact Energy", "https://www.contactenergy.co.nz", "energy", "large", "high", 1)
c("Mercury NZ", "https://www.mercury.co.nz", "energy", "large", "high", 1)
c("Genesis Energy", "https://www.genesisenergy.co.nz", "energy", "large", "high", 1)
c("Transpower", "https://www.transpower.co.nz", "energy", "mid", "high", 1,
  "Grid operator; publishes an energy-transition planning programme.")
c("Vector", "https://www.vector.co.nz", "utilities", "large", "medium", 2)
c("Powerco", "https://www.powerco.co.nz", "utilities", "mid", "medium", 3)
c("Orion NZ", "https://www.oriongroup.co.nz", "utilities", "mid", "medium", 3)
c("Trustpower / Manawa Energy", "https://www.manawaenergy.co.nz", "energy", "mid",
  "high", 2)
c("Z Energy", "https://www.z.co.nz", "energy", "large", "medium", 3)
c("Air New Zealand", "https://www.airnewzealand.co.nz", "transport", "large",
  "medium", 3, "Has a formal decarbonisation programme.")
c("KiwiRail", "https://www.kiwirail.co.nz", "transport", "large", "medium", 3)

# --- water
c("Watercare", "https://www.watercare.co.nz", "water", "large", "high", 1,
  "Auckland's water utility; the largest single water employer.")
c("Wellington Water", "https://www.wellingtonwater.co.nz", "water", "mid", "high", 2)
c("Christchurch City Council Water", "https://www.ccc.govt.nz", "water", "large",
  "medium", 3)
c("Taumata Arowai", "https://www.taumataarowai.govt.nz", "public_body", "mid",
  "high", 2, "The water-services regulator, established recently.")
c("Dunedin City Council - Three Waters", "https://www.dunedin.govt.nz", "water",
  "mid", "medium", 3)

# --- waste and environmental services
c("Waste Management NZ", "https://www.wastemanagement.co.nz", "waste", "large",
  "high", 1)
c("EnviroWaste", "https://www.envirowaste.co.nz", "waste", "large", "high", 2)
c("Veolia New Zealand", "https://www.veolia.co.nz", "waste", "large", "high", 2)
c("Ecolab NZ", "https://www.ecolab.com", "services", "large", "low", 3)
c("Toha", "https://www.toha.nz", "software_data", "sme", "medium", 3,
  "Environmental data platform; small team, data-heavy roles.")

# --- research and public bodies
c("NIWA", "https://niwa.co.nz", "research", "large", "high", 1,
  "National Institute of Water and Atmospheric Research; the strongest research match.")
c("Manaaki Whenua - Landcare Research", "https://www.landcareresearch.co.nz",
  "research", "mid", "high", 1)
c("Scion", "https://www.scionresearch.com", "research", "mid", "high", 2,
  "Forestry and biomaterials research.")
c("AgResearch", "https://www.agresearch.co.nz", "research", "mid", "high", 2)
c("Plant & Food Research", "https://www.plantandfood.co.nz", "research", "mid",
  "high", 2)
c("GNS Science", "https://www.gns.cri.nz", "research", "mid", "high", 2)
c("ESR", "https://www.esr.cri.nz", "research", "mid", "medium", 3)
c("Ministry for the Environment", "https://www.mfe.govt.nz", "public_body", "mid",
  "high", 1, "The central policy department for this profile.")
c("Department of Conservation", "https://www.doc.govt.nz", "public_body", "large",
  "high", 1)
c("Ministry for Primary Industries", "https://www.mpi.govt.nz", "public_body",
  "large", "high", 2)
c("Ministry of Business, Innovation and Employment (energy policy)",
  "https://www.mbie.govt.nz", "public_body", "large", "high", 2)
c("Environment Canterbury", "https://www.ecan.govt.nz", "public_body", "mid", "high", 2,
  "Regional council; water and land management.")
c("Greater Wellington Regional Council", "https://www.gw.govt.nz", "public_body",
  "mid", "high", 3)
c("Auckland Council", "https://www.aucklandcouncil.govt.nz", "public_body", "large",
  "high", 2)
c("Waikato Regional Council", "https://www.waikatoregion.govt.nz", "public_body",
  "mid", "high", 3)
c("Otago Regional Council", "https://www.orc.govt.nz", "public_body", "mid", "high", 3)
c("Callaghan Innovation", "https://www.callaghaninnovation.govt.nz", "research",
  "mid", "medium", 3)
c("EECA (Energy Efficiency and Conservation Authority)", "https://www.eeca.govt.nz",
  "public_body", "sme", "high", 1, "Small agency, directly on-topic.")

# --- engineering and environmental consulting
c("Tonkin + Taylor", "https://www.tonkintaylor.co.nz", "env_consulting", "mid",
  "high", 1, "New Zealand's best-known environmental and geotechnical consultancy.")
c("Beca", "https://www.beca.com", "engineering", "large", "high", 1)
c("Pattle Delamore Partners", "https://www.pdp.co.nz", "env_consulting", "mid",
  "high", 1, "Environmental and water consultancy.")
c("Deloitte New Zealand", "https://www.deloitte.com/nz", "services", "large", "high", 2)
c("PwC New Zealand", "https://www.pwc.co.nz", "services", "large", "high", 2)
c("EY New Zealand", "https://www.ey.com/en_nz", "services", "large", "high", 2)
c("KPMG New Zealand", "https://kpmg.com/nz", "services", "large", "high", 2)

# --- food, agriculture, industry
c("Fonterra", "https://www.fonterra.com", "agri_food", "large", "high", 1,
  "Dairy cooperative; large sustainability and on-farm emissions programme.")
c("Silver Fern Farms", "https://www.silverfern.co.nz", "agri_food", "large", "high", 2)
c("Zespri", "https://www.zespri.com", "agri_food", "large", "high", 2)
c("Synlait", "https://www.synlait.com", "agri_food", "mid", "high", 2)
c("Fletcher Building", "https://www.fletcherbuilding.com", "buildings", "large",
  "medium", 2)
c("Fulton Hogan", "https://www.fultonhogan.com", "engineering", "large", "medium", 3)
c("Downer NZ", "https://www.downer.com", "engineering", "large", "medium", 3)
c("Venture Taranaki", "https://www.venture.org.nz", "public_body", "sme", "low", 3)
c("ANZ New Zealand", "https://www.anz.co.nz", "finance", "large", "medium", 3)
c("Westpac New Zealand", "https://www.westpac.co.nz", "finance", "large", "medium", 3)
c("ASB Bank", "https://www.asb.co.nz", "finance", "large", "medium", 3)
