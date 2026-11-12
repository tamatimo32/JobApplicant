"""Australia. The water utilities and the state environmental regulators are
the structural matches: they hire environmental scientists and data analysts
in bulk, and they are used to sponsoring visas for the right candidate.
"""

from .model import company as C

ROWS = []
_add = ROWS.append


def c(name, url, sector, size, fit="medium", priority=2, note=""):
    _add(C("AU", name, url, sector, size, fit, priority, note))


# --- water utilities (the biggest single cluster for this profile)
c("Sydney Water", "https://www.sydneywater.com.au", "water", "large", "high", 1,
  "Australia's largest water utility; hires environmental scientists and data analysts.")
c("Melbourne Water", "https://www.melbournewater.com.au", "water", "large", "high", 1)
c("Yarra Valley Water", "https://www.yvw.com.au", "water", "mid", "high", 2)
c("South East Water (VIC)", "https://www.southeastwater.com.au", "water", "mid", "high", 2)
c("Seqwater", "https://www.seqwater.com.au", "water", "large", "high", 2)
c("Water Corporation (WA)", "https://www.watercorporation.com.au", "water", "large", "high", 2)
c("SA Water", "https://www.sawater.com.au", "water", "large", "high", 2)
c("Icon Water", "https://www.iconwater.com.au", "water", "mid", "high", 3)
c("TasWater", "https://www.taswater.com.au", "water", "mid", "high", 3)
c("Hunter Water", "https://www.hunterwater.com.au", "water", "mid", "high", 3)
c("Unitywater", "https://www.unitywater.com.au", "water", "mid", "high", 3)
c("WaterNSW", "https://www.waternsw.com.au", "water", "large", "high", 2)
c("Power and Water Corporation (NT)", "https://www.powerwater.com.au", "utilities",
  "mid", "high", 3)

# --- energy
c("AGL Energy", "https://www.agl.com.au", "energy", "large", "high", 1)
c("Origin Energy", "https://www.originenergy.com.au", "energy", "large", "high", 1)
c("EnergyAustralia", "https://www.energyaustralia.com.au", "energy", "large", "high", 2)
c("Snowy Hydro", "https://www.snowyhydro.com.au", "energy", "large", "high", 2)
c("Transgrid", "https://www.transgrid.com.au", "energy", "mid", "high", 2)
c("AusNet Services", "https://www.ausnetservices.com.au", "energy", "large", "high", 2)
c("Powerlink Queensland", "https://www.powerlink.com.au", "energy", "mid", "high", 3)
c("ElectraNet", "https://www.electranet.com.au", "energy", "mid", "high", 3)
c("Western Power", "https://www.westernpower.com.au", "utilities", "large", "high", 3)
c("Endeavour Energy", "https://www.endeavourenergy.com.au", "utilities", "large",
  "medium", 3)
c("Essential Energy", "https://www.essentialenergy.com.au", "utilities", "large",
  "medium", 3)
c("Ausgrid", "https://www.ausgrid.com.au", "utilities", "large", "medium", 3)
c("Neoen Australia", "https://neoen.com", "energy", "mid", "high", 2)
c("Tilt Renewables", "https://www.tiltrenewables.com", "energy", "mid", "high", 3)
c("APA Group", "https://www.apa.com.au", "energy", "large", "medium", 2)
c("Woodside Energy", "https://www.woodside.com", "energy", "large", "medium", 2)
c("Santos", "https://www.santos.com", "energy", "large", "medium", 3)
c("Fortescue", "https://www.fortescue.com", "mining", "large", "high", 2,
  "Heavy investment in green hydrogen and decarbonisation.")

# --- environment, waste, engineering, research
c("Cleanaway", "https://www.cleanaway.com.au", "waste", "large", "high", 1,
  "Largest waste-management company in the country.")
c("Veolia Australia", "https://www.veolia.com.au", "waste", "large", "high", 1)
c("SUEZ Australia", "https://www.suez.com.au", "waste", "large", "high", 2)
c("Repurpose It", "https://www.repurposeit.com.au", "waste", "sme", "high", 3)
c("Orica", "https://www.orica.com", "chemicals", "large", "medium", 2)
c("Incitec Pivot", "https://www.incitecpivot.com.au", "chemicals", "large", "medium", 3)
c("BHP", "https://www.bhp.com", "mining", "large", "medium", 2)
c("Rio Tinto", "https://www.riotinto.com", "mining", "large", "medium", 2)
c("South32", "https://www.south32.net", "mining", "large", "medium", 3)
c("Newmont Australia", "https://www.newmont.com", "mining", "large", "low", 3)
c("Aurecon", "https://www.aurecongroup.com", "engineering", "large", "high", 1)
c("GHD", "https://www.ghd.com", "engineering", "large", "high", 1)
c("EMM Consulting", "https://www.emmconsulting.com.au", "env_consulting", "mid",
  "high", 2, "Australian environmental planning and impact assessment firm.")
c("Umwelt", "https://www.umwelt.net.au", "env_consulting", "mid", "high", 2)
c("Niche Environment and Heritage", "https://www.niche-eh.com.au", "env_consulting",
  "sme", "high", 3)
c("Biosis", "https://www.biosis.com.au", "env_consulting", "sme", "high", 3)
c("Ecosure", "https://www.ecosure.com.au", "env_consulting", "sme", "high", 3)
c("Alluvium", "https://www.alluvium.com.au", "env_consulting", "sme", "high", 2,
  "Water and environmental science consultancy.")
c("Hydrobiology", "https://www.hydrobiology.com.au", "env_consulting", "sme", "high", 3)
c("CSIRO", "https://www.csiro.au", "research", "large", "high", 1,
  "Australia's national science agency; environment, water and energy divisions.")
c("Australian Institute of Marine Science", "https://www.aims.gov.au", "research",
  "mid", "high", 3)
c("Bureau of Meteorology", "https://www.bom.gov.au", "public_body", "large", "medium", 2)
c("Geoscience Australia", "https://www.ga.gov.au", "public_body", "large", "medium", 3)
c("ANSTO", "https://www.ansto.gov.au", "research", "mid", "low", 3)

# --- government departments (job-specific, beyond APS Jobs)
c("DCCEEW (Climate Change, Energy, Environment and Water)",
  "https://www.dcceew.gov.au", "public_body", "large", "high", 1,
  "The central federal department for this profile.")
c("DAFF (Agriculture, Fisheries and Forestry)", "https://www.agriculture.gov.au",
  "public_body", "large", "high", 2)
c("Clean Energy Regulator", "https://www.cleanenergyregulator.gov.au", "public_body",
  "mid", "high", 1, "Administers the carbon market and renewable schemes.")
c("Net Zero Economy Authority", "https://www.nzea.gov.au", "public_body", "mid",
  "high", 2)
c("ARENA (Australian Renewable Energy Agency)", "https://arena.gov.au", "public_body",
  "mid", "high", 2)
c("CEFC (Clean Energy Finance Corporation)", "https://www.cefc.com.au", "finance",
  "mid", "high", 1, "Green bank; investment and impact reporting roles.")
c("EPA Victoria", "https://www.epa.vic.gov.au", "public_body", "mid", "high", 1)
c("NSW EPA", "https://www.epa.nsw.gov.au", "public_body", "mid", "high", 1)
c("Queensland DESI", "https://www.des.qld.gov.au", "public_body", "large", "high", 2)
c("WA Department of Water and Environmental Regulation", "https://www.dwer.wa.gov.au",
  "public_body", "mid", "high", 2)
c("SA Department for Environment and Water", "https://www.environment.sa.gov.au",
  "public_body", "mid", "high", 2)

# --- finance and food
c("Macquarie Group", "https://www.macquarie.com", "finance", "large", "medium", 2,
  "Large green-investment and climate-reporting function.")
c("Westpac", "https://www.westpac.com.au", "finance", "large", "medium", 3)
c("NAB", "https://www.nab.com.au", "finance", "large", "medium", 3)
c("CBA", "https://www.commbank.com.au", "finance", "large", "medium", 3)
c("ANZ", "https://www.anz.com.au", "finance", "large", "medium", 3)
c("Woolworths Group", "https://www.woolworthsgroup.com.au", "retail", "large", "high", 2)
c("Coles Group", "https://www.colesgroup.com.au", "retail", "large", "high", 2)
c("Brambles", "https://www.brambles.com", "services", "large", "medium", 3)
c("Lendlease", "https://www.lendlease.com", "buildings", "large", "medium", 2)
c("Stockland", "https://www.stockland.com.au", "buildings", "large", "medium", 3)
c("Dexus", "https://www.dexus.com", "buildings", "large", "high", 2,
  "Property group with a serious ESG and climate-resilience programme.")
