"""The BetterBusiness archetype: small independent sustainability and ESG
consultancies that advise SMEs on B Corp, carbon accounting, CSRD and
reporting.

BetterBusiness is the model because it is exactly the kind of firm that hires
one junior analyst and expects them to do everything: B Corp assessment,
carbon footprint, a Power BI dashboard and the CSRD gap analysis. There are
thousands of these across the six countries and they are the least visible on
job boards, so they are worth listing by name.

`verified="yes"` means the domain appeared in a source during the build;
`verified="no"` means the domain was inferred from the firm's name and must be
checked before a scraper relies on it. Every row here is `sme` unless the firm
is a mid-sized practice.
"""

from .model import company as C

ROWS = []
_add = ROWS.append


def b(country, name, url, sector="env_consulting", size="sme", fit="high",
      priority=1, note="", verified="no", listing=""):
    row = C(country, name, url, sector, size, fit, priority, note, verified)
    if listing:
        row.listing_url = listing
    _add(row)


# =========================================================================== #
# BELGIUM - Francophone and Brussels
# =========================================================================== #
b("BE", "Sustenuto (formerly BetterBusiness)", "https://sustenuto.com",
  listing="https://sustenuto.com/countries/belgium?lang=en",
  note="The reference row. betterbusiness.be now redirects here: the two firms "
       "merged, and Sustenuto runs Belgium, Luxembourg and Switzerland practices. "
       "ESG strategy, CSRD and VSME reporting, double materiality, B Corp, "
       "EcoVadis, LCA and EPD. One row for all three countries because it is one "
       "career site. Its Swiss practice also covers the CH seeker.", verified="yes")
b("BE", "RDC Environment", "https://www.rdcenvironment.be",
  note="Brussels environmental economics and LCA consultancy, 30+ years, 11-50 staff. "
       "Life-cycle assessment is a direct match to the masters.", verified="no")
b("BE", "Encon", "https://www.encon.be",
  note="Bilzen-based sustainability agency, 51-200 staff; one of the larger "
       "independent Belgian players.", verified="yes")
b("BE", "Intraco Consulting", "https://www.intraco.be",
  note="Blegny; strategy, environment and safety consulting, 11-50 staff.",
  verified="no")
b("BE", "Consultes", "https://www.consultes.be",
  note="Zwevegem; environment, prevention, energy and sustainability for SMEs.",
  verified="yes")
b("BE", "Geolys", "https://www.geolys.be",
  note="Ciney; soil, water and energy studies. Strong fit with the bioengineering "
       "and soil-science side of the degree.", verified="yes")
b("BE", "Wiels", "https://www.wiels.be",
  note="Zwevegem; environmental and safety advice bureau, 30+ years.",
  verified="yes")
b("BE", "Data4Green", "https://www.data4green.be",
  note="Brussels; data engineering for sustainability reporting. The closest "
       "possible match to the Power BI and CSRD combination.", verified="yes")
b("BE", "Smart2Circle", "https://www.smart2circle.be",
  note="Liege; circular economy and carbon neutrality, 1-10 staff.",
  verified="yes")
b("BE", "SLO (Samen Leven Ondernemen)", "https://www.slo.be",
  note="Brussels sustainability consultancy.", verified="no")
b("BE", "BLEEN", "https://www.bleen.be",
  note="Brussels sustainability consultancy.", verified="no")
b("BE", "21 Solutions", "https://www.21solutions.eu",
  note="Brussels; sustainability and public affairs, works in BE and FR.",
  verified="yes")
b("BE", "DR(EA)2M", "https://www.dream.be",
  note="Pont-a-Celles; territorial development, environment and landscape studies.",
  verified="no")
b("BE", "Studio D", "https://www.studiod.be",
  note="Leuven; sustainability strategy and policy for small organisations.",
  verified="yes")
b("BE", "Prospect C&S", "https://www.prospectcs.be",
  note="Brussels; independent consultancy, food and sustainability.",
  verified="yes")
b("BE", "Material Mastery", "https://www.materialmastery.be",
  note="Circular transition for product companies.", verified="no")
b("BE", "Revalor", "https://www.revalor.be",
  note="Nivelles; sustainable IT and governance.", verified="yes")
b("BE", "Adviesbureau Decock", "https://www.adviesbureaudecock.be",
  note="Langemark; permits and environmental advice for companies and individuals.",
  verified="yes")
b("BE", "Associates Engineers", "https://www.associates.be",
  note="Zaventem; technical and environmental engineering, 51-200 staff.",
  verified="no")
b("BE", "ORA Group", "https://www.oragroup.be",
  note="Wevelgem; environmental and safety consultancy.", verified="no")
b("BE", "Schuttelaar & Partners", "https://www.schuttelaar-partners.com",
  note="Brussels office of the Dutch food and sustainability public-affairs "
       "consultancy, 51-200 staff.", verified="yes")
b("BE", "Sustain & Enable", "https://www.sustainenable.be",
  note="Small sustainability consultancy.", verified="no")
b("BE", "E-Luse", "https://www.e-luse.be",
  note="Harelbeke; small sustainability advisory.", verified="yes")
b("BE", "Ariane Environment", "https://www.ariane-env.be",
  note="Environmental studies and permitting.", verified="no")
b("BE", "Meesen", "https://www.meesen.be",
  note="Environmental consultancy.", verified="no")
b("BE", "Ecoteam", "https://www.ecoteam.be",
  note="Environmental advice and audits.", verified="no")
b("BE", "Advize", "https://www.advize.be",
  note="Sustainability advisory.", verified="no")
b("BE", "Arcade", "https://www.arcade.be",
  note="Environmental and planning consultancy.", verified="no")

# =========================================================================== #
# BELGIUM - Flemish
# =========================================================================== #

b("BE", "Axilium", "https://www.axilium.be",
  note="Schilde; technical engineering bureau with a sustainability practice.",
  verified="yes")
b("BE", "Peritas", "https://www.peritas.be",
  note="Antwerp; engineering and sustainability studies.", verified="yes")
b("BE", "Raco by Studibo", "https://www.raco.be",
  note="Heusden-Zolder; building services and energy studies.", verified="yes")
b("BE", "Mobius", "https://www.mobius.be",
  note="Brussels; circular economy and CSRD for businesses and public bodies.",
  verified="no")
b("BE", "Climact", "https://www.climact.com",
  note="Climate strategy and carbon consulting, Brussels and Paris.",
  verified="no")
b("BE", "CO2logic", "https://www.co2logic.com",
  note="Carbon accounting and the CO2 Neutral label; a very direct match.",
  verified="no")
b("BE", "Greenfish", "https://www.greenfish.be",
  note="Sustainability and environmental recruitment and consulting.",
  verified="no")
b("BE", "Sustacon", "https://www.sustacon.be",
  note="Berchem; ESG policy, CSRD reporting and risk management for SMEs.",
  verified="yes")
b("BE", "The Sustainable Recruiter", "https://www.thesustainablerecruiter.com",
  note="Specialist recruiter for sustainability roles; useful as a market signal "
       "even though it is not an employer.", verified="no")

# =========================================================================== #
# LUXEMBOURG
# =========================================================================== #
b("LU", "Deveco", "https://www.deveco.lu",
  note="The Luxembourg BetterBusiness: founded 2017, INDR-accredited ESR label "
       "expert, B Corp and CSRD/VSME reporting, carbon footprint. Now part of "
       "ATOZ ESG Solutions.", verified="yes")
b("LU", "ATOZ ESG Solutions", "https://www.atoz.lu",
  note="The ESG arm that absorbed Deveco; double materiality, CSRD, VSME, SFDR "
       "and ISO 14001 implementation.", verified="yes")
b("LU", "Ripple Effect", "https://www.rippleeffect.lu",
  note="Small independent advisory: non-executive directors, governance and "
       "sustainability advisory.", verified="yes")
b("LU", "SustainCERT", "https://www.sustaincert.com",
  note="Climate impact verification for carbon markets and value chains, 51-100 "
       "staff; verification is a growing niche.", verified="yes")
b("LU", "Meliora", "https://www.meliora.lu",
  note="Sustainable-finance management consulting.", verified="yes")
b("LU", "InCites Consulting", "https://www.incites.lu",
  note="Research and advisory, socioeconomic impact analysis.", verified="yes")
b("LU", "Luxconsult", "https://www.luxconsult.lu",
  note="Engineering consultancy with environmental studies.", verified="yes")
b("LU", "Sustain SA / Exxus", "https://www.sustain.lu",
  note="Sustainable development and strategic management consulting.",
  verified="no")
b("LU", "LuxFLAG", "https://www.luxflag.org",
  note="Labels sustainable investment funds; small team, high relevance for ESG "
       "data work in finance.", verified="yes")
b("LU", "Ecofund", "https://www.ecofund.lu",
  note="Sustainability funder and advisory body.", verified="no")

# =========================================================================== #
# SWITZERLAND
# =========================================================================== #
b("CH", "Responsibility Consulting", "https://responsibility-consulting.ch",
  note="Independent sustainability consultancy for SMEs, foundations and the "
       "public sector; B Corp certification, GHG Protocol, ESGoGo tool, "
       "Cercle Indicateurs. The Swiss BetterBusiness.", verified="yes")
b("CH", "Swiss Climate", "https://www.swissclimate.ch",
  note="Bern; CO2 management, sustainability and energy consulting.",
  verified="yes")
b("CH", "econcept", "https://www.econcept.ch",
  note="Zurich; sustainability and environmental research consultancy.",
  verified="yes")
b("CH", "Infras", "https://www.infras.ch",
  note="Zurich and Bern; research and consultancy on energy, environment and "
       "transport policy.", verified="yes")
b("CH", "TEP Energy", "https://www.tep-energy.ch",
  note="Zurich; energy and climate policy modelling.", verified="yes")
b("CH", "Planair", "https://www.planair.ch",
  note="La Chaux-de-Fonds and Lausanne; energy and climate engineering.",
  verified="yes")
b("CH", "Intep", "https://www.intep.com",
  note="Zurich; sustainable building and business.", verified="yes")
b("CH", "EBP", "https://www.ebp.ch",
  note="Zurich; large Swiss sustainability and infrastructure consultancy, "
       "mid-sized rather than a boutique.", size="mid", verified="yes")
b("CH", "Carbura", "https://www.carbura.ch",
  note="Swiss climate protection foundation. Carbon offset funds and "
       "verification, not employer-side ESG work.", verified="yes")
b("CH", "ClimatePartner Switzerland", "https://www.climatepartner.com",
  note="Carbon labelling and climate action for companies.", size="mid",
  verified="yes")
b("CH", "MyClimate", "https://www.myclimate.org",
  note="Carbon-offset foundation; project development and advisory roles.",
  size="mid", verified="yes")
b("CH", "BSD Consulting", "https://www.bsdconsulting.com",
  note="Zurich, 1998, B Corp. Sustainability strategy and reporting for "
       "companies and foundations.", verified="yes")
b("CH", "Quantis", "https://quantis.com",
  note="Lausanne, with Paris, Zurich, Berlin, Milan and Boston. Quantified "
       "environmental footprints, CSRD and ESRS, LCA. Strongest single fit in "
       "Switzerland for a bioengineering profile.", size="mid", verified="yes")
b("CH", "AdvantiKA", "https://www.advantika.com",
  note="Geneva boutique, B Corp since 2021. ESG strategy and transformation for "
       "mid-sized companies.", verified="no")
b("CH", "Basler & Hofmann", "https://www.baslerhofmann.ch",
  note="Zurich engineering and environmental consultancy; the hiring is "
       "engineering-led rather than sustainability-led.", size="mid",
  verified="yes")

# =========================================================================== #
# AUSTRALIA
# =========================================================================== #
b("AU", "Edge Impact", "https://www.edgeimpact.global",
  note="Australian sustainability consultancy, 10-100 staff; ESG strategy, "
       "carbon footprinting, climate resilience.", verified="yes")
b("AU", "Pangolin Associates", "https://www.pangolinassociates.com",
  note="Sydney; carbon accounting and energy efficiency for SMEs.",
  verified="yes")
b("AU", "The Growth Activists", "https://thegrowthactivists.com",
  note="ESG transformation, B Corp certification and carbon advisory.",
  verified="yes")
b("AU", "Green Moves", "https://www.greenmoves.com.au",
  note="Independent sustainability consulting for business, government and "
       "households.", verified="yes")
b("AU", "Linden Sustainability", "https://www.lindensustainability.com",
  note="Carbon accounting, climate risk and scenario analysis.",
  verified="yes")
b("AU", "Ndevr Environmental", "https://ndevr.com.au",
  note="Decarbonisation strategy and climate compliance.", verified="yes")
b("AU", "Climate Zero", "https://www.climatezero.com.au",
  note="Carbon accounting for small business.", verified="yes")
b("AU", "Cress Consulting", "https://www.cressconsulting.com.au",
  note="Sydney; climate risk, ESG reporting and carbon accounting, 51-100 staff.",
  verified="yes")
b("AU", "Melomys Advisory", "https://www.melomysadvisory.com",
  note="ESG due diligence, taxonomy compliance, materiality and sustainable "
       "finance; teams in Australia and the EU.", verified="yes")
b("AU", "auverde", "https://auverde.com",
  note="Mandatory climate disclosure and net-zero pathways.", verified="yes")
b("AU", "STSG Consulting", "https://www.stsgconsulting.com",
  note="Climate considerations in financial and strategic decisions.",
  verified="yes")
b("AU", "Northmore Gordon", "https://northmoregordon.com",
  note="Energy efficiency and greenhouse-gas performance.", verified="yes")
b("AU", "Rewild Agency", "https://www.rewildagency.com.au",
  note="Sustainability strategy and transformation.", verified="yes")
b("AU", "Cool Planet", "https://www.coolplanet.com.au",
  note="Carbon accounting and climate advisory.", verified="yes")
b("AU", "EC Sustainable", "https://www.ecsustainable.com.au",
  note="Waste, resource recovery and sustainability consultancy.",
  verified="yes")
b("AU", "Practice Capital", "https://www.practicecapital.com.au",
  note="Perth; puts SMEs on a net-zero pathway with an ESG reporting framework.",
  verified="yes")
b("AU", "GECA", "https://www.geca.eco",
  note="Good Environmental Choice Australia; ecolabelling and advisory.",
  verified="yes")
b("AU", "Sustinere Group", "https://www.sustineregroup.com",
  note="Small ESG and nature advisory.", verified="yes")
b("AU", "&BLOOM Sustainability", "https://www.andbloom.com",
  note="ESG consultancy across Australia, NZ and Europe.", verified="yes")
b("AU", "Losee Consulting", "https://www.loseeconsulting.com.au",
  note="Climate and environmental advisory.", verified="yes")
b("AU", "Tamarack Consulting", "https://www.tamarackconsulting.com.au",
  note="Sustainability advisory.", verified="yes")
b("AU", "Fair and Forward", "https://fairandforward.com.au",
  note="Sustainability and social impact consulting.", verified="yes")
b("AU", "Small Mighty CSR", "https://smallmightyscr.com.au",
  note="CSR and sustainability for small business.", verified="yes")
b("AU", "Oxygen Consulting", "https://oxygenconsulting.co.nz",
  note="Sustainability advisory, NZ-based and works across the Tasman.",
  verified="yes")
b("AU", "Go Well Consulting", "https://gowellconsulting.co.nz",
  note="Sustainability and wellbeing consulting.", verified="yes")

# =========================================================================== #
# NEW ZEALAND
# =========================================================================== #
b("NZ", "Toitu Envirocare", "https://www.toitu.co.nz",
  note="Runs the Toitu carbon certification programme; audit and advisory roles. "
       "The closest NZ equivalent to a certification-body-plus-consultancy.",
  size="mid", verified="yes")
b("NZ", "Ekos", "https://www.ekos.co.nz",
  note="Carbon and biodiversity certification and advice.", verified="yes")
b("NZ", "Aider", "https://www.aider.nz",
  note="ESG structuring with a defined methodology for SMEs.", verified="yes")
b("NZ", "ESP (Energy Solution Providers)", "https://www.esp.co.nz",
  note="Energy efficiency, decarbonisation and AI-assisted carbon reporting.",
  verified="yes")
b("NZ", "Pres Strategy", "https://www.presstrategy.co.nz",
  note="Zero-carbon, circular and regenerative transition consulting, 1-10 staff.",
  verified="yes")
b("NZ", "Babbage Consultants", "https://www.babbage.co.nz",
  note="Multidisciplinary engineering; first NZ firm to reach Toitu net carbonzero.",
  size="mid", verified="yes")
b("NZ", "Harrison Grierson", "https://www.harrisongrierson.com",
  note="Engineering and environmental consultancy, net-zero by 2032 target.",
  size="mid", verified="yes")
b("NZ", "Kokiri Solutions", "https://kokiri.co.nz",
  note="Environmental and cultural advisory.", verified="yes")
b("NZ", "Meadowbank Consulting", "https://www.meadowbank.co.nz",
  note="Water and environmental consultancy.", verified="yes")
b("NZ", "Sustain and Enable", "https://www.sustainandenable.co.nz",
  note="Social enterprise doing sustainability assessments.", verified="yes")
b("NZ", "Sustainable Solutions", "https://www.sustainablesolutions.co.nz",
  note="Sustainability advisory.", verified="yes")
b("NZ", "Thinkstep-anz", "https://www.thinkstep-anz.com",
  note="LCA and product sustainability, Australia and NZ.", size="mid",
  verified="yes")

# =========================================================================== #
# UAE
# =========================================================================== #
b("AE", "Planet First Consultants", "https://theplanetfirst.org",
  note="Dubai; the UAE BetterBusiness. EcoVadis, EPD, LCA, product carbon "
       "footprint to ISO 14067, GHG reporting and ISO systems, aimed at SMEs "
       "and exporters. Almost a line-by-line match to this CV.", verified="yes")
b("AE", "Kaynat Advisory", "https://kaynatadvisory.com",
  note="Boutique sustainability consultancy for SMEs: EcoVadis, emissions "
       "reporting, EPD and LCA.", verified="yes")
b("AE", "Farnek Sustainability", "https://farneksustainability.com",
  note="Consulting division of a facilities-management group; ESG strategy, "
       "carbon management and energy retrofits with operational backing.",
  size="mid", verified="yes")
b("AE", "SAM Corporate", "https://www.samcorporate.com",
  note="ESG software, managed services, consulting and training.", size="mid",
  verified="yes")
b("AE", "Agile Advisors", "https://agileadvisors.ae",
  note="ESG and sustainability advisory across UAE, Oman, KSA, UK and India.",
  size="mid", verified="yes")
b("AE", "EcoMENA", "https://www.ecomena.org",
  note="Sustainability platform and small advisory practice.", verified="yes")
b("AE", "Dubai Carbon Centre of Excellence", "https://www.dubicarbon.com",
  note="Carbon measurement and MRV.", verified="yes")
b("AE", "Sustainability Knowledge Group", "https://www.sustainabilityknowledgegroup.com",
  note="ESG training and advisory.", verified="yes")
b("AE", "Alpin Limited", "https://www.alpinme.com",
  note="Dubai, 2011, 10-100 staff. ESG strategy, commissioning, energy and "
       "environmental compliance.", size="mid", verified="yes")
b("AE", "Sustainable Square", "https://www.sustainablesquare.com",
  note="Dubai, 2011. ESG advisory and a benchmark platform; SME and government "
       "clients.", size="mid", verified="yes")
b("AE", "Aridzone Sustainability Management Consulting", "https://aridzone.ae",
  note="Dubai boutique, 1-10 staff. ESG management consulting.",
  verified="no")
b("AE", "ImpactGulf", "https://impactgulf.com",
  note="Abu Dhabi boutique, 1-10 staff. Sustainability innovation and advisory.",
  verified="no")
b("AE", "Zest Associates", "https://www.zestassociates.com",
  note="Dubai boutique, 1-10 staff. Low-carbon economy research and policy.",
  verified="no")
b("AE", "MenetZero", "https://app.menetzero.com",
  note="Directory of 50 verified UAE carbon consultants; a route to many small "
       "practices rather than an employer itself.", verified="yes")
b("AE", "Green Advisory", "https://www.greenadvisory.ae",
  note="Scope 1 and 2 inventories and MOCCAE-aligned reporting for SMEs.",
  verified="no")
b("AE", "Atlas Services", "https://www.atlasehs.com",
  note="Environmental, health and safety consultancy.", verified="no")
