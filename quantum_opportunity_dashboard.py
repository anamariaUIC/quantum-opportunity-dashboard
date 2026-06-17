"""
Quantum × HPC Pathways: South Side Opportunity Dashboard
Chicago Women in High Performance Computing (Chicago WHPC)
Ana Marija Sokovic, PhD, MBA - Lead Computational Scientist, Research Computing

Research dashboard supporting the Quantum x HPC Pathways civic action plan (https://drive.google.com/file/d/159AwW3Hso4aAdoUL485qzhfV81VM0IeJ/view?usp=drive_link).
Data sources: ACS 2023, CPS/To&Through 2024, ISTC 2026, BCG/CQE 2024, IBM 2026.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from io import BytesIO

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quantum × HPC Pathways | South Side Opportunity Dashboard",
    page_icon="️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── COLORS ───────────────────────────────────────────────────────────────────
NAVY = "#1B3A6B"
TEAL = "#1A7A6E"
GOLD = "#B07D2A"
LGRAY = "#F5F6F8"
MGRAY = "#555555"
RED = "#C0392B"
GREEN = "#27AE60"
LIGHT_TEAL = "#E8F4F3"
LIGHT_NAVY = "#EEF2F8"

# ─── EMBEDDED DATA ────────────────────────────────────────────────────────────

# South Side community areas - ACS 2023 educational attainment + demographics
# Source: U.S. Census Bureau, American Community Survey 5-Year Estimates 2019–2023
# All communities: study areas (South Side program targets) + comparison communities
# Comparison communities selected from other Chicago neighborhoods with different
# socioeconomic profiles to provide analytical contrast. Source: ACS 5-Year 2023.
ALL_COMMUNITIES = pd.DataFrame([
    # Study communities (South Side program targets)
    {"area": "South Shore",          "group": "Study Area", "ca": 43, "lat": 41.762, "lon": -87.568, "bach_pct": 24.9, "hs_pct": 87.2, "pop_25plus": 27400, "med_income": 42800,  "youth_pop": 4200, "college_enroll_pct": 48.1, "black_pct": 92, "transit_min_iqmp": 18},
    {"area": "South Chicago",        "group": "Study Area", "ca": 46, "lat": 41.740, "lon": -87.550, "bach_pct": 21.7, "hs_pct": 81.3, "pop_25plus": 20100, "med_income": 42456,  "youth_pop": 5100, "college_enroll_pct": 44.2, "black_pct": 70, "transit_min_iqmp": 12},
    {"area": "Woodlawn",             "group": "Study Area", "ca": 42, "lat": 41.773, "lon": -87.597, "bach_pct": 22.1, "hs_pct": 84.6, "pop_25plus": 19800, "med_income": 35200,  "youth_pop": 3900, "college_enroll_pct": 46.3, "black_pct": 86, "transit_min_iqmp": 25},
    {"area": "Calumet Heights",      "group": "Study Area", "ca": 48, "lat": 41.726, "lon": -87.573, "bach_pct": 28.4, "hs_pct": 91.2, "pop_25plus": 11200, "med_income": 54300,  "youth_pop": 2100, "college_enroll_pct": 52.4, "black_pct": 97, "transit_min_iqmp": 15},
    {"area": "Greater Grand Crossing","group": "Study Area", "ca": 69, "lat": 41.762, "lon": -87.609, "bach_pct": 17.8, "hs_pct": 82.1, "pop_25plus": 22600, "med_income": 32100,  "youth_pop": 5800, "college_enroll_pct": 41.8, "black_pct": 97, "transit_min_iqmp": 30},
    {"area": "Roseland",             "group": "Study Area", "ca": 49, "lat": 41.694, "lon": -87.620, "bach_pct": 16.2, "hs_pct": 80.4, "pop_25plus": 33400, "med_income": 38900,  "youth_pop": 7200, "college_enroll_pct": 39.6, "black_pct": 98, "transit_min_iqmp": 22},
    {"area": "Pullman",              "group": "Study Area", "ca": 50, "lat": 41.699, "lon": -87.609, "bach_pct": 14.8, "hs_pct": 79.3, "pop_25plus": 8100,  "med_income": 36700,  "youth_pop": 1900, "college_enroll_pct": 38.2, "black_pct": 96, "transit_min_iqmp": 20},
    {"area": "Auburn Gresham",       "group": "Study Area", "ca": 71, "lat": 41.745, "lon": -87.651, "bach_pct": 15.6, "hs_pct": 82.8, "pop_25plus": 35200, "med_income": 34500,  "youth_pop": 7400, "college_enroll_pct": 40.1, "black_pct": 98, "transit_min_iqmp": 38},
    {"area": "Chatham",              "group": "Study Area", "ca": 44, "lat": 41.744, "lon": -87.625, "bach_pct": 22.8, "hs_pct": 88.4, "pop_25plus": 25600, "med_income": 45200,  "youth_pop": 4800, "college_enroll_pct": 49.3, "black_pct": 98, "transit_min_iqmp": 32},
    {"area": "Englewood",            "group": "Study Area", "ca": 68, "lat": 41.779, "lon": -87.644, "bach_pct": 11.3, "hs_pct": 74.2, "pop_25plus": 20800, "med_income": 24100,  "youth_pop": 6100, "college_enroll_pct": 35.7, "black_pct": 97, "transit_min_iqmp": 35},
    # Comparison communities (other Chicago neighborhoods for analytical contrast)
    {"area": "Hyde Park (comp.)",    "group": "Comparison", "ca": 41, "lat": 41.795, "lon": -87.590, "bach_pct": 72.3, "hs_pct": 96.1, "pop_25plus": 19200, "med_income": 73400,  "youth_pop": 4100, "college_enroll_pct": 74.2, "black_pct": 30, "transit_min_iqmp": 22},
    {"area": "Bridgeport (comp.)",   "group": "Comparison", "ca": 60, "lat": 41.835, "lon": -87.640, "bach_pct": 31.4, "hs_pct": 84.6, "pop_25plus": 25800, "med_income": 52100,  "youth_pop": 4600, "college_enroll_pct": 51.3, "black_pct": 4,  "transit_min_iqmp": 40},
    {"area": "Albany Park (comp.)",  "group": "Comparison", "ca": 14, "lat": 41.973, "lon": -87.727, "bach_pct": 33.8, "hs_pct": 80.2, "pop_25plus": 37400, "med_income": 55200,  "youth_pop": 8100, "college_enroll_pct": 53.8, "black_pct": 4,  "transit_min_iqmp": 65},
    {"area": "Logan Square (comp.)", "group": "Comparison", "ca": 22, "lat": 41.921, "lon": -87.708, "bach_pct": 56.2, "hs_pct": 88.4, "pop_25plus": 48200, "med_income": 78600,  "youth_pop": 9200, "college_enroll_pct": 64.1, "black_pct": 5,  "transit_min_iqmp": 58},
])

SOUTH_SIDE_AREAS = ALL_COMMUNITIES[ALL_COMMUNITIES["group"] == "Study Area"].copy().reset_index(drop=True)

# Chicago citywide benchmark
CITYWIDE_BACH = 41.1
CITYWIDE_HS = 87.4
CITYWIDE_INCOME = 65100

# ISTC 2026 quantum workforce data
# Source: ISTC/CQE/IQMP/Illinois EDC, "Mapping Illinois' Quantum Talent Pipeline," May 2026
ISTC_CREDENTIALS = pd.DataFrame([
    {"credential": "Certificates (IT & Technical)", "completions_2024": 11891, "growth_pct": 1275, "note": "Fastest growing - from 18 awards in 2014 to 2,475 in IT alone"},
    {"credential": "Associate's Degrees", "completions_2024": 3240, "growth_pct": 42, "note": "Community college pathway"},
    {"credential": "Bachelor's Degrees", "completions_2024": 10842, "growth_pct": 28, "note": "Includes CS, Engineering, Data Science"},
    {"credential": "Master's Degrees", "completions_2024": 5814, "growth_pct": 31, "note": ""},
    {"credential": "Doctoral Degrees", "completions_2024": 1654, "growth_pct": 18, "note": ""},
])

ISTC_FIELDS = pd.DataFrame([
    {"field": "Computer & Information Sciences", "share_pct": 44, "completions": 14764, "growth_since_2014": 140},
    {"field": "Engineering", "share_pct": 24, "completions": 8026, "growth_since_2014": 22},
    {"field": "Engineering Technology", "share_pct": 12, "completions": 4013, "growth_since_2014": 29},
    {"field": "Physical Sciences", "share_pct": 8, "completions": 2675, "growth_since_2014": 15},
    {"field": "Mathematics & Statistics", "share_pct": 7, "completions": 2341, "growth_since_2014": 44},
    {"field": "Manufacturing & Production", "share_pct": 5, "completions": 1672, "growth_since_2014": 31},
])

# IBM/IQMP job announcement data
# Source: Capitol News Illinois, April 2026; IQMP newsroom
IQMP_JOBS = pd.DataFrame([
    {"category": "Cybersecurity", "jobs": 200, "credential_min": "Bachelor's or Certificate", "timeline": "2026–2028"},
    {"category": "AI & Data Science", "jobs": 250, "credential_min": "Bachelor's", "timeline": "2026–2028"},
    {"category": "Supercomputing Ops", "jobs": 150, "credential_min": "Associate's or Certificate","timeline": "2027–2029"},
    {"category": "Apprenticeships", "jobs": 500, "credential_min": "High School + Training", "timeline": "2026–2030"},
    {"category": "Quantum Research", "jobs": 150, "credential_min": "Master's or PhD", "timeline": "2028–2032"},
])

# Chicago WHPC survey data
# Source: Chicago WHPC Quantum Meets HPC event survey, 2026 (N=181)
WHPC_SURVEY = pd.DataFrame([
    {"question": "Never used a quantum computing tool", "pct": 56},
    {"question": "Want to understand quantum-HPC connection", "pct": 76},
    {"question": "Prefer virtual or hybrid learning format", "pct": 66},
    {"question": "Interested in HPC career pathways", "pct": 71},
    {"question": "No clear next step identified after the event", "pct": 62},
])

# Ecosystem asset map
ECOSYSTEM_ASSETS = pd.DataFrame([
    {"org": "IQMP", "type": "Infrastructure", "lat": 41.737, "lon": -87.545, "focus": "Quantum & microelectronics campus", "community_access": "None yet", "has_community_nav": False},
    {"org": "Chicago Quantum Exchange", "type": "Research Hub", "lat": 41.789, "lon": -87.600, "focus": "Ecosystem coordination, education", "community_access": "Limited", "has_community_nav": False},
    {"org": "Argonne National Lab", "type": "National Lab", "lat": 41.716, "lon": -87.979, "focus": "Quantum research, computing", "community_access": "Limited", "has_community_nav": False},
    {"org": "Fermilab", "type": "National Lab", "lat": 41.840, "lon": -88.258, "focus": "Quantum science, SMQ* program", "community_access": "Some", "has_community_nav": False},
    {"org": "Research University HPC Center", "type": "University", "lat": 41.870, "lon": -87.650, "focus": "HPC infrastructure, quantum training", "community_access": "Some", "has_community_nav": False},
    {"org": "Olive Harvey College", "type": "City College", "lat": 41.712, "lon": -87.591, "focus": "SMQ* host, IBM apprenticeship", "community_access": "Strong", "has_community_nav": False},
    {"org": "SMQ* (Fermilab)", "type": "Program", "lat": 41.712, "lon": -87.591, "focus": "10-week quantum program, 37 students", "community_access": "Strong", "has_community_nav": False},
    {"org": "DPI / Chi-Craft (CPS)", "type": "Program", "lat": 41.838, "lon": -87.627, "focus": "Teacher training, student awareness", "community_access": "Strong", "has_community_nav": False},
    {"org": "Chicago WHPC", "type": "Bridge Org", "lat": 41.762, "lon": -87.568, "focus": "Community nav, HPC workshops, mentorship","community_access": "Strong","has_community_nav": True},
])

# Community Readiness Profile - scored by community area
# Composite: bach_pct (neg weight), hs_pct, college_enroll_pct, youth_pop (normalized), transit_min_iqmp (neg weight)
def compute_qoi(df):
    df = df.copy()
    # Community Readiness Profile (CRP) components
    # Transit excluded from composite: our core argument is that institutional
    # disconnection - not physical distance - is the barrier. Transit is shown
    # separately in the Geographic Proximity tab.
    # Weight rationale documented in methodology section below.
    df["edu_gap"]     = (CITYWIDE_BACH - df["bach_pct"]).clip(0) / CITYWIDE_BACH * 45   # 45%: educational potential gap
    df["hs_strength"] = (df["hs_pct"] / 100) * 25                                        # 25%: existing HS graduation foundation
    df["college_str"] = (df["college_enroll_pct"] / 100) * 20                            # 20%: college-going culture
    df["youth_score"] = (df["youth_pop"] / df["youth_pop"].max()) * 10                   # 10%: population reach potential
    df["crp"] = (df["edu_gap"] + df["hs_strength"] + df["college_str"] + df["youth_score"]).round(1)
    return df

SOUTH_SIDE_AREAS = compute_qoi(SOUTH_SIDE_AREAS)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### Quantum x HPC Pathways")
    st.markdown("**Chicago WHPC**")
    st.markdown("---")
    st.markdown("**Navigate by audience:**")
    audience = st.radio("I am...", [
        "Overview",
        "Academia",
        "CPS / Educators",
        "IQMP / CQE / Labs",
        "Funders and Foundations",
        "Employers and Industry",
    ], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**About this dashboard**")
    st.caption(
        "Research supporting the Quantum x HPC Pathways <a href='https://drive.google.com/file/d/159AwW3Hso4aAdoUL485qzhfV81VM0IeJ/view?usp=drive_link' target='_blank'>civic action plan</a>. "
        "Data: ACS 2023, CPS To&Through 2024, ISTC 2026, BCG/CQE 2024, IBM 2026. "
        "Geography note: community area boundaries are used for planning purposes. "
        "Zip codes, CPS networks, and community areas do not align exactly."
    )
    st.markdown("---")
    st.markdown("[chicagowhpc.org](https://www.chicagowhpc.org)")
    st.markdown("[Mentorship Program](https://www.chicagowhpc.org/mentorship)")

# ─── HELPER: METRIC ROW ───────────────────────────────────────────────────────
def metric_row(items):
    cols = st.columns(len(items))
    for col, (label, value, delta, color) in zip(cols, items):
        with col:
            st.markdown(
                f"""<div style='background:{LGRAY};border-top:4px solid {color};
                border-radius:6px;padding:16px 12px;text-align:center;margin-bottom:8px'>
                <div style='font-size:2rem;font-weight:700;color:{color}'>{value}</div>
                <div style='font-size:0.78rem;color:{MGRAY};margin-top:4px'>{label}</div>
                {f'<div style="font-size:0.72rem;color:{MGRAY};margin-top:2px;font-style:italic">{delta}</div>' if delta else ''}
                </div>""",
                unsafe_allow_html=True
            )

def section_header(title, subtitle=""):
    sub_html = f'<p style="color:{MGRAY};margin:4px 0 0 0;font-size:0.9rem">{subtitle}</p>' if subtitle else ''
    st.markdown(
        f"<div style='border-left:5px solid {TEAL};padding:8px 16px;margin:24px 0 12px 0'>"
        f"<h2 style='color:{NAVY};margin:0;font-size:1.5rem'>{title}</h2>"
        f"{sub_html}</div>",
        unsafe_allow_html=True
    )

def callout(text, color=TEAL):
    st.markdown(
        f"""<div style='background:{color}18;border-left:4px solid {color};
        padding:12px 16px;border-radius:4px;margin:12px 0;color:{NAVY};font-size:0.95rem'>{text}</div>""",
        unsafe_allow_html=True
    )

def cta_box(audience_name, items, color=GOLD):
    rows = ''.join(f'<div style="margin:8px 0;color:{NAVY}">&#9744; {item}</div>' for item in items)
    st.markdown(
        f"<div style='background:{color}15;border:2px solid {color};border-radius:8px;padding:20px;margin-top:24px'>"
        f"<h3 style='color:{color};margin:0 0 12px 0'>What we need from {audience_name}</h3>"
        f"{rows}</div>",
        unsafe_allow_html=True
    )

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────

# PAGE TITLE
st.markdown(
    f"""<div style='background:linear-gradient(135deg,{NAVY},{TEAL});
    padding:32px 32px 24px 32px;border-radius:10px;margin-bottom:24px'>
    <h1 style='color:white;margin:0;font-size:2rem'>Quantum x HPC Pathways</h1>
    <p style='color:#B8D4E8;margin:8px 0 4px 0;font-size:1.1rem'>
    South Side Opportunity Dashboard</p>
    <p style='color:#8BB8CC;margin:0;font-size:0.85rem'>
    Chicago Women in High Performance Computing (Chicago WHPC) | Ana Marija Sokovic, PhD, MBA | 2026 Change Collective Fellow</p>
    </div>""",
    unsafe_allow_html=True
)

# ── TAB ROUTING ───────────────────────────────────────────────────────────────

# ── AUDIENCE-SPECIFIC PANEL (above tabs, always visible) ────────────────────
# Audience-specific landing (sidebar selection)
if audience != "Overview":
    st.markdown("---")
    section_header("Viewing as: " + audience)

    if audience == "Academia":
        st.markdown("""
        **Why this matters for academic partners:** Quantum × HPC Pathways directly advances three of the university's
        five strategic priorities - Build Strong Partnerships, Transform Educational Programs,
        and Accelerate Student Success. The initiative uses institutional HPC infrastructure
        and expertise to deliver community impact aligned with the university's civic mission as a
        public research university on Chicago's South Side.
        """)
        cta_box("Academic Partners", [
            "Name Chicago WHPC as a community partner in strategic planning documents",
            "Facilitate HPC resource access for community workshop participants through institutional computing infrastructure",
            "Connect the initiative to relevant departments for curriculum alignment and grant co-leadership",
            "Include Quantum × HPC Pathways as a case study for the Strategic Priorities Task Force",
            "Co-apply for NSF INCLUDES or EDA Tech Hub workforce grants",
        ], TEAL)

    elif audience == "CPS / Educators":
        st.markdown("""
        **Why this matters for CPS:** Your students are building quantum curiosity through
        Chi-Craft and DPI training. But curiosity without a next step fades. Quantum × HPC
        Pathways is the technical on-ramp that picks up where CPS computer science leaves off -
        connecting Network 17 students to HPC skills, mentorship, and careers at IQMP.
        """)
        cta_box("CPS", [
            "Introduce us to 2–3 Network 17 CS teachers who completed DPI quantum training",
            "Allow us to recruit Chi-Craft alumni for our beginner cohort",
            "Sign on as a community partner in grant applications (letter of support)",
            "Host one community education session at a Network 17 school",
            "Connect us to the principal network in South Shore and East Side",
        ], GREEN)

    elif audience == "IQMP / CQE / Labs":
        st.markdown("""
        **Why this matters for IQMP and CQE:** You are building the destination.
        We are building the on-ramp. Community trust, local talent awareness, and
        neighborhood participation metrics are all things your ecosystem needs -
        and very few organizations are currently collecting or generating them.
        """)
        cta_box("IQMP / CQE", [
            "Provide a guest speaker for one community education session (60 min, low prep)",
            "Host a facility tour for 10–15 workshop participants",
            "Share 2–3 entry-level role descriptions for the South Side Quantum Opportunity Guide",
            "Name Chicago WHPC in community benefits documentation",
            "Co-author a future workforce gap analysis using our community participation data",
        ], NAVY)

    elif audience == "Funders and Foundations":
        st.markdown("""
        **Why this matters for funders:** This initiative generates something that doesn't
        currently exist: one of the few community-level datasets tracking who actually participates in
        quantum workforce pipeline. Year 1 produces documented participants, progression
        metrics, a replicable toolkit, and 2–3 institutional partnerships - the evidence
        base for scaling.
        """)
        cta_box("Funders", [
            "Fund Year 1 pilot: $25K–$50K covers instructional coordination, stipends, curriculum, and evaluation",
            "Co-fund with institutional partners (NVIDIA, IBM education programs) reducing cash ask",
            "Consider multi-year commitment for toolkit development and replication in Year 2",
            "Require community-level equity reporting - we already track this",
            "Connect us to other grantees working on workforce equity in Illinois",
        ], GOLD)

    elif audience == "Employers and Industry":
        st.markdown("""
        **Why this matters for employers:** The South Side is full of technically capable
        young people who don't know your jobs exist or that they qualify. Our program
        builds that awareness - and gives you a structured, low-lift way to reach them
        before your competitors do.
        """)
        cta_box("Employers", [
            "Participate as a guest speaker in one community session (60 min)",
            "Provide one mentor for a semester-long match (Chicago WHPC coordinates everything)",
            "Share an internship information session with our 15–20 workshop participants",
            "Contribute one page of entry-level role descriptions to the Opportunity Guide",
            "Sponsor the workshop series ($5K–$15K, recognition at all sessions and in materials)",
        ], GOLD)

# ── GROUPED NAVIGATION ────────────────────────────────────────────────────────
st.markdown(
    f"<div style='background:{LGRAY};border-radius:8px;padding:10px 16px;margin-bottom:16px'>"
    f"<div style='font-size:0.78rem;font-weight:700;color:{MGRAY};text-transform:uppercase;"
    f"letter-spacing:1px;margin-bottom:8px'>Navigate by section</div>"
    f"</div>",
    unsafe_allow_html=True
)

nav_section = st.radio(
    "Section",
    ["Why This Matters", "The Ecosystem", "The Evidence", "The Plan", "Get Involved"],
    horizontal=True,
    label_visibility="collapsed"
)

# Sub-page within each section
sub_pages = {
    "Why This Matters": ["Workforce Bridge", "Why Chicago WHPC?"],
    "The Ecosystem":    ["Ecosystem Map", "Why HPC?"],
    "The Evidence":     ["Illinois Opportunity", "South Side Strengths and Assets",
                         "Geographic Proximity", "Community Profiles", "Community Readiness Profile"],
    "The Plan":         ["Pathway Ladder", "What Success Looks Like"],
    "Get Involved":     ["Community Impact Dashboard", "Partnership Opportunities"],
}

sub_choice = st.radio(
    "Page",
    sub_pages[nav_section],
    horizontal=True,
    label_visibility="collapsed"
)

# Map sub_choice to a numeric index for tab rendering
all_pages = [p for pages in sub_pages.values() for p in pages]
page_idx = all_pages.index(sub_choice)

# Use a single set of "tabs" but render only the selected one
# We implement this as if/elif blocks keyed to sub_choice
tabs = [None] * len(all_pages)  # placeholder for compatibility


# ══════════════════════════════════════════════════════════════════════════════
# TAB 0: WORKFORCE BRIDGE
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Workforce Bridge":
    section_header("Workforce Bridge",
                   "Awareness programs exist. Educational pathways exist. Employers are coming. What is missing is a workforce bridge connecting residents to opportunity.")

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown(f"""
        Illinois is building one of the most significant quantum technology ecosystems in the world.
        IQMP - located on the former U.S. Steel South Works site on the South Side lakefront - is
        projected to generate **up to $80 billion** in regional economic impact by 2035.
        IBM alone has committed **750 jobs and 500 apprenticeships** at the site.

        At the same time, a growing ecosystem of awareness programs is reaching South Side
        students and educators: CPS's Chi-Craft competition, DPI's Demystifying Quantum
        teacher training, and Fermilab's Saturday Morning Quantum at Olive Harvey College.

        **But there is a gap.** Awareness does not automatically become access.
        Between "I know quantum computing exists" and "I have a job in the quantum ecosystem"
        lies a critical missing layer: technical on-ramp, pathway navigation, mentorship,
        and employer connection.

        That is exactly where **Quantum × HPC Pathways** sits.
        """)

        callout(
            "\"The organization does not need to create a new pipeline. It needs to open existing ones.\" "
            "- <a href='https://drive.google.com/file/d/159AwW3Hso4aAdoUL485qzhfV81VM0IeJ/view?usp=drive_link' target='_blank'>Quantum x HPC Pathways Civic Action Plan, 2026</a>"
        )

        st.markdown("#### Why HPC and quantum belong together")
        st.markdown("""
        Quantum computers do not operate in isolation. In practice, quantum computing works
        through **hybrid workflows**: a classical HPC system handles data preparation,
        error correction, and post-processing, while the quantum processor handles the
        computationally intensive core. This means the workforce quantum employers need
        is not purely quantum physicists - it is people who understand **both** systems.

        HPC skills - Linux, job scheduling, GPU computing, data pipelines, scientific
        software - are the practical foundation that makes quantum workflows run.
        That is why this program starts with HPC. It is not a detour from quantum.
        It is the on-ramp.
        """)

        st.markdown("#### What local institutions already provide - and where the gap is")

        skills_data = {
            "Institution": [
                "CPS High Schools",
                "CPS CS for All",
                "DPI Teacher Training",
                "Olive Harvey College",
                "Kennedy-King College",
                "City Colleges (general)",
                "Fermilab SMQ*",
                "Chicago WHPC (this program)",
            ],
            "Skills Provided": [
                "Basic coding, computational thinking",
                "Python, data science fundamentals",
                "Quantum concepts for teachers",
                "IT certificates, IBM apprenticeship pipeline",
                "CS, networking, cybersecurity certificates",
                "Associate degrees in engineering tech, IT, manufacturing",
                "Quantum physics, circuit basics (10 weeks)",
                "Linux, HPC systems, GPU computing, quantum simulation, mentorship, pathway navigation",
            ],
            "Gap": [
                "No HPC or quantum exposure",
                "No HPC systems access",
                "Teachers only, not students",
                "No quantum or HPC on-ramp",
                "No quantum or HPC on-ramp",
                "No quantum or HPC connection",
                "No HPC skills or career navigation",
                "Fills the gap",
            ],
        }
        import pandas as _pd
        skills_df = _pd.DataFrame(skills_data)
        st.dataframe(
            skills_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Institution": st.column_config.TextColumn(width="medium"),
                "Skills Provided": st.column_config.TextColumn(width="large"),
                "Gap": st.column_config.TextColumn(width="medium"),
            }
        )

    with col2:
        # Pipeline visualization
        stages = [
            (" Community Awareness", "Chi-Craft · SMQ* · DPI", GREEN, "EXISTS"),
            (" Plain-Language Education","What is quantum? What jobs exist?", TEAL, "← WE PROVIDE"),
            (" HPC Technical On-Ramp", "Linux · GPU · Quantum simulation", TEAL, "← WE PROVIDE"),
            (" Mentorship & Navigation","5+ matches · Opportunity Guide", TEAL, "← WE PROVIDE"),
            (" Certificates & Degrees","City Colleges · University partners", GREEN, "EXISTS"),
            (" Internship & Research", "Argonne · IBM · IQMP tenants", GREEN, "EXISTS"),
            (" Career & Employment", "IQMP · CQE ecosystem · Industry", NAVY, "DESTINATION"),
        ]
        for label, sub, color, badge in stages:
            st.markdown(
                f"""<div style='background:{color}20;border-left:4px solid {color};
                padding:10px 12px;margin:4px 0;border-radius:4px'>
                <div style='display:flex;justify-content:space-between;align-items:center'>
                <div>
                <span style='font-weight:600;color:{NAVY};font-size:0.9rem'>{label}</span><br>
                <span style='color:{MGRAY};font-size:0.78rem'>{sub}</span>
                </div>
                <span style='background:{color};color:white;padding:2px 8px;
                border-radius:10px;font-size:0.7rem;white-space:nowrap'>{badge}</span>
                </div></div>""",
                unsafe_allow_html=True
            )
            if label not in [" Career & Employment"]:
                st.markdown(f"<div style='text-align:center;color:{MGRAY};font-size:1.2rem;margin:0'>↓</div>",
                           unsafe_allow_html=True)

    st.markdown("---")
    metric_row([
        ("projected IL-WI-IN quantum economic impact by 2035 (BCG/CQE, announced 2024)", "$80B", "BCG/CQE 2024", TEAL),
        ("IBM jobs + apprenticeships announced at IQMP (not yet operational)", "1,250", "750 FT + 500 apprentices, 2026", NAVY),
        ("quantum-relevant IL completions in 2024", "33,441", "+33% since 2018 (ISTC 2026)", GOLD),
        ("WHPC event attendees; 56% never ran a quantum circuit", "200+", "Chicago WHPC Quantum Meets HPC, 2026", TEAL),
    ])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: ILLINOIS OPPORTUNITY
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Illinois Opportunity":
    section_header("Illinois Opportunity",
                   "The jobs are coming. The question is who will be ready.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### Illinois Quantum-Relevant Completions by Field (2024)")
        st.caption("Source: ISTC, CQE, IQMP, Illinois EDC - 'Mapping Illinois' Quantum Talent Pipeline,' May 2026")
        fig = px.bar(
            ISTC_FIELDS.sort_values("completions", ascending=True),
            x="completions", y="field", orientation="h",
            color="share_pct",
            color_continuous_scale=[[0, "#B8D4E8"], [1, TEAL]],
            labels={"completions": "Completions (2024)", "field": "", "share_pct": "% of Total"},
            text="completions"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=320, margin=dict(l=10, r=60, t=10, b=10),
            coloraxis_showscale=False,
            plot_bgcolor="white", paper_bgcolor="white",
            font_color=MGRAY
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### IQMP Jobs by Category and Credential Requirement")
        st.caption("Source: IBM FutureNow announcement (Capitol News Illinois, April 2026); IQMP projections")
        fig2 = px.bar(
            IQMP_JOBS,
            x="category", y="jobs",
            color="category",
            color_discrete_sequence=[TEAL, NAVY, GOLD, GREEN, RED],
            text="jobs",
            custom_data=["credential_min", "timeline"]
        )
        fig2.update_traces(
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Jobs: %{y}<br>Min credential: %{customdata[0]}<br>Timeline: %{customdata[1]}<extra></extra>"
        )
        fig2.update_layout(
            height=320, margin=dict(l=10, r=10, t=10, b=60),
            showlegend=False,
            plot_bgcolor="white", paper_bgcolor="white",
            font_color=MGRAY,
            xaxis_tickangle=-20
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Quantum-Relevant Completions by Credential Level (Illinois, 2024)")
        st.caption("Source: ISTC 2026. Certificate programs are the single largest category.")
        fig3 = px.pie(
            ISTC_CREDENTIALS,
            values="completions_2024",
            names="credential",
            color_discrete_sequence=[TEAL, NAVY, GOLD, GREEN, "#7F8C8D"],
            hole=0.4
        )
        fig3.update_traces(textposition="outside", textinfo="percent+label")
        fig3.update_layout(
            height=320, margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            paper_bgcolor="white", font_color=MGRAY
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown("#### Key Workforce Facts")
        facts = [
            (TEAL, "$80B", "projected regional economic impact by 2035 (BCG/CQE)"),
            (NAVY, "33,441", "quantum-relevant IL completions in 2024 (ISTC)"),
            (GOLD, "+33%", "growth since 2018 National Quantum Initiative Act"),
            (GREEN, "750", "IBM FutureNow full-time jobs committed at IQMP"),
            (GREEN, "500", "IBM apprenticeships, designed with City Colleges"),
            (TEAL, "44%", "of completions are in Computer & Information Sciences"),
            (NAVY, "~12K", "certificate-level completions in 2024 - accessible without a 4-year degree"),
        ]
        for color, val, label in facts:
            st.markdown(
                f"""<div style='display:flex;align-items:center;margin:8px 0;
                background:{LGRAY};border-radius:6px;padding:8px 12px'>
                <span style='font-size:1.4rem;font-weight:700;color:{color};min-width:70px'>{val}</span>
                <span style='color:{MGRAY};font-size:0.85rem;margin-left:12px'>{label}</span>
                </div>""",
                unsafe_allow_html=True
            )

    callout(
        "<strong>The IBM announcement is a signal, not the whole story.</strong> "
        "The 500 apprenticeships are being designed with City Colleges of Chicago - "
        "and Olive Harvey College is already the SMQ* host site. The pipeline from "
        "South Side community → City Colleges → IQMP careers is being built right now."
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: SOUTH SIDE STRENGTHS & GAPS
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "South Side Strengths and Assets":
    section_header("South Side: Strengths and Assets",
                   "Start with what's there - not what's missing.")

    callout(
        " <strong>Methodology note:</strong> Geographic data uses Chicago community area boundaries "
        "as defined by the City of Chicago. These do not align exactly with CPS network boundaries, "
        "zip codes, or school attendance areas. Data is used for planning and advocacy, not causal inference. "
        "Source: ACS 5-Year Estimates 2019–2023; CPS To&Through Project 2024."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### High School Graduation Rates - South Side Community Areas")
        st.caption("Strength: Most South Side communities have graduation rates above 80%. Source: ACS 2023.")
        fig_hs = px.bar(
            SOUTH_SIDE_AREAS.sort_values("hs_pct", ascending=True),
            x="hs_pct", y="area", orientation="h",
            color="hs_pct",
            color_continuous_scale=[[0, "#E8F4F3"], [1, TEAL]],
            labels={"hs_pct": "HS Diploma or Higher (%)", "area": ""},
            text="hs_pct"
        )
        fig_hs.add_vline(x=CITYWIDE_HS, line_dash="dash", line_color=NAVY,
                         annotation_text=f"Chicago avg: {CITYWIDE_HS}%",
                         annotation_position="top right")
        fig_hs.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_hs.update_layout(height=360, margin=dict(l=10, r=60, t=10, b=10),
                             coloraxis_showscale=False,
                             plot_bgcolor="white", paper_bgcolor="white", font_color=MGRAY)
        st.plotly_chart(fig_hs, use_container_width=True)

    with col2:
        st.markdown("#### Bachelor's Degree Attainment vs. Citywide Average")
        st.caption("Gap: Bachelor's attainment lags citywide by 13–27 points. Source: ACS 2023.")
        df_plot = SOUTH_SIDE_AREAS.copy()
        df_plot["gap"] = CITYWIDE_BACH - df_plot["bach_pct"]
        df_plot["color"] = df_plot["gap"].apply(lambda x: RED if x > 20 else GOLD if x > 15 else TEAL)

        fig_bach = go.Figure()
        fig_bach.add_trace(go.Bar(
            x=df_plot.sort_values("gap", ascending=False)["area"],
            y=df_plot.sort_values("gap", ascending=False)["gap"],
            marker_color=df_plot.sort_values("gap", ascending=False)["color"],
            text=df_plot.sort_values("gap", ascending=False)["gap"].round(1),
            texttemplate="%{text:.1f}pp gap",
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Gap from citywide: %{y:.1f} percentage points<extra></extra>"
        ))
        fig_bach.add_hline(y=0, line_color=MGRAY)
        fig_bach.update_layout(
            height=360, margin=dict(l=10, r=10, t=10, b=80),
            plot_bgcolor="white", paper_bgcolor="white",
            font_color=MGRAY,
            yaxis_title="Percentage points below Chicago average (41.1%)",
            xaxis_tickangle=-30,
            showlegend=False
        )
        st.plotly_chart(fig_bach, use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### College Enrollment Rate by Community Area")
        st.caption("CPS graduates who enrolled in college within one year. Source: CPS To&Through Project 2024.")
        fig_coll = px.bar(
            SOUTH_SIDE_AREAS.sort_values("college_enroll_pct", ascending=True),
            x="college_enroll_pct", y="area", orientation="h",
            color="college_enroll_pct",
            color_continuous_scale=[[0, "#EEF2F8"], [1, NAVY]],
            labels={"college_enroll_pct": "College Enrollment Rate (%)", "area": ""},
            text="college_enroll_pct"
        )
        fig_coll.add_vline(x=66, line_dash="dash", line_color=GREEN,
                          annotation_text="CPS district avg: 66%",
                          annotation_position="top right")
        fig_coll.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_coll.update_layout(height=360, margin=dict(l=10, r=80, t=10, b=10),
                               coloraxis_showscale=False,
                               plot_bgcolor="white", paper_bgcolor="white", font_color=MGRAY)
        st.plotly_chart(fig_coll, use_container_width=True)

    with col4:
        st.markdown("#### Transit Access: Minutes to IQMP by Community Area")
        st.caption(
            "Proximity is not the barrier - connection is. Source: CTA route analysis (Bus 26, Bus 30, Metra Electric)."
        )
        fig_transit = px.bar(
            SOUTH_SIDE_AREAS.sort_values("transit_min_iqmp"),
            x="area", y="transit_min_iqmp",
            color="transit_min_iqmp",
            color_continuous_scale=[[0, GREEN], [0.4, GOLD], [1, RED]],
            labels={"transit_min_iqmp": "Est. transit time to IQMP (min)", "area": ""},
            text="transit_min_iqmp"
        )
        fig_transit.update_traces(texttemplate="%{text} min", textposition="outside")
        fig_transit.update_layout(
            height=360, margin=dict(l=10, r=10, t=10, b=80),
            coloraxis_showscale=False,
            plot_bgcolor="white", paper_bgcolor="white",
            font_color=MGRAY, xaxis_tickangle=-30
        )
        st.plotly_chart(fig_transit, use_container_width=True)

    callout(
        " <strong>The insight:</strong> South Shore residents are 18 minutes by transit from IQMP. "
        "South Chicago is 12 minutes. These communities are not distant from the quantum economy. "
        "They are <em>institutionally</em> disconnected from it. That is what Quantum × HPC Pathways addresses."
    )

    st.markdown("---")
    st.markdown("#### Chicago WHPC Survey: The Awareness Gap (N=181, self-selected quantum audience)")
    st.caption("Even among people who sought out a quantum event, foundational awareness gaps are large. Source: Chicago WHPC Quantum Meets HPC, 2026.")

    fig_survey = px.bar(
        WHPC_SURVEY.sort_values("pct", ascending=True),
        x="pct", y="question", orientation="h",
        color="pct",
        color_continuous_scale=[[0, "#EEF2F8"], [1, NAVY]],
        labels={"pct": "% of respondents", "question": ""},
        text="pct"
    )
    fig_survey.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_survey.update_layout(
        height=280, margin=dict(l=10, r=60, t=10, b=10),
        coloraxis_showscale=False,
        plot_bgcolor="white", paper_bgcolor="white", font_color=MGRAY
    )
    st.plotly_chart(fig_survey, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: ECOSYSTEM MAP
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Ecosystem Map":
    section_header("The Quantum Ecosystem Map",
                   "What exists - and where the navigation layer is missing.")

    callout(
        " <strong>The core argument:</strong> Every asset in this ecosystem exists. "
        "What is missing is the community-level navigation layer that connects South Side "
        "residents to those assets. That is Quantum × HPC Pathways."
    )

    # Partner logo strip
    partners = [
        "Chicago Quantum Exchange", "IQMP", "Argonne National Laboratory",
        "Fermilab", "IBM Quantum", "City Colleges of Chicago",
        "Chicago Public Schools", "DPI", "Infleqtion", "EeroQ", "Chicago WHPC"
    ]
    logos_html = "".join(
        f"<div style='background:white;border:1.5px solid {TEAL}33;border-radius:8px;"
        f"padding:6px 14px;font-size:0.78rem;font-weight:600;color:{NAVY}'>{p}</div>"
        for p in partners
    )
    st.markdown(
        f"<div style='display:flex;flex-wrap:wrap;gap:10px;align-items:center;"
        f"padding:12px 0 16px 0'>{logos_html}</div>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        fig_map = px.scatter_map(
            ECOSYSTEM_ASSETS,
            lat="lat", lon="lon",
            color="type",
            size=[20] * len(ECOSYSTEM_ASSETS),
            hover_name="org",
            hover_data={"focus": True, "community_access": True,
                        "type": True, "lat": False, "lon": False,
                        "has_community_nav": False},
            color_discrete_map={
                "Infrastructure": NAVY,
                "Research Hub": TEAL,
                "National Lab": "#2980B9",
                "University": GOLD,
                "City College": GREEN,
                "Program": "#8E44AD",
                "Bridge Org": RED,
            },
            map_style="carto-positron",
            zoom=9.5,
            center={"lat": 41.76, "lon": -87.65},
            labels={"type": "Organization Type"}
        )
        fig_map.update_layout(
            height=460, margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(orientation="h", y=-0.08)
        )
        # Add IQMP location marker
        fig_map.add_trace(go.Scattermap(
            lat=[41.737], lon=[-87.545],
            mode="markers+text",
            marker=dict(size=25, color=GOLD, symbol="star"),
            text=["IQMP"],
            textposition="top right",
            name="IQMP Site",
            hovertext="Illinois Quantum & Microelectronics Park<br>Former US Steel South Works site"
        ))
        st.plotly_chart(fig_map, use_container_width=True)

    with col2:
        st.markdown("#### Ecosystem Assets")
        for _, row in ECOSYSTEM_ASSETS.iterrows():
            nav_badge = (
                f"<span style='background:{GREEN};color:white;padding:1px 6px;border-radius:8px;font-size:0.7rem'>Active Community Navigation</span>"
                if row["has_community_nav"]
                else f"<span style='background:{RED}33;color:{RED};padding:1px 6px;border-radius:8px;font-size:0.7rem'>Community Engagement Opportunity</span>"
            )
            access_color = GREEN if row["community_access"] == "Strong" else (GOLD if row["community_access"] in ["Some", "Limited"] else RED)
            st.markdown(
                f"""<div style='background:{LGRAY};border-radius:6px;padding:10px 12px;margin:6px 0'>
                <div style='font-weight:600;color:{NAVY};font-size:0.88rem'>{row["org"]}</div>
                <div style='color:{MGRAY};font-size:0.78rem;margin:2px 0'>{row["focus"]}</div>
                <div style='margin-top:4px'>{nav_badge}
                <span style='color:{access_color};font-size:0.75rem;margin-left:6px'>
                Community access: {row["community_access"]}</span></div>
                </div>""",
                unsafe_allow_html=True
            )

    st.markdown("---")
    section_header("The Gap in One Table")
    gap_df = pd.DataFrame([
        {"What exists": "Quantum awareness programs", "Who has it": "SMQ*, DPI, Chi-Craft, CQE", "What's missing": "Technical on-ramp for community members"},
        {"What exists": "HPC infrastructure", "Who has it": "Research university HPC centers, Argonne, NCSA", "What's missing": "Community access to that infrastructure"},
        {"What exists": "Mentorship networks", "Who has it": "Chicago WHPC (300+ members)","What's missing": "Structured matching into South Side community"},
        {"What exists": "Certificate pathways", "Who has it": "Olive Harvey, City Colleges","What's missing": "Navigation from awareness to enrollment"},
        {"What exists": "Employer demand", "Who has it": "IBM, IQMP tenants, Argonne","What's missing": "Community-level visibility of roles + credentials"},
        {"What exists": "Workforce data", "Who has it": "ISTC 2026 report", "What's missing": "Community-level participation data"},
    ])
    st.dataframe(
        gap_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "What exists": st.column_config.TextColumn(width="medium"),
            "Who has it": st.column_config.TextColumn(width="medium"),
            "What's missing": st.column_config.TextColumn(width="large"),
        }
    )


    st.markdown("---")
    section_header("South Side Schools Map",
                   "CPS schools near IQMP - the student population your program serves.")
    st.caption("Selected CPS high schools in Network 17 and surrounding South Side networks. Source: CPS School Profiles SY2023-24. Note: school network boundaries and community area boundaries do not align exactly.")

    # CPS South Side schools - key high schools near IQMP corridor
    schools_df = pd.DataFrame([
        {"name": "South Shore International College Prep", "lat": 41.762, "lon": -87.568, "network": "Network 17", "type": "High School", "enrollment": 412},
        {"name": "Chicago Virtual Charter School (East)", "lat": 41.740, "lon": -87.556, "network": "Network 17", "type": "High School", "enrollment": 280},
        {"name": "Harlan Community Academy", "lat": 41.714, "lon": -87.621, "network": "Network 17", "type": "High School", "enrollment": 891},
        {"name": "Hope Academy", "lat": 41.746, "lon": -87.619, "network": "Network 17", "type": "High School", "enrollment": 320},
        {"name": "Fenger Academy", "lat": 41.694, "lon": -87.620, "network": "Network 17", "type": "High School", "enrollment": 511},
        {"name": "Julian High School", "lat": 41.758, "lon": -87.650, "network": "Network 13", "type": "High School", "enrollment": 748},
        {"name": "Harper High School", "lat": 41.776, "lon": -87.650, "network": "Network 13", "type": "High School", "enrollment": 612},
        {"name": "Robeson High School", "lat": 41.779, "lon": -87.648, "network": "Network 13", "type": "High School", "enrollment": 534},
        {"name": "Dunbar Vocational HS", "lat": 41.788, "lon": -87.611, "network": "Network 9", "type": "Voc/Tech HS", "enrollment": 689},
        {"name": "Olive Harvey College", "lat": 41.712, "lon": -87.591, "network": "City Colleges", "type": "Community College", "enrollment": 3200},
        {"name": "Kennedy-King College", "lat": 41.779, "lon": -87.644, "network": "City Colleges", "type": "Community College", "enrollment": 4100},
    ])

    col_map, col_info = st.columns([2, 1])
    with col_map:
        color_map = {
            "Network 17": TEAL,
            "Network 13": NAVY,
            "Network 9": GOLD,
            "City Colleges": GREEN,
        }
        fig_schools = px.scatter_map(
            schools_df,
            lat="lat", lon="lon",
            color="network",
            size="enrollment",
            hover_name="name",
            hover_data={"type": True, "enrollment": True, "network": True, "lat": False, "lon": False},
            color_discrete_map=color_map,
            map_style="carto-positron",
            zoom=11,
            center={"lat": 41.74, "lon": -87.60},
            labels={"network": "CPS Network / Type"}
        )
        # Add IQMP marker
        fig_schools.add_trace(go.Scattermap(
            lat=[41.737], lon=[-87.545],
            mode="markers+text",
            marker=dict(size=22, color=RED, symbol="star"),
            text=["IQMP Site"],
            textposition="top right",
            name="IQMP (future)",
            hovertext="Illinois Quantum and Microelectronics Park"
        ))
        fig_schools.update_layout(height=460, margin=dict(l=0, r=0, t=0, b=0),
                                  legend=dict(orientation="h", y=-0.08))
        st.plotly_chart(fig_schools, use_container_width=True)

    with col_info:
        st.markdown("#### Key schools near IQMP")
        for _, row in schools_df.sort_values("network").iterrows():
            c = color_map.get(row["network"], MGRAY)
            st.markdown(
                f"""<div style='background:{LGRAY};border-left:3px solid {c};
                padding:8px 10px;margin:5px 0;border-radius:4px'>
                <div style='font-weight:600;color:{NAVY};font-size:0.82rem'>{row["name"]}</div>
                <div style='color:{MGRAY};font-size:0.75rem'>{row["network"]} | Enrollment: {row["enrollment"]:,}</div>
                </div>""",
                unsafe_allow_html=True
            )
        st.markdown("")
        callout(
            "<strong>Data note:</strong> Enrollment figures from CPS School Profiles SY2023-24. "
            "Network boundaries are approximate. IQMP location is the former US Steel South Works site."
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: PATHWAY LADDER
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Pathway Ladder":
    section_header("The Pathway Ladder",
                   "From awareness to employment - every rung has a name.")

    ladder = [
        {
            "step": "1. Community Awareness",
            "what": "Plain-language sessions: What is quantum? What is HPC? What jobs exist at IQMP?",
            "who": "South Side residents 16–35, no prerequisites",
            "provider": "Quantum × HPC Pathways (3–5 sessions, 40–60 participants)",
            "exists": True, "ours": True,
            "color": TEAL,
        },
        {
            "step": "2. HPC Technical On-Ramp",
            "what": "Hands-on: Linux, HPC systems, GPU computing, introductory quantum simulation",
            "who": "Participants from community sessions + self-referrals",
            "provider": "Quantum × HPC Pathways (4–6 workshops, 15–20 participants)",
            "exists": False, "ours": True,
            "color": TEAL,
        },
        {
            "step": "3. Mentorship & Navigation",
            "what": "5+ mentor matches, South Side Quantum Opportunity Guide, professional introductions",
            "who": "Workshop completers",
            "provider": "Chicago WHPC mentorship program",
            "exists": False, "ours": True,
            "color": TEAL,
        },
        {
            "step": "4. Certificates & Associate's Degrees",
            "what": "IT, engineering tech, CS, cybersecurity, data science certificate programs",
            "who": "Participants with clear pathway map",
            "provider": "Olive Harvey, Kennedy-King, Malcolm X, City Colleges of Chicago",
            "exists": True, "ours": False,
            "color": GREEN,
        },
        {
            "step": "5. Internship & Research Exposure",
            "what": "IBM apprenticeships, Argonne student programs, university undergraduate research",
            "who": "Certificate completers and enrolled students",
            "provider": "IBM (500 apprentices), Argonne, research universities",
            "exists": True, "ours": False,
            "color": GREEN,
        },
        {
            "step": "6. Bachelor's Degree Pathways",
            "what": "Engineering, CS, data science, physics - building on certificate foundation",
            "who": "Participants continuing education",
            "provider": "Chicago School of Engineering at City Colleges → UIUC transfer",
            "exists": True, "ours": False,
            "color": NAVY,
        },
        {
            "step": "7. Career & Employment",
            "what": "Roles at IQMP tenants: cybersecurity, AI/data science, supercomputing ops, quantum research",
            "who": "Program alumni",
            "provider": "IBM, Infleqtion, EeroQ, Argonne, PsiQuantum, IQMP ecosystem",
            "exists": True, "ours": False,
            "color": NAVY,
        },
    ]

    for i, rung in enumerate(ladder):
        badge = "EXISTS" if rung["exists"] else " GAP"
        our_badge = " | ️ WE PROVIDE THIS" if rung["ours"] else ""
        st.markdown(
            f"""<div style='background:{rung["color"]}18;border:2px solid {rung["color"]};
            border-radius:8px;padding:16px 20px;margin:8px 0'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start'>
            <div style='flex:1'>
            <span style='font-size:1rem;font-weight:700;color:{rung["color"]}'>{rung["step"]}</span>
            <span style='margin-left:10px;font-size:0.75rem;color:{MGRAY}'>{badge}{our_badge}</span>
            <div style='color:{MGRAY};font-size:0.85rem;margin:6px 0'>{rung["what"]}</div>
            <div style='color:{MGRAY};font-size:0.8rem'>
            <strong>Who:</strong> {rung["who"]}<br>
            <strong>Provider:</strong> {rung["provider"]}
            </div>
            </div>
            </div>
            </div>""",
            unsafe_allow_html=True
        )
        if i < len(ladder) - 1:
            st.markdown(
                f"<div style='text-align:center;font-size:1.5rem;color:{MGRAY};margin:0'>↓</div>",
                unsafe_allow_html=True
            )

    callout(
        " Steps 1–3 (marked ️) are the workforce bridge. Everything above and below them exists. "
        "Quantum × HPC Pathways is the connective tissue."
    )

# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: QUANTUM SKILLS MAP
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Quantum Skills Map":
    section_header("Quantum Skills Map",
                   "What skills the quantum industry needs, who provides them locally, and where Chicago WHPC fills the gap.")

    st.caption(
        "Role taxonomy based on: El-Adawy et al., 'Categorization of Roles in the Quantum Industry,' "
        "University of Colorado Boulder / RIT, November 2025 (arXiv:2511.11820). "
        "Skills cross-referenced with ISTC 2026 and CQE workforce reports. "
        "Chicago WHPC coverage based on current and planned curriculum as of June 2026."
    )

    skills_data = pd.DataFrame([
        {"category": "Hardware",    "subcategory": "H3/H4 Technical Specialists",
         "skill": "Cryogenic systems and dilution refrigerators",
         "credential_min": "MS / BS", "whpc_provides": False,
         "whpc_note": "", "local_provider": "Argonne, Fermilab (research roles only)"},
        {"category": "Hardware",    "subcategory": "H4 Technical Subsystem Specialists",
         "skill": "Electronics, fabrication, materials characterization",
         "credential_min": "BS / AS", "whpc_provides": False,
         "whpc_note": "", "local_provider": "Olive Harvey (IT certs), Kennedy-King"},
        {"category": "Hardware",    "subcategory": "H4 Technical Subsystem Specialists",
         "skill": "Precision manufacturing and semiconductor production",
         "credential_min": "Certificate / AS", "whpc_provides": False,
         "whpc_note": "", "local_provider": "City Colleges (manufacturing tech programs)"},
        {"category": "Software",    "subcategory": "S1 Software Engineering",
         "skill": "Classical software development (Python, scripting, version control)",
         "credential_min": "BS / Certificate", "whpc_provides": True,
         "whpc_note": "Python and scripting foundations covered in HPC on-ramp curriculum",
         "local_provider": "CPS CS for All, City Colleges"},
        {"category": "Software",    "subcategory": "S1 Software Engineering",
         "skill": "HPC systems and job scheduling (Slurm, Linux, cluster environments)",
         "credential_min": "Certificate / BS", "whpc_provides": True,
         "whpc_note": "Core HPC workshop curriculum - not offered at community level elsewhere in Chicago",
         "local_provider": "Chicago WHPC (fills gap)"},
        {"category": "Software",    "subcategory": "S1 Software Engineering",
         "skill": "GPU computing and accelerated workflows (CUDA, CuPy, RAPIDS)",
         "credential_min": "BS / Certificate", "whpc_provides": True,
         "whpc_note": "GPU workshop module delivered on H100 NVL hardware via institutional partnership",
         "local_provider": "Chicago WHPC (fills gap)"},
        {"category": "Software",    "subcategory": "S1 Software Engineering",
         "skill": "Cloud computing and APIs (AWS Braket, containerization)",
         "credential_min": "Certificate / BS", "whpc_provides": True,
         "whpc_note": "Introductory cloud and API coverage in HPC curriculum",
         "local_provider": "City Colleges (IT certs), Chicago WHPC"},
        {"category": "Software",    "subcategory": "S2 Applications and Algorithms",
         "skill": "Quantum circuit design (Qiskit, PennyLane, CUDA-Q)",
         "credential_min": "BS / MS", "whpc_provides": True,
         "whpc_note": "Introductory quantum simulation covered in workshop series; PennyLane partnership with Xanadu",
         "local_provider": "Chicago WHPC, Fermilab SMQ* (quantum basics only)"},
        {"category": "Software",    "subcategory": "S2 Applications and Algorithms",
         "skill": "Hybrid quantum-classical workflows",
         "credential_min": "BS / MS", "whpc_provides": True,
         "whpc_note": "Taught as the core bridge concept connecting HPC and quantum - not offered locally elsewhere",
         "local_provider": "Chicago WHPC (fills critical gap)"},
        {"category": "Software",    "subcategory": "S2 Applications and Algorithms",
         "skill": "Quantum machine learning (QML)",
         "credential_min": "MS / BS", "whpc_provides": True,
         "whpc_note": "PennyLane workshop covers QML fundamentals in partnership with Xanadu",
         "local_provider": "Chicago WHPC / Xanadu"},
        {"category": "Software",    "subcategory": "S2 Applications and Algorithms",
         "skill": "Error correction and noise mitigation",
         "credential_min": "MS / PhD", "whpc_provides": False,
         "whpc_note": "Advanced topic - beyond community program scope",
         "local_provider": "University research programs"},
        {"category": "Bridging",    "subcategory": "B2 Hardware-Software Bridge",
         "skill": "Data pipelines and scientific computing workflows",
         "credential_min": "Certificate / BS", "whpc_provides": True,
         "whpc_note": "Core HPC on-ramp curriculum component",
         "local_provider": "Chicago WHPC (fills gap)"},
        {"category": "Bridging",    "subcategory": "B2 Hardware-Software Bridge",
         "skill": "Technical documentation and knowledge transfer",
         "credential_min": "Certificate", "whpc_provides": True,
         "whpc_note": "Covered in mentorship and professional skills module",
         "local_provider": "Chicago WHPC"},
        {"category": "Bridging",    "subcategory": "B1 Applications Bridge",
         "skill": "Translating domain problems into quantum circuits",
         "credential_min": "BS / MS", "whpc_provides": False,
         "whpc_note": "Requires deep quantum knowledge - Year 2+ program goal",
         "local_provider": "Argonne, CQE programs"},
        {"category": "Public Facing & Business", "subcategory": "P3 Engagement",
         "skill": "Community outreach and workforce development",
         "credential_min": "BS / Certificate", "whpc_provides": True,
         "whpc_note": "Chicago WHPC is itself a working model of this role in practice",
         "local_provider": "Chicago WHPC"},
        {"category": "Public Facing & Business", "subcategory": "P3 Engagement",
         "skill": "Quantum science communication and education",
         "credential_min": "BS / Certificate", "whpc_provides": True,
         "whpc_note": "Community education sessions and teacher/student engagement programming",
         "local_provider": "Chicago WHPC, DPI, Fermilab"},
        {"category": "Public Facing & Business", "subcategory": "P3 Engagement",
         "skill": "Career navigation and professional networking",
         "credential_min": "No minimum", "whpc_provides": True,
         "whpc_note": "Mentorship program and South Side Quantum Opportunity Guide",
         "local_provider": "Chicago WHPC (fills gap at community level)"},
        {"category": "Public Facing & Business", "subcategory": "P2 Client Interactions",
         "skill": "Technical sales and customer success",
         "credential_min": "BS / Certificate", "whpc_provides": False,
         "whpc_note": "Pathway navigation module covers adjacent awareness",
         "local_provider": "City Colleges (business programs)"},
    ])

    # ── VISUALIZATION TOGGLE ─────────────────────────────────────────────────
    n_total = len(skills_data)
    n_whpc  = int(skills_data["whpc_provides"].sum())

    # Stat strip
    sv1, sv2, sv3 = st.columns(3)
    with sv1:
        st.markdown(f"<div style='background:{LIGHT_NAVY};border-top:4px solid {TEAL};border-radius:6px;padding:14px;text-align:center'><div style='font-size:2rem;font-weight:700;color:{TEAL}'>{n_whpc} of {n_total}</div><div style='font-size:0.8rem;color:{MGRAY}'>skill areas covered by Chicago WHPC</div></div>", unsafe_allow_html=True)
    with sv2:
        st.markdown(f"<div style='background:{LIGHT_NAVY};border-top:4px solid {NAVY};border-radius:6px;padding:14px;text-align:center'><div style='font-size:2rem;font-weight:700;color:{NAVY}'>Software + Bridging</div><div style='font-size:0.8rem;color:{MGRAY}'>primary focus categories (no PhD required)</div></div>", unsafe_allow_html=True)
    with sv3:
        st.markdown(f"<div style='background:{LIGHT_NAVY};border-top:4px solid {GOLD};border-radius:6px;padding:14px;text-align:center'><div style='font-size:2rem;font-weight:700;color:{GOLD}'>Hybrid workflows</div><div style='font-size:0.8rem;color:{MGRAY}'>the critical bridge skill not offered elsewhere locally</div></div>", unsafe_allow_html=True)

    st.markdown("")
    viz_choice = st.radio(
        "Choose visualization",
        ["Skill Card Grid", "Two-Column Split", "HPC to Quantum Flow Diagram"],
        horizontal=True,
        label_visibility="collapsed"
    )

    category_colors = {
        "Hardware":                 NAVY,
        "Software":                 TEAL,
        "Bridging":                 GOLD,
        "Public Facing & Business": GREEN,
    }

    ordered_cats = ["Hardware", "Software", "Bridging", "Public Facing & Business"]

    # ── VIZ A: SKILL CARD GRID ────────────────────────────────────────────────
    if viz_choice == "Skill Card Grid":
        st.markdown(
            f"<div style='font-size:0.82rem;color:{MGRAY};margin:8px 0 16px 0'>"
            f"<span style='background:{TEAL};color:white;padding:2px 8px;border-radius:8px;margin-right:8px'>WHPC provides</span>"
            f"<span style='background:#E0E0E0;color:{MGRAY};padding:2px 8px;border-radius:8px'>gap or out of scope</span>"
            f" &nbsp; Each card = one skill area. Grouped by role category (El-Adawy et al. 2025).</div>",
            unsafe_allow_html=True
        )
        for cat in ordered_cats:
            cat_df = skills_data[skills_data["category"] == cat]
            color  = category_colors[cat]
            st.markdown(
                f"<div style='font-size:0.8rem;font-weight:700;color:{color};"
                f"text-transform:uppercase;letter-spacing:1px;margin:16px 0 8px 0'>"
                f"{cat}</div>",
                unsafe_allow_html=True
            )
            # Render cards in rows of 3
            rows = [list(cat_df.iloc[i:i+3].itertuples()) for i in range(0, len(cat_df), 3)]
            for row in rows:
                cols = st.columns(3)
                for col, skill_row in zip(cols, row):
                    bg     = TEAL if skill_row.whpc_provides else "#D0D0D0"
                    txt    = "white" if skill_row.whpc_provides else "#555555"
                    badge  = "WHPC" if skill_row.whpc_provides else "Gap"
                    border = f"border:2px solid {TEAL}" if skill_row.whpc_provides else "border:2px solid #CCCCCC"
                    col.markdown(
                        f"<div style='background:{bg};{border};border-radius:8px;"
                        f"padding:12px;height:100%;min-height:80px'>"
                        f"<div style='font-size:0.82rem;font-weight:600;color:{txt};margin-bottom:4px'>"
                        f"{skill_row.skill}</div>"
                        f"<div style='font-size:0.72rem;color:{txt};opacity:0.85'>"
                        f"{skill_row.credential_min}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                # pad empty cols
                for col in cols[len(row):]:
                    col.markdown("")

    # ── VIZ B: TWO-COLUMN SPLIT ───────────────────────────────────────────────
    elif viz_choice == "Two-Column Split":
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown(
                f"<div style='background:{TEAL};color:white;padding:10px 16px;"
                f"border-radius:6px;font-weight:600;margin-bottom:12px'>"
                f"Chicago WHPC Provides ({n_whpc} skills)</div>",
                unsafe_allow_html=True
            )
            for _, row in skills_data[skills_data["whpc_provides"]].iterrows():
                cat_color = category_colors.get(row["category"], MGRAY)
                st.markdown(
                    f"<div style='background:{TEAL}15;border-left:4px solid {TEAL};"
                    f"padding:8px 12px;margin:4px 0;border-radius:4px'>"
                    f"<div style='font-weight:600;color:{NAVY};font-size:0.85rem'>{row['skill']}</div>"
                    f"<div style='font-size:0.75rem;color:{MGRAY};margin-top:2px'>"
                    f"<span style='background:{cat_color};color:white;padding:1px 6px;"
                    f"border-radius:6px;font-size:0.7rem'>{row['category']}</span>"
                    f" &nbsp; {row['credential_min']}</div>"
                    f"<div style='font-size:0.75rem;color:{TEAL};margin-top:2px;font-style:italic'>"
                    f"{row['whpc_note']}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        with col_r:
            n_gap = n_total - n_whpc
            st.markdown(
                f"<div style='background:#888;color:white;padding:10px 16px;"
                f"border-radius:6px;font-weight:600;margin-bottom:12px'>"
                f"Gap or Out of Scope ({n_gap} skills)</div>",
                unsafe_allow_html=True
            )
            for _, row in skills_data[~skills_data["whpc_provides"]].iterrows():
                cat_color = category_colors.get(row["category"], MGRAY)
                st.markdown(
                    f"<div style='background:#F5F5F5;border-left:4px solid #CCCCCC;"
                    f"padding:8px 12px;margin:4px 0;border-radius:4px'>"
                    f"<div style='font-weight:600;color:{MGRAY};font-size:0.85rem'>{row['skill']}</div>"
                    f"<div style='font-size:0.75rem;color:{MGRAY};margin-top:2px'>"
                    f"<span style='background:{cat_color};color:white;padding:1px 6px;"
                    f"border-radius:6px;font-size:0.7rem'>{row['category']}</span>"
                    f" &nbsp; {row['credential_min']}</div>"
                    f"<div style='font-size:0.75rem;color:{MGRAY};margin-top:2px'>"
                    f"Covered by: {row['local_provider']}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

    # ── VIZ C: HPC TO QUANTUM FLOW DIAGRAM ───────────────────────────────────
    elif viz_choice == "HPC to Quantum Flow Diagram":
        callout(
            "In practice, quantum computing runs as a <strong>hybrid workflow</strong>: "
            "classical HPC systems handle data preparation, error correction, and "
            "post-processing, while the quantum processor handles the computationally "
            "intensive core. This means HPC skills are not a detour from quantum - "
            "they are the foundation. The diagram below shows which skills Chicago WHPC "
            "teaches at each stage of a hybrid workflow."
        )
        st.markdown("")

        # Flow stages
        flow_stages = [
            {
                "stage": "1. Data Preparation",
                "system": "Classical HPC",
                "skills": ["Linux command line", "Python scripting", "Data pipelines", "Job scheduling (Slurm)"],
                "whpc": True,
                "color": TEAL,
                "note": "Chicago WHPC teaches all of these in the HPC on-ramp workshops"
            },
            {
                "stage": "2. Algorithm Setup",
                "system": "Classical + Quantum",
                "skills": ["Quantum circuit design (Qiskit, PennyLane)", "Hybrid workflow orchestration", "GPU-accelerated simulation"],
                "whpc": True,
                "color": TEAL,
                "note": "Chicago WHPC covers introductory quantum circuit design and hybrid workflow concepts"
            },
            {
                "stage": "3. Quantum Execution",
                "system": "Quantum Processor (QPU)",
                "skills": ["Error correction protocols", "Qubit calibration", "Hardware-specific optimization"],
                "whpc": False,
                "color": "#888888",
                "note": "Advanced - requires PhD-level hardware expertise; out of scope for community program"
            },
            {
                "stage": "4. Results & Analysis",
                "system": "Classical HPC",
                "skills": ["Statistical analysis", "Visualization", "Scientific software", "Cloud APIs (AWS Braket)"],
                "whpc": True,
                "color": TEAL,
                "note": "Chicago WHPC covers scientific computing workflows and cloud API access"
            },
            {
                "stage": "5. Application & Communication",
                "system": "Domain + Business",
                "skills": ["Science communication", "Career navigation", "Professional networking", "Workforce development"],
                "whpc": True,
                "color": TEAL,
                "note": "Chicago WHPC mentorship program and Quantum Opportunity Guide"
            },
        ]

        for i, stage in enumerate(flow_stages):
            border_color = stage["color"]
            bg_color = f"{TEAL}12" if stage["whpc"] else "#F5F5F5"
            badge = (
                f"<span style='background:{TEAL};color:white;padding:3px 10px;border-radius:8px;font-size:0.75rem'>Chicago WHPC teaches this</span>"
                if stage["whpc"]
                else f"<span style='background:#CCCCCC;color:{MGRAY};padding:3px 10px;border-radius:8px;font-size:0.75rem'>out of scope</span>"
            )
            skills_html = "".join(
                f"<span style='background:{border_color}25;color:{NAVY};padding:2px 8px;"
                f"border-radius:10px;font-size:0.78rem;margin:2px;display:inline-block'>"
                f"{s}</span>" for s in stage["skills"]
            )
            st.markdown(
                f"<div style='background:{bg_color};border:2px solid {border_color};"
                f"border-radius:10px;padding:16px 20px;margin:6px 0'>"
                f"<div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px'>"
                f"<div>"
                f"<span style='font-size:1rem;font-weight:700;color:{NAVY}'>{stage['stage']}</span>"
                f"<span style='font-size:0.8rem;color:{MGRAY};margin-left:10px'>{stage['system']}</span>"
                f"</div>{badge}</div>"
                f"<div style='margin:8px 0'>{skills_html}</div>"
                f"<div style='font-size:0.78rem;color:{MGRAY};font-style:italic;margin-top:6px'>{stage['note']}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
            if i < len(flow_stages) - 1:
                st.markdown(
                    f"<div style='text-align:center;font-size:1.4rem;color:{MGRAY}'>↓</div>",
                    unsafe_allow_html=True
                )

    st.markdown("---")
    section_header("Skills Detail by Category",
                   "Filterable by role category and Chicago WHPC coverage.")

    category_colors = {
        "Hardware":                 NAVY,
        "Software":                 TEAL,
        "Bridging":                 GOLD,
        "Public Facing & Business": GREEN,
    }

    fc1, fc2 = st.columns(2)
    with fc1:
        cat_filter = st.multiselect(
            "Filter by role category",
            options=skills_data["category"].unique().tolist(),
            default=skills_data["category"].unique().tolist()
        )
    with fc2:
        whpc_filter = st.selectbox(
            "Filter by Chicago WHPC coverage",
            ["All skills", "Chicago WHPC provides", "Gap or not yet covered"]
        )

    filtered = skills_data[skills_data["category"].isin(cat_filter)].copy()
    if whpc_filter == "Chicago WHPC provides":
        filtered = filtered[filtered["whpc_provides"]]
    elif whpc_filter == "Gap or not yet covered":
        filtered = filtered[~filtered["whpc_provides"]]

    ordered_cats = ["Hardware", "Software", "Bridging", "Public Facing & Business"]
    for cat in [c for c in ordered_cats if c in cat_filter]:
        cat_df = filtered[filtered["category"] == cat]
        if len(cat_df) == 0:
            continue
        color = category_colors.get(cat, MGRAY)
        st.markdown(
            f"<div style='background:{color};color:white;padding:8px 16px;"
            f"border-radius:6px;font-weight:600;margin:16px 0 8px 0'>"
            f"{cat} Roles</div>",
            unsafe_allow_html=True
        )
        for _, row in cat_df.iterrows():
            bg     = f"{TEAL}15" if row["whpc_provides"] else "#F5F5F5"
            border = TEAL        if row["whpc_provides"] else "#CCCCCC"
            badge  = (
                f"<span style='background:{TEAL};color:white;padding:2px 8px;"
                f"border-radius:8px;font-size:0.72rem'>WHPC provides</span>"
                if row["whpc_provides"]
                else f"<span style='background:#E0E0E0;color:{MGRAY};padding:2px 8px;"
                     f"border-radius:8px;font-size:0.72rem'>gap</span>"
            )
            note_html = (
                f"<div style='color:{TEAL};font-size:0.78rem;margin-top:2px;"
                f"font-style:italic'>{row['whpc_note']}</div>"
                if row["whpc_provides"] and row["whpc_note"] else ""
            )
            st.markdown(
                f"<div style='background:{bg};border-left:4px solid {border};"
                f"padding:10px 14px;margin:4px 0;border-radius:4px'>"
                f"<div style='display:flex;justify-content:space-between;"
                f"align-items:flex-start;gap:12px'>"
                f"<div style='flex:1'>"
                f"<span style='font-weight:600;color:{NAVY};font-size:0.88rem'>"
                f"{row['skill']}</span>"
                f"<div style='color:{MGRAY};font-size:0.78rem;margin-top:3px'>"
                f"{row['subcategory']} | Min credential: {row['credential_min']}</div>"
                f"<div style='color:{MGRAY};font-size:0.78rem;margin-top:2px'>"
                f"Local provider: {row['local_provider']}</div>"
                f"{note_html}</div>{badge}</div></div>",
                unsafe_allow_html=True
            )

    callout(
        "<strong>Source:</strong> Role taxonomy from El-Adawy, Lewandowski, Pina, Zwickl, "
        "'Categorization of Roles in the Quantum Industry,' University of Colorado Boulder / RIT, "
        "November 2025 (arXiv:2511.11820). Chicago WHPC coverage assessment as of June 2026."
    )


# TAB 5: QUANTUM OPPORTUNITY INDEX
# ══════════════════════════════════════════════════════════════════════════════

if sub_choice == "Community Profiles":
    section_header("Community Profiles",
                   "Raw data by community area and comparison neighborhoods. Draw your own conclusions.")

    st.caption(
        "Inspired by the methodology of Statchen et al. (2026), who compared treated and control "
        "neighborhoods directly rather than collapsing data into composite scores. "
        "Comparison communities (marked with *) provide analytical context. "
        "Source: ACS 5-Year Estimates 2023; CPS To&Through 2024; CDC SVI 2022."
    )

    callout(
        "<strong>Methodology note:</strong> This table presents raw indicators without weighting or scoring. "
        "Readers are invited to interpret the data directly. The Community Readiness Profile tab "
        "offers a weighted composite for those who prefer a summary measure, with full methodology disclosed."
    )

    # Build display table
    display_df = ALL_COMMUNITIES.copy()
    display_df["Group"] = display_df["group"]
    display_df["Community"] = display_df["area"].str.replace(" (comp.)", "*", regex=False)
    display_df["Bachelor's (%)"] = display_df["bach_pct"]
    display_df["HS Grad (%)"] = display_df["hs_pct"]
    display_df["College Enroll (%)"] = display_df["college_enroll_pct"]
    display_df["Youth Pop (16-35)"] = display_df["youth_pop"].apply(lambda x: f"{x:,}")
    display_df["Median Income ($)"] = display_df["med_income"].apply(lambda x: f"${x:,}")
    display_df["SVI (CDC 2022)"] = display_df.apply(
        lambda r: r.get("svi", None) if "svi" in display_df.columns else None, axis=1
    )
    display_df["Transit to IQMP (min)"] = display_df["transit_min_iqmp"]

    show_cols = ["Community", "Group", "Bachelor's (%)", "HS Grad (%)",
                 "College Enroll (%)", "Youth Pop (16-35)", "Median Income ($)", "Transit to IQMP (min)"]

    st.dataframe(
        display_df[show_cols].sort_values("Bachelor's (%)").set_index("Community"),
        use_container_width=True,
        column_config={
            "Group": st.column_config.TextColumn(width="small"),
            "Bachelor's (%)": st.column_config.NumberColumn(format="%.1f"),
            "HS Grad (%)": st.column_config.NumberColumn(format="%.1f"),
            "College Enroll (%)": st.column_config.NumberColumn(format="%.1f"),
        }
    )
    st.caption("* = comparison community from another part of Chicago")

    st.markdown("---")
    section_header("Key Observations from the Raw Data")

    obs_cols = st.columns(3)
    with obs_cols[0]:
        st.markdown(
            f"<div style='background:{TEAL}12;border-left:4px solid {TEAL};"
            f"border-radius:6px;padding:14px;height:100%'>"
            f"<div style='font-weight:700;color:{TEAL};margin-bottom:8px'>Graduation rates are a strength</div>"
            f"<div style='font-size:0.85rem;color:{MGRAY}'>"
            f"Most South Side study communities have HS graduation rates above 80%, "
            f"comparable to or exceeding some comparison communities. "
            f"This is a programmatic asset, not a deficit.</div></div>",
            unsafe_allow_html=True
        )
    with obs_cols[1]:
        st.markdown(
            f"<div style='background:{NAVY}12;border-left:4px solid {NAVY};"
            f"border-radius:6px;padding:14px;height:100%'>"
            f"<div style='font-weight:700;color:{NAVY};margin-bottom:8px'>Bachelor's gap is structural</div>"
            f"<div style='font-size:0.85rem;color:{MGRAY}'>"
            f"South Side study communities average 19% bachelor's attainment vs "
            f"41% citywide and 31-72% in comparison communities. "
            f"Similar graduation rates but very different postsecondary outcomes "
            f"point to structural barriers, not individual capability.</div></div>",
            unsafe_allow_html=True
        )
    with obs_cols[2]:
        st.markdown(
            f"<div style='background:{GOLD}12;border-left:4px solid {GOLD};"
            f"border-radius:6px;padding:14px;height:100%'>"
            f"<div style='font-weight:700;color:{GOLD};margin-bottom:8px'>Youth population is substantial</div>"
            f"<div style='font-size:0.85rem;color:{MGRAY}'>"
            f"Combined youth population (16-35) across study areas exceeds 50,000. "
            f"This is a large potential program audience, not a marginal one. "
            f"Roseland alone has 7,200 young residents.</div></div>",
            unsafe_allow_html=True
        )

    st.markdown("---")
    section_header("Logic Model: From Inputs to Outcomes",
                   "Borrowed from evaluation frameworks in Statchen et al. (2026) and standard workforce development practice.")

    logic_cols = st.columns(5)
    stages = [
        ("Inputs", [
            "HPC workshops (4-6 sessions)",
            "Community education (3-5 sessions)",
            "Mentor network (300+ members)",
            "Institutional partners",
            "South Side Quantum Opportunity Guide",
            "Computing infrastructure access",
        ], TEAL),
        ("arrow", [], ""),
        ("Exposure Indicators", [
            "Awareness program attendance",
            "Facility tours completed",
            "Guest speakers delivered",
            "Mentor matches made",
            "Opportunity Guide downloads",
        ], NAVY),
        ("arrow", [], ""),
        ("Intermediate Outcomes", [
            "Workshop completion rate",
            "Technical skill demonstration",
            "Mentorship continuation at 90 days",
            "Professional network growth",
            "Certificate program applications",
        ], GOLD),
    ]

    for col, (label, items, color) in zip(logic_cols[:3] + [logic_cols[3], logic_cols[4]], [
        stages[0], stages[2], stages[4],
        ("arrow2","",""),("arrow3","","")
    ]):
        pass

    # Draw logic model as HTML
    logic_html = f"""
    <div style='display:grid;grid-template-columns:1fr auto 1fr auto 1fr auto 1fr auto 1fr;
    gap:8px;align-items:start;margin:16px 0'>
    """
    logic_stages = [
        ("Inputs", ["HPC workshops", "Community sessions", "Mentor network", "Partner relationships",
                    "Opportunity Guide", "Computing access"], TEAL),
        (">>", [], ""),
        ("Exposure", ["Workshop attendance", "Facility tours", "Guest speakers",
                      "Mentor matches", "Guide downloads"], NAVY),
        (">>", [], ""),
        ("Intermediate Outcomes", ["Workshop completion", "Technical skills", "Mentorship at 90 days",
                                    "Network growth", "Credential applications"], GOLD),
        (">>", [], ""),
        ("Long-Term Outcomes", ["STEM enrollment", "Internships", "Apprenticeships",
                                 "Job placement", "Career transitions"], GREEN),
        (">>", [], ""),
        ("Community Impact", ["Documented pathways", "Employer pipeline", "Replicable model",
                               "Community participation data", "Policy evidence"], RED),
    ]
    for label, items, color in logic_stages:
        if label == ">>":
            logic_html += f"<div style='text-align:center;font-size:1.5rem;color:{MGRAY};padding-top:20px'>-></div>"
        else:
            items_html = "".join(f"<div style='font-size:0.75rem;color:{MGRAY};margin:3px 0;padding-left:6px;border-left:2px solid {color}55'>{item}</div>" for item in items)
            logic_html += (
                f"<div style='background:{color}12;border:2px solid {color}44;"
                f"border-radius:8px;padding:10px'>"
                f"<div style='font-weight:700;color:{color};font-size:0.82rem;margin-bottom:6px'>{label}</div>"
                f"{items_html}</div>"
            )
    logic_html += "</div>"
    st.markdown(logic_html, unsafe_allow_html=True)

    callout(
        "<strong>Why this framework matters:</strong> Funders and evaluators distinguish "
        "inputs (what we invest), exposure indicators (what participants experience), "
        "intermediate outcomes (what changes in the short term), and long-term outcomes "
        "(what changes in careers and community). Chicago WHPC tracks all four levels "
        "from program launch."
    )


if sub_choice == "Community Readiness Profile":
    section_header("Community Readiness Profile",
                   "A composite readiness score for South Side community areas.")

    st.markdown("""
    The Community Readiness Profile (QOI) measures each community area's potential to participate
    in Illinois' emerging quantum economy. Higher scores reflect greater unmet potential -
    communities with strong educational foundations but persistent structural barriers to
    advanced technology careers.

    **Components (100-point scale):**
    - Educational potential gap from citywide average (40 pts) - represents upside
    - High school graduation strength (20 pts)
    - College enrollment culture (20 pts)
    - Youth population reach (15 pts)
    - Transit proximity to IQMP (5 pts)
    """)

    callout(
        "️ <strong>Methodology note:</strong> The QOI is a planning tool, not a causal measure. "
        "It is designed to identify communities where intervention has the greatest potential impact, "
        "not to rank communities by need or deficit. All components are derived from publicly "
        "available ACS 2023 and CPS 2024 data."
    )

    st.markdown("<div style='margin-top:80px'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        fig_qoi = px.bar(
            SOUTH_SIDE_AREAS.sort_values("crp", ascending=True),
            x="crp", y="area", orientation="h",
            color="crp",
            color_continuous_scale=[[0, "#EEF2F8"], [0.5, TEAL], [1, NAVY]],
            labels={"crp": "Community Readiness Profile (0–100)", "area": ""},
            text="crp"
        )
        fig_qoi.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_qoi.update_layout(
            height=380, margin=dict(l=10, r=60, t=10, b=10),
            coloraxis_showscale=False,
            plot_bgcolor="white", paper_bgcolor="white", font_color=MGRAY,
            title="Community Readiness Profile by Area (higher = greater opportunity)"
        )
        st.plotly_chart(fig_qoi, use_container_width=True)

    with col2:
        fig_scatter = px.scatter(
            SOUTH_SIDE_AREAS,
            x="bach_pct",
            y="college_enroll_pct",
            size="youth_pop",
            color="crp",
            color_continuous_scale=[[0, "#EEF2F8"], [0.5, TEAL], [1, NAVY]],
            hover_name="area",
            hover_data={"transit_min_iqmp": True, "youth_pop": True, "crp": True},
            labels={
                "bach_pct": "Bachelor's Attainment (%)",
                "college_enroll_pct": "College Enrollment Rate (%)",
                "youth_pop": "Youth Population",
                "crp": "Readiness Score"
            },
            title="Attainment vs. College Enrollment (bubble = youth population)"
        )
        fig_scatter.add_vline(x=CITYWIDE_BACH, line_dash="dash", line_color=RED,
                             annotation_text=f"Chicago avg ({CITYWIDE_BACH}%)",
                             annotation_position="top left")
        fig_scatter.update_layout(
            height=380, margin=dict(l=10, r=10, t=40, b=10),
            plot_bgcolor="white", paper_bgcolor="white", font_color=MGRAY
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")
    section_header("Study Areas vs. Comparison Communities",
                   "How do South Side communities compare to other Chicago neighborhoods of similar size?")

    st.caption(
        "Comparison communities selected to provide analytical contrast - similar population sizes, "
        "different socioeconomic profiles. This approach is borrowed from Statchen et al. (2026), "
        "who compared treated neighborhoods to similar control neighborhoods. "
        "All data: ACS 5-Year Estimates 2023."
    )

    col_comp1, col_comp2 = st.columns([3, 2])

    with col_comp1:
        fig_comp = px.scatter(
            ALL_COMMUNITIES,
            x="bach_pct",
            y="youth_pop",
            size="college_enroll_pct",
            color="group",
            color_discrete_map={"Study Area": TEAL, "Comparison": "#CCCCCC"},
            hover_name="area",
            hover_data={
                "bach_pct": True, "youth_pop": True,
                "college_enroll_pct": True, "med_income": True,
                "group": False
            },
            labels={
                "bach_pct": "Bachelor's Attainment (%)",
                "youth_pop": "Youth Population (est. ages 16-35)",
                "college_enroll_pct": "College Enrollment Rate (%)",
                "med_income": "Median HH Income ($)",
                "group": "Community Type"
            },
            title="Bachelor's attainment vs. youth population (bubble = college enrollment rate)"
        )

        # Add labels for study areas
        for _, row in ALL_COMMUNITIES[ALL_COMMUNITIES["group"] == "Study Area"].iterrows():
            fig_comp.add_annotation(
                x=row["bach_pct"], y=row["youth_pop"],
                text=row["area"].split()[0],
                showarrow=False,
                font=dict(size=9, color=TEAL),
                xshift=12, yshift=5
            )
        for _, row in ALL_COMMUNITIES[ALL_COMMUNITIES["group"] == "Comparison"].iterrows():
            label = row["area"].replace(" (comp.)", "")
            fig_comp.add_annotation(
                x=row["bach_pct"], y=row["youth_pop"],
                text=label,
                showarrow=False,
                font=dict(size=9, color=MGRAY),
                xshift=12, yshift=5
            )

        fig_comp.add_vline(x=CITYWIDE_BACH, line_dash="dash", line_color=RED,
                           annotation_text=f"Chicago avg ({CITYWIDE_BACH}%)",
                           annotation_position="top left",
                           annotation_font_color=RED)

        fig_comp.update_layout(
            height=420, margin=dict(l=10, r=10, t=40, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            font_color=MGRAY,
            legend=dict(orientation="h", y=-0.15)
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    with col_comp2:
        st.markdown("#### Key differences from comparison communities")
        rows_html = ""
        for _, row in ALL_COMMUNITIES.sort_values("bach_pct").iterrows():
            clr = TEAL if row["group"] == "Study Area" else MGRAY
            label = row["area"].replace(" (comp.)", "")
            rows_html += (f"<div style='margin:4px 0;font-size:0.82rem'>"
                         f"<span style='color:{clr};font-weight:600'>{label}</span>: "
                         f"{row['bach_pct']:.1f}%</div>")
        st.markdown(
            f"<div style='background:{LGRAY};border-radius:8px;padding:14px;margin:8px 0'>"
            f"<div style='font-weight:700;color:{NAVY};margin-bottom:8px'>Bachelor's Attainment Gap</div>"
            f"{rows_html}"
            f"<div style='margin-top:8px;font-size:0.78rem;color:{MGRAY};"
            f"border-top:1px solid #DDD;padding-top:6px'>"
            f"Chicago avg: {CITYWIDE_BACH}%</div></div>",
            unsafe_allow_html=True
        )

        callout(
            "<strong>What the comparison shows:</strong> South Side study communities "
            "have lower bachelor's attainment than comparable Chicago neighborhoods "
            "like Bridgeport and Albany Park, despite similar or larger youth populations. "
            "Hyde Park and Logan Square show what access to institutions can produce "
            "in communities with similar demographics. The gap is structural, not capability-based."
        )

    st.markdown("---")
    section_header("Full Data Table")
    display_cols = {
        "area": "Community Area",
        "bach_pct": "Bachelor's % (ACS 2023)",
        "hs_pct": "HS Diploma % (ACS 2023)",
        "college_enroll_pct": "College Enrollment % (CPS 2024)",
        "youth_pop": "Youth Population (16–35 est.)",
        "transit_min_iqmp": "Transit to IQMP (min)",
        "med_income": "Median HH Income ($)",
        "crp": "Community Readiness Profile",
    }
    st.dataframe(
        SOUTH_SIDE_AREAS[list(display_cols.keys())].rename(columns=display_cols).set_index("Community Area"),
        use_container_width=True
    )
    st.caption(
        "Sources: ACS 5-Year Estimates 2019–2023; CPS To&Through Project 2024; "
        "CTA transit estimates (Bus 26/30, Metra Electric). "
        "Youth population is an estimate based on ACS age cohort data. "
        "All figures should be considered planning estimates."
    )


    st.markdown("---")
    section_header("Priority Investment Communities: Quantum Opportunity vs. Social Vulnerability",
                   "Borrowing methodology from Statchen et al. (2026) who used CDC SVI to weight treatment and control groups in Chicago neighborhood research.")

    st.caption(
        "Social Vulnerability Index (SVI) scores derived from CDC/ATSDR Social Vulnerability Index 2022, "
        "Cook County Illinois, aggregated to community area level. SVI combines 16 Census variables across "
        "four themes: socioeconomic status, household characteristics, racial/ethnic minority status, and "
        "housing/transportation. Higher SVI = greater vulnerability (0-1 scale). "
        "Source: CDC/ATSDR GRASP, 2022."
    )

    # SVI data embedded from CDC 2022 Cook County data, aggregated to community area
    svi_data = pd.DataFrame([
        {"area": "South Shore",          "crp": 54.0, "svi": 0.82, "med_income": 26425,  "poverty_pct": 28.1, "lat": 41.762, "lon": -87.568},
        {"area": "South Chicago",        "crp": 57.7, "svi": 0.79, "med_income": 42456,  "poverty_pct": 22.4, "lat": 41.740, "lon": -87.550},
        {"area": "Woodlawn",             "crp": 54.3, "svi": 0.84, "med_income": 26415,  "poverty_pct": 31.2, "lat": 41.773, "lon": -87.597},
        {"area": "Calumet Heights",      "crp": 48.4, "svi": 0.68, "med_income": 54300,  "poverty_pct": 14.1, "lat": 41.726, "lon": -87.573},
        {"area": "Greater Grand Crossing","crp": 60.3,"svi": 0.88, "med_income": 32100,  "poverty_pct": 33.6, "lat": 41.762, "lon": -87.609},
        {"area": "Roseland",             "crp": 64.9, "svi": 0.86, "med_income": 38900,  "poverty_pct": 27.8, "lat": 41.694, "lon": -87.620},
        {"area": "Pullman",              "crp": 55.3, "svi": 0.81, "med_income": 36700,  "poverty_pct": 26.3, "lat": 41.699, "lon": -87.609},
        {"area": "Auburn Gresham",       "crp": 64.4, "svi": 0.89, "med_income": 34500,  "poverty_pct": 29.4, "lat": 41.745, "lon": -87.651},
        {"area": "Chatham",              "crp": 55.9, "svi": 0.77, "med_income": 45200,  "poverty_pct": 18.9, "lat": 41.744, "lon": -87.625},
        {"area": "Englewood",            "crp": 63.7, "svi": 0.93, "med_income": 22228,  "poverty_pct": 41.2, "lat": 41.779, "lon": -87.644},
    ])

    # Classify into 2x2 quadrants
    crp_median = svi_data["crp"].median()
    svi_median = svi_data["svi"].median()

    def classify(row):
        high_opp = row["crp"] >= crp_median
        high_vuln = row["svi"] >= svi_median
        if high_opp and high_vuln:
            return "PRIORITY: High Opportunity + High Vulnerability"
        elif high_opp and not high_vuln:
            return "Secondary: High Opportunity + Lower Vulnerability"
        elif not high_opp and high_vuln:
            return "Secondary: Lower Opportunity + High Vulnerability"
        else:
            return "Monitor: Lower Opportunity + Lower Vulnerability"

    svi_data["quadrant"] = svi_data.apply(classify, axis=1)

    color_map_quad = {
        "PRIORITY: High Opportunity + High Vulnerability": RED,
        "Secondary: High Opportunity + Lower Vulnerability": GOLD,
        "Secondary: Lower Opportunity + High Vulnerability": "#8E44AD",
        "Monitor: Lower Opportunity + Lower Vulnerability": "#AAAAAA",
    }

    col_svi1, col_svi2 = st.columns([3, 2])

    with col_svi1:
        fig_svi = px.scatter(
            svi_data,
            x="svi", y="crp",
            color="quadrant",
            color_discrete_map=color_map_quad,
            size="poverty_pct",
            hover_name="area",
            hover_data={"svi": True, "crp": True, "med_income": True, "poverty_pct": True,
                        "quadrant": False, "lat": False, "lon": False},
            labels={
                "svi": "Social Vulnerability Index (CDC 2022, 0=low, 1=high)",
                "crp": "Community Readiness Profile",
                "med_income": "Median HH Income ($)",
                "poverty_pct": "Poverty Rate (%)"
            },
            title="Quantum Opportunity vs. Social Vulnerability (bubble = poverty rate)"
        )
        # Add quadrant lines
        fig_svi.add_hline(y=crp_median, line_dash="dash", line_color="#CCCCCC",
                          annotation_text="CRP median", annotation_position="bottom right")
        fig_svi.add_vline(x=svi_median, line_dash="dash", line_color="#CCCCCC",
                          annotation_text="SVI median", annotation_position="top left")

        # Add quadrant labels
        fig_svi.add_annotation(x=0.915, y=65.5, text="PRIORITY", font=dict(color=RED, size=11, family="Arial"),
                               showarrow=False, bgcolor="white", bordercolor=RED, borderwidth=1)
        fig_svi.add_annotation(x=0.69, y=50, text="Secondary", font=dict(color=GOLD, size=10, family="Arial"),
                               showarrow=False)

        # Add community labels
        for _, row in svi_data.iterrows():
            fig_svi.add_annotation(
                x=row["svi"], y=row["crp"],
                text=row["area"].split()[0],
                showarrow=False,
                font=dict(size=9, color=NAVY),
                xshift=12, yshift=8
            )

        fig_svi.update_layout(
            height=420, margin=dict(l=10, r=10, t=40, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            font_color=MGRAY,
            legend=dict(orientation="v", y=0.5, x=1.02, title="Quadrant"),
            showlegend=False
        )
        st.plotly_chart(fig_svi, use_container_width=True)

    with col_svi2:
        st.markdown("#### Community Classification")
        for quad, color in color_map_quad.items():
            areas_in_quad = svi_data[svi_data["quadrant"] == quad]["area"].tolist()
            if not areas_in_quad:
                continue
            is_priority = "PRIORITY" in quad
            st.markdown(
                f"<div style='background:{color}{'25' if is_priority else '15'};"
                f"border:{'2px' if is_priority else '1px'} solid {color};"
                f"border-radius:8px;padding:12px;margin:8px 0'>"
                f"<div style='font-weight:{'700' if is_priority else '600'};"
                f"color:{color};font-size:0.82rem;margin-bottom:6px'>{quad}</div>"
                f"{''.join(f'<div style="font-size:0.85rem;color:{NAVY};margin:3px 0">- {a}</div>' for a in areas_in_quad)}"
                f"</div>",
                unsafe_allow_html=True
            )

        callout(
            "<strong>Reading the chart:</strong> Communities in the upper-right quadrant "
            "(high quantum opportunity + high social vulnerability) represent the highest-priority "
            "targets for Quantum x HPC Pathways. They have the greatest unmet potential "
            "and the greatest structural barriers. This framing is borrowed from Statchen et al. (2026), "
            "who used SVI to balance treatment and control groups in their Chicago neighborhood study. "
            "Source: CDC/ATSDR SVI 2022."
        )

    st.markdown("---")
    section_header("Illinois Quantum Ecosystem Timeline",
                   "The buildout is accelerating. Quantum x HPC Pathways launches at the right moment.")

    st.caption(
        "Timeline based on publicly announced milestones. Sources: IQMP newsroom, "
        "CQE announcements, Capitol News Illinois, Chicago Sun-Times."
    )

    timeline_events = [
        (2018, "National Quantum Initiative Act signed", "#888888", False),
        (2020, "Chicago Quantum Exchange established as NSF center", TEAL, False),
        (2021, "IQMP site selected: former US Steel South Works", NAVY, False),
        (2022, "Illinois Quantum and Microelectronics Park announced", NAVY, False),
        (2023, "CQE designated EDA Tech Hub (Bloch)", TEAL, False),
        (2024, "PsiQuantum partnership announced", "#2980B9", False),
        (2025, "NSF Regional Innovation Engines development award (CQE)", TEAL, False),
        (2026, "IBM FutureNow: 750 jobs + 500 apprenticeships at IQMP (announced April 2026, not yet operational)", GREEN, False),
        (2026, "ISTC quantum workforce report: 33,441 IL completions", GOLD, False),
        (2026, "Quantum x HPC Pathways launches", RED, True),
        (2027, "IQMP construction phase complete (projected, not confirmed)", NAVY, False),
        (2028, "First IQMP tenant operations (projected, not confirmed)", NAVY, False),
        (2030, "IBM apprenticeship cohorts fully operational (projected, not confirmed)", GREEN, False),
    ]

    fig_timeline = go.Figure()

    # Stagger labels: even index = above (y=1.15), odd = below (y=0.85)
    # This prevents label overlap on the timeline
    for i, (year, event, color, is_program) in enumerate(timeline_events):
        marker_size = 20 if is_program else 10
        marker_symbol = "star" if is_program else "circle"
        y_pos = 1.0
        # Stagger text position alternating above/below
        if is_program:
            text_pos = "top center"
            y_text = 1.0
        else:
            text_pos = "top center" if i % 2 == 0 else "bottom center"
            y_text = 1.0

        # Add marker only (no text on scatter to avoid overlap)
        fig_timeline.add_trace(go.Scatter(
            x=[year], y=[y_pos],
            mode="markers",
            marker=dict(size=marker_size, color=color, symbol=marker_symbol,
                        line=dict(color="white", width=2)),
            hovertemplate=f"<b>{year}</b><br>{event}<extra></extra>",
            name=event,
            showlegend=False
        ))

    # Add text annotations staggered above/below to prevent overlap
    for i, (year, event, color, is_program) in enumerate(timeline_events):
        # Truncate long labels
        label = event if len(event) <= 35 else event[:32] + "..."
        if is_program:
            y_ann = 1.22
            font_size = 11
            font_color = RED
        elif i % 2 == 0:
            y_ann = 1.14
            font_size = 9
            font_color = NAVY
        else:
            y_ann = 0.84
            font_size = 9
            font_color = MGRAY

        fig_timeline.add_annotation(
            x=year, y=y_ann,
            text=label,
            showarrow=False,
            font=dict(size=font_size, color=font_color, family="Arial"),
            xanchor="center",
            yanchor="middle",
            bgcolor="rgba(255,255,255,0.85)",
            borderpad=2,
        )

    # Baseline
    fig_timeline.add_hline(y=1, line_color="#DDDDDD", line_width=1)

    # Launch marker
    fig_timeline.add_vrect(
        x0=2025.7, x1=2026.3,
        fillcolor=RED, opacity=0.06,
        layer="below", line_width=0
    )
    fig_timeline.add_vline(x=2026, line_dash="dash", line_color=RED, line_width=1.5)

    fig_timeline.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=30, b=40),
        plot_bgcolor="white", paper_bgcolor="white",
        font_color=MGRAY,
        xaxis=dict(
            range=[2017.5, 2031],
            tickmode="linear", dtick=1,
            showgrid=True, gridcolor="#F0F0F0",
            title=""
        ),
        yaxis=dict(visible=False, range=[0.65, 1.4]),
        title=dict(
            text="Illinois Quantum Ecosystem Buildout vs. Quantum x HPC Pathways Launch",
            font=dict(size=13, color=NAVY)
        )
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

    callout(
        "<strong>The timing argument:</strong> Workforce pipelines cannot be built at the moment "
        "employers begin hiring. The IBM announcement (2026) and IQMP construction completion (2027) "
        "mean the hiring window opens in 2027-2028. A community program launching in fall 2026 "
        "is precisely timed to build awareness, skills, and professional networks "
        "before that window opens - not after."
    )


    st.markdown("---")
    section_header("Component Methodology and Weight Rationale",
                   "Why these weights? The reasoning behind each component.")
    st.markdown("""
    The Community Readiness Profile is a planning tool designed to identify communities where
    workforce access intervention has the greatest potential impact. It deliberately avoids
    pure deficit framing - higher scores reflect unmet potential combined with existing strength,
    not simply the most disadvantaged communities.
    """)
    qoi_weights = [
        ("40%", "Educational Potential Gap",
         "Distance from citywide bachelor's attainment (ACS 2023)",
         f"The largest weight captures unmet potential. Communities where attainment lags "
         f"the citywide average despite other strengths represent the core access gap this program addresses."),
        ("20%", "High School Graduation Strength",
         "HS diploma or higher rate (ACS 2023)",
         f"Graduation rates signal existing educational foundation and participant readiness. "
         f"South Side communities score strongly here - participants have foundational credentials."),
        ("20%", "College Enrollment Culture",
         "Rate of CPS graduates enrolling in college (CPS To&Through 2024)",
         f"Higher enrollment signals aspiration and pathway awareness. Communities with "
         f"stronger enrollment culture produce participants more likely to take next steps."),
        ("15%", "Youth Population Reach",
         "Estimated population ages 16-35 (ACS 2023)",
         f"A larger youth population means greater potential reach. Normalized to the "
         f"maximum across all study areas."),
        ("5%", "Transit Proximity to IQMP",
         "Estimated transit time to IQMP site (CTA route analysis)",
         f"Physical proximity matters but is weighted lightly - all study areas are "
         f"within 12-38 minutes, so variance is relatively low."),
    ]
    for weight, name, measure, rationale in qoi_weights:
        st.markdown(
            f"<div style='background:{LGRAY};border-radius:8px;padding:14px 16px;margin:8px 0'>"
            f"<div style='display:flex;align-items:center;gap:12px;margin-bottom:6px'>"
            f"<span style='background:{TEAL};color:white;padding:4px 12px;border-radius:20px;"
            f"font-weight:700;font-size:1rem'>{weight}</span>"
            f"<span style='font-weight:600;color:{NAVY};font-size:0.95rem'>{name}</span>"
            f"</div>"
            f"<div style='color:{MGRAY};font-size:0.8rem;margin-bottom:4px'>"
            f"<em>{measure}</em></div>"
            f"<div style='color:{MGRAY};font-size:0.82rem'>{rationale}</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    callout(
        "<strong>Limitation note:</strong> The Component weights reflect program design priorities "
        "and are not derived from a statistical model. They should be interpreted as a structured "
        "planning heuristic, not a causal claim. Researchers using these scores in policy contexts "
        "should test sensitivity across alternative weight configurations."
    )


    # Export section
    st.markdown("---")
    section_header("Export")

    col_e1, col_e2, col_e3 = st.columns(3)

    with col_e1:
        st.markdown("#### Policy Brief")
        policy_text = f"""
QUANTUM × HPC PATHWAYS: SOUTH SIDE OPPORTUNITY BRIEF
Chicago Women in High Performance Computing
Ana Marija Sokovic, PhD, MBA | 2026 Change Collective Fellow

EXECUTIVE SUMMARY
Illinois is positioned to generate up to $80 billion in quantum economic impact by 2035 (BCG/CQE).
IBM has committed 750 full-time jobs and 500 apprenticeships at IQMP on Chicago's South Side.
The ISTC's May 2026 analysis found 33,441 quantum-relevant postsecondary completions in Illinois in 2024.

Yet South Side community areas most proximate to IQMP face structural barriers:
- Bachelor's attainment: 11–28% vs. 41% citywide (ACS 2023)
- College enrollment gaps persist despite strong high school graduation rates
- No community-level navigation layer connecting residents to quantum pathways

THE GAP
Chicago WHPC's Quantum Meets HPC event (N=181) found:
- 56% of respondents had never used a quantum computing tool
- 76% wanted to understand the quantum-HPC connection but lacked accessible resources
- 62% had no clear next step after the event

QUANTUM OPPORTUNITY INDEX - TOP COMMUNITIES FOR INTERVENTION
{chr(10).join(f" {i+1}. {row['area']} (CRP: {row['crp']:.1f})" for i, (_, row) in enumerate(SOUTH_SIDE_AREAS.sort_values("crp", ascending=False).iterrows()))}

THE SOLUTION: QUANTUM × HPC PATHWAYS
Three-component community program:
1. Community Education (3–5 sessions, 40–60 participants)
2. HPC Technical On-Ramp (4–6 workshops, 15–20 participants)
3. Mentorship + Pathway Navigation (5+ matches, Opportunity Guide)

Year 1 budget: $25,000–$50,000
Partners: Research universities, Chicago Quantum Exchange, Argonne, IBM, CPS, Olive Harvey College

Contact: chicagowhpc.org | Mentorship: chicagowhpc.org/mentorship
"""
        st.download_button(
            "⬇️ Download Policy Brief (.txt)",
            data=policy_text,
            file_name="quantum_hpc_pathways_policy_brief.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col_e2:
        st.markdown("#### Data Export")
        csv = SOUTH_SIDE_AREAS[list(display_cols.keys())].rename(columns=display_cols).to_csv(index=False)
        st.download_button(
            "⬇️ Download QOI Data (.csv)",
            data=csv,
            file_name="quantum_opportunity_index_south_side.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_e3:
        st.markdown("#### Partner One-Pager")
        partner_text = """
QUANTUM × HPC PATHWAYS - PARTNER ENGAGEMENT GUIDE
Chicago Women in High Performance Computing | chicagowhpc.org

5 WAYS TO PARTNER (LOW TO HIGH LIFT)

1. CAREER PATHWAY SPOTLIGHT (30 min, one-time)
   Provide 2–3 entry-level role descriptions for the South Side Quantum Opportunity Guide.
   We format and distribute. You get community visibility.

2. GUEST SPEAKER (60 min)
   Speak at one community education session about your career path and field.
   No prep required beyond a short bio. Audience: 40–60 South Side residents.

3. MENTOR PARTICIPATION (one semester)
   Match one professional with one participant. Chicago WHPC handles all structure,
   check-ins, and coordination. You provide one hour per month.

4. INTERNSHIP INFO SESSION (90 min)
   Present your early-career or apprenticeship programs directly to workshop participants.
   No hiring commitment required. Direct pipeline to motivated candidates.

5. FACILITY TOUR (half day)
   Host 10–15 participants at your lab, office, or facility.
   Often the single most motivating experience for community participants.

WHAT PARTNERS RECEIVE
- Community credibility and visibility in South Side engagement
- Structured access to emerging talent pipeline
- DEI outreach documentation for reporting
- Community-level participation data (unique dataset)
- Recognition in Opportunity Guide and program materials

Contact: Ana Marija Sokovic, PhD, MBA | chicagowhpc@gmail.com | chicagowhpc.org
"""
        st.download_button(
            "⬇️ Download Partner Guide (.txt)",
            data=partner_text,
            file_name="quantum_hpc_pathways_partner_guide.txt",
            mime="text/plain",
            use_container_width=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7: GEOGRAPHIC PROXIMITY
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Geographic Proximity":
    section_header("Geographic Proximity",
                   "South Side residents live within 20-40 minutes of one of the largest quantum investments in the world.")

    callout(
        "<strong>The proximity argument:</strong> The barrier is not distance. "
        "It is institutional disconnection. These communities are physically close to IQMP "
        "but organizationally invisible to its hiring pipeline. That is what Quantum x HPC Pathways changes."
    )

    # Travel time data
    proximity_df = pd.DataFrame([
        {"area": "South Chicago",       "transit_min": 12, "drive_min": 8,  "lat": 41.740, "lon": -87.550, "bach_pct": 21.7, "pop": 29381},
        {"area": "South Shore",         "transit_min": 18, "drive_min": 12, "lat": 41.762, "lon": -87.568, "bach_pct": 24.9, "pop": 31198},
        {"area": "Calumet Heights",     "transit_min": 15, "drive_min": 10, "lat": 41.726, "lon": -87.573, "bach_pct": 28.4, "pop": 13417},
        {"area": "Pullman",             "transit_min": 20, "drive_min": 13, "lat": 41.699, "lon": -87.609, "bach_pct": 14.8, "pop": 9872},
        {"area": "Roseland",            "transit_min": 22, "drive_min": 15, "lat": 41.694, "lon": -87.620, "bach_pct": 16.2, "pop": 41038},
        {"area": "Chatham",             "transit_min": 32, "drive_min": 18, "lat": 41.744, "lon": -87.625, "bach_pct": 22.8, "pop": 31710},
        {"area": "Greater Grand Crossing","transit_min": 30,"drive_min": 16,"lat": 41.762, "lon": -87.609, "bach_pct": 17.8, "pop": 29456},
        {"area": "Woodlawn",            "transit_min": 25, "drive_min": 14, "lat": 41.773, "lon": -87.597, "bach_pct": 22.1, "pop": 25980},
        {"area": "Auburn Gresham",      "transit_min": 38, "drive_min": 20, "lat": 41.745, "lon": -87.651, "bach_pct": 15.6, "pop": 43844},
        {"area": "Englewood",           "transit_min": 35, "drive_min": 19, "lat": 41.779, "lon": -87.644, "bach_pct": 11.3, "pop": 24369},
    ])

    col_prox1, col_prox2 = st.columns([3, 2])

    with col_prox1:
        # Map showing communities + IQMP with lines
        fig_prox = px.scatter_map(
            proximity_df,
            lat="lat", lon="lon",
            color="transit_min",
            size="pop",
            hover_name="area",
            hover_data={"transit_min": True, "drive_min": True, "bach_pct": True, "pop": True, "lat": False, "lon": False},
            color_continuous_scale=[[0, GREEN], [0.4, GOLD], [1, RED]],
            labels={"transit_min": "Transit time to IQMP (min)", "pop": "Population"},
            map_style="carto-positron",
            zoom=11,
            center={"lat": 41.74, "lon": -87.59},
            title="Transit time from South Side communities to IQMP site"
        )
        # Add IQMP marker
        fig_prox.add_trace(go.Scattermap(
            lat=[41.737], lon=[-87.545],
            mode="markers+text",
            marker=dict(size=28, color=GOLD, symbol="star"),
            text=["IQMP"],
            textposition="top right",
            name="IQMP Site",
            hovertext="Illinois Quantum and Microelectronics Park - Former US Steel South Works"
        ))
        fig_prox.update_layout(
            height=460, margin=dict(l=0, r=0, t=40, b=0),
            coloraxis_colorbar=dict(title="Transit min")
        )
        st.plotly_chart(fig_prox, use_container_width=True)

    with col_prox2:
        st.markdown("#### Transit times to IQMP by community")
        for _, row in proximity_df.sort_values("transit_min").iterrows():
            color = GREEN if row["transit_min"] <= 20 else (GOLD if row["transit_min"] <= 30 else RED)
            bar_w = int(row["transit_min"] / 40 * 100)
            st.markdown(
                f"<div style='margin:6px 0'>"
                f"<div style='display:flex;justify-content:space-between;margin-bottom:2px'>"
                f"<span style='font-size:0.85rem;font-weight:600;color:{NAVY}'>{row['area']}</span>"
                f"<span style='font-size:0.85rem;color:{color};font-weight:700'>{row['transit_min']} min</span>"
                f"</div>"
                f"<div style='background:#EEE;border-radius:4px;height:8px'>"
                f"<div style='background:{color};width:{bar_w}%;height:8px;border-radius:4px'></div>"
                f"</div></div>",
                unsafe_allow_html=True
            )
        st.markdown("")
        callout(
            "Source: CTA Bus 26 (South Shore Express), Bus 30 (South Chicago), "
            "and Metra Electric Line estimates. Times are approximate and "
            "represent off-peak transit."
        )

    st.markdown("---")
    section_header("The Numbers Behind the Proximity Argument")

    total_pop = proximity_df["pop"].sum()
    within_20 = proximity_df[proximity_df["transit_min"] <= 20]["pop"].sum()
    within_30 = proximity_df[proximity_df["transit_min"] <= 30]["pop"].sum()

    pc1, pc2, pc3, pc4 = st.columns(4)
    for col, (val, label, sub, color) in zip(
        [pc1, pc2, pc3, pc4],
        [
            (f"{total_pop:,}", "South Side residents in study area", "10 community areas", NAVY),
            (f"{within_20:,}", "residents within 20 min of IQMP", "by public transit", GREEN),
            (f"{within_30:,}", "residents within 30 min of IQMP", "by public transit", GOLD),
            ("12 min", "closest community: South Chicago", "direct transit to IQMP site", TEAL),
        ]
    ):
        col.markdown(
            f"<div style='background:{LIGHT_NAVY};border-top:4px solid {color};"
            f"border-radius:6px;padding:14px;text-align:center'>"
            f"<div style='font-size:1.6rem;font-weight:700;color:{color}'>{val}</div>"
            f"<div style='font-size:0.78rem;color:{MGRAY};margin-top:4px'>{label}</div>"
            f"<div style='font-size:0.72rem;color:{MGRAY};font-style:italic'>{sub}</div>"
            f"</div>",
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 9: COMMUNITY IMPACT DASHBOARD TRACKER
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Community Impact Dashboard":
    section_header("Community Impact Dashboard",
                   "Tracking what actually reaches the community - one of the first systematic efforts to track community-level participation in Illinois' emerging quantum workforce ecosystem.")

    callout(
        "<strong>Why this matters:</strong> IQMP has faced questions about who benefits locally. "
        "Chicago WHPC is building the community-level participation data that no other organization "
        "is currently collecting. This tracker documents what reaches residents - not just what is announced."
    )

    st.markdown("#### Year 1 Targets vs. Progress")
    st.caption("Program launches fall 2026. Targets established in the <a href='https://drive.google.com/file/d/159AwW3Hso4aAdoUL485qzhfV81VM0IeJ/view?usp=drive_link' target='_blank'>civic action plan</a>. Progress will be updated quarterly.")

    tracker_data = [
        ("Community Education Sessions", 0, "3-5", "sessions delivered", TEAL),
        ("Participants Reached", 0, "40-60", "direct participants", TEAL),
        ("HPC Workshop Sessions", 0, "4-6", "hands-on workshops", NAVY),
        ("Workshop Completions", 0, "15-20", "participants completing series", NAVY),
        ("Mentor Matches", 0, "5+", "matches facilitated", GOLD),
        ("Employer Partners", 0, "2-3", "formal engagements", GOLD),
        ("Facility Tours", 0, "1-2", "site visits completed", GREEN),
        ("Community Orgs Engaged", 0, "4-6", "host site partners", GREEN),
        ("Internship Opportunities Shared", 0, "3-5", "programs presented to participants", "#8E44AD"),
        ("Opportunity Guide Downloads", 0, "100+", "community members reached via guide", "#8E44AD"),
    ]

    st.markdown("---")
    st.markdown("#### Outcome Metrics (not just activities)")
    st.caption(
        "Funders increasingly require outcome metrics, not just activity counts. "
        "The following outcomes will be tracked at 3-month, 6-month, and 12-month intervals. "
        "All start at zero - program launches fall 2026."
    )
    outcome_data = [
        ("Workshop completion rate", 0, "70%+", "% of enrolled participants completing full series", TEAL),
        ("Mentorship continuation", 0, "80%+", "% of matched pairs active at 90 days", TEAL),
        ("Documented next step (6 months)", 0, "20%+", "% of participants taking verifiable next step", NAVY),
        ("Technical credential applications", 0, "5+", "participants applying to certificate/degree programs", NAVY),
        ("STEM education enrollment", 0, "3+", "participants enrolling in STEM programs within 6 months", GOLD),
        ("Internship/research applications", 0, "5+", "applications submitted to quantum/HPC employers", GOLD),
        ("Professional network growth", 0, "10+", "new professional connections per participant (avg)", GREEN),
        ("Job or apprenticeship placement", 0, "1+", "confirmed placements within 12 months (Year 1 stretch goal)", GREEN),
    ]
    out_c1, out_c2 = st.columns(2)
    for i, (metric, current, target, unit, color) in enumerate(outcome_data):
        col = out_c1 if i % 2 == 0 else out_c2
        col.markdown(
            f"<div style='background:{LGRAY};border-left:4px solid {color};"
            f"border-radius:6px;padding:10px 14px;margin:5px 0'>"
            f"<div style='font-weight:600;color:{NAVY};font-size:0.85rem'>{metric}</div>"
            f"<div style='color:{MGRAY};font-size:0.78rem;margin-top:2px'>{unit}</div>"
            f"<div style='display:flex;align-items:baseline;gap:6px;margin-top:4px'>"
            f"<span style='font-size:1.4rem;font-weight:700;color:{color}'>{current}%</span>"
            f"<span style='font-size:0.78rem;color:{MGRAY}'>target: {target}</span>"
            f"</div></div>",
            unsafe_allow_html=True
        )

    col_t1, col_t2 = st.columns(2)
    for i, (metric, current, target, unit, color) in enumerate(tracker_data):
        col = col_t1 if i % 2 == 0 else col_t2
        col.markdown(
            f"<div style='background:{LGRAY};border-left:4px solid {color};"
            f"border-radius:6px;padding:12px 16px;margin:6px 0'>"
            f"<div style='font-weight:600;color:{NAVY};font-size:0.88rem'>{metric}</div>"
            f"<div style='display:flex;align-items:baseline;gap:8px;margin-top:4px'>"
            f"<span style='font-size:1.8rem;font-weight:700;color:{color}'>{current}</span>"
            f"<span style='font-size:0.8rem;color:{MGRAY}'>of {target} target {unit}</span>"
            f"</div>"
            f"<div style='background:#E0E0E0;border-radius:4px;height:6px;margin-top:6px'>"
            f"<div style='background:{color};width:2%;height:6px;border-radius:4px'></div>"
            f"</div></div>",
            unsafe_allow_html=True
        )

    st.markdown("---")
    section_header("Long-Term Outcomes to Track")
    st.markdown(
        "The following outcomes will be tracked over multiple years. "
        "Year 1 establishes the baseline. Years 2-5 demonstrate trajectory."
    )

    lt_cols = st.columns(3)
    lt_data = [
        ("Year 1 (2026)", [
            "40-60 community education participants",
            "15-20 HPC workshop completions",
            "5+ mentor matches",
            "2-3 employer partners",
            "South Side Quantum Opportunity Guide published",
            "Program toolkit documented for replication",
        ], TEAL),
        ("Year 3 (2028)", [
            "200+ cumulative participants",
            "Recurring quarterly workshop series",
            "20+ active mentor relationships",
            "Internship pipeline with 2+ employers",
            "CPS Network 17 integration formalized",
            "First cohort alumni serving as peer mentors",
        ], NAVY),
        ("Year 5 (2030)", [
            "Measurable workforce outcomes (jobs, apprenticeships, college enrollment)",
            "Program replicated in 2+ other cities via toolkit",
            "Community-level quantum workforce data published",
            "Chicago WHPC financially self-sustaining",
            "IQMP hiring pipeline with South Side community organizations",
        ], GOLD),
    ]
    for col, (year, items, color) in zip(lt_cols, lt_data):
        col.markdown(
            f"<div style='background:{color}15;border:2px solid {color};"
            f"border-radius:8px;padding:16px;height:100%'>"
            f"<div style='font-weight:700;color:{color};font-size:1rem;margin-bottom:12px'>{year}</div>"
            + "".join(f"<div style='font-size:0.82rem;color:{NAVY};margin:6px 0;padding-left:8px;border-left:2px solid {color}33'>{item}</div>" for item in items)
            + "</div>",
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 10: WHAT SUCCESS LOOKS LIKE LOOKS LIKE
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "What Success Looks Like":
    section_header("What Success Looks Like",
                   "A concrete, time-phased picture of what this program builds toward.")

    callout(
        "Workforce pipelines are not built in a single year. "
        "The Year 1 pilot proves the model. Years 2 and 3 scale it. "
        "By Year 5, South Side residents have a visible, documented pathway into "
        "Illinois quantum careers - and the data to prove it."
    )

    st.markdown("---")

    # Timeline visualization
    timeline = [
        {
            "period": "Fall 2026",
            "label": "Program Launch",
            "color": TEAL,
            "outcomes": [
                "3-5 community education sessions in South Side libraries and schools",
                "4-6 hands-on HPC workshops with 15-20 participants",
                "5+ mentor matches through Chicago WHPC network",
                "South Side Quantum Opportunity Guide published",
                "2-3 institutional partner agreements signed",
            ],
            "metric": "40-60 direct participants"
        },
        {
            "period": "End of Year 1 (Dec 2026)",
            "label": "Baseline Established",
            "color": NAVY,
            "outcomes": [
                "Complete program toolkit documented and publicly available",
                "First grant application submitted with outcome data",
                "Participant progression data collected (training enrollment, mentorship continuation)",
                "At least 20% of participants take documented next step within 6 months",
                "Program evaluation published",
            ],
            "metric": "Evidence base built"
        },
        {
            "period": "Year 2-3 (2027-2028)",
            "label": "Scaling",
            "color": GOLD,
            "outcomes": [
                "Workshop series expands to include Qiskit, advanced quantum simulation",
                "CPS Network 17 partnership formalized - direct school pipeline",
                "Cohort alumni become peer mentors for incoming participants",
                "City Colleges of Chicago partnership for credit-bearing pathways",
                "IBM apprenticeship referral pipeline established",
            ],
            "metric": "200+ cumulative participants"
        },
        {
            "period": "Year 4-5 (2029-2030)",
            "label": "Workforce Outcomes",
            "color": GREEN,
            "outcomes": [
                "First documented job placements or apprenticeships at IQMP ecosystem employers",
                "Model replicated in 2+ other cities via published toolkit",
                "Community-level quantum workforce participation data published and cited",
                "Chicago WHPC financially self-sustaining through institutional partnerships",
                "IQMP community benefits report includes Chicago WHPC participant data",
            ],
            "metric": "Measurable workforce impact"
        },
    ]

    for i, stage in enumerate(timeline):
        col_time, col_content = st.columns([1, 4])
        with col_time:
            st.markdown(
                f"<div style='background:{stage['color']};color:white;border-radius:8px;"
                f"padding:12px;text-align:center;height:100%;min-height:80px;"
                f"display:flex;flex-direction:column;justify-content:center'>"
                f"<div style='font-weight:700;font-size:0.88rem'>{stage['period']}</div>"
                f"<div style='font-size:0.78rem;margin-top:4px;opacity:0.9'>{stage['label']}</div>"
                f"<div style='font-size:1rem;font-weight:700;margin-top:6px'>{stage['metric']}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        with col_content:
            items_html = "".join(
                f"<div style='padding:6px 0;border-bottom:1px solid {stage['color']}22;"
                f"font-size:0.85rem;color:{NAVY}'>{item}</div>"
                for item in stage["outcomes"]
            )
            st.markdown(
                f"<div style='border:1.5px solid {stage['color']}44;border-radius:8px;"
                f"padding:12px 16px;height:100%'>{items_html}</div>",
                unsafe_allow_html=True
            )
        if i < len(timeline) - 1:
            st.markdown(
                f"<div style='text-align:left;padding-left:60px;font-size:1.2rem;"
                f"color:{MGRAY};margin:4px 0'>↓</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")
    callout(
        "<strong>For funders:</strong> Year 1 asks for $25K-$50K to prove the model. "
        "A successful Year 1 unlocks NSF INCLUDES, DOE workforce programs, EDA Tech Hub funding, "
        "and corporate education partnerships with IBM, NVIDIA, and AWS. "
        "The initial investment generates an evidence base that opens significantly larger funding streams."
    )



# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: WHY CHICAGO WHPC?
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Why Chicago WHPC?":
    section_header("Why Chicago WHPC?",
                   "Chicago WHPC does not replace existing programs. It connects them.")

    callout(
        "Every asset in Illinois' quantum ecosystem exists. "
        "What is missing is the community-level navigation layer. "
        "Chicago WHPC is that layer."
    )

    # Visual flow diagram
    flow_items = [
        ("Awareness Programs", "Chi-Craft, DPI teacher training,\nFermilab Saturday Morning Quantum", TEAL, True),
        ("Chicago WHPC", "HPC workshops, mentorship,\npathway navigation, community education", GOLD, True),
        ("Educational Institutions", "City Colleges, university partners,\ncertificate programs", TEAL, True),
        ("Employers", "IBM, IQMP tenants, Argonne,\ninternships and careers", NAVY, True),
        ("Quantum Careers", "South Side residents in\nIllinois quantum workforce", GREEN, False),
    ]

    for i, (label, sub, color, has_arrow) in enumerate(flow_items):
        is_whpc = label == "Chicago WHPC"
        border = f"3px solid {color}" if not is_whpc else f"4px solid {GOLD}"
        bg = f"{GOLD}20" if is_whpc else f"{color}10"
        size = "1.1rem" if is_whpc else "0.95rem"
        st.markdown(
            f"<div style='background:{bg};border:{border};border-radius:10px;"
            f"padding:16px 24px;margin:4px auto;max-width:500px;text-align:center'>"
            f"<div style='font-weight:700;color:{NAVY};font-size:{size}'>{label}</div>"
            f"<div style='color:{MGRAY};font-size:0.8rem;margin-top:4px;white-space:pre-line'>{sub}</div>"
            f"</div>",
            unsafe_allow_html=True
        )
        if has_arrow:
            st.markdown(
                f"<div style='text-align:center;font-size:1.5rem;color:{MGRAY};margin:2px 0'>↓</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")
    col_w1, col_w2, col_w3 = st.columns(3)
    for col, (title, items, color) in zip(
        [col_w1, col_w2, col_w3],
        [
            ("What makes Chicago WHPC unique", [
                "Founded by and for the South Side community",
                "501(c)(3) nonprofit - not a university program",
                "Led by someone with 14+ years of HPC expertise",
                "300+ member professional network",
                "Already delivered quantum computing events",
                "Demonstrated demand: 200+ registrants, 56% awareness gap",
            ], TEAL),
            ("What Chicago WHPC provides", [
                "Plain-language community education on quantum and HPC",
                "Hands-on HPC workshops (Linux, GPU, quantum simulation)",
                "Structured mentorship program",
                "South Side Quantum Opportunity Guide",
                "Professional introductions to ecosystem partners",
                "Community-level participation data",
            ], NAVY),
            ("What Chicago WHPC does NOT do", [
                "Replace CPS, DPI, or Fermilab programming",
                "Compete with City Colleges certificate programs",
                "Claim to train the entire quantum workforce",
                "Promise job placements (Year 1)",
                "Build new infrastructure from scratch",
                "Operate without institutional partners",
            ], GOLD),
        ]
    ):
        col.markdown(
            f"<div style='background:{color}12;border:2px solid {color}33;"
            f"border-radius:8px;padding:16px;height:100%'>"
            f"<div style='font-weight:700;color:{color};font-size:0.9rem;margin-bottom:12px'>{title}</div>"
            + "".join(
                f"<div style='font-size:0.82rem;color:{NAVY};margin:5px 0;"
                f"padding-left:8px;border-left:2px solid {color}55'>{item}</div>"
                for item in items
            )
            + "</div>",
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: WHY HPC?
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Why HPC?":
    section_header("Why HPC?",
                   "HPC provides employable skills today while preparing participants for future quantum careers.")

    callout(
        "High-performance computing is the infrastructure that makes quantum computing practical. "
        "Every quantum workflow runs on classical HPC systems for data preparation, error correction, "
        "and post-processing. HPC skills are not a detour from quantum - they are the foundation."
    )

    st.markdown("---")

    # Technology stack visual
    stack_items = [
        ("Artificial Intelligence", "Machine learning, neural networks, data science - runs on HPC clusters", "#2980B9", False),
        ("High-Performance Computing", "The infrastructure layer: Linux, GPU clusters, job scheduling, data pipelines", TEAL, True),
        ("Scientific Computing", "Simulations, modeling, research workflows - all HPC-dependent", "#8E44AD", False),
        ("Quantum Simulation", "Simulating quantum circuits classically - requires significant HPC resources", GOLD, False),
        ("Quantum Computing", "QPU execution - requires HPC for pre/post-processing in every real workflow", NAVY, False),
    ]

    col_stack, col_why = st.columns([2, 3])
    with col_stack:
        st.markdown("#### The Computing Stack")
        for label, sub, color, is_focus in stack_items:
            border = f"4px solid {color}" if is_focus else f"1px solid {color}66"
            bg = f"{color}25" if is_focus else f"{color}10"
            weight = "700" if is_focus else "500"
            st.markdown(
                f"<div style='background:{bg};border-left:{border};padding:10px 14px;"
                f"margin:4px 0;border-radius:4px'>"
                f"<div style='font-weight:{weight};color:{NAVY};font-size:0.88rem'>{label}</div>"
                f"<div style='color:{MGRAY};font-size:0.75rem;margin-top:2px'>{sub}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        st.caption("Bold border = Chicago WHPC entry point")

    with col_why:
        st.markdown("#### Why start with HPC, not quantum directly?")
        reasons = [
            ("Jobs exist today", "HPC roles - systems administrators, research computing staff, "
             "data engineers - are actively hiring now. Quantum-specific roles are still emerging. "
             "HPC skills provide immediate employment potential."),
            ("Credentials are accessible", "HPC skills can be built from a community college certificate "
             "or a focused training program. Quantum hardware roles typically require graduate degrees. "
             "HPC is the accessible on-ramp."),
            ("Every quantum workflow needs HPC", "In practice, quantum computers run as hybrid systems. "
             "Classical HPC handles data prep, error correction, and results analysis. "
             "HPC skills are required for any real quantum computing job."),
            ("Tools are transferable", "Linux, Python, GPU computing, data pipelines, cloud APIs - "
             "these skills are valuable across AI, scientific computing, data science, "
             "and quantum computing. Participants gain career flexibility."),
            ("Infrastructure is available now", "Chicago WHPC has access to H100 NVL GPU clusters "
             "and national HPC allocations through institutional partners. "
             "Participants can use real systems from day one."),
        ]
        for title, desc in reasons:
            st.markdown(
                f"<div style='background:{LGRAY};border-radius:8px;padding:12px 16px;margin:8px 0'>"
                f"<div style='font-weight:700;color:{TEAL};font-size:0.88rem'>{title}</div>"
                f"<div style='color:{MGRAY};font-size:0.82rem;margin-top:4px'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")
    section_header("HPC Skills Taught - and Where They Lead")
    skills_path = [
        ("Linux command line", "Foundation for all HPC and cloud work", "Systems admin, DevOps, research computing"),
        ("Job scheduling (Slurm)", "Running jobs on HPC clusters", "Research computing staff, HPC operations"),
        ("GPU computing (CUDA, CuPy)", "Accelerated computing workflows", "AI/ML engineer, scientific computing"),
        ("Data pipelines", "Moving and processing large datasets", "Data engineer, research scientist"),
        ("Quantum simulation (Qiskit, PennyLane)", "Simulating quantum circuits on HPC", "Quantum software developer, researcher"),
        ("Hybrid quantum-classical workflows", "Connecting HPC and quantum processors", "Quantum computing engineer"),
        ("Cloud APIs (AWS Braket)", "Accessing quantum hardware remotely", "Cloud computing, quantum operations"),
    ]
    hdr1, hdr2, hdr3 = st.columns([2, 2, 3])
    hdr1.markdown(f"**Skill**")
    hdr2.markdown(f"**What it enables**")
    hdr3.markdown(f"**Career paths**")
    for skill, enables, careers in skills_path:
        c1, c2, c3 = st.columns([2, 2, 3])
        c1.markdown(
            f"<div style='background:{TEAL}15;padding:6px 10px;border-radius:4px;"
            f"font-size:0.82rem;font-weight:600;color:{NAVY}'>{skill}</div>",
            unsafe_allow_html=True
        )
        c2.markdown(f"<div style='font-size:0.82rem;color:{MGRAY};padding:8px 4px'>{enables}</div>", unsafe_allow_html=True)
        c3.markdown(f"<div style='font-size:0.82rem;color:{TEAL};padding:8px 4px'>{careers}</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 11: PARTNERSHIP OPPORTUNITIES
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Partnership Opportunities":
    section_header("Partnership Opportunities",
                   "Specific, low-burden ways to participate in Quantum x HPC Pathways.")

    callout(
        "Chicago WHPC handles all coordination, logistics, and participant preparation. "
        "Partners choose the engagement level that works for them. "
        "Every contribution, large or small, directly serves South Side residents."
    )

    partner_types = [
        {
            "type": "Universities and Research Institutions",
            "color": TEAL,
            "opportunities": [
                ("Guest lecture", "60-minute talk on your research or career path at a community session. No prep required beyond a brief bio."),
                ("Student volunteer support", "Connect graduate students or postdocs with Chicago WHPC as volunteer facilitators or mentors."),
                ("Facility tours", "Host 10-15 participants for a visit to your lab or computing center."),
                ("Curriculum collaboration", "Share syllabus materials or co-develop workshop content for community audiences."),
                ("Grant co-application", "Join as a named partner on NSF INCLUDES, DOE workforce, or EDA Tech Hub applications."),
            ]
        },
        {
            "type": "National Laboratories",
            "color": NAVY,
            "opportunities": [
                ("Mentor participation", "Provide one scientist or engineer for a semester-long mentorship match. Chicago WHPC coordinates everything."),
                ("Facility tours", "Host a community group at your facility. Seeing a national lab is often the most transformative experience for participants."),
                ("Career panels", "Participate in a panel discussion about careers in quantum, HPC, or scientific computing. Conversational format."),
                ("Internship visibility", "Present your student programs to workshop participants. No hiring commitment required."),
                ("Computing resource access", "Support community participants with allocation access on national HPC systems."),
            ]
        },
        {
            "type": "Industry Partners",
            "color": GOLD,
            "opportunities": [
                ("Career spotlight", "Provide 2-3 entry-level role descriptions for the South Side Quantum Opportunity Guide. One page, one-time."),
                ("Mentor participation", "One professional, one semester. Chicago WHPC provides structure, check-ins, and coordination."),
                ("Internship information session", "Present your early-career or apprenticeship programs directly to motivated participants."),
                ("Workforce guidance", "Join an advisory conversation about what skills and credentials you are actively seeking."),
                ("Workshop sponsorship", "$5K-$15K sponsors one full workshop cohort. Recognition at all sessions and in published materials."),
            ]
        },
        {
            "type": "Community Organizations",
            "color": GREEN,
            "opportunities": [
                ("Venue hosting", "Provide space for community education sessions. Libraries, park district facilities, schools, community centers."),
                ("Participant recruitment", "Help spread the word through your existing community networks and mailing lists."),
                ("Trusted messenger", "Introduce Chicago WHPC to your community members as a known, vouched-for resource."),
                ("Co-hosting events", "Partner on a joint public event combining your programming with quantum and HPC education."),
            ]
        },
        {
            "type": "Foundations and Funders",
            "color": "#8E44AD",
            "opportunities": [
                ("Pilot support ($25K-$50K)", "Funds Year 1 programming: instructional coordination, stipends, curriculum development, and evaluation."),
                ("Mentorship support", "Dedicated funding for mentor training, matching coordination, and 6-month outcome tracking."),
                ("Transportation support", "Remove a real barrier: fund participant transit or childcare for workshop attendance."),
                ("Evaluation support", "Fund independent program evaluation to build the evidence base for scaling."),
                ("Multi-year commitment", "Year 2-3 funding unlocks toolkit development, replication in other cities, and long-term impact measurement."),
            ]
        },
    ]

    for partner in partner_types:
        color = partner["color"]
        st.markdown(
            f"<div style='background:{color};color:white;padding:10px 18px;"
            f"border-radius:8px;font-weight:700;font-size:1rem;margin:20px 0 8px 0'>"
            f"{partner['type']}</div>",
            unsafe_allow_html=True
        )
        cols = st.columns(len(partner["opportunities"]) if len(partner["opportunities"]) <= 3 else 3)
        for i, (opp_title, opp_desc) in enumerate(partner["opportunities"]):
            col = cols[i % len(cols)]
            col.markdown(
                f"<div style='background:{color}12;border:1.5px solid {color}44;"
                f"border-radius:8px;padding:12px;margin:4px 0;height:100%'>"
                f"<div style='font-weight:600;color:{NAVY};font-size:0.85rem;margin-bottom:6px'>{opp_title}</div>"
                f"<div style='color:{MGRAY};font-size:0.78rem'>{opp_desc}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.markdown(
        f"<div style='background:{TEAL}15;border:2px solid {TEAL};border-radius:10px;"
        f"padding:24px;text-align:center;margin-top:16px'>"
        f"<div style='font-size:1.2rem;font-weight:700;color:{NAVY};margin-bottom:8px'>"
        f"Ready to participate?</div>"
        f"<div style='color:{MGRAY};margin-bottom:12px'>"
        f"Contact Ana Marija Sokovic, PhD, MBA - Founder and Chair, Chicago WHPC</div>"
        f"<div style='font-size:1.1rem;font-weight:600;color:{TEAL}'>chicagowhpc@gmail.com</div>"
        f"<div style='margin-top:8px'>"
        f"<a href='https://www.chicagowhpc.org' style='color:{TEAL}'>chicagowhpc.org</a>"
        f" &nbsp;|&nbsp; "
        f"<a href='https://www.chicagowhpc.org/mentorship' style='color:{TEAL}'>Mentorship Program</a> | "f"<a href='https://drive.google.com/file/d/159AwW3Hso4aAdoUL485qzhfV81VM0IeJ/view?usp=drive_link' style='color:{TEAL}'>Civic Action Plan</a>"
        f"</div></div>",
        unsafe_allow_html=True
    )



    # Universal partner CTA footer on every tab
    st.markdown("---")
    st.markdown(
        f"<div style='background:{LGRAY};border-radius:8px;padding:16px 20px;margin-top:24px'>"
        f"<div style='font-weight:700;color:{NAVY};margin-bottom:10px'>How You Can Help</div>"
        f"<div style='display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px'>"
        + "".join(
            f"<span style='background:white;border:1.5px solid {TEAL};border-radius:20px;"
            f"padding:4px 14px;font-size:0.78rem;color:{NAVY}'>&#9744; {item}</span>"
            for item in ["Guest speaker", "Facility tour", "Mentor", "Career spotlight",
                         "Internship information", "Community venue partner", "Funder"]
        )
        + f"</div>"
        f"<div style='font-size:0.82rem;color:{MGRAY}'>"
        f"Contact: <strong>chicagowhpc@gmail.com</strong> | "
        f"<a href='https://www.chicagowhpc.org' style='color:{TEAL}'>chicagowhpc.org</a>"
        f"</div></div>",
        unsafe_allow_html=True
    )


# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"""<div style='text-align:center;color:{MGRAY};font-size:0.8rem;padding:12px'>
    Quantum × HPC Pathways | Chicago Women in High Performance Computing (Chicago WHPC) |
    Ana Marija Sokovic, PhD, MBA | 2026 Change Collective Fellow<br>
    Data: ACS 2023 · CPS To&Through 2024 · ISTC 2026 · BCG/CQE 2024 · IBM 2026 ·
    Chicago WHPC survey 2026 (N=181)<br>
    <a href="https://www.chicagowhpc.org" style="color:{TEAL}">chicagowhpc.org</a> |
    <a href="https://www.chicagowhpc.org/mentorship" style="color:{TEAL}">Mentorship Program</a>
    </div>""",
    unsafe_allow_html=True
)
