"""
test_matching.py — Unit tests for advisor matching logic.
Run standalone: python test_matching.py
No external dependencies beyond pandas (already in requirements.txt).
"""
import sys, pandas as pd

_src = open("quantum_opportunity_dashboard.py").read()
_cutoff = _src.index("\n# ── SIDEBAR NAVIGATION")
exec(compile("import pandas as pd\n" + _src[:_cutoff], "<dashboard>", "exec"), globals())

PASS = 0
FAIL = 0

def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        print(f"  PASS  {label}")
        PASS += 1
    else:
        print(f"  FAIL  {label}" + (f": {detail}" if detail else ""))
        FAIL += 1

print("[Pre-check] Allowlist pipeline resolution")
contractual_names = EMPLOYER_DATA.loc[
    EMPLOYER_DATA["jobs_committed"].apply(_is_contractual_employer), "employer"
].tolist()
appren      = CREDENTIAL_DATA[CREDENTIAL_DATA["program"].str.contains("IBM Apprenticeship")].iloc[0]
skillsbuild = CREDENTIAL_DATA[CREDENTIAL_DATA["program"].str.contains("SkillsBuild")].iloc[0]
evolve      = CREDENTIAL_DATA[CREDENTIAL_DATA["program"].str.contains("Project Evolve")].iloc[0]
perscholas  = CREDENTIAL_DATA[CREDENTIAL_DATA["program"].str.contains("Per Scholas")].iloc[0]
appren_c = _has_pipeline_connection(appren["program"], contractual_names)
skills_c = _has_pipeline_connection(skillsbuild["program"], contractual_names)
evolve_c = _has_pipeline_connection(evolve["program"], contractual_names)
perscholas_c = _has_pipeline_connection(perscholas["program"], contractual_names)
check("Pre-check: CCC-IBM Apprenticeship IS contractual", appren_c is True)
check("Pre-check: IBM SkillsBuild is NOT contractual", skills_c is False)
check("Pre-check: Project Evolve is NOT contractual", evolve_c is False)
check("Pre-check: Per Scholas is NOT contractual (not in employer-demand data)", perscholas_c is False)
check("Per Scholas is NOT tagged quantum", "quantum" not in perscholas["pathway_tags"])
check("Per Scholas IS tagged technician", "technician" in perscholas["pathway_tags"])
check("Per Scholas IS tagged software", "software" in perscholas["pathway_tags"])
check("Per Scholas is South Side accessible", perscholas["south_side_accessible"] == True)

true_count = 0
for _, row in CREDENTIAL_DATA.iterrows():
    hc = _has_pipeline_connection(row["program"], contractual_names)
    if hc:
        true_count += 1
check("Exactly one credential resolves as contractual", true_count == 1, f"got {true_count}")

intake_high = {
    "education": "Some college (no degree)", "experience": "Computer / IT / software experience",
    "employment": "Currently unemployed", "interests": ["Software, data, and programming"],
    "time": "Full-time upskilling (10+ hrs/week)", "transportation": "I have reliable transportation",
    "childcare": "Childcare is not a barrier",
}
r1 = match_pathways(intake_high, EMPLOYER_DATA, CREDENTIAL_DATA, SKILLS_DATA, SUPPORT_RESOURCES)
check("Returns at least 1 pathway", len(r1["pathways"]) >= 1)
check("Confidence is 'high'", r1["confidence"] == "high")
check("Top pathway is CCC-IBM Apprenticeship",
      r1["pathways"][0]["pathway_name"] == "CCC\u2013IBM Apprenticeship")

intake_technician = {
    "education": "Some college (no degree)", "experience": "No technical experience",
    "employment": "Currently unemployed", "interests": ["Technician-level roles (hands-on)"],
    "time": "Full-time upskilling (10+ hrs/week)", "transportation": "I have reliable transportation",
    "childcare": "Childcare is not a barrier",
}
r_tech = match_pathways(intake_technician, EMPLOYER_DATA, CREDENTIAL_DATA, SKILLS_DATA, SUPPORT_RESOURCES)
tech_names = [p["pathway_name"] for p in r_tech["pathways"]]
check("Per Scholas appears in technician-interest results",
      any("Per Scholas" in n for n in tech_names), f"got {tech_names}")

intake_zero = {
    "education": "Some college (no degree)", "experience": "No technical experience",
    "employment": "Currently unemployed", "interests": [],
    "time": "Full-time upskilling (10+ hrs/week)",
    "transportation": "Transportation is a barrier for me",
    "childcare": "Childcare is a barrier for me",
}
r4 = match_pathways(intake_zero, EMPLOYER_DATA, CREDENTIAL_DATA, SKILLS_DATA, SUPPORT_RESOURCES)
check("Zero-interest profile returns zero pathways", len(r4["pathways"]) == 0)
check("Zero-interest confidence is 'low'", r4["confidence"] == "low")

print(f"\n{'='*55}")
print(f"Results: {PASS} passed, {FAIL} failed")
if FAIL:
    sys.exit(1)

print("\n[Additional] CCC-IBM Apprenticeship prerequisite resolution (IQMP confirmation)")
intake_no_hs = {
    "education": "Less than high school diploma", "experience": "Computer / IT / software experience",
    "employment": "Currently unemployed", "interests": ["Software, data, and programming"],
    "time": "Full-time upskilling (10+ hrs/week)", "transportation": "I have reliable transportation",
    "childcare": "Childcare is not a barrier",
}
cands_no_hs = score_opportunity(intake_no_hs, EMPLOYER_DATA, CREDENTIAL_DATA, SKILLS_DATA)
names_no_hs = [c["program"] for c in cands_no_hs]
check("CCC-IBM Apprenticeship excluded for 'Less than high school diploma'",
      "CCC\u2013IBM Apprenticeship" not in names_no_hs, f"got {names_no_hs}")

intake_hs = dict(intake_no_hs, education="High school diploma or GED")
cands_hs = score_opportunity(intake_hs, EMPLOYER_DATA, CREDENTIAL_DATA, SKILLS_DATA)
names_hs = [c["program"] for c in cands_hs]
check("CCC-IBM Apprenticeship included for 'High school diploma or GED'",
      "CCC\u2013IBM Apprenticeship" in names_hs, f"got {names_hs}")

appren_row = [c for c in cands_hs if c["program"] == "CCC\u2013IBM Apprenticeship"]
check("CCC-IBM Apprenticeship unspecified_prereq is now False",
      len(appren_row) == 1 and appren_row[0]["unspecified_prereq"] is False)

print("\n[Additional] CQuEST (Chicago State University) entry")
cquest = CREDENTIAL_DATA[CREDENTIAL_DATA["program"].str.contains("CQuEST")].iloc[0]
check("CQuEST is tagged quantum", "quantum" in cquest["pathway_tags"])
check("CQuEST is South Side accessible", cquest["south_side_accessible"] == True)
intake_quantum = {
    "education": "Bachelor's degree", "experience": "Science or engineering background",
    "employment": "Currently unemployed", "interests": ["Quantum hardware (devices, lab work)"],
    "time": "Full-time upskilling (10+ hrs/week)", "transportation": "I have reliable transportation",
    "childcare": "Childcare is not a barrier",
}
cands_q = score_opportunity(intake_quantum, EMPLOYER_DATA, CREDENTIAL_DATA, SKILLS_DATA)
names_q = [c["program"] for c in cands_q]
check("CQuEST appears for quantum hardware interest",
      any("CQuEST" in n for n in names_q), f"got {names_q}")

print(f"\n{'='*55}")
print(f"Final results: {PASS} passed, {FAIL} failed")
if FAIL:
    sys.exit(1)
