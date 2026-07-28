# Quantum × HPC Pathways: Interactive Advisor — Spec

## Project context

This app is the Quantum × HPC Pathways: South Side Advanced Technology Workforce
Strategy dashboard, supporting a civic workforce-development initiative connecting
South Side Chicago residents to the emerging quantum and HPC economy.

Current state (Phase: static dashboard):
- Built in Streamlit, 33+ pages, single on-page selectbox navigation
- Data sources integrated: ACS, CDC SVI, CPS, ISTC, BCG/CQE, IBM data
- Core analytical model: two-axis Opportunity and Vulnerability framework
- Purpose to date: exploration and presentation tool for stakeholder pitches
  (e.g. Global Quantum Forum) and grant applications

Target state (Phase: interactive advisor):
Add an advisor layer on top of the existing dashboard that lets an individual
resident get a personalized pathway recommendation, rather than only exploring
aggregate/regional data.

## Advisor input

A short intake capturing, at minimum:
- Current background: education level, relevant experience (tech, none, adjacent
  trades), employment status
- Interests: which pathway domains appeal (e.g. quantum hardware, HPC systems
  administration, data/software, technician-level roles)
- Constraints: geography within South Side Chicago, time availability
  (full-time upskilling vs. part-time), transportation

Keep the intake short. This is a civic tool for residents, not a job-matching
platform with dozens of fields.

## Matching logic

Recommendations must be derived from, and traceable to, the existing
Opportunity and Vulnerability framework and underlying data sources already
in the app — not from a new, separately invented scoring system. Specifically:

- Use the Opportunity axis (e.g. CQE/BCG labor demand signals, ISTC program
  availability) to identify which pathway(s) fit the resident's stated
  interests and background.
- Use the Vulnerability axis (e.g. CDC SVI, ACS demographic/economic data) to
  flag where additional support resources (transportation, childcare,
  financial aid) are likely relevant, and surface those alongside the
  recommendation rather than silently.
- Every recommendation must cite which data source(s) drove it. This is a
  hard requirement: "recommended because of X employer demand signal from
  CQE" not "recommended based on your profile."

## Output

For each resident, the advisor should return:
1. 1–3 recommended pathways, ranked, each in plain language
2. For each pathway: the specific program or on-ramp (e.g. an ISTC course,
   a named employer/partner), and why it fits, with source attribution
3. Any relevant support-resource flags surfaced by the Vulnerability axis
4. A visible "confidence" or "data coverage" note — if a resident's profile
   falls outside what current data covers well, say so rather than forcing
   a recommendation

## Explicit non-goals

- This is not a general career-matching product. It should stay scoped to
  quantum/HPC-adjacent pathways already represented in the existing dashboard
  data.
- Do not invent new data sources or scoring weights without flagging them as
  assumptions for review — the existing framework has been vetted for
  stakeholder presentations and grant applications, and quiet changes to its
  logic would undermine that.
- No fabricated employer names, program names, or statistics. If the
  underlying data doesn't support a specific claim, the advisor should say
  the recommendation is directional rather than specific.

## Current constraints to work within

- Existing single on-page selectbox navigation pattern — the advisor should
  either integrate as a new page/section using the same navigation approach,
  or a clearly justified addition should be proposed if that pattern doesn't
  scale to an interactive feature.
- Data files/sources currently loaded by the app should be reused as-is
  where possible rather than re-ingested or duplicated.

## Open questions for planning phase

- Where should intake state live given Streamlit's session model — is this
  a single-session interaction, or should responses be saved for later
  reference (e.g. for grant-reporting purposes)?
- Should the advisor be usable standalone (a link shared separately from the
  full dashboard) or only reachable via the existing navigation?
