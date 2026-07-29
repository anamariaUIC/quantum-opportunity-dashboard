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
appren_c = _has_pipeline_connection(appren["program"], contractual_names)
skills_c = _has_pipeline_connection(skillsbuild["program"], contractual_names)
evolve_c = _has_pipeline_connection(evolve["program"], contractual_names)
check("Pre-check: CCC-IBM Apprenticeship IS contractual", appren_c is True)
check("Pre-check: IBM SkillsBuild is NOT contractual", skills_c is False)
check("Pre-check: Project Evolve is NOT contractual", evolve_c is False)

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
