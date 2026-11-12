"""Luxembourg. Small country, so this is close to a complete list of the
employers that matter for this profile: the EU institutions, the fund
industry's ESG functions, the energy and water utilities, and a thin but
real environmental-consulting layer.
"""

from .model import company as C

ROWS = []
_add = ROWS.append


def c(name, url, sector, size, fit="medium", priority=2, note=""):
    _add(C("LU", name, url, sector, size, fit, priority, note))


# --- EU institutions and international bodies based in Luxembourg
c("European Investment Bank", "https://www.eib.org", "finance", "large", "high", 1,
  "The EU's climate bank; large environment, climate and impact teams.")
c("European Investment Fund", "https://www.eif.org", "finance", "mid", "high", 2)
c("Court of Justice of the European Union", "https://curia.europa.eu", "public_body",
  "large", "low", 3)
c("European Court of Auditors", "https://www.eca.europa.eu", "public_body", "large",
  "medium", 3)
c("Eurostat", "https://ec.europa.eu/eurostat", "public_body", "mid", "medium", 3)
c("Publications Office of the EU", "https://op.europa.eu", "public_body", "mid",
  "low", 3)
c("European Stability Mechanism", "https://www.esm.europa.eu", "finance", "mid",
  "medium", 3)

# --- finance and funds (ESG reporting and sustainable finance)
c("BGL BNP Paribas", "https://www.bgl.lu", "finance", "large", "medium", 2)
c("Spuerkeess (Banque et Caisse d'Epargne de l'Etat)", "https://www.spuerkeess.lu",
  "finance", "large", "medium", 2)
c("Banque Internationale a Luxembourg", "https://www.bil.com", "finance", "large",
  "medium", 2)
c("Banque de Luxembourg", "https://www.banquedeluxembourg.com", "finance", "mid",
  "medium", 3)
c("ING Luxembourg", "https://www.ing.lu", "finance", "large", "medium", 3)
c("Societe Generale Luxembourg", "https://www.societegenerale.lu", "finance", "large",
  "medium", 3)
c("RBC Luxembourg", "https://www.rbc.com", "finance", "large", "medium", 3)
c("Northern Trust Luxembourg", "https://www.northerntrust.com", "finance", "large",
  "medium", 3)
c("State Street Luxembourg", "https://www.statestreet.com", "finance", "large",
  "medium", 3)
c("BNP Paribas Asset Management", "https://www.bnpparibas-am.com", "finance", "large",
  "high", 2, "Large sustainable-investment research team.")
c("Amundi Luxembourg", "https://www.amundi.lu", "finance", "large", "high", 2)
c("BlackRock Luxembourg", "https://www.blackrock.com", "finance", "large", "medium", 3)
c("DekaBank Luxembourg", "https://www.deka.de", "finance", "mid", "medium", 3)
c("Luxembourg Stock Exchange", "https://www.luxse.com", "finance", "mid", "high", 2,
  "Runs the Luxembourg Green Exchange; a natural home for ESG-data work.")
c("ALFI", "https://www.alfi.lu", "finance", "mid", "medium", 3,
  "Fund industry association.")
c("PwC Luxembourg", "https://www.pwc.lu", "services", "large", "high", 2)
c("Deloitte Luxembourg", "https://www.deloitte.com/lu", "services", "large", "high", 2)
c("EY Luxembourg", "https://www.ey.com/en_lu", "services", "large", "high", 2)
c("KPMG Luxembourg", "https://kpmg.com/lu", "services", "large", "high", 2)

# --- energy, water, waste
c("Encevo", "https://www.encevo.lu", "energy", "large", "high", 1)
c("Enovos", "https://www.enovos.lu", "energy", "large", "high", 1)
c("Creos", "https://www.creos.net", "energy", "mid", "high", 1,
  "Electricity and gas grid operator.")
c("Sudstroum", "https://www.sudstroum.lu", "energy", "sme", "medium", 3)
c("Societe Electrique de l'Our", "https://www.seo.lu", "energy", "sme", "medium", 3)
c("Luxenergie", "https://www.luxenergie.lu", "energy", "sme", "medium", 3)
c("SIDOR", "https://www.sidor.lu", "waste", "mid", "high", 2,
  "Waste-management syndicate for the south of the country.")
c("Administration de l'environnement", "https://environnement.public.lu", "public_body",
  "mid", "high", 1, "The environment ministry's administration; the regulator here.")
c("Administration de la gestion de l'eau", "https://eau.public.lu", "public_body",
  "mid", "high", 2)
c("Ministere de l'Energie et de l'Amenagement du territoire",
  "https://energie.public.lu", "public_body", "mid", "high", 2)
c("Luxembourg Institute of Science and Technology (LIST)",
  "https://www.list.lu", "research", "mid", "high", 1,
  "Environmental research and remote sensing; a strong match.")
c("Luxembourg Institute of Health", "https://www.lih.lu", "research", "mid", "low", 3)
c("Luxembourg National Data Service", "https://www.lnds.lu", "software_data", "sme",
  "medium", 3)
c("SIGI", "https://www.sigi.lu", "utilities", "sme", "medium", 3)

# --- industry, transport, services
c("ArcelorMittal Luxembourg", "https://luxembourg.arcelormittal.com", "industry",
  "large", "medium", 2)
c("Cargolux", "https://www.cargolux.com", "transport", "large", "medium", 2,
  "Air freight; has a carbon-reduction programme.")
c("Luxair", "https://www.luxair.lu", "transport", "large", "low", 3)
c("CFL (railways)", "https://www.cfl.lu", "transport", "large", "medium", 3)
c("POST Luxembourg", "https://www.post.lu", "services", "large", "medium", 3)
c("SES", "https://www.ses.com", "services", "large", "low", 3)
c("Ferrero Luxembourg", "https://www.ferrero.com", "agri_food", "large", "medium", 3)
c("Goodyear Luxembourg", "https://www.goodyear.com", "industry", "large", "medium", 3)
c("Husky Injection Molding", "https://www.husky.ca", "industry", "mid", "low", 3)
c("Guardian Glass", "https://www.guardianglass.com", "industry", "mid", "medium", 3)
c("Tarkett", "https://www.tarkett.com", "industry", "large", "medium", 3)
c("DuPont Luxembourg", "https://www.dupont.com", "chemicals", "mid", "medium", 3)
c("Luxembourg Chamber of Commerce", "https://www.cc.lu", "services", "mid", "low", 3)
c("FEDIL", "https://www.fedil.lu", "services", "sme", "medium", 3,
  "Industry federation; recruits for sustainability programmes.")
c("Chambre des Salaries", "https://www.csl.lu", "public_body", "sme", "low", 3)
c("Cactus", "https://www.cactus.lu", "retail", "large", "medium", 3)
c("Auchan Luxembourg", "https://www.auchan.lu", "retail", "large", "low", 3)
