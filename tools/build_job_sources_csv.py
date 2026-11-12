#!/usr/bin/env python3
"""Build the job-source registry CSV.

One row per place a vacancy can be found or a CV submitted. Written to
google_drive/ so it never enters git (see .gitignore: the whole directory is
ignored).

Columns are chosen for the *next* step, the scraper:
  id            stable slug, safe to use as a primary key
  category      job_board | pes | public_sector | institution | big4 |
                company | aggregator | remote
  country       ISO-ish code, or GLOBAL
  name
  url           the site itself, always the most stable form (root domain
                where a deep path was not confirmed)
  listing_url   the search/results page, blank when the site has none stable
  language
  what_it_lists  short description of the coverage
  access        open | login_required | api | tos_restricted
  fit           high | medium | low  (fit to an environmental bioengineer
                doing sustainability data, ESG reporting, energy and
                environmental compliance)
  priority      1 = check every run, 2 = weekly, 3 = occasionally
  notes         caveats and anything the scraper author must know
"""

import csv
import pathlib

OUT = pathlib.Path("google_drive/job_sources_registry.csv")

# (category, country, name, url, listing_url, language, what_it_lists,
#  access, fit, priority, notes)
ROWS = []


def add(cat, country, name, url, listing, lang, what, access, fit, prio, notes=""):
    ROWS.append({
        "category": cat, "country": country, "name": name, "url": url,
        "listing_url": listing, "language": lang, "what_it_lists": what,
        "access": access, "fit": fit, "priority": prio, "notes": notes,
    })


# --------------------------------------------------------------------------- #
# BELGIUM — public employment services
# --------------------------------------------------------------------------- #
add("pes", "BE", "Actiris (Brussels)", "https://www.actiris.brussels",
    "https://www.actiris.brussels/fr/citoyens/offres-d-emploi/", "fr/nl",
    "All vacancies notified in the Brussels-Capital Region", "open", "high", 1,
    "Regional PES. Site confirmed 2026-11-10.")
add("pes", "BE", "Le Forem (Wallonia)", "https://www.leforem.be", "", "fr",
    "Walloon regional vacancies, including stage and alternance", "open", "high", 1,
    "Job search section is behind a search form, no stable results URL.")
add("pes", "BE", "VDAB (Flanders)", "https://www.vdab.be", "", "nl",
    "Flemish regional vacancies", "open", "medium", 2,
    "Dutch-language interface; most Flemish vacancies also reach StepStone/Indeed.")
add("pes", "BE", "ADG (German-speaking Community)", "https://adg.be", "", "de",
    "Vacancies in the German-speaking municipalities", "open", "low", 3,
    "Small volume, low relevance unless the Ostbelgien area is of interest.")
add("public_sector", "BE", "Travailler pour la fonction publique federale",
    "https://travaillerpour.be", "https://travaillerpour.be/fr/jobs", "fr/nl",
    "Federal civil service vacancies (the former Selor portal)", "open", "medium", 2,
    "Selor was folded into this BOSA-run portal.")

# --------------------------------------------------------------------------- #
# BELGIUM — general boards
# --------------------------------------------------------------------------- #
add("job_board", "BE", "StepStone Belgium", "https://www.stepstone.be", "", "fr/nl",
    "Large commercial board, all sectors", "open", "medium", 1, "")
add("job_board", "BE", "Jobat", "https://www.jobat.be", "", "nl",
    "Flemish commercial board, strong on SMEs", "open", "medium", 2, "")
add("job_board", "BE", "References.be", "https://www.references.be", "", "fr",
    "Francophone commercial board", "open", "medium", 2, "")
add("job_board", "BE", "Jobijoba Belgium", "https://www.jobijoba.be", "", "fr/nl",
    "Aggregator over Belgian boards", "open", "medium", 3, "")
add("job_board", "BE", "JobsinBrussels", "https://jobsinbrussels.com", "", "en/fr/nl",
    "English-first Brussels vacancies, NGOs and EU affairs", "open", "high", 1,
    "Directly relevant to an English/French bilingual profile in Brussels.")
add("job_board", "BE", "EuroBrussels", "https://www.eurobrussels.com",
    "https://www.eurobrussels.com/jobs/environment", "en",
    "EU institutions, NGOs, think tanks and industry associations in Brussels; "
    "there is a dedicated Environment section", "open", "high", 1,
    "Best single board for the EU bubble, and the environment filter removes most of the noise.")

# --------------------------------------------------------------------------- #
# BELGIUM — environment / energy / engineering niche
# --------------------------------------------------------------------------- #
add("job_board", "BE", "Greenjobs.nl (covers Belgium)", "https://greenjobs.nl",
    "https://greenjobs.nl/en/jobs", "nl/en",
    "Sustainable and impact jobs at B Corps, social enterprises and public bodies; "
    "Belgium is a selectable work region", "open", "high", 1,
    "Replaces greenjobs.be, which no longer resolves (checked 2026-11-10). "
    "Dutch-language interface but Belgian vacancies appear and may be in French or English.")
add("job_board", "BE", "Alterjob", "https://www.alterjob.be", "https://www.alterjob.be/fr/offres", "fr",
    "Social and environmental economy, non-profit", "open", "high", 2, "")
add("job_board", "BE", "Nature Jobs (Belgium filter)", "https://www.nature.com/naturecareers", "",
    "en", "Academic and research posts in environmental science", "open", "medium", 3,
    "Filter by Belgium; low volume but high relevance when it appears.")
add("job_board", "BE", "Academic Positions (Belgium)", "https://academicpositions.be", "",
    "en", "PhD, postdoc and university research staff", "open", "medium", 3,
    "Relevant if the research/academic angle is kept in play.")

# --------------------------------------------------------------------------- #
# LUXEMBOURG
# --------------------------------------------------------------------------- #
add("pes", "LU", "ADEM (JobBoard)", "https://adem.public.lu", "https://jobboard.adem.public.lu",
    "fr/de/en", "Official Luxembourg vacancies and the national job board",
    "login_required", "high", 1,
    "ADEM JobBoard requires an account for some functions; the public listing is browsable.")
add("job_board", "LU", "Work in Luxembourg", "https://workinluxembourg.com", "", "en/fr",
    "Official international recruitment platform, shortage occupations",
    "open", "high", 1,
    "Run by the Luxembourg government with EURES; aimed at cross-border and foreign candidates.")
add("job_board", "LU", "Moovijob", "https://en.moovijob.com", "", "en/fr",
    "Broad commercial board, all sectors", "open", "medium", 2, "")
add("job_board", "LU", "Jobs.lu", "https://www.jobs.lu", "", "en/fr",
    "Professional and sector-specific vacancies", "open", "medium", 2, "")
add("job_board", "LU", "Jobfinder.lu", "https://www.jobfinder.lu", "", "fr",
    "General board", "open", "medium", 3, "")
add("job_board", "LU", "Paperjam Jobs", "https://jobs.paperjam.lu", "", "fr",
    "Business and finance vacancies", "open", "medium", 3, "")
add("job_board", "LU", "Optioncarriere Luxembourg", "https://www.optioncarriere.lu", "", "fr",
    "Aggregator", "open", "low", 3, "")
add("job_board", "LU", "ABBL jobs (banking)", "https://www.abbl.lu", "", "en/fr",
    "Luxembourg banking and fund industry vacancies", "open", "medium", 3,
    "Sector federation; useful for ESG-in-finance roles specifically.")

# --------------------------------------------------------------------------- #
# SWITZERLAND
# --------------------------------------------------------------------------- #
add("pes", "CH", "Job-Room / arbeit.swiss", "https://www.job-room.ch",
    "https://www.job-room.ch/job-search", "de/fr/it/en",  # verified 2026-11-10: 73k live positions
    "Official SECO portal, vacancies that RAV-registered employers must report",
    "login_required", "high", 1,
    "Job search is public; an account is needed for some services.")
add("job_board", "CH", "jobs.ch", "https://www.jobs.ch", "", "de/fr",
    "Largest Swiss board, all sectors, strong German-speaking coverage",
    "open", "medium", 1, "")
add("job_board", "CH", "jobup.ch", "https://www.jobup.ch", "", "fr",
    "Leading French-speaking Swiss board", "open", "medium", 2, "")
add("job_board", "CH", "JobScout24", "https://www.jobscout24.ch", "", "de", 
    "General board", "open", "medium", 3, "")
add("job_board", "CH", "ostjob.ch", "https://www.ostjob.ch", "", "de",
    "Eastern Switzerland regional board", "open", "low", 3, "")
add("public_sector", "CH", "Stellenportal Bund (federal government)",
    "https://www.stelle.admin.ch", "", "de/fr/it",
    "Federal administration vacancies", "open", "medium", 2, "")
add("job_board", "CH", "ETH Zurich jobs", "https://jobs.ethz.ch", "", "en/de",
    "University and research vacancies", "open", "high", 3,
    "Relevant for environmental science and data roles.")
add("job_board", "CH", "EPFL jobs", "https://www.epfl.ch/campus/jobs/", "", "fr/en",
    "University and research vacancies", "open", "medium", 3, "")

# --------------------------------------------------------------------------- #
# AUSTRALIA
# --------------------------------------------------------------------------- #
add("public_sector", "AU", "APS Jobs", "https://www.apsjobs.gov.au",
    "https://www.apsjobs.gov.au/s/job-search", "en",
    "Australian Public Service, all federal departments and agencies",
    "open", "high", 1,
    "Environment and climate departments recruit here first. See the state/territory links page.")
add("pes", "AU", "Workforce Australia / JobSearch", "https://www.jobsearch.gov.au", "",
    "en", "Government job search service", "open", "low", 3,
    "Aimed at registered jobseekers; thin on professional roles.")
add("job_board", "AU", "SEEK Australia", "https://www.seek.com.au", "", "en",
    "Largest commercial board", "open", "medium", 1, "")
add("job_board", "AU", "CareerOne", "https://www.careerone.com.au", "", "en",
    "General board", "open", "low", 3, "")
add("job_board", "AU", "Ethical Jobs", "https://www.ethicaljobs.com.au", "", "en",
    "Environment, sustainability, social purpose and non-profit roles",
    "open", "high", 1,
    "One of the most relevant boards in Australia for this profile.")
add("job_board", "AU", "GradConnection Australia", "https://au.gradconnection.com", "",
    "en", "Graduate programmes and internships", "open", "high", 2, "")
add("public_sector", "AU", "NSW Government jobs", "https://iworkfor.nsw.gov.au", "", "en",
    "New South Wales public sector", "open", "medium", 2, "")
add("public_sector", "AU", "Victorian Government jobs", "https://careers.vic.gov.au", "", "en",
    "Victoria public sector", "open", "medium", 2, "")
add("public_sector", "AU", "Queensland Smart Jobs", "https://smartjobs.qld.gov.au", "", "en",
    "Queensland public sector", "open", "medium", 2,
    "The external search URL carries an organid parameter; use the root and search.")
add("public_sector", "AU", "WA Government jobs", "https://jobs.wa.gov.au", "", "en",
    "Western Australia public sector", "open", "medium", 3, "")
add("public_sector", "AU", "SA Government jobs", "https://iworkfor.sa.gov.au", "", "en",
    "South Australia public sector", "open", "medium", 3, "")
add("public_sector", "AU", "Tasmanian Government jobs", "https://www.jobs.tas.gov.au", "",
    "en", "Tasmania public sector", "open", "low", 3, "")
add("public_sector", "AU", "NT Government jobs", "https://nt.gov.au/employ/work-for-government",
    "", "en", "Northern Territory public sector", "open", "low", 3, "")
add("public_sector", "AU", "ACT Government jobs", "https://www.jobs.act.gov.au", "", "en",
    "Canberra public sector", "open", "medium", 3, "")

# --------------------------------------------------------------------------- #
# NEW ZEALAND
# --------------------------------------------------------------------------- #
add("public_sector", "NZ", "jobs.govt.nz", "https://jobs.govt.nz", "", "en",
    "All New Zealand public service vacancies", "open", "high", 1,
    "Ministry for the Environment, DOC, MPI and councils recruit here.")
add("job_board", "NZ", "SEEK New Zealand", "https://www.seek.co.nz", "", "en",
    "Largest commercial board", "open", "medium", 1, "")
add("job_board", "NZ", "Trade Me Jobs", "https://www.trademe.co.nz/jobs", "", "en",
    "Most-visited NZ job site", "open", "medium", 2, "")
add("job_board", "NZ", "Careers.govt.nz", "https://www.careers.govt.nz", "", "en",
    "Careers advice plus a vacancy database and recruiter directory",
    "open", "medium", 2, "")
add("job_board", "NZ", "Student Job Search", "https://www.sjs.co.nz", "", "en",
    "Student and graduate work, part-time and summer", "login_required", "medium", 3,
    "Requires proof of enrolment; likely closed to a graduate.")
add("pes", "NZ", "Work and Income job search", "https://www.workandincome.govt.nz", "",
    "en", "Government job database", "open", "low", 3, "")
add("job_board", "NZ", "Jora New Zealand", "https://nz.jora.com", "", "en",
    "Aggregator", "open", "low", 3, "")
add("job_board", "NZ", "GradConnection New Zealand", "https://nz.gradconnection.com", "",
    "en", "Graduate programmes and internships", "open", "high", 2, "")

# --------------------------------------------------------------------------- #
# UAE
# --------------------------------------------------------------------------- #
add("public_sector", "AE", "Dubai Careers", "https://www.dubaicareers.ae", "", "en/ar",
    "Official portal for 45+ Dubai government entities", "open", "medium", 2,
    "Open to expatriates, unlike several emirate portals.")
add("public_sector", "AE", "TAMM Abu Dhabi", "https://www.tamm.abudhabi", "", "en/ar",
    "Abu Dhabi government services, including public-sector jobs",
    "login_required", "medium", 3,
    "Jobs sit inside a wider services portal, so scraping is awkward.")
add("public_sector", "AE", "FAHR federal government portal", "https://www.fahr.gov.ae",
    "", "en/ar", "Federal ministries and authorities", "open", "medium", 3, "")
add("public_sector", "AE", "Nafis", "https://nafis.gov.ae", "", "en/ar",
    "Emiratisation programme; private-sector roles for UAE nationals",
    "login_required", "low", 3,
    "Restricted to UAE nationals, so not applicable to this profile.")
add("pes", "AE", "MoHRE", "https://www.mohre.gov.ae", "", "en/ar",
    "Ministry of Human Resources; labour market and work permit rules",
    "open", "low", 3,
    "Regulator rather than a job board, but the work-permit rules matter before applying.")
add("job_board", "AE", "Bayt.com", "https://www.bayt.com", "", "en/ar",
    "Largest MENA board, all sectors", "login_required", "medium", 1, "")
add("job_board", "AE", "GulfTalent", "https://www.gulftalent.com", "", "en",
    "Professional and managerial roles across the Gulf", "login_required", "medium", 2, "")
add("job_board", "AE", "Naukrigulf", "https://www.naukrigulf.com", "", "en",
    "Large volume board, strong on engineering and construction",
    "open", "medium", 2, "")
add("job_board", "AE", "Dubizzle Jobs", "https://www.dubizzle.com", "", "en",
    "Classifieds-style listings, quick-start roles", "open", "low", 3, "")

# --------------------------------------------------------------------------- #
# BIG FOUR — global plus the country sites that matter here
# --------------------------------------------------------------------------- #
add("big4", "GLOBAL", "Deloitte careers (global)", "https://www.deloitte.com/careers.html",
    "https://jobs.deloitte.com", "en",
    "All member-firm vacancies, filterable by country", "open", "high", 1,
    "Sustainability and climate advisory sit inside Audit & Assurance and Risk Advisory.")
add("big4", "GLOBAL", "PwC careers (global)", "https://www.pwc.com/gx/en/careers.html", "",
    "en", "All member-firm vacancies", "open", "high", 1,
    "Sustainability reporting (CSRD) is a large PwC service line in the EU.")
add("big4", "GLOBAL", "EY careers (global)", "https://www.ey.com/en_gl/careers", "", "en",
    "All member-firm vacancies", "open", "high", 1,
    "EY has a dedicated Climate Change and Sustainability Services practice.")
add("big4", "GLOBAL", "KPMG careers (global)", "https://kpmg.com/xx/en/careers.html", "",
    "en", "All member-firm vacancies", "open", "high", 1,
    "ESG advisory and the KPMG IMPACT network.")
add("big4", "BE", "Deloitte Belgium", "https://www.deloitte.com/be/en/careers.html", "",
    "en/fr/nl", "Belgian member-firm vacancies", "open", "high", 2, "")
add("big4", "BE", "PwC Belgium", "https://www.pwc.be/en/careers.html", "", "en/fr/nl",
    "Belgian member-firm vacancies", "open", "high", 2, "")
add("big4", "BE", "EY Belgium", "https://www.ey.com/en_be/careers", "", "en/fr/nl",
    "Belgian member-firm vacancies", "open", "high", 2, "")
add("big4", "BE", "KPMG Belgium", "https://kpmg.com/be/en/careers.html", "", "en/fr/nl",
    "Belgian member-firm vacancies", "open", "high", 2, "")
add("big4", "LU", "Deloitte Luxembourg", "https://www.deloitte.com/lu/en/careers.html", "",
    "en/fr", "Luxembourg member-firm vacancies", "open", "high", 2, "")
add("big4", "LU", "PwC Luxembourg", "https://www.pwc.lu/en/careers.html", "", "en/fr",
    "Luxembourg member-firm vacancies", "open", "high", 2, "")
add("big4", "LU", "EY Luxembourg", "https://www.ey.com/en_lu/careers", "", "en/fr",
    "Luxembourg member-firm vacancies", "open", "high", 2, "")
add("big4", "LU", "KPMG Luxembourg", "https://kpmg.com/lu/en/careers.html", "", "en/fr",
    "Luxembourg member-firm vacancies", "open", "high", 2, "")

# --------------------------------------------------------------------------- #
# INSTITUTIONS — UN, EU
# --------------------------------------------------------------------------- #
add("institution", "GLOBAL", "UN Careers", "https://careers.un.org", "", "en/fr",
    "UN Secretariat and field missions, all duty stations", "open", "high", 1,
    "Inspira-based. Vacancies are also mirrored on the UN Global Careers site.")
add("institution", "GLOBAL", "UNDP Jobs", "https://jobs.undp.org", "", "en",
    "UNDP country offices, including climate and environment programmes",
    "open", "high", 1, "UNDP runs a large environment and climate portfolio.")
add("institution", "GLOBAL", "UNOPS", "https://jobs.unops.org", "", "en",
    "Project services, infrastructure and procurement", "open", "medium", 2, "")
add("institution", "GLOBAL", "UNICEF", "https://jobs.unicef.org", "", "en",
    "Programme, data and evaluation roles", "open", "medium", 3, "")
add("institution", "GLOBAL", "UN Volunteers", "https://www.unv.org", "", "en/fr",
    "UN Volunteer assignments, a common entry route", "open", "high", 2,
    "Often the realistic first step into the UN system for a recent graduate.")
add("institution", "GLOBAL", "Green Climate Fund", "https://www.greenclimate.fund/careers",
    "", "en", "Climate finance roles, Songdo, Korea", "open", "high", 2, "")
add("institution", "GLOBAL", "World Bank Group careers", "https://www.worldbank.org/en/careers",
    "", "en", "Climate and environment practice, Washington and country offices",
    "open", "medium", 3, "")
add("institution", "EU", "EU Careers", "https://eu-careers.europa.eu",
    "https://eu-careers.europa.eu/jobs_en", "en/fr",
    "Vacancies across all EU institutions and agencies", "open", "high", 1,
    "The plain /en/home path 404s; the homepage is /index_en.")
add("institution", "EU", "EPSO (competitions and CAST)", "https://selection.eu-careers.europa.eu",
    "https://selection.eu-careers.europa.eu/en", "en/fr",
    "Permanent-official competitions and the always-open contract-agent registration",
    "login_required", "high", 1,
    "EPSO used to live at epso.europa.eu and has moved here. Fixed opening and closing windows.")
add("institution", "EU", "European Commission traineeships (Blue Book)",
    "https://traineeships.ec.europa.eu", "", "en/fr",
    "Five-month paid traineeships in the Commission", "login_required", "high", 1,
    "Two intakes a year; one of the realistic routes into the institutions.")
add("institution", "EU", "European Environment Agency", "https://www.eea.europa.eu", "",
    "en", "Environment agency of the EU, Copenhagen", "open", "high", 2,
    "Recruits through EPSO and its own temporary-agent calls.")
add("institution", "EU", "European Investment Bank careers", "https://www.eib.org/en/about/careers",
    "", "en", "Climate and environment lending, Luxembourg", "open", "high", 2,
    "Based in Luxembourg, so it sits in both the EU and Luxembourg buckets.")
add("institution", "BE", "EURES", "https://eures.europa.eu", "", "en/fr/de",
    "Cross-border European vacancies and mobility services", "open", "medium", 2,
    "Also the data source behind several national portals.")

# --------------------------------------------------------------------------- #
# AGGREGATORS — present, but read the access note
# --------------------------------------------------------------------------- #
add("aggregator", "GLOBAL", "LinkedIn Jobs", "https://www.linkedin.com/jobs", "", "en",
    "Everything, including roles never posted elsewhere", "tos_restricted", "high", 1,
    "The user agreement prohibits automated scraping. Use the official Job Posting "
    "API with an approved partner account, or manual saved searches.")
add("aggregator", "GLOBAL", "Indeed", "https://www.indeed.com", "", "en",
    "Aggregated listings across most countries", "tos_restricted", "high", 1,
    "Terms prohibit scraping. Indeed offers a publisher/partner API; without it, "
    "treat this source as manual only.")
add("aggregator", "GLOBAL", "Google Jobs", "https://www.google.com/search?q=jobs", "",
    "en", "Aggregates structured job postings across the web", "tos_restricted", "medium", 3,
    "No public feed; scraping the results page breaks Google's terms.")
add("aggregator", "GLOBAL", "Glassdoor", "https://www.glassdoor.com/Job/index.htm", "",
    "en", "Listings plus salary and interview data", "tos_restricted", "medium", 3,
    "Scraping prohibited; useful for research rather than harvesting.")

# --------------------------------------------------------------------------- #
# REMOTE
# --------------------------------------------------------------------------- #
add("remote", "GLOBAL", "We Work Remotely", "https://weworkremotely.com", "", "en",
    "Remote roles worldwide, strong on tech and ops", "open", "medium", 2, "")
add("remote", "GLOBAL", "Remote OK", "https://remoteok.com", "", "en",
    "Remote roles, aggregated", "open", "medium", 2,
    "Publishes a public JSON feed; check its terms before relying on it.")
add("remote", "GLOBAL", "Remotive", "https://remotive.com", "", "en",
    "Remote roles with a public API", "api", "medium", 1,
    "Has a documented free API for job listings, which makes it the easiest to wire in.")
add("remote", "GLOBAL", "Himalayas", "https://himalayas.app/jobs", "", "en",
    "Remote roles, searchable by country and timezone", "open", "medium", 2, "")
add("remote", "GLOBAL", "Working Nomads", "https://www.workingnomads.com/jobs", "",
    "en", "Curated remote listings", "open", "low", 3, "")
add("remote", "GLOBAL", "FlexJobs", "https://www.flexjobs.com", "", "en",
    "Curated remote and flexible roles", "login_required", "low", 3,
    "Paid subscription; no scraping.")
add("remote", "EU", "EU Remote Jobs", "https://euremotejobs.com", "", "en",
    "Remote roles restricted to European time zones", "open", "medium", 2, "")

# --------------------------------------------------------------------------- #
# COMPANY CAREER PAGES — a seed list, not an enumeration
# --------------------------------------------------------------------------- #
COMPANIES = [
    # Belgium — energy, utilities, industry, environment, engineering
    ("BE", "Engie Belgium", "https://www.engie.be", "high"),
    ("BE", "Elia Group (transmission system operator)", "https://www.elia.be", "high"),
    ("BE", "Fluxys", "https://www.fluxys.com", "medium"),
    ("BE", "Veolia Belgium", "https://www.veolia.be", "high"),
    ("BE", "SUEZ Belgium", "https://www.suez.be", "high"),
    ("BE", "Umicore", "https://www.umicore.com", "high"),
    ("BE", "Solvay", "https://www.solvay.com", "medium"),
    ("BE", "AGC Glass Europe", "https://www.agc.com", "medium"),
    ("BE", "ArcelorMittal", "https://corporate.arcelormittal.com", "medium"),
    ("BE", "BASF Antwerp", "https://www.basf.com", "medium"),
    ("BE", "Colruyt Group", "https://www.colruytgroup.com", "high"),
    ("BE", "AB InBev", "https://www.ab-inbev.com", "medium"),
    ("BE", "Barry Callebaut", "https://www.barry-callebaut.com", "high"),
    ("BE", "Puratos", "https://www.puratos.com", "medium"),
    ("BE", "UCB", "https://www.ucb.com", "medium"),
    ("BE", "Proximus", "https://www.proximus.com", "low"),
    ("BE", "KBC", "https://www.kbc.com", "medium"),
    ("BE", "Belfius", "https://www.belfius.be", "medium"),
    ("BE", "BNP Paribas Fortis", "https://www.bnpparibasfortis.be", "medium"),
    ("BE", "DEME Group", "https://www.deme-group.com", "high"),
    ("BE", "Jan De Nul", "https://www.jandenul.com", "high"),
    ("BE", "BESIX", "https://www.besix.com", "medium"),
    ("BE", "Tractebel (Engie)", "https://www.tractebel-engie.com", "high"),
    ("BE", "Arcadis Belgium", "https://www.arcadis.com", "high"),
    ("BE", "Sweco Belgium", "https://www.sweco.be", "high"),
    ("BE", "Antea Group Belgium", "https://www.anteagroup.be", "high"),
    ("BE", "Vinçotte (Apave)", "https://www.vincotte.be", "high"),
    ("BE", "SGS", "https://www.sgs.com", "high"),
    ("BE", "Bureau Veritas", "https://www.bureauveritas.com", "high"),
    ("BE", "ERM (Environmental Resources Management)", "https://www.erm.com", "high"),
    ("BE", "Anthesis Group", "https://www.anthesisgroup.com", "high"),
    ("BE", "South Pole", "https://www.southpole.com", "high"),
    ("BE", "WSP", "https://www.wsp.com", "high"),
    ("BE", "Arup", "https://www.arup.com", "high"),
    ("BE", "Ramboll", "https://www.ramboll.com", "high"),
    ("BE", "Mott MacDonald", "https://www.mottmac.com", "high"),
    ("BE", "Royal HaskoningDHV", "https://www.royalhaskoningdhv.com", "high"),
    ("BE", "ICF", "https://www.icf.com", "high"),
    ("BE", "Guidehouse", "https://guidehouse.com", "high"),
    # Luxembourg
    ("LU", "European Investment Bank", "https://www.eib.org", "high"),
    ("LU", "SES", "https://www.ses.com", "low"),
    ("LU", "BGL BNP Paribas", "https://www.bgl.lu", "medium"),
    ("LU", "Spuerkeess", "https://www.spuerkeess.lu", "medium"),
    ("LU", "Banque Internationale à Luxembourg", "https://www.bil.com", "medium"),
    ("LU", "Cargolux", "https://www.cargolux.com", "medium"),
    ("LU", "Luxair", "https://www.luxair.lu", "low"),
    ("LU", "POST Luxembourg", "https://www.post.lu", "medium"),
    ("LU", "Encevo / Enovos", "https://www.encevo.lu", "high"),
    ("LU", "Creos", "https://www.creos.net", "high"),
    ("LU", "Ferrero", "https://www.ferrero.com", "medium"),
    ("LU", "Goodyear", "https://www.goodyear.com", "medium"),
    # Switzerland
    ("CH", "Nestlé", "https://www.nestle.com", "high"),
    ("CH", "Roche", "https://www.roche.com", "medium"),
    ("CH", "Novartis", "https://www.novartis.com", "medium"),
    ("CH", "ABB", "https://www.abb.com", "medium"),
    ("CH", "Holcim", "https://www.holcim.com", "high"),
    ("CH", "Lonza", "https://www.lonza.com", "medium"),
    ("CH", "Syngenta", "https://www.syngenta.com", "high"),
    ("CH", "Swiss Re", "https://www.swissre.com", "medium"),
    ("CH", "Zurich Insurance", "https://www.zurich.com", "low"),
    ("CH", "UBS", "https://www.ubs.com", "medium"),
    ("CH", "Swisscom", "https://www.swisscom.ch", "low"),
    ("CH", "SBB", "https://www.sbb.ch", "medium"),
    ("CH", "Axpo", "https://www.axpo.com", "high"),
    ("CH", "BKW", "https://www.bkw.ch", "high"),
    ("CH", "Alpiq", "https://www.alpiq.com", "high"),
    ("CH", "Eawag (aquatic research)", "https://www.eawag.ch", "high"),
    ("CH", "Empa (materials research)", "https://www.empa.ch", "high"),
    # Australia
    ("AU", "BHP", "https://www.bhp.com", "medium"),
    ("AU", "Rio Tinto", "https://www.riotinto.com", "medium"),
    ("AU", "Fortescue", "https://www.fortescue.com", "medium"),
    ("AU", "Woodside Energy", "https://www.woodside.com", "medium"),
    ("AU", "AGL Energy", "https://www.agl.com.au", "high"),
    ("AU", "Origin Energy", "https://www.originenergy.com.au", "high"),
    ("AU", "Snowy Hydro", "https://www.snowyhydro.com.au", "high"),
    ("AU", "Transgrid", "https://www.transgrid.com.au", "high"),
    ("AU", "APA Group", "https://www.apa.com.au", "medium"),
    ("AU", "Cleanaway", "https://www.cleanaway.com.au", "high"),
    ("AU", "Orica", "https://www.orica.com", "medium"),
    ("AU", "Veolia Australia", "https://www.veolia.com.au", "high"),
    ("AU", "Aurecon", "https://www.aurecongroup.com", "high"),
    ("AU", "GHD", "https://www.ghd.com", "high"),
    ("AU", "Jacobs", "https://www.jacobs.com", "high"),
    ("AU", "CSIRO", "https://www.csiro.au", "high"),
    ("AU", "Department of Climate Change, Energy, the Environment and Water",
     "https://www.dcceew.gov.au", "high"),
    # New Zealand
    ("NZ", "Fonterra", "https://www.fonterra.com", "high"),
    ("NZ", "Air New Zealand", "https://www.airnewzealand.co.nz", "low"),
    ("NZ", "Contact Energy", "https://www.contactenergy.co.nz", "high"),
    ("NZ", "Meridian Energy", "https://www.meridianenergy.co.nz", "high"),
    ("NZ", "Mercury", "https://www.mercury.co.nz", "high"),
    ("NZ", "Genesis Energy", "https://www.genesisenergy.co.nz", "high"),
    ("NZ", "Transpower", "https://www.transpower.co.nz", "high"),
    ("NZ", "Watercare", "https://www.watercare.co.nz", "high"),
    ("NZ", "Ministry for the Environment", "https://www.mfe.govt.nz", "high"),
    ("NZ", "Department of Conservation", "https://www.doc.govt.nz", "high"),
    ("NZ", "NIWA", "https://niwa.co.nz", "high"),
    ("NZ", "Scion", "https://www.scionresearch.com", "high"),
    ("NZ", "Tonkin + Taylor", "https://www.tonkintaylor.co.nz", "high"),
    ("NZ", "Beca", "https://www.beca.com", "high"),
    # UAE
    ("AE", "ADNOC", "https://www.adnoc.ae", "medium"),
    ("AE", "Masdar", "https://www.masdar.ae", "high"),
    ("AE", "DEWA", "https://www.dewa.gov.ae", "high"),
    ("AE", "TAQA", "https://www.taqa.com", "high"),
    ("AE", "Emirates Global Aluminium", "https://www.ega.ae", "medium"),
    ("AE", "DP World", "https://www.dpworld.com", "medium"),
    ("AE", "Emirates Group", "https://www.emiratesgroupcareers.com", "low"),
    ("AE", "Majid Al Futtaim", "https://www.majidalfuttaim.com", "medium"),
    ("AE", "Emaar", "https://www.emaar.com", "low"),
    ("AE", "Aldar Properties", "https://www.aldar.com", "medium"),
    ("AE", "Mubadala", "https://www.mubadala.com", "medium"),
    ("AE", "Bee'ah", "https://www.beeah.ae", "high"),
    ("AE", "Environment Agency Abu Dhabi", "https://www.ead.gov.ae", "high"),
    ("AE", "Ministry of Climate Change and Environment", "https://www.moccae.gov.ae", "high"),
]

for country, name, url, fit in COMPANIES:
    add("company", country, name, url, "", "",
        "Employer career page (find Careers from the homepage)",
        "open", fit, 2 if fit == "high" else 3,
        "Root domain on purpose: career-page paths vary by ATS and break when the "
        "employer migrates. Resolve the link once, then cache it.")


# --------------------------------------------------------------------------- #
def slug(s):
    keep = [c.lower() if c.isalnum() else "-" for c in s]
    out = "".join(keep)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def main():
    seen_urls, seen_ids = {}, set()
    rows = []
    for i, r in enumerate(ROWS, 1):
        base = f"{r['category']}-{r['country']}-{slug(r['name'])}"
        rid = base
        n = 2
        while rid in seen_ids:
            rid = f"{base}-{n}"
            n += 1
        seen_ids.add(rid)
        row = {"id": rid}
        row.update(r)
        rows.append(row)
        if r["url"] in seen_urls:
            print(f"  duplicate url: {r['url']} ({r['name']} / {seen_urls[r['url']]})")
        seen_urls[r["url"]] = r["name"]

    fields = ["id", "category", "country", "name", "url", "listing_url",
              "language", "what_it_lists", "access", "fit", "priority", "notes"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    by_cat, by_country = {}, {}
    for r in rows:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
        by_country[r["country"]] = by_country.get(r["country"], 0) + 1
    print(f"wrote {OUT} with {len(rows)} rows")
    print("  by category:", dict(sorted(by_cat.items())))
    print("  by country: ", dict(sorted(by_country.items())))


if __name__ == "__main__":
    main()
