"""Belgium: employers whose career pages are worth polling for an
environmental bioengineer working in sustainability data, ESG reporting,
energy, water, waste and environmental compliance.

`size` is large (>250 staff or a listed/major group), mid (roughly 50-250)
or sme (<50, or a specialist boutique). Bigger is not better here: an SME
often has one person doing exactly this job.
"""

from .model import company as C

ROWS = []
_add = ROWS.append


def c(name, url, sector, size, fit="medium", priority=2, note=""):
    _add(C("BE", name, url, sector, size, fit, priority, note))


# --- energy and utilities
c("Engie Belgium", "https://www.engie.be", "energy", "large", "high", 1)
c("Engie Electrabel", "https://www.engie-electrabel.be", "energy", "large", "high", 3)
c("Luminus", "https://www.luminus.be", "energy", "large", "high", 1)
c("Eneco Belgium", "https://www.eneco.be", "energy", "mid", "high", 2)
c("Elia Group", "https://www.elia.be", "energy", "large", "high", 1,
  "Transmission system operator; publishes a big energy-transition research programme.")
c("Fluxys", "https://www.fluxys.com", "energy", "large", "medium", 2)
c("Tractebel", "https://www.tractebel-engie.com", "engineering", "large", "high", 1,
  "Engie's engineering arm; strong on nuclear, hydro and grid studies.")
c("Eoly (Colruyt Group)", "https://www.eoly.be", "energy", "mid", "high", 2)
c("Aspiravi", "https://www.aspiravi.be", "energy", "mid", "high", 2)
c("Parkwind", "https://www.parkwind.be", "energy", "mid", "high", 2)
c("Elicio", "https://www.elicio.be", "energy", "mid", "high", 2)
c("Otary", "https://www.otary.be", "energy", "sme", "high", 3)
c("Renner Energies", "https://www.rennerenergies.be", "energy", "sme", "high", 3)
c("Storm", "https://www.storm.be", "energy", "sme", "high", 3)
c("Enersol", "https://www.enersol.be", "energy", "sme", "high", 3)
c("Aukera Energy", "https://www.aukera.com", "energy", "sme", "high", 3)
c("PerPetum Energy", "https://www.perpetum.be", "energy", "sme", "high", 3)
c("Bolt (Belgian energy)", "https://www.bolt.be", "energy", "sme", "medium", 3)
c("Belgian Eco Energy", "https://www.be-eco.be", "energy", "sme", "medium", 3)
c("Resa", "https://www.resa.be", "utilities", "mid", "medium", 3)
c("ORES", "https://www.ores.be", "utilities", "mid", "medium", 3)
c("Sibelga", "https://www.sibelga.be", "utilities", "mid", "medium", 3)
c("Fluvius", "https://www.fluvius.be", "utilities", "large", "medium", 3)
c("Farys", "https://www.farys.be", "water", "large", "high", 2)
c("Water-Link", "https://www.water-link.be", "water", "mid", "high", 2)
c("Vivaqua", "https://www.vivaqua.be", "water", "large", "high", 2)
c("SWDE (Societe wallonne des eaux)", "https://www.swde.be", "water", "large", "high", 2)
c("De Watergroep", "https://www.dewatergroep.be", "water", "large", "high", 2)
c("PIDPA", "https://www.pidpa.be", "water", "mid", "high", 3)
c("Aquafin", "https://www.aquafin.be", "water", "large", "high", 1,
  "Wastewater treatment for Flanders; heavy on environmental reporting.")
c("in BW", "https://www.inbw.be", "water", "mid", "medium", 3)
c("CILE", "https://www.cile.be", "water", "mid", "medium", 3)
c("Waterleau", "https://www.waterleau.com", "water", "mid", "high", 2,
  "Belgian water-technology exporter, 600 staff.")
c("Eloy Water", "https://www.eloywater.com", "water", "sme", "high", 3)
c("BOSAQ", "https://www.bosaq.com", "water", "sme", "high", 3,
  "Water consultancy and technology spin-off; audits and water studies.")
c("Shayp", "https://www.shayp.com", "water", "sme", "high", 3,
  "Brussels water-data startup; very close to the data side of this profile.")

# --- waste and circular economy
c("Indaver", "https://www.indaver.be", "waste", "large", "high", 1)
c("Renewi", "https://www.renewi.com", "waste", "large", "high", 2)
c("Veolia Belgium", "https://www.veolia.be", "waste", "large", "high", 1)
c("SUEZ Belgium", "https://www.suez.be", "waste", "large", "high", 1)
c("Galloo", "https://www.galloo.com", "waste", "large", "medium", 2)
c("Quatra", "https://www.quatra.be", "waste", "large", "medium", 2)
c("Vanheede Environmental Logistics", "https://www.vanheede.be", "waste", "large", "medium", 2)
c("DERICHEBOURG Belgium", "https://www.derichebourg.com", "waste", "large", "medium", 3)
c("REMONDIS Belgium", "https://www.remondis.be", "waste", "mid", "medium", 3)
c("Campine", "https://www.campine.be", "chemicals", "mid", "high", 2,
  "Metals recycling; a real environmental-compliance employer.")
c("Ekopak", "https://www.ekopak.be", "water", "mid", "medium", 3)
c("Hygea", "https://www.hygea.be", "waste", "mid", "medium", 3)
c("Belgian Scrap Terminal", "https://www.bst.be", "waste", "large", "low", 3)
c("Carglass Belgium", "https://www.carglass.be", "services", "mid", "low", 3)
c("BEE(bee)", "https://www.bee.be", "waste", "sme", "medium", 3)

# --- environmental and sustainability consulting (the core target)
c("ERM", "https://www.erm.com", "env_consulting", "large", "high", 1,
  "World's largest specialist sustainability consultancy; practices in BE, "
  "LU, CH, AU, NZ and AE.")
c("South Pole", "https://www.southpole.com", "env_consulting", "large", "high", 1,
  "One row for the firm; offices in BE and CH.")
c("Ricardo", "https://www.ricardo.com", "env_consulting", "large", "high", 2)
c("SLR Consulting", "https://www.slrconsulting.com", "env_consulting", "large", "high", 2,
  "One row for the firm; practices in BE, CH and AU.")
c("RSK Group", "https://www.rskgroup.com", "env_consulting", "large", "high", 2)
c("Antea Group Belgium", "https://www.anteagroup.be", "env_consulting", "mid", "high", 1)
c("Arcadis", "https://www.arcadis.com", "env_consulting", "large", "high", 1,
  "One row for the firm; practices in BE, CH and AU.")
c("Sweco Belgium", "https://www.sweco.be", "env_consulting", "large", "high", 1)
c("WSP", "https://www.wsp.com", "env_consulting", "large", "high", 1,
  "One row for the firm; filter by country on the careers site. "
  "Practices exist in BE, CH, AU, NZ and AE.")
c("Ramboll", "https://www.ramboll.com", "env_consulting", "large", "high", 1,
  "One row for the firm; practices in BE, CH, AU, NZ and AE.")
c("Arup Belgium", "https://www.arup.com", "engineering", "large", "high", 2)
c("Mott MacDonald", "https://www.mottmac.com", "engineering", "large", "high", 2,
  "One row for the firm; practices in BE, CH, AU, NZ and AE.")
c("Royal HaskoningDHV", "https://www.royalhaskoningdhv.com", "engineering", "large", "high", 2)
c("ICF", "https://www.icf.com", "env_consulting", "large", "high", 2,
  "Heavy EU-policy practice in Brussels.")
c("Guidehouse", "https://guidehouse.com", "env_consulting", "large", "high", 2)
c("Tetra Tech", "https://www.tetratech.com", "env_consulting", "large", "high", 3)
c("AECOM", "https://aecom.com", "env_consulting", "large", "high", 2,
  "One row for the firm; practices in BE, CH, AU, NZ and AE.")
c("Stantec", "https://www.stantec.com", "env_consulting", "large", "high", 3,
  "One row for the firm; practices in BE, CH, AU, NZ and AE.")
c("Jacobs", "https://www.jacobs.com", "env_consulting", "large", "high", 2,
  "One row for the firm; practices in BE, CH, AU, NZ and AE.")
c("COWI", "https://www.cowi.com", "engineering", "large", "medium", 3)
c("Vinçotte (Apave)", "https://www.vincotte.be", "services", "large", "high", 2)
c("TÜV Rheinland Belgium", "https://www.tuv.com", "services", "large", "medium", 3)
c("DNV Belgium", "https://www.dnv.com", "services", "large", "medium", 3)
c("Kiwa Belgium", "https://www.kiwa.com", "services", "mid", "medium", 3)
c("Enhesa", "https://www.enhesa.com", "software_data", "mid", "high", 1,
  "Brussels firm selling regulatory compliance intelligence; extremely close to "
  "the regulatory-watch part of this profile.")
c("Greenfish", "https://www.greenfish.be", "env_consulting", "sme", "high", 2)
c("Möbius", "https://www.mobius.be", "env_consulting", "sme", "high", 2,
  "Brussels sustainability consultancy; circular economy and CSRD.")
c("Klimaatzaak / Climact", "https://www.climact.com", "env_consulting", "sme", "high", 2,
  "Climate strategy consultancy.")
c("CO2logic", "https://www.co2logic.com", "env_consulting", "sme", "high", 1,
  "Carbon accounting and climate-label specialist; the archetypal target employer.")
c("The Shift", "https://www.theshift.be", "ngo", "sme", "medium", 3,
  "Sustainability business network; recruits project staff.")
c("Bopro", "https://www.bopro.be", "buildings", "mid", "high", 2,
  "Sustainable real estate and BREEAM/GRESB certification.")
c("CES (Clean Energy Solutions)", "https://www.ces.be", "env_consulting", "sme", "high", 3)
c("T/DENZ", "https://www.tdenz.be", "env_consulting", "sme", "medium", 3)
c("Sustacon", "https://www.sustacon.be", "env_consulting", "sme", "high", 3)
c("Sigma Sustainability", "https://www.sigma-sustainability.com", "env_consulting",
  "sme", "medium", 3)

# --- engineering and construction
c("BESIX", "https://www.besix.com", "engineering", "large", "medium", 2)
c("DEME Group", "https://www.deme-group.com", "engineering", "large", "high", 1,
  "Dredging and marine; QHSE trainee programmes run most years.")
c("Jan De Nul", "https://www.jandenul.com", "engineering", "large", "high", 2)
c("CFE", "https://www.cfe.be", "engineering", "large", "medium", 3)
c("Willemen Group", "https://www.willemen.be", "buildings", "large", "medium", 3)
c("Cordeel", "https://www.cordeel.be", "buildings", "large", "medium", 3)
c("Van Roey", "https://www.vanroey.be", "buildings", "mid", "medium", 3)
c("Studiebureau Boydens", "https://www.boydens.be", "buildings", "mid", "high", 3,
  "Building services and energy studies.")
c("VK Engineering", "https://www.vk.be", "buildings", "mid", "high", 3)
c("Ingenium", "https://www.ingenium.be", "buildings", "mid", "high", 2,
  "Sustainability and energy performance for buildings; a strong SME target.")
c("3E", "https://www.3e.eu", "energy", "mid", "high", 2,
  "Renewable-energy consultancy with a data and modelling core.")
c("Energinvest", "https://www.energinvest.be", "energy", "sme", "high", 2)
c("Across Group", "https://www.across.be", "energy", "sme", "medium", 3)

# --- industry, chemicals, pharma, food, packaging
c("Umicore", "https://www.umicore.com", "chemicals", "large", "high", 1,
  "Battery materials and recycling; large sustainability reporting team.")
c("Solvay", "https://www.solvay.com", "chemicals", "large", "medium", 2)
c("BASF Antwerp", "https://www.basf.com", "chemicals", "large", "medium", 2)
c("ArcelorMittal Belgium", "https://belgium.arcelormittal.com", "industry", "large", "medium", 2)
c("AGC Glass Europe", "https://www.agc.com", "industry", "large", "medium", 2)
c("Aliaxis", "https://www.aliaxis.com", "industry", "large", "medium", 2)
c("Bekaert", "https://www.bekaert.com", "industry", "large", "medium", 2)
c("Agfa-Gevaert", "https://www.agfa.com", "chemicals", "large", "medium", 3)
c("Syensqo", "https://www.syensqo.com", "chemicals", "large", "medium", 2)
c("TotalEnergies Belgium", "https://totalenergies.be", "energy", "large", "medium", 3)
c("ExxonMobil Antwerp", "https://www.exxonmobil.be", "energy", "large", "medium", 3)
c("UCB", "https://www.ucb.com", "pharma", "large", "medium", 2)
c("Janssen (J&J) Beerse", "https://www.jnj.com", "pharma", "large", "medium", 2)
c("Galapagos", "https://www.glpg.com", "pharma", "large", "low", 3)
c("Novo Nordisk Belgium", "https://www.novonordisk.be", "pharma", "large", "medium", 3)
c("Colruyt Group", "https://www.colruytgroup.com", "retail", "large", "high", 1,
  "Belgium's most sustainability-forward retailer; large CSR reporting team.")
c("Delhaize (Ahold Delhaize)", "https://www.delhaize.be", "retail", "large", "high", 2)
c("AB InBev", "https://www.ab-inbev.com", "agri_food", "large", "medium", 2)
c("Barry Callebaut", "https://www.barry-callebaut.com", "agri_food", "large", "high", 1,
  "Has a dedicated sustainability and traceability function.")
c("Puratos", "https://www.puratos.com", "agri_food", "large", "medium", 2)
c("Lotus Bakeries", "https://www.lotusbakeries.com", "agri_food", "mid", "medium", 3)
c("Spadel", "https://www.spadel.com", "agri_food", "large", "high", 2,
  "B Corp certified water company.")
c("Alken-Maes", "https://www.alken-maes.be", "agri_food", "large", "low", 3)
c("Duvel Moortgat", "https://www.duvelmoortgat.be", "agri_food", "mid", "medium", 3)
c("FrieslandCampina Belgium", "https://www.frieslandcampina.com", "agri_food", "large", "medium", 3)
c("Danone Belgium", "https://www.danone.be", "agri_food", "large", "medium", 3)
c("Nestlé Belgium", "https://www.nestle.be", "agri_food", "large", "medium", 3)
c("Alpro (Danone)", "https://www.alpro.com", "agri_food", "large", "medium", 3)
c("Beneo", "https://www.beneo.com", "agri_food", "mid", "medium", 3)
c("Soudal", "https://www.soudal.com", "chemicals", "mid", "medium", 3)
c("Deceuninck", "https://www.deceuninck.com", "industry", "large", "medium", 3,
  "PVC recycling programmes.")
c("Picanol", "https://www.picanol.be", "industry", "large", "low", 3)
c("Ontex", "https://www.ontexglobal.com", "industry", "large", "medium", 3)
c("Etex", "https://www.etexgroup.com", "industry", "large", "medium", 2,
  "Building materials with a large decarbonisation agenda.")
c("Wienerberger Belgium", "https://www.wienerberger.be", "buildings", "large", "medium", 3)
c("Lhoist", "https://www.lhoist.com", "mining", "large", "medium", 2)
c("Carmeuse", "https://www.carmeuse.com", "mining", "large", "medium", 2)
c("Nyrstar", "https://www.nyrstar.com", "mining", "large", "medium", 3)
c("Aperam", "https://www.aperam.com", "industry", "large", "medium", 3)
c("Domo Chemicals", "https://www.domo-chemicals.com", "chemicals", "large", "medium", 3)
c("Ravago", "https://www.ravago.com", "chemicals", "large", "medium", 2,
  "Polymers recycling and distribution.")
c("Induflex", "https://www.induflex.be", "packaging", "sme", "medium", 3)
c("Green Stems (employer)", "https://www.greenstems.eu", "packaging", "sme", "high", 3,
  "Current employer; included for completeness, not for applications.")

# --- finance and insurance (ESG reporting and sustainable finance)
c("KBC", "https://www.kbc.com", "finance", "large", "medium", 2)
c("Belfius", "https://www.belfius.be", "finance", "large", "medium", 2)
c("BNP Paribas Fortis", "https://www.bnpparibasfortis.be", "finance", "large", "medium", 2)
c("ING Belgium", "https://www.ing.be", "finance", "large", "medium", 2)
c("Argenta", "https://www.argenta.be", "finance", "large", "medium", 3)
c("AXA Belgium", "https://www.axa.be", "finance", "large", "medium", 3)
c("Ethias", "https://www.ethias.be", "finance", "large", "medium", 3)
c("Federal Holding and Investment Company (SFPIM)", "https://www.sfpim.be", "finance",
  "mid", "medium", 3)
c("Triodos Bank Belgium", "https://www.triodos.be", "finance", "mid", "high", 2,
  "Sustainable bank; mission-aligned employer.")
c("NewB", "https://www.newb.coop", "finance", "sme", "medium", 3,
  "Cooperative ethical bank.")
c("Forum Ethibel", "https://www.forumethibel.org", "finance", "sme", "high", 3,
  "SRI screening and certification.")

# --- research, universities, public bodies
c("Universite libre de Bruxelles", "https://www.ulb.be", "research", "large", "high", 1,
  "Alma mater; research and teaching assistant posts.")
c("KU Leuven", "https://www.kuleuven.be", "research", "large", "high", 2)
c("UCLouvain", "https://uclouvain.be", "research", "large", "high", 2)
c("Ghent University", "https://www.ugent.be", "research", "large", "high", 2)
c("University of Antwerp", "https://www.uantwerpen.be", "research", "large", "medium", 3)
c("VUB", "https://www.vub.be", "research", "large", "medium", 2)
c("VITO", "https://www.vito.be", "research", "mid", "high", 1,
  "Flemish institute for technological research; energy, water and materials.")
c("VIB", "https://www.vib.be", "research", "mid", "medium", 3)
c("ILVO", "https://www.ilvo.vlaanderen.be", "research", "mid", "high", 2,
  "Flanders research institute for agriculture, fisheries and food.")
c("CRA-W", "https://www.cra.wallonie.be", "research", "mid", "high", 2,
  "Walloon agricultural research centre.")
c("Universite de Liege - Gembloux", "https://www.uliege.be", "research", "large", "high", 2,
  "Gembloux Agro-Bio Tech; the closest academic match to the degree.")
c("Royal Belgian Institute of Natural Sciences", "https://www.naturalsciences.be",
  "research", "mid", "high", 2)
c("Royal Museum for Central Africa", "https://www.africamuseum.be", "research",
  "mid", "medium", 3)
c("Sciensano", "https://www.sciensano.be", "research", "mid", "medium", 3)
c("Institut Scientifique de Service Public (ISSeP)", "https://www.issep.be", "research",
  "sme", "high", 2, "Walloon environmental monitoring institute.")
c("VMM (Flemish Environment Agency)", "https://www.vmm.be", "public_body", "mid", "high", 2)
c("Departement Omgeving (Flanders)", "https://omgeving.vlaanderen.be", "public_body",
  "mid", "high", 2)
c("SPW Agriculture, Ressources naturelles et Environnement",
  "https://agriculture.wallonie.be", "public_body", "mid", "high", 2)
c("Bruxelles Environnement", "https://environnement.brussels", "public_body", "mid",
  "high", 1, "The Brussels environment agency; recruits regularly.")
c("Agence federale pour la securite de la chaine alimentaire (AFSCA)",
  "https://www.afsca.be", "public_body", "large", "medium", 3)
c("Institut Royal Meteorologique", "https://www.meteo.be", "public_body", "mid",
  "medium", 3)
c("SPF Sante publique", "https://www.health.belgium.be", "public_body", "large",
  "medium", 3)
c("SPF Environnement (federal)", "https://www.environnement.belgium.be", "public_body",
  "mid", "high", 2)
c("CREG", "https://www.creg.be", "public_body", "sme", "medium", 3,
  "Federal energy regulator.")
c("CWAPE", "https://www.cwape.be", "public_body", "sme", "medium", 3,
  "Walloon energy regulator.")
c("VREG", "https://www.vreg.be", "public_body", "sme", "medium", 3,
  "Flemish energy regulator.")
c("Port of Antwerp-Bruges", "https://www.portofantwerpbruges.com", "transport",
  "large", "high", 2, "Large sustainability and environmental department.")
c("Port of Brussels", "https://www.portofbrussels.be", "transport", "mid", "medium", 3)
c("North Sea Port", "https://www.northseaport.com", "transport", "mid", "medium", 3)
c("Brussels Airport Company", "https://www.brusselsairport.be", "transport", "large",
  "medium", 2)
c("SNCB / NMBS", "https://www.sncb.be", "transport", "large", "medium", 3)
c("STIB / MIVB", "https://www.stib.be", "transport", "large", "medium", 3)
c("De Lijn", "https://www.delijn.be", "transport", "large", "medium", 3)
c("TEC", "https://www.letec.be", "transport", "large", "medium", 3)
c("Brussels Mobility", "https://mobilite-mobiliteit.brussels", "public_body", "mid",
  "medium", 3)
