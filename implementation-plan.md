# Implementation Plan: Quantum × HPC Pathways Interactive Advisor

## Top-Level Overview

**Goal:** Add a personalized pathway-recommendation advisor on top of the existing
33-page static dashboard. A resident fills in a short intake form; the advisor
returns 1–3 ranked pathways drawn entirely from the existing Opportunity/Vulnerability
framework, with source citations, support-resource flags, and a confidence note.

**Scope boundary:** New "Pathway Advisor" page in the existing `st.selectbox`
navigation. All matching logic written as pure Python functions (no Streamlit calls)
so they are independently testable. Session state (Python `st.session_state`) holds
intake answers for the lifetime of the browser session only — no persistence.

**What is not in scope:** Persistent storage, new data sources not present in the
codebase or research report, general career matching outside quantum/HPC pathways,
and changes to any existing dashboard pages.

**Key decisions already made:**
- Session state: session-only (no persistence).
- Navigation: new entry in the `all_pages_mobile` selectbox list, using
  `st.session_state` internally for intake → recommendation sub-steps.
- New structured constants (`EMPLOYER_DATA`, `CREDENTIAL_DATA`, `SUPPORT_RESOURCES`)
  must be sourced exclusively from `Quantum-HPC-Pathways-Research-Report.md`,
  following the same citation standard as existing constants.

---

## Sub-Tasks

---

### Sub-Task 1: Extract Skills Taxonomy into Top-Level Constant

**Status:** [x] done

**Intent**
The 18-skill taxonomy that the advisor's matching logic will use is currently defined
as a local variable (`skills_data`) inside the "Quantum Skills Map" page renderer
(lines 1263–1351). Because it is mixed with rendering code, it cannot be referenced
by the advisor's matching functions without duplication or tight coupling.

Moving it to a module-level constant (`SKILLS_DATA`) makes it available to both the
existing Skills Map renderer and the new matching functions, with no duplication and
no behaviour change for the existing page.

**Expected Outcomes**
- A new `SKILLS_DATA` constant defined near the other top-level constants
  (after `ECOSYSTEM_ASSETS`, before `compute_qoi()`).
- The "Quantum Skills Map" page block references `SKILLS_DATA` instead of its own
  local definition.
- The existing Skills Map page renders identically to before.
- No other page is affected.

**Todo List**
1. Read lines 1263–1351 of `quantum_opportunity_dashboard.py` to confirm the exact
   current definition of `skills_data`.
2. Insert a new top-level constant `SKILLS_DATA` (a `pd.DataFrame` built from the
   same list-of-dicts) immediately after `ECOSYSTEM_ASSETS` (after line ~200 and
   before `compute_qoi()` at line ~204).
3. In the "Quantum Skills Map" page block, replace the local `skills_data = pd.DataFrame([...])` 
   definition with `skills_data = SKILLS_DATA.copy()`.
4. Verify the Skills Map page block still uses `skills_data` everywhere (no further
   rename needed downstream in that page block — just the construction line changes).

**Relevant Context**
- Current location: lines 1263–1351 in `quantum_opportunity_dashboard.py`
- Schema: `category`, `subcategory`, `skill`, `credential_min`, `whpc_provides` (bool),
  `whpc_note`, `local_provider`
- Placement target: after `ECOSYSTEM_ASSETS` (line ~200), before `compute_qoi()` (line ~204)
- Existing constants for style reference: `ALL_COMMUNITIES`, `ISTC_CREDENTIALS`,
  `ISTC_FIELDS`, `IQMP_JOBS`, `WHPC_SURVEY`, `ECOSYSTEM_ASSETS` (lines 124–200)

---

### Sub-Task 2: Build EMPLOYER_DATA and CREDENTIAL_DATA Constants

**Status:** [x] done

**Intent**
The advisor's Opportunity-axis matching needs structured, citable employer and
credential records. These must be built exclusively from `Quantum-HPC-Pathways-Research-Report.md`
following the same citation pattern already used for `IQMP_JOBS`, `ISTC_CREDENTIALS`,
and `ISTC_FIELDS` — every entry carries a `source` field with the attribution string
from the report.

This replaces the thin `IQMP_JOBS` data (5 categories, no employer names or specific
programs) with richer, named records that the matching logic can reason about.

**Expected Outcomes**
- A new `EMPLOYER_DATA` `pd.DataFrame` constant added to the top-level constants block.
- A new `CREDENTIAL_DATA` `pd.DataFrame` constant added to the top-level constants block.
- Both placed immediately after `SKILLS_DATA` (Sub-Task 1's new constant).
- Every record contains a `source` field citing the research report attribution for
  that entry, matching the format already used in the app's methodology pages.
- No fabricated entries. If the report does not specify a value (e.g., salary for
  Pasqal), the field is `None` or `"Not specified"` rather than invented.

**EMPLOYER_DATA schema and entries to include**

Columns: `employer`, `type`, `jobs_committed`, `salary_range`, `credential_min`,
`timeline`, `domain`, `pathway_tags`, `source`

Entries (all from research report):
- PsiQuantum — 154 jobs — $107K–$147K — Degree required — Groundbreak Sept 2025
  — Quantum Hardware — tags: hardware, quantum — Source: psiquantum.com/illinois; illinoisanswers.org
- Infleqtion — 36 new + 14 retained — Quantum Physicist $115K–$165K — Degree required
  — First neutral-atom computer 2027 — Quantum Hardware — tags: hardware, quantum
  — Source: illinoisanswers.org; Forbes Jul 22 2026
- Pasqal — 50 jobs — Not specified — Degree required — Not specified — Quantum Hardware
  — tags: hardware, quantum — Source: illinoisanswers.org (Feb 5, 2026)
- IBM FutureNow Chicago (IQMP portion) — 50 jobs — Not specified — Mixed — By 2028
  — Mixed (AI/cyber/data/quantum) — tags: software, data, hpc, quantum
  — Source: colleges.ccc.edu; gov-pritzker-newsroom (April 2026)
- Argonne National Laboratory — Multiple (CCI/SULI internships) — ~$105,990 median IT
  — Community college or undergraduate enrollment — Year-round
  — HPC/Quantum Research — tags: hpc, quantum, research — Source: anl.gov
- Fermilab — Multiple (TECHS/PACMAN/Quantum Computing internship) — Paid (amount unspecified)
  — High school to undergraduate — Year-round — HPC/Quantum Research
  — tags: hpc, quantum, technician, research — Source: fnal.gov
- Chicago Quantum Exchange (CQE Talent Portal) — 755 active listings across 62 employers
  — Varies — Varies — Active — Cross-sector quantum roles
  — tags: software, hardware, data, quantum — Source: chicagoquantum.org

**CREDENTIAL_DATA schema and entries to include**

Columns: `program`, `provider`, `duration`, `cost`, `credential_type`, `prerequisite`,
`target_group`, `pathway_tags`, `south_side_accessible`, `source`

Entries (all from research report):
- CCC–IBM Apprenticeship — City Colleges of Chicago / IBM — Year-long — Paid to participant
  — Apprenticeship — Entry requirements not specified — General adult learner — tags: software, hpc, data
  — South Side accessible (Olive-Harvey) — Source: colleges.ccc.edu (April 2026)
- Project Evolve (WEI) — Olive-Harvey College — Short-term — Free + transit + childcare + $500 stipend
  — Short certificate (13 programs) — Open admission — Black unemployed/underemployed residents
  — tags: technician, software — South Side accessible — Source: pages.ccc.edu/wei (Sept 2025)
- IBM SkillsBuild (Quantum credentials) — IBM — Self-paced — Free — Digital badge (Credly)
  — 18+ adult learner — General adult — tags: quantum, software — Accessible online
  — Source: skillsbuild.org; credly.com/org/ibm
- Q-Ready — Chicago Quantum Exchange — Short-term — Free — Professional development certificate
  — Current student or postdoc (IL/WI/IN) — Undergrad/grad/postdoc — tags: quantum, software
  — Not yet extended to adult career-changers (flagged gap) — Source: chicagoquantum.org (March 2026)
- OQI Undergraduate Fellowship — Multiple host institutions — 10 weeks — Paid
  — Research fellowship — Undergraduate enrollment — Undergraduates — tags: quantum, research
  — Not South Side specific — Source: chicagoquantum.org
- DOE Community College Internship (CCI) — Argonne — 10 weeks — Paid — Internship
  — Community college enrollment — Community college students — tags: hpc, quantum, research
  — South Side accessible (with transit) — Source: anl.gov
- Fermilab TECHS — Fermilab — Multi-year — Paid — Apprenticeship
  — High school enrollment — High school students — tags: technician, quantum
  — Not South Side specific — Source: fnal.gov
- Fermilab Quantum Computing Internship — Fermilab — Year-long — Paid — Internship
  — Physics undergraduate enrollment — Physics undergraduates — tags: quantum, research
  — Not South Side specific — Source: fnal.gov
- CCC WEI Technology Works — Daley College — Short-term — Free + stipend
  — Short certificate — Open admission — Adult learners — tags: technician
  — Not South Side (Daley College) — Source: pages.ccc.edu/wei (Sept 2025)
- ISTC Quantum-Relevant Credentials (statewide pipeline) — Various IL institutions
  — Varies — Varies — Certificate through PhD — Varies — Varies
  — tags: quantum, software, hardware, data — Statewide
  — Source: ISTC "Mapping Illinois' Quantum Talent Pipeline" (May 21, 2026); istcoalition.org

**Relevant Context**
- Placement: after `SKILLS_DATA`, before `compute_qoi()` (line ~204)
- Citation format reference: existing app methodology pages (lines ~4025–4190)
  and research report's "primary, current" source format
- Research report sourcing: `Quantum-HPC-Pathways-Research-Report.md`

---

### Sub-Task 3: Build SUPPORT_RESOURCES Constant

**Status:** [ ] pending

**Intent**
The advisor's Vulnerability-axis output must surface support resources (childcare,
transportation, financial aid, food security, WIOA job centers) when a resident's
profile indicates likely barriers. Currently, all support resource information exists
only as narrative text in the "Sustainability Model" and "Partnership Opportunities"
page blocks. It must be converted to a structured constant so matching functions can
reference it programmatically.

Every entry must be sourced from the research report. Entries with no source in
the report must not be added.

**Expected Outcomes**
- A new `SUPPORT_RESOURCES` list-of-dicts constant in the top-level constants block.
- Each record carries: `category`, `name`, `provider`, `eligibility`, `cost_to_participant`,
  `location`, `contact`, `barrier_addressed`, `source`.
- The "Sustainability Model" and "Partnership Opportunities" page blocks are unchanged
  (they continue to render their existing narrative text — the new constant is
  additive, not a replacement).
- Matching functions in Sub-Task 5 can filter `SUPPORT_RESOURCES` by `barrier_addressed`
  category (childcare, transportation, financial, food, training_cost, wraparound).

**Records to include** (all sourced from research report)

Childcare:
- Illinois CCAP — IDHS / Illinois Action for Children — Parents in education/training
  — Free (subsidized) — Cook County (South Side: 8741 S. Greenwood Ave, Suite 300; 312.823.1100)
  — Childcare — Source: dhs.state.il.us; actforchildren.org
- CCC Child Development Laboratory Schools — City Colleges of Chicago — CCC students/families
  — Subsidized — 5 CCC campuses — Childcare — Source: ccc.edu

Transportation:
- RTA Reduced-Fare / Transit Benefit Program — Regional Transportation Authority
  — Low-income; training participants — Reduced fare / pre-tax up to $300/month
  — Chicago region (Ventra card) — Transportation — Source: rtachicago.org; ventrachicago.com
- CCC WEI Program-Issued Transit Cards — City Colleges of Chicago (WEI programs)
  — WEI program participants — Free — At enrollment — Transportation
  — Source: pages.ccc.edu/wei (Sept 2025)

Financial aid / wraparound:
- One Million Degrees (OMD) — Chicago nonprofit — Low-income CCC students
  — Free (+ up to $1,000/yr performance stipend) — Expanding to Olive-Harvey (South Side) April 2026
  — Comprehensive (childcare navigation, transportation, academic coaching, financial, mental health)
  — Source: onemilliondegrees.org; colleges.ccc.edu; harris.uchicago.edu (April 2026)
- CCC WEI Stipends — City Colleges of Chicago — WEI program participants
  — Up to $500 per completion/employment milestone — CCC campuses
  — Financial (income support during training) — Source: pages.ccc.edu/wei (Sept 2025)
- WIOA Individual Training Accounts — Chicago Cook Workforce Partnership (LWIA 7)
  — Low-income, public-assistance recipients, basic-skills-deficient
  — Covers approved training costs — ~10 American Job Centers; Mid-South: 4314 S. Cottage Grove
  — Training cost / wraparound — Source: chicookworks.org; dol.gov (current)
- CCC Financial Aid Offices / Future Ready CCC / Fresh Start — City Colleges of Chicago
  — CCC students with financial need / prior debt — Free / last-dollar scholarship
  — All CCC campuses — Financial — Source: pages.ccc.edu (current)

Food security:
- CCC Wellness Centers + Greater Chicago Food Depository Partnership — City Colleges / GCFD
  — CCC students — Free — All CCC campuses — Food security / mental health
  — Source: ccc.edu; WBEZ/Sun-Times/Chalkbeat (April 2026)

**Relevant Context**
- Placement: after `CREDENTIAL_DATA`, before `compute_qoi()` (line ~204)
- Narrative sources (for cross-reference only, not to be changed):
  - "Sustainability Model" page: lines 4757–4826
  - "Partnership Opportunities" page: lines 2988–3090
- Research report vulnerability section: full structured support data confirmed present

---

### Sub-Task 4: Intake Form UI

**Status:** [x] done

**Intent**
Build the resident-facing intake form as a Streamlit UI rendered when the advisor
page is first loaded (sub-step 0 of session state). The form must be short (civic
tool, not job platform), accessible, and aligned with the matching fields the logic
needs. All form state lives in `st.session_state` under namespaced keys.

**Expected Outcomes**
- A new `"Pathway Advisor"` entry added to `all_pages_mobile` (the selectbox list).
- When the user navigates to "Pathway Advisor" and no intake has been submitted, the
  intake form is displayed.
- On submit, intake values are written to `st.session_state` and the advisor
  advances to the recommendation step (Sub-Task 5's renderer).
- A "Start over" button clears the session state keys and returns to the intake form.
- No Streamlit rendering calls appear outside the `if sub_choice == "Pathway Advisor":` block.

**Intake fields (minimum per spec.md)**

| Field | Widget | Options |
|---|---|---|
| Education level | `st.selectbox` | "Less than high school diploma", "High school diploma or GED", "Some college (no degree)", "Associate's degree", "Bachelor's degree", "Graduate degree (Master's or higher)" |
| Relevant experience | `st.selectbox` | "No technical experience", "Adjacent trades or hands-on technical work", "Computer / IT / software experience", "Science or engineering background" |
| Employment status | `st.selectbox` | "Currently unemployed", "Employed part-time", "Employed full-time (looking to transition)" |
| Pathway interests | `st.multiselect` | "Quantum hardware (devices, lab work)", "HPC systems / infrastructure", "Software, data, and programming", "Technician-level roles (hands-on)", "Community education and outreach" |
| Time availability | `st.radio` | "Full-time upskilling (10+ hrs/week)", "Part-time (under 10 hrs/week)" |
| Transportation | `st.radio` | "I have reliable transportation", "Transportation is a barrier for me" |
| Childcare | `st.radio` | "Childcare is not a barrier", "Childcare is a barrier for me" |

**Session state keys**
- `advisor_education`, `advisor_experience`, `advisor_employment`
- `advisor_interests` (list)
- `advisor_time`, `advisor_transportation`, `advisor_childcare`
- `advisor_submitted` (bool) — controls intake vs. results display

**Relevant Context**
- Navigation list: `all_pages_mobile`, lines 306–340 in `quantum_opportunity_dashboard.py`
- Page dispatch: `if sub_choice == "Pathway Advisor":` block (new, to be added after
  the last existing `if sub_choice == "..."` block before the footer at line ~5368)
- Helper functions available: `section_header()` (line 239), `callout()` (line 248)
- Color constants: `NAVY`, `TEAL`, `GOLD`, `LGRAY`, `MGRAY` (lines ~108–115)
- `st.session_state` is not currently used anywhere in the file — this is the
  first use. No conflicts expected.

---

### Sub-Task 5: Matching Logic (Pure Functions)

**Status:** [ ] pending

**Intent**
Write the core advisor logic as pure Python functions with no Streamlit calls.
These functions receive the intake dict and the top-level data constants; they
return structured recommendation and support-flag objects. Because they are pure,
they can be unit-tested without a running Streamlit server.

All recommendations must cite the data source that drove them (hard requirement
from spec.md): "recommended because of X employer demand signal from CQE/BCG"
not "based on your profile."

**Expected Outcomes**
- A block of pure functions defined in the top-level function area of the file
  (after the helper rendering functions `metric_row`, `section_header`, `callout`,
  `cta_box` but before the navigation/page dispatch code).
- Functions contain zero `st.*` calls.
- A test harness (simple `assert`-based inline or a separate `test_matching.py`
  file) verifies at least the main matching logic paths.
- Given a representative intake dict, `match_pathways()` returns a list of dicts
  each containing `rank`, `pathway_name`, `description`, `on_ramp`, `why_it_fits`,
  `source_citation`, and `confidence`.

**Functions to write**

`score_opportunity(intake, employer_data, credential_data, skills_data) → list[dict]`
- Maps `intake["interests"]` to `pathway_tags` in `EMPLOYER_DATA` and `CREDENTIAL_DATA`.
- Maps `intake["education"]` and `intake["experience"]` to `credential_min` /
  `prerequisite` fields to filter accessible pathways.
- Maps `intake["time"]` to `duration` category (full-time vs. short-term / self-paced).
- Returns scored pathway candidates with source citations from the matching records.
- Uses the Opportunity axis (CQE/BCG demand signals, ISTC completion data) for
  citation text.

`score_vulnerability(intake) → list[dict]`
- Checks `intake["transportation"]`, `intake["childcare"]`, `intake["employment"]`
  against `SUPPORT_RESOURCES["barrier_addressed"]` categories.
- Returns the list of relevant support-resource records to surface in the output.

`assess_confidence(intake, pathway_candidates) → str`
- Returns one of: `"high"`, `"moderate"`, or `"low"`.
- "low" if: `intake["interests"]` is empty, or all matched pathways require a degree
  the resident does not yet have with no accessible on-ramp, or no `CREDENTIAL_DATA`
  records match both the interest tags and the prerequisite.
- "moderate" if: at least one accessible credential matches but the employer demand
  data for that specific tag is indirect (e.g. BCG 2035 projection, not contractual).
- "high" if: at least one match is to a currently-active, South-Side-accessible
  program (e.g. CCC–IBM Apprenticeship, Project Evolve) AND employer demand is
  contractually backed (IQMP incentive agreements).
- Confidence text must explain the rating in one sentence (for display).

`match_pathways(intake, employer_data, credential_data, skills_data, support_resources) → dict`
- Orchestrator: calls the three functions above.
- Returns `{"pathways": [...], "support_flags": [...], "confidence": str, "confidence_note": str}`.
- `pathways` is sorted by score descending, capped at 3.
- If zero pathways match, `pathways` is empty and `confidence` is `"low"` with an
  explanatory note — the advisor says so explicitly rather than forcing a result.

**Matching rules (Opportunity axis, derived from existing framework)**

Interest → pathway_tags mapping:
- "Quantum hardware" → tags: `hardware`, `quantum`
- "HPC systems / infrastructure" → tags: `hpc`, `software`
- "Software, data, and programming" → tags: `software`, `data`
- "Technician-level roles" → tags: `technician`
- "Community education and outreach" → tags: `outreach` (SKILLS_DATA category:
  "Public Facing & Business")

Education filter:
- "Less than HS diploma" → only match `prerequisite: "None"` or `"18+ adult learner"`
- "HS diploma / GED" → match above + `prerequisite: "Open admission"` + `"High school enrollment"`
- "Some college" / "Associate's" → match all above + `prerequisite: "Community college enrollment"`
- "Bachelor's" / "Graduate" → all credentials accessible

Time filter:
- "Full-time" → all duration categories
- "Part-time" → only `duration` in: "Self-paced", "Short-term", "Short certificate"
  (excludes year-long apprenticeships)

**Source citation format** (must appear in every pathway record's `source_citation`)
Format: `"[Program name] ([Provider], [source URL], [date])"` — matching the
existing methodology page citation style.

**Relevant Context**
- Placement: after `cta_box()` (line ~262), before navigation (line ~306)
- Data constants available after Sub-Tasks 1–3: `SKILLS_DATA`, `EMPLOYER_DATA`,
  `CREDENTIAL_DATA`, `SUPPORT_RESOURCES`
- Existing scoring function for style reference: `compute_qoi()` (lines 204–216)
- Spec.md hard requirements: citations mandatory; no invented data; confidence note
  required; advisor says it's directional when data doesn't support specifics

---

### Sub-Task 6: Ranked Output Renderer

**Status:** [ ] pending

**Intent**
Build the Streamlit UI that displays the output of `match_pathways()` when
`st.session_state["advisor_submitted"]` is `True`. The renderer calls the pure
matching functions, then formats the results using the existing helper functions
(`section_header`, `callout`, `metric_row`) and the established color palette and
HTML-card styling patterns already used throughout the dashboard.

**Expected Outcomes**
- When "Pathway Advisor" is selected and `advisor_submitted` is `True`, the
  recommendation results are displayed instead of the intake form.
- Each of the 1–3 recommended pathways is shown as a card with:
  - Rank badge (1st / 2nd / 3rd)
  - Pathway name (plain language)
  - Specific on-ramp (named program/employer from `CREDENTIAL_DATA` / `EMPLOYER_DATA`)
  - Why it fits (1–2 sentences, plain language)
  - Source citation (from `source_citation` field — displayed visibly, not hidden)
- Support resource flags (from `score_vulnerability`) are shown in a separate
  section below pathways, with name, provider, contact/location, and source.
- A confidence/data coverage note (from `assess_confidence`) is shown prominently —
  either as a `callout()` box or a styled inline note. If confidence is "low",
  the note explains what data is missing rather than showing a forced recommendation.
- A "Start over" button clears `st.session_state` advisor keys and re-renders
  the intake form.
- All rendering code is inside `if sub_choice == "Pathway Advisor":` — no global
  side effects.

**Card styling pattern**
Follow the existing HTML card pattern used in "Participant Deliverables" (lines ~3368–3415)
and "Partnership Opportunities" (lines 2988–3090):
- Colored top border or left border based on rank (TEAL for rank 1, NAVY for rank 2,
  GOLD for rank 3)
- White background, `border-radius:8px`, `padding:16px`
- Source citation rendered in a smaller, muted font (`MGRAY`, `font-size:0.78rem`)
  below the main card content — mimicking the existing callout/methodology note style
- Support flags in GREEN-bordered cards, matching the existing insight-box pattern

**Relevant Context**
- Page block location: same `if sub_choice == "Pathway Advisor":` block as Sub-Task 4
- Helper functions: `section_header()` line 239, `callout()` line 248, `metric_row()` line 225
- Card pattern reference: "Participant Deliverables" lines 3368–3415
- Color constants: `NAVY` (#1B3A6B), `TEAL` (#1A7A6E), `GOLD` (#B07D2A),
  `GREEN`, `LGRAY`, `MGRAY`
- The renderer calls `match_pathways(st.session_state, EMPLOYER_DATA, CREDENTIAL_DATA,
  SKILLS_DATA, SUPPORT_RESOURCES)` — it does not contain matching logic itself

---

## Cross-Cutting Notes for Implementation

**Order dependency:** Sub-Tasks 1, 2, and 3 must be complete before Sub-Task 5
(matching logic references all four constants). Sub-Task 5 must be complete before
Sub-Task 6 (renderer calls `match_pathways()`). Sub-Task 4 can be built in parallel
with 1–3 since it only needs to know the session state key names.

**File:** All changes are in `quantum_opportunity_dashboard.py` only. No new files
are required except an optional `test_matching.py` for the pure-function unit tests.

**Adding "Pathway Advisor" to navigation:** In Sub-Task 4, append `"Pathway Advisor"`
to `all_pages_mobile` (lines 306–340). Place it near the top of the list for
discoverability — suggestion: second entry after "Why Now?".

**Avoiding regression:** The existing 33 pages share no state and are fully
conditional on `sub_choice`. Adding a new `elif sub_choice == "Pathway Advisor":`
block cannot affect existing page rendering. The only shared mutation is the
`all_pages_mobile` list insertion and the new top-level constants, neither of which
touches existing page blocks.

**Citation standard:** Every `source` field in `EMPLOYER_DATA`, `CREDENTIAL_DATA`,
and `SUPPORT_RESOURCES` must use the format already established in the app's
"Methodology and Data Sources" page (lines 4025–4190) and in the research report:
`"[Name], [URL] ([status, date])"`  — e.g.,
`"CCC newsroom, colleges.ccc.edu (primary, April 2026)"`.

**Confidence note non-goal:** The confidence note is not a disclaimer to protect
the tool's credibility — it is a transparency feature for the resident. Write it
in plain language: "This recommendation is based on program availability data from
early 2026. If you're applying after 2027, verify program status directly."
