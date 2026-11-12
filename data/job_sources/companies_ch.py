"""Switzerland. Two federal research institutes (Eawag, Empa) and the ETH
domain are the closest structural matches to an environmental bioengineering
degree, alongside the energy utilities and the food and materials majors.
"""

from .model import company as C

ROWS = []
_add = ROWS.append


def c(name, url, sector, size, fit="medium", priority=2, note=""):
    _add(C("CH", name, url, sector, size, fit, priority, note))


# --- federal research and universities
c("Eawag", "https://www.eawag.ch", "research", "mid", "high", 1,
  "Swiss Federal Institute of Aquatic Science and Technology; the best single "
  "research match in the country.")
c("Empa", "https://www.empa.ch", "research", "mid", "high", 1,
  "Federal Laboratories for Materials Science and Technology.")
c("PSI (Paul Scherrer Institute)", "https://www.psi.ch", "research", "large", "high", 2,
  "Energy systems analysis and environmental research.")
c("WSL (Snow and Landscape Research)", "https://www.wsl.ch", "research", "mid",
  "high", 1, "Federal research institute for landscape, forest and snow.")
c("ETH Zurich", "https://ethz.ch", "research", "large", "high", 1)
c("EPFL", "https://www.epfl.ch", "research", "large", "high", 2)
c("University of Zurich", "https://www.uzh.ch", "research", "large", "medium", 2)
c("University of Bern", "https://www.unibe.ch", "research", "large", "medium", 3)
c("University of Basel", "https://www.unibas.ch", "research", "large", "medium", 3)
c("ETH Domain - EAWAG spin-offs", "https://www.eawag.ch/en/aboutus/spinoffs", "research",
  "sme", "high", 3, "Spin-off directory; each hire is a niche fit.")
c("Agroscope", "https://www.agroscope.admin.ch", "research", "mid", "high", 1,
  "Federal agricultural research; agronomy and environmental impact.")
c("WSL Institute for Snow and Avalanche Research", "https://www.slf.ch", "research",
  "mid", "medium", 3)
c("Swiss Federal Office for the Environment (FOEN)", "https://www.bafu.admin.ch",
  "public_body", "mid", "high", 1, "The federal environment agency.")
c("Swiss Federal Office of Energy", "https://www.bfe.admin.ch", "public_body", "mid",
  "high", 2)
c("Swiss Federal Office for Agriculture", "https://www.blw.admin.ch", "public_body",
  "mid", "medium", 3)
c("MeteoSwiss", "https://www.meteoswiss.admin.ch", "public_body", "mid", "medium", 3)
c("Swisstopo", "https://www.swisstopo.admin.ch", "public_body", "mid", "medium", 3)

# --- energy and utilities
c("Axpo", "https://www.axpo.com", "energy", "large", "high", 1)
c("BKW", "https://www.bkw.ch", "energy", "large", "high", 1)
c("Alpiq", "https://www.alpiq.com", "energy", "large", "high", 1)
c("Swissgrid", "https://www.swissgrid.ch", "energy", "mid", "high", 2)
c("Swisspower", "https://www.swisspower.ch", "energy", "sme", "high", 3)
c("ewz (Zurich municipal utility)", "https://www.ewz.ch", "energy", "large", "high", 2)
c("IWB Basel", "https://www.iwb.ch", "energy", "mid", "high", 2)
c("Energie 360", "https://www.energie360.ch", "energy", "mid", "high", 2)
c("CKW", "https://www.ckw.ch", "energy", "mid", "high", 2)
c("Repower", "https://www.repower.com", "energy", "mid", "medium", 3)
c("Romande Energie", "https://www.romande-energie.ch", "energy", "large", "high", 2)
c("Services Industriels de Geneve (SIG)", "https://ww2.sig-ge.ch", "utilities",
  "large", "high", 2)
c("Helvetia Environment", "https://www.helvetia-environment.ch", "waste", "mid",
  "high", 2, "One of the larger Swiss waste and recycling groups.")
c("Veolia Switzerland", "https://www.veolia.ch", "waste", "large", "high", 2)
c("ERZ Entsorgung + Recycling Zurich", "https://www.stadt-zuerich.ch/erz", "waste",
  "mid", "high", 3)
c("Gruner", "https://www.gruner.ch", "engineering", "mid", "high", 2)
c("Implenia", "https://www.implenia.com", "engineering", "large", "medium", 2)
c("Eberhard", "https://www.eberhard.ch", "engineering", "mid", "medium", 3)
c("Basler & Hofmann", "https://www.baslerhofmann.ch", "engineering", "mid", "high", 2)
c("Amstein + Walthert", "https://www.amstein-walthert.ch", "buildings", "mid",
  "high", 2)
c("CSD Ingenieure", "https://www.csd.ch", "engineering", "mid", "high", 3)
c("Holinger", "https://www.holinger.com", "engineering", "mid", "high", 3)

# --- environmental consulting and certification
c("EBP (Ernst Basler + Partner)", "https://www.ebp.ch", "env_consulting", "mid",
  "high", 1, "Swiss sustainability and infrastructure consultancy.")
c("econcept", "https://www.econcept.ch", "env_consulting", "sme", "high", 2)
c("Infras", "https://www.infras.ch", "env_consulting", "sme", "high", 2,
  "Research and consultancy on energy and environment policy.")
c("TEP Energy", "https://www.tep-energy.ch", "env_consulting", "sme", "high", 2)
c("Planair", "https://www.planair.ch", "env_consulting", "sme", "high", 2)
c("Intep", "https://www.intep.com", "env_consulting", "sme", "high", 2)
c("Carbura", "https://www.carbura.ch", "env_consulting", "sme", "medium", 3)
c("Anthesis", "https://www.anthesisgroup.com", "env_consulting", "large",
  "high", 1, "One row for the firm; offices in BE, CH, AU and AE.")
c("Swiss Climate", "https://www.swissclimate.ch", "env_consulting", "sme", "high", 2)
c("MyClimate", "https://www.myclimate.org", "ngo", "sme", "high", 2,
  "Carbon-offset foundation; project and advisory roles.")
c("ClimatePartner Switzerland", "https://www.climatepartner.com", "env_consulting",
  "mid", "high", 2)
c("WWF Switzerland", "https://www.wwf.ch", "ngo", "mid", "medium", 2)
c("Pro Natura", "https://www.pronatura.ch", "ngo", "mid", "medium", 3)
c("Greenpeace Switzerland", "https://www.greenpeace.ch", "ngo", "mid", "medium", 3)

# --- food, pharma, materials, industry
c("Nestlé", "https://www.nestle.com", "agri_food", "large", "high", 1,
  "Headquartered in Vevey; large sustainability and sourcing function.")
c("Syngenta", "https://www.syngenta.com", "agri_food", "large", "high", 1,
  "Crop science; agronomy and environmental fate work.")
c("Syngenta Group", "https://www.syngentagroup.com", "agri_food", "large", "high", 3)
c("Lonza", "https://www.lonza.com", "pharma", "large", "medium", 2)
c("Roche", "https://www.roche.com", "pharma", "large", "medium", 2)
c("Novartis", "https://www.novartis.com", "pharma", "large", "medium", 2)
c("Holcim", "https://www.holcim.com", "industry", "large", "high", 1,
  "Cement; one of the largest industrial decarbonisation programmes in Europe.")
c("ABB", "https://www.abb.com", "industry", "large", "medium", 2)
c("Georg Fischer", "https://www.georgfischer.com", "industry", "large", "medium", 3)
c("Sika", "https://www.sika.com", "chemicals", "large", "medium", 2)
c("Clariant", "https://www.clariant.com", "chemicals", "large", "medium", 2)
c("Givaudan", "https://www.givaudan.com", "chemicals", "large", "medium", 2)
c("Firmenich (dsm-firmenich)", "https://www.dsm-firmenich.com", "chemicals", "large",
  "medium", 2)
c("Buhler", "https://www.buhlergroup.com", "industry", "large", "medium", 3)
c("Swiss Re", "https://www.swissre.com", "finance", "large", "high", 2,
  "Climate-risk research is a genuine business line here.")
c("Zurich Insurance", "https://www.zurich.com", "finance", "large", "medium", 2)
c("UBS", "https://www.ubs.com", "finance", "large", "high", 2,
  "Sustainable finance and climate-risk reporting.")
c("Migros", "https://www.migros.ch", "retail", "large", "high", 2)
c("Coop", "https://www.coop.ch", "retail", "large", "high", 2)
c("Swisscom", "https://www.swisscom.ch", "services", "large", "low", 3)
c("SBB", "https://www.sbb.ch", "transport", "large", "high", 2,
  "Rail operator with a large environmental function.")
c("Swiss Post", "https://www.post.ch", "services", "large", "medium", 3)
c("Emch+Berger", "https://www.emchberger.ch", "engineering", "mid", "medium", 3)
c("Geotest", "https://www.geotest.ch", "env_consulting", "sme", "high", 3)
c("Soilcom", "https://www.soilcom.ch", "env_consulting", "sme", "medium", 3)
