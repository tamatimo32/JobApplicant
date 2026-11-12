"""Boards, public employment services, public-sector portals, institutions,
aggregators and remote boards.

These are the *search layer*: places that list other people's vacancies.
Company career pages live in companies_*.py.
"""

from .model import board

ROWS = []
_add = ROWS.append


def A(*args, **kw):
    _add(board(*args, **kw))


# =========================================================================== #
# BELGIUM
# =========================================================================== #
# --- public employment services
A("pes", "BE", "Actiris (Brussels)", "https://www.actiris.brussels",
  "https://www.actiris.brussels/fr/citoyens/offres-d-emploi/", "fr/nl",
  "All vacancies notified in Brussels-Capital; strong on stage and alternance",
  fit="high", priority=1, notes="Regional PES. Listing path verified 2026-11-10.")
A("pes", "BE", "Le Forem (Wallonia)", "https://www.leforem.be", "", "fr",
  "Walloon vacancies plus formation and stage", fit="high", priority=1,
  notes="Search form only, no stable results URL.")
A("pes", "BE", "VDAB (Flanders)", "https://www.vdab.be", "", "nl",
  "Flemish vacancies, largest single pool in the country", fit="medium", priority=2,
  notes="Dutch interface. Most volume also reaches StepStone.")
A("pes", "BE", "ADG (German-speaking Community)", "https://adg.be", "", "de",
  "Vacancies in the German-speaking municipalities", fit="low", priority=3)
A("pes", "BE", "EURES Belgium", "https://eures.europa.eu/index_en", "", "en/fr/de",
  "Cross-border and EU-wide vacancies, including Belgium", fit="medium", priority=2,
  notes="Also the data source behind several national portals.")

# --- public sector
A("public_sector", "BE", "Travailler pour l'administration federale",
  "https://travaillerpour.be", "https://travaillerpour.be/fr/jobs", "fr/nl",
  "Federal civil service vacancies (the former Selor portal)",
  fit="medium", priority=2, notes="Selor was folded into this BOSA-run portal.")
A("public_sector", "BE", "Bruxelles Economie et Emploi", "https://economie-emploi.brussels",
  "", "fr", "Brussels regional administration and support bodies",
  fit="medium", priority=3)
A("public_sector", "BE", "Wallonie emploi", "https://emploi.wallonie.be", "", "fr",
  "Walloon public administration vacancies", fit="medium", priority=3)
A("public_sector", "BE", "Vlaanderen Werkt / Vlaamse overheid", "https://www.vlaanderen.be/werken-bij-vlaanderen",
  "", "nl", "Flemish government vacancies", fit="medium", priority=3)
A("public_sector", "BE", "Societe wallonne du Credit public", "https://www.swcs.be",
  "", "fr", "Walloon public finance institution", fit="low", priority=3)

# --- general boards
A("job_board", "BE", "StepStone Belgium", "https://www.stepstone.be", "", "fr/nl",
  "Large commercial board, all sectors", fit="medium", priority=1)
A("job_board", "BE", "Jobat", "https://www.jobat.be", "", "nl",
  "Flemish commercial board, strong on SMEs", fit="medium", priority=2)
A("job_board", "BE", "References.be", "https://www.references.be", "", "fr",
  "Francophone commercial board", fit="medium", priority=2)
A("job_board", "BE", "Jobijoba Belgium", "https://www.jobijoba.be", "", "fr/nl",
  "Aggregator over Belgian boards", fit="medium", priority=3)
A("job_board", "BE", "JobsinBrussels", "https://jobsinbrussels.com", "", "en/fr/nl",
  "English-first Brussels vacancies, NGOs and EU affairs", fit="high", priority=1,
  notes="Verified 2026-11-10. Canonical host has no www.")
A("job_board", "BE", "EuroBrussels", "https://www.eurobrussels.com",
  "https://www.eurobrussels.com/jobs/environment", "en",
  "EU institutions, NGOs, think tanks, industry associations; dedicated Environment section",
  fit="high", priority=1, notes="The environment filter removes most of the noise.")
A("job_board", "BE", "Greenjobs.nl (covers Belgium)", "https://greenjobs.nl",
  "https://greenjobs.nl/en/jobs", "nl/en",
  "Sustainable and impact jobs at B Corps, social enterprises and public bodies; "
  "Belgium is a selectable work region", fit="high", priority=1,
  notes="Replaces greenjobs.be, which no longer resolves (checked 2026-11-10).")
A("job_board", "BE", "Alterjob", "https://www.alterjob.be", "https://www.alterjob.be/fr/offres",
  "fr", "Social and environmental economy, non-profit, CPAS, education",
  fit="high", priority=2, notes="Has Environnement and Developpement durable themes.")
A("job_board", "BE", "Guide social", "https://www.guidesocial.be", "", "fr",
  "Non-profit and social sector vacancies", fit="medium", priority=3)
A("job_board", "BE", "Jobat.be (public sector filter)", "https://www.jobat.be/fr/offres",
  "", "fr/nl", "Public and semi-public vacancies", fit="medium", priority=3)
A("job_board", "BE", "Monster Belgium", "https://www.monster.be", "", "fr/nl",
  "General board", fit="low", priority=3)
A("job_board", "BE", "Nature Jobs (Belgium filter)", "https://www.nature.com/naturecareers",
  "", "en", "Academic and research posts in environmental science",
  fit="medium", priority=3, notes="Low volume, high relevance when it appears.")
A("job_board", "BE", "Academic Positions (Belgium)", "https://academicpositions.be", "",
  "en", "PhD, postdoc and university research staff", fit="medium", priority=3)
A("job_board", "BE", "Euraxess Belgium", "https://www.euraxess.be", "", "en",
  "Research funding, PhD and postdoc posts across the EU", fit="medium", priority=3,
  notes="Relevant to the masters-level research angle.")
A("job_board", "BE", "Interim offices (Federgon members)", "https://www.federgon.be",
  "", "fr/nl", "Temporary and contract work via licensed agencies",
  fit="low", priority=3, notes="Federation directory, not a vacancy list itself.")

# =========================================================================== #
# LUXEMBOURG
# =========================================================================== #
A("pes", "LU", "ADEM (JobBoard)", "https://adem.public.lu",
  "https://jobboard.adem.public.lu", "fr/de/en",
  "Official Luxembourg vacancies and the national job board",
  access="login_required", fit="high", priority=1,
  notes="JobBoard needs an account for some functions; public listing is browsable.")
A("job_board", "LU", "Work in Luxembourg", "https://workinluxembourg.com", "", "en/fr",
  "Official international recruitment platform, shortage occupations",
  fit="high", priority=1,
  notes="Run by the Luxembourg government with EURES, aimed at foreign candidates.")
A("job_board", "LU", "Moovijob", "https://en.moovijob.com", "", "en/fr",
  "Broad commercial board, all sectors", fit="medium", priority=2)
A("job_board", "LU", "Jobs.lu", "https://www.jobs.lu", "", "en/fr",
  "Professional and sector-specific vacancies", fit="medium", priority=2)
A("job_board", "LU", "Jobfinder.lu", "https://www.jobfinder.lu", "", "fr",
  "General board", fit="medium", priority=3)
A("job_board", "LU", "Paperjam Jobs", "https://jobs.paperjam.lu", "", "fr",
  "Business and finance vacancies", fit="medium", priority=3)
A("job_board", "LU", "Optioncarriere Luxembourg", "https://www.optioncarriere.lu", "",
  "fr", "Aggregator", fit="low", priority=3)
A("job_board", "LU", "ABBL jobs (banking)", "https://www.abbl.lu", "", "en/fr",
  "Luxembourg banking and fund industry vacancies", fit="medium", priority=3,
  notes="Sector federation; the place to look for ESG-in-finance roles.")
A("job_board", "LU", "Monster Luxembourg", "https://www.monster.lu", "", "fr/en",
  "General board", fit="low", priority=3)
A("public_sector", "LU", "Guichet.lu - emploi", "https://guichet.public.lu", "", "fr/de/en",
  "Official procedures plus public-sector recruitment notices",
  fit="medium", priority=3)
A("public_sector", "LU", "Fonction publique luxembourgeoise", "https://www.fonction-publique.public.lu",
  "", "fr", "State and municipal vacancies", fit="medium", priority=3)

# =========================================================================== #
# SWITZERLAND
# =========================================================================== #
A("pes", "CH", "Job-Room / arbeit.swiss", "https://www.job-room.ch",
  "https://www.job-room.ch/job-search", "de/fr/it/en",
  "Official SECO portal; vacancies employers must report",
  fit="high", priority=1,
  notes="Verified 2026-11-10: 73,503 live positions. Exposes a JSON search endpoint.")
A("job_board", "CH", "jobs.ch", "https://www.jobs.ch", "", "de/fr",
  "Largest Swiss board, all sectors", fit="medium", priority=1)
A("job_board", "CH", "jobup.ch", "https://www.jobup.ch", "", "fr",
  "Leading French-speaking Swiss board", fit="medium", priority=2)
A("job_board", "CH", "JobScout24", "https://www.jobscout24.ch", "", "de",
  "General board", fit="medium", priority=3)
A("job_board", "CH", "ostjob.ch", "https://www.ostjob.ch", "", "de",
  "Eastern Switzerland regional board", fit="low", priority=3)
A("job_board", "CH", "Jobtic", "https://www.jobtic.ch", "", "fr",
  "Romandie board", fit="medium", priority=3)
A("public_sector", "CH", "Stellenportal Bund", "https://www.stelle.admin.ch", "",
  "de/fr/it", "Federal administration vacancies", fit="medium", priority=2)
A("public_sector", "CH", "Kanton Zurich jobs", "https://www.zh.ch/de/ueber-uns/jobs.html",
  "", "de", "Cantonal administration and universities", fit="medium", priority=3)
A("public_sector", "CH", "Canton de Vaud emploi", "https://www.vd.ch/emploi", "", "fr",
  "Cantonal administration", fit="medium", priority=3)
A("job_board", "CH", "ETH Zurich jobs", "https://jobs.ethz.ch", "", "en/de",
  "University and research vacancies", fit="high", priority=3,
  notes="Relevant for environmental science and data roles.")
A("job_board", "CH", "EPFL jobs", "https://www.epfl.ch/campus/jobs/", "", "fr/en",
  "University and research vacancies", fit="medium", priority=3)
A("job_board", "CH", "University of Zurich jobs", "https://www.uzh.ch/en/about/jobs.html",
  "", "de/en", "University and research vacancies", fit="medium", priority=3)
A("job_board", "CH", "Euraxess Switzerland", "https://www.euraxess.ch", "", "en",
  "Research posts and fellowships", fit="medium", priority=3)

# =========================================================================== #
# AUSTRALIA
# =========================================================================== #
A("public_sector", "AU", "APS Jobs", "https://www.apsjobs.gov.au",
  "https://www.apsjobs.gov.au/s/job-search", "en",
  "Australian Public Service: all federal departments and agencies",
  fit="high", priority=1,
  notes="Environment, climate and net-zero agencies recruit here first.")
A("pes", "AU", "Workforce Australia / JobSearch", "https://www.jobsearch.gov.au", "",
  "en", "Government job search service", fit="low", priority=3,
  notes="Aimed at registered jobseekers; thin on professional roles.")
A("job_board", "AU", "SEEK Australia", "https://www.seek.com.au", "", "en",
  "Largest commercial board", fit="medium", priority=1)
A("job_board", "AU", "CareerOne", "https://www.careerone.com.au", "", "en",
  "General board", fit="low", priority=3)
A("job_board", "AU", "Ethical Jobs", "https://www.ethicaljobs.com.au", "", "en",
  "Environment, sustainability, social purpose and non-profit roles",
  fit="high", priority=1,
  notes="One of the most relevant boards in Australia for this profile.")
A("job_board", "AU", "GradConnection Australia", "https://au.gradconnection.com", "",
  "en", "Graduate programmes and internships", fit="high", priority=2)
A("job_board", "AU", "Graduate Careers Australia", "https://www.graduatecareers.com.au", "",
  "en", "Graduate labour market and programmes", fit="medium", priority=3)
A("job_board", "AU", "Jora Australia", "https://au.jora.com", "", "en",
  "Aggregator", fit="low", priority=3)
A("public_sector", "AU", "NSW Government jobs", "https://iworkfor.nsw.gov.au", "", "en",
  "New South Wales public sector", fit="medium", priority=2)
A("public_sector", "AU", "Victorian Government jobs", "https://careers.vic.gov.au", "",
  "en", "Victoria public sector", fit="medium", priority=2)
A("public_sector", "AU", "Queensland Smart Jobs", "https://smartjobs.qld.gov.au", "",
  "en", "Queensland public sector", fit="medium", priority=2,
  notes="External search carries an organid parameter; start from the root.")
A("public_sector", "AU", "WA Government jobs", "https://jobs.wa.gov.au", "", "en",
  "Western Australia public sector", fit="medium", priority=3)
A("public_sector", "AU", "SA Government jobs", "https://iworkfor.sa.gov.au", "", "en",
  "South Australia public sector", fit="medium", priority=3)
A("public_sector", "AU", "Tasmanian Government jobs", "https://www.jobs.tas.gov.au", "",
  "en", "Tasmania public sector", fit="low", priority=3)
A("public_sector", "AU", "NT Government jobs", "https://nt.gov.au/employ/work-for-government",
  "", "en", "Northern Territory public sector", fit="low", priority=3)
A("public_sector", "AU", "ACT Government jobs", "https://www.jobs.act.gov.au", "",
  "en", "Canberra public sector", fit="medium", priority=3)

# =========================================================================== #
# NEW ZEALAND
# =========================================================================== #
A("public_sector", "NZ", "jobs.govt.nz", "https://jobs.govt.nz", "", "en",
  "All New Zealand public service vacancies", fit="high", priority=1,
  notes="Ministry for the Environment, DOC, MPI and councils recruit here.")
A("job_board", "NZ", "SEEK New Zealand", "https://www.seek.co.nz", "", "en",
  "Largest commercial board", fit="medium", priority=1)
A("job_board", "NZ", "Trade Me Jobs", "https://www.trademe.co.nz/jobs", "", "en",
  "Most-visited NZ job site", fit="medium", priority=2)
A("job_board", "NZ", "Careers.govt.nz", "https://www.careers.govt.nz", "", "en",
  "Careers advice plus a vacancy database and recruiter directory",
  fit="medium", priority=2)
A("job_board", "NZ", "Student Job Search", "https://www.sjs.co.nz", "", "en",
  "Student and graduate work, part-time and summer",
  access="login_required", fit="medium", priority=3,
  notes="Requires proof of enrolment; likely closed to a graduate.")
A("pes", "NZ", "Work and Income job search", "https://www.workandincome.govt.nz", "",
  "en", "Government job database", fit="low", priority=3)
A("job_board", "NZ", "Jora New Zealand", "https://nz.jora.com", "", "en",
  "Aggregator", fit="low", priority=3)
A("job_board", "NZ", "GradConnection New Zealand", "https://nz.gradconnection.com", "",
  "en", "Graduate programmes and internships", fit="high", priority=2)
A("job_board", "NZ", "MyJobSpace", "https://www.myjobspace.co.nz", "", "en",
  "General board", fit="low", priority=3)

# =========================================================================== #
# UAE
# =========================================================================== #
A("public_sector", "AE", "Dubai Careers", "https://www.dubaicareers.ae", "", "en/ar",
  "Official portal for 45+ Dubai government entities", fit="medium", priority=2,
  notes="Open to expatriates, unlike several emirate portals.")
A("public_sector", "AE", "TAMM Abu Dhabi", "https://www.tamm.abudhabi", "", "en/ar",
  "Abu Dhabi government services, including public-sector jobs",
  access="login_required", fit="medium", priority=3,
  notes="Jobs sit inside a wider services portal; awkward to automate.")
A("public_sector", "AE", "FAHR federal government portal", "https://www.fahr.gov.ae",
  "", "en/ar", "Federal ministries and authorities", fit="medium", priority=3)
A("public_sector", "AE", "Nafis", "https://nafis.gov.ae", "", "en/ar",
  "Emiratisation programme; private-sector roles for UAE nationals",
  access="login_required", fit="low", priority=3,
  notes="Restricted to UAE nationals, so not applicable to this profile.")
A("pes", "AE", "MoHRE", "https://www.mohre.gov.ae", "", "en/ar",
  "Ministry of Human Resources; labour market and work-permit rules",
  fit="low", priority=3, notes="Regulator, not a job board. The permit rules matter before applying.")
A("job_board", "AE", "Bayt.com", "https://www.bayt.com", "", "en/ar",
  "Largest MENA board, all sectors", access="login_required", fit="medium", priority=1)
A("job_board", "AE", "GulfTalent", "https://www.gulftalent.com", "", "en",
  "Professional and managerial roles across the Gulf",
  access="login_required", fit="medium", priority=2)
A("job_board", "AE", "Naukrigulf", "https://www.naukrigulf.com", "", "en",
  "Large volume board, strong on engineering and construction", fit="medium", priority=2)
A("job_board", "AE", "Dubizzle Jobs", "https://www.dubizzle.com", "", "en",
  "Classifieds-style listings, quick-start roles", fit="low", priority=3)
A("job_board", "AE", "Oliv", "https://oliv.com", "", "en",
  "Internships and first jobs for students and graduates in the Gulf",
  access="login_required", fit="medium", priority=2)

# =========================================================================== #
# BIG FOUR
# =========================================================================== #
A("big4", "GLOBAL", "Deloitte careers (global)", "https://www.deloitte.com/careers.html",
  "https://jobs.deloitte.com", "en", "All member-firm vacancies, filterable by country",
  fit="high", priority=1,
  notes="Sustainability and climate advisory sit in Audit & Assurance and Risk Advisory.")
A("big4", "GLOBAL", "PwC careers (global)", "https://www.pwc.com/gx/en/careers.html", "",
  "en", "All member-firm vacancies", fit="high", priority=1,
  notes="CSRD and sustainability reporting is a large PwC service line in the EU.")
A("big4", "GLOBAL", "EY careers (global)", "https://www.ey.com/en_gl/careers", "", "en",
  "All member-firm vacancies", fit="high", priority=1,
  notes="Climate Change and Sustainability Services is a dedicated practice.")
A("big4", "GLOBAL", "KPMG careers (global)", "https://kpmg.com/xx/en/careers.html", "",
  "en", "All member-firm vacancies", fit="high", priority=1,
  notes="ESG advisory under the KPMG IMPACT network.")
for c, label in [("BE", "Belgium"), ("LU", "Luxembourg")]:
    A("big4", c, f"Deloitte {label}", f"https://www.deloitte.com/{c.lower()}/en/careers.html",
      "", "en/fr/nl", f"{label} member-firm vacancies", fit="high", priority=2)
    A("big4", c, f"PwC {label}", f"https://www.pwc.{c.lower()}/en/careers.html",
      "", "en/fr", f"{label} member-firm vacancies", fit="high", priority=2)
    A("big4", c, f"EY {label}", f"https://www.ey.com/en_{c.lower()}/careers",
      "", "en/fr", f"{label} member-firm vacancies", fit="high", priority=2)
    A("big4", c, f"KPMG {label}", f"https://kpmg.com/{c.lower()}/en/careers.html",
      "", "en/fr", f"{label} member-firm vacancies", fit="high", priority=2)

# =========================================================================== #
# UN, EU and other international bodies
# =========================================================================== #
A("institution", "GLOBAL", "UN Careers", "https://careers.un.org", "", "en/fr",
  "UN Secretariat and field missions, all duty stations", fit="high", priority=1,
  notes="Inspira-based.")
A("institution", "GLOBAL", "UNDP Jobs", "https://jobs.undp.org", "", "en",
  "UNDP country offices, including climate and environment programmes",
  fit="high", priority=1)
A("institution", "GLOBAL", "UNEP", "https://www.unep.org/work-with-us", "", "en",
  "UN Environment Programme, Nairobi and regional offices", fit="high", priority=1,
  notes="The single most on-topic UN body for this degree.")
A("institution", "GLOBAL", "UNOPS", "https://jobs.unops.org", "", "en",
  "Project services, infrastructure and procurement", fit="medium", priority=2)
A("institution", "GLOBAL", "UNICEF", "https://jobs.unicef.org", "", "en",
  "Programme, data and evaluation roles", fit="medium", priority=3)
A("institution", "GLOBAL", "WFP", "https://www.wfp.org/careers", "", "en",
  "Food security and climate resilience", fit="medium", priority=3)
A("institution", "GLOBAL", "FAO", "https://www.fao.org/employment", "", "en",
  "Food and agriculture, Rome", fit="high", priority=2,
  notes="Strong overlap with the agronomy and bioengineering background.")
A("institution", "GLOBAL", "UN Volunteers", "https://www.unv.org", "", "en/fr",
  "UN Volunteer assignments, a common entry route", fit="high", priority=2,
  notes="Often the realistic first step into the UN system for a recent graduate.")
A("institution", "GLOBAL", "Green Climate Fund", "https://www.greenclimate.fund/careers",
  "", "en", "Climate finance roles, Songdo", fit="high", priority=2)
A("institution", "GLOBAL", "World Bank Group careers",
  "https://www.worldbank.org/en/careers", "", "en",
  "Climate and environment practice, Washington and country offices", fit="medium", priority=3)
A("institution", "GLOBAL", "IFC", "https://www.ifc.org/en/careers", "", "en",
  "Private-sector climate finance", fit="medium", priority=3)
A("institution", "EU", "EU Careers", "https://eu-careers.europa.eu",
  "https://eu-careers.europa.eu/jobs_en", "en/fr",
  "Vacancies across all EU institutions and agencies", fit="high", priority=1,
  notes="The /en/home path 404s; the homepage is /index_en.")
A("institution", "EU", "EPSO (competitions and CAST)", "https://selection.eu-careers.europa.eu",
  "https://selection.eu-careers.europa.eu/en", "en/fr",
  "Permanent-official competitions and the always-open contract-agent register",
  access="login_required", fit="high", priority=1,
  notes="EPSO moved here from epso.europa.eu. Fixed opening and closing windows.")
A("institution", "EU", "European Commission traineeships (Blue Book)",
  "https://traineeships.ec.europa.eu", "", "en/fr",
  "Five-month paid traineeships in the Commission", access="login_required",
  fit="high", priority=1, notes="Two intakes a year; a realistic route into the institutions.")
A("institution", "EU", "European Environment Agency", "https://www.eea.europa.eu", "",
  "en", "Environment agency of the EU, Copenhagen", fit="high", priority=2,
  notes="Recruits through EPSO and its own temporary-agent calls.")
A("institution", "EU", "European Investment Bank careers",
  "https://www.eib.org/en/about/careers", "", "en",
  "Climate and environment lending, Luxembourg", fit="high", priority=2)
A("institution", "EU", "European Parliament traineeships", "https://www.europarl.europa.eu/committees/en/traineeships",
  "", "en/fr", "Schuman and other internal traineeships", fit="medium", priority=3)
A("institution", "EU", "EUIPO", "https://euipo.europa.eu/ohimportal/en/jobs", "", "en",
  "EU Intellectual Property Office, Alicante", fit="low", priority=3)
A("institution", "BE", "NATO", "https://www.nato.int/cps/en/natohq/careers.htm", "",
  "en", "International staff, Brussels", fit="medium", priority=3)

# =========================================================================== #
# AGGREGATORS - present, but read the access note
# =========================================================================== #
A("aggregator", "GLOBAL", "LinkedIn Jobs", "https://www.linkedin.com/jobs", "", "en",
  "Everything, including roles never posted elsewhere",
  access="tos_restricted", fit="high", priority=1,
  notes="User agreement prohibits automated scraping. Use the official Job Posting "
        "API with an approved partner account, or saved searches run manually.")
A("aggregator", "GLOBAL", "Indeed", "https://www.indeed.com", "", "en",
  "Aggregated listings across most countries",
  access="tos_restricted", fit="high", priority=1,
  notes="Terms prohibit scraping. There is a publisher/partner API; without it, "
        "treat Indeed as manual only.")
A("aggregator", "GLOBAL", "Google Jobs", "https://www.google.com/search?q=jobs", "",
  "en", "Aggregates structured job postings across the web",
  access="tos_restricted", fit="medium", priority=3,
  notes="No public feed; scraping the results page breaks Google's terms.")
A("aggregator", "GLOBAL", "Glassdoor", "https://www.glassdoor.com/Job/index.htm", "",
  "en", "Listings plus salary and interview data", access="tos_restricted",
  fit="medium", priority=3, notes="Useful for research rather than harvesting.")

# =========================================================================== #
# REMOTE
# =========================================================================== #
A("remote", "GLOBAL", "We Work Remotely", "https://weworkremotely.com", "", "en",
  "Remote roles worldwide, strong on tech and ops", fit="medium", priority=2)
A("remote", "GLOBAL", "Remote OK", "https://remoteok.com", "", "en",
  "Remote roles, aggregated", fit="medium", priority=2,
  notes="Publishes a public JSON feed; check terms before relying on it.")
A("remote", "GLOBAL", "Remotive", "https://remotive.com", "", "en",
  "Remote roles with a documented free API", access="api", fit="medium", priority=1,
  notes="Easiest source in the file to wire in.")
A("remote", "GLOBAL", "Himalayas", "https://himalayas.app/jobs", "", "en",
  "Remote roles searchable by country and timezone", fit="medium", priority=2)
A("remote", "GLOBAL", "Working Nomads", "https://www.workingnomads.com/jobs", "",
  "en", "Curated remote listings", fit="low", priority=3)
A("remote", "GLOBAL", "FlexJobs", "https://www.flexjobs.com", "", "en",
  "Curated remote and flexible roles", access="login_required", fit="low", priority=3,
  notes="Paid subscription; no scraping.")
A("remote", "GLOBAL", "Jobgether", "https://jobgether.com", "", "en",
  "Remote-first roles aggregated with a matching score", fit="medium", priority=3)
A("remote", "EU", "EU Remote Jobs", "https://euremotejobs.com", "", "en",
  "Remote roles restricted to European time zones", fit="medium", priority=2)
A("remote", "EU", "Green Remote Jobs", "https://greenremotejobs.com", "", "en",
  "Remote climate and sustainability roles", fit="high", priority=2,
  notes="Small board, but every listing is on-topic.")
