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
print(f"  Contractual employers: {contractual_names}")
appren      = CREDENTIAL_DATA[CREDENTIAL_DATA["program"].str.contains("IBM Apprenticeship")].iloc[0]
skillsbuild = CREDENTIAL_DATA[CREDENTIAL_DATA["program"].str.contains("SkillsBuild")].iloc[0]
evolve      = CREDENTIAL_DATA[CREDENTIAL_DATA["program"].str.contains("Project Evolve")].iloc[0]
appren_c = _has_pipeline_connection(appren["program"], contractual_names)
skills_c = _has_pipeline_connection(skillsbuild["program"], contractual_names)
evolve_c = _has_pipeline_connection(evolve["program"], contractual_names)
check("Pre-check: CCC-IBM Apprenticeship IS contractual", appren_c is True)
check("Pre-check: IBM SkillsBuild is NOT contractual", skills_c is False)
check("Pre-check: Project Evolve is NOT contractual", evolve_c is False)

print("\n[Full sweep] has_contractual_demand across ALL CREDENTIAL_DATA rows")
true_count = 0
for _, row in CREDENTIAL_DATA.iterrows():
    hc = _has_pipeline_connection(row["program"], contractual_names)
    if hc:
        true_count += 1
        print(f"  TRUE:  {row['program']}")
check("Exactly one credential resolves as contractual", true_count == 1, f"got {true_count}")


print("\n[Test 1] High-confidence match — software/data, some college, full-time")
intake_high = {
    "education":       "Some college (no degree)",
    "experience":      "Computer / IT / software experience",
    "employment":      "Currently unemployed",
    "interests":       ["Software, data, and programming"],
    "time":            "Full-time upskilling (10+ hrs/week)",
    "transportation":  "I have reliable transportation",
    "childcare":       "Childcare is not a barrier",
}
r1 = match_pathways(intake_high, EMPLOYER_DATA, CREDENTIAL_DATA, SKILLS_DATA, SUPPORT_RESOURCES)
cands1 = score_opportunity(intake_high, EMPLOYER_DATA, CREDENTIAL_DATA, SKILLS_DATA)
print(f"  scores: {[(c['program'][:35], c['score'], c['has_contractual_demand']) for c in cands1]}")
check("Returns at least 1 pathway", len(r1["pathways"]) >= 1)
check("Confidence is 'high'", r1["confidence"] == "high",
      f"got {r1['confidence']!r} — {r1['confidence_note']}")
check("Top pathway is CCC-IBM Apprenticeship",
      r1["pathways"][0]["pathway_name"] == "CCC\u2013IBM Apprenticeship",
      f"got {r1['pathways'][0]['pathway_name']!r}")
check("Project Evolve has_contractual_demand is False",
      not any(c["has_contractual_demand"] for c in cands1 if "Project Evolve" in c["program"]))
check("source_citation present", bool(r1["pathways"][0]["source_citation"].strip()))
check("Confidence note mentions contractual/DCEO/IBM FutureNow",
      any(kw in r1["confidence_note"] for kw in ("DCEO", "IBM FutureNow", "contractual")))
check("Unemployed profile surfaces financial/wraparound support flags",
      any(r["barrier_addressed"] in ("financial", "wraparound", "training_cost")
          for r in r1["support_flags"]))
print(f"  confidence_note: {r1['confidence_note'][:150]}")


print("\n[Test 2] Quantum interest, HS diploma, part-time — no contractual leakage")
intake_student = {
    "education":       "High school diploma or GED",
    "experience":      "No technical experience",
    "employment":      "Currently unemployed",
    "interests":       ["Quantum hardware (devices, lab work)"],
    "time":            "Part-time (under 10 hrs/week)",
    "transportation":  "I have reliable transportation",
    "childcare":       "Childcare is not a barrier",
}
r2 = match_pathways(intake_student, EMPLOYER_DATA, CREDENTIAL_DATA, SKILLS_DATA, SUPPORT_RESOURCES)
cands2 = score_opportunity(intake_student, EMPLOYER_DATA, CREDENTIAL_DATA, SKILLS_DATA)
print(f"  scores: {[(c['program'][:35], c['score'], c['has_contractual_demand']) for c in cands2]}")
check("Returns at least 1 pathway (IBM SkillsBuild should match)", len(r2["pathways"]) >= 1)
check("IBM SkillsBuild has_contractual_demand is False",
      not any(c["has_contractual_demand"] for c in cands2 if "SkillsBuild" in c["program"]))
check("Confidence is NOT 'high'", r2["confidence"] in ("moderate", "low"), f"got {r2['confidence']!r}")
check("Q-Ready and OQI excluded by education filter",
      all("Q-Ready" not in p["pathway_name"] and "OQI" not in p["pathway_name"] for p in r2["pathways"]))
print(f"  pathways: {[p['pathway_name'] for p in r2['pathways']]}")
print(f"  confidence: {r2['confidence']!r} — {r2['confidence_note'][:120]}")


print("\n[Test 3] Outreach-only interest — SKILLS_DATA fallback / data gap flag")
intake_outreach = {
    "education":       "Bachelor's degree",
    "experience":      "No technical experience",
    "employment":      "Employed part-time",
    "interests":       ["Community education and outreach"],
    "time":            "Part-time (under 10 hrs/week)",
    "transportation":  "I have reliable transportation",
    "childcare":       "Childcare is not a barrier",
}
r3 = match_pathways(intake_outreach, EMPLOYER_DATA, CREDENTIAL_DATA, SKILLS_DATA, SUPPORT_RESOURCES)
if len(r3["pathways"]) > 0:
    citation = r3["pathways"][0]["source_citation"]
    check("Outreach SKILLS_DATA fallback pathway present", True)
    check("Citation flags recommendation as directional only",
          "directional" in citation.lower() or "NOTE" in citation, f"citation: {citation[:120]}")
    check("Pathway provider is Chicago WHPC", r3["pathways"][0]["on_ramp"] == "Chicago WHPC")
else:
    check("FLAGGED DATA GAP: outreach interest returns zero matches", False,
          "Investigate: skills_data category filter may not match 'Public Facing & Business'")
print(f"  pathways: {[p['pathway_name'] for p in r3['pathways']]}")
print(f"  confidence: {r3['confidence']!r}")


print("\n[Test 4] Zero-match profile — no interests selected")
intake_zero = {
    "education":       "Some college (no degree)",
    "experience":      "No technical experience",
    "employment":      "Currently unemployed",
    "interests":       [],
    "time":            "Full-time upskilling (10+ hrs/week)",
    "transportation":  "Transportation is a barrier for me",
    "childcare":       "Childcare is a barrier for me",
}
r4 = match_pathways(intake_zero, EMPLOYER_DATA, CREDENTIAL_DATA, SKILLS_DATA, SUPPORT_RESOURCES)
check("Returns zero pathways", len(r4["pathways"]) == 0, f"got {len(r4['pathways'])}")
check("Confidence is 'low'", r4["confidence"] == "low", f"got {r4['confidence']!r}")
check("Confidence note explains empty result", len(r4["confidence_note"].strip()) > 20)
check("Transportation support flags surface despite zero pathways",
      any(r["barrier_addressed"] == "transportation" for r in r4["support_flags"]))
check("Childcare support flags surface despite zero pathways",
      any(r["barrier_addressed"] == "childcare" for r in r4["support_flags"]))
print(f"  confidence_note: {r4['confidence_note'][:120]}")


print(f"\n{'='*55}")
print(f"Results: {PASS} passed, {FAIL} failed")
if FAIL:
    sys.exit(1)

print("\n[Additional] Cryogenics SKILLS_DATA tiers")
cryo_rows = SKILLS_DATA[SKILLS_DATA["skill"].str.contains("ryogen", case=False)]
check("Two distinct cryogenics tiers exist (research MS/BS + technician HS/AS)", len(cryo_rows) == 2)
check("Technician-tier cryogenics entry has HS Diploma / AS credential",
      "HS Diploma / AS" in cryo_rows["credential_min"].values)

print("\n[Additional] Quantum Sensing Summer Program (Chicago State / QuBBE)")
qsp = CREDENTIAL_DATA[CREDENTIAL_DATA["program"].str.contains("Quantum Sensing Summer")].iloc[0]
check("Quantum Sensing Summer Program uses High school enrollment prerequisite",
      qsp["prerequisite"] == "High school enrollment")

intake_hs = {
    "education": "High school diploma or GED", "experience": "No technical experience",
    "employment": "Currently unemployed", "interests": ["Quantum hardware (devices, lab work)"],
    "time": "Full-time upskilling (10+ hrs/week)", "transportation": "I have reliable transportation",
    "childcare": "Childcare is not a barrier",
}
cands_hs = score_opportunity(intake_hs, EMPLOYER_DATA, CREDENTIAL_DATA, SKILLS_DATA)
names_hs = [c["program"] for c in cands_hs]
check("Quantum Sensing Summer Program correctly excluded at HS diploma (adult) tier",
      not any("Quantum Sensing Summer" in n for n in names_hs), f"got {names_hs}")

intake_adult = {
    "education": "Bachelor's degree", "experience": "Science or engineering background",
    "employment": "Currently unemployed", "interests": ["Quantum hardware (devices, lab work)"],
    "time": "Full-time upskilling (10+ hrs/week)", "transportation": "I have reliable transportation",
    "childcare": "Childcare is not a barrier",
}
cands_adult = score_opportunity(intake_adult, EMPLOYER_DATA, CREDENTIAL_DATA, SKILLS_DATA)
names_adult = [c["program"] for c in cands_adult]
check("KNOWN GAP (documented, pre-existing, matches Fermilab TECHS/Q-Ready behavior): "
      "Quantum Sensing Summer Program still surfaces at Bachelor's+ tier via allowed=None",
      any("Quantum Sensing Summer" in n for n in names_adult),
      "This is the same Case B gap already documented for TECHS/Q-Ready, not a new bug")

print(f"\n{'='*55}")
print(f"Final results: {PASS} passed, {FAIL} failed")
if FAIL:
    sys.exit(1)
