"""
Quantum × HPC Pathways: South Side Advanced Technology Workforce Strategy
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
    page_title="Quantum × HPC Pathways | South Side Advanced Technology Workforce Strategy",
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
# audience variable kept for backward compat
audience = "Overview"

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

# ── SIDEBAR NAVIGATION ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"<div style='padding:4px 0 10px 0'>"
        f"<div style='font-size:1.05rem;font-weight:700;color:{NAVY}'>Quantum x HPC Pathways</div>"
        f"<div style='font-size:0.76rem;color:{MGRAY};margin-top:2px'>South Side Advanced Technology Workforce Strategy</div>"
        f"</div>",
        unsafe_allow_html=True
    )
    st.markdown(f"<hr style='border:none;border-top:2px solid {TEAL};margin:0 0 12px 0'>",
                unsafe_allow_html=True)

    st.markdown(
        f"<div style='font-size:0.68rem;font-weight:700;color:{TEAL};"
        f"text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px'>Core Story</div>",
        unsafe_allow_html=True
    )
    sub_choice = st.radio(
        "nav",
        ["Why Now?", "Workforce Bridge", "Why Chicago WHPC?"],
        label_visibility="collapsed",
        key="nav_main",
        index=0
    )

    st.markdown(
        f"<div style='font-size:0.68rem;font-weight:700;color:{MGRAY};"
        f"text-transform:uppercase;letter-spacing:1.5px;margin:12px 0 4px 0'>Supporting Evidence</div>",
        unsafe_allow_html=True
    )
    evidence_groups = {
        "The Ecosystem": ["Ecosystem Map", "Emerging Workforce Roles", "Talent Retention", "Building the Ecosystem"],
        "The Evidence":  ["South Side Strengths and Assets", "Geographic Proximity",
                          "Community Profiles", "Opportunity and Vulnerability Analysis"],
        "The Program":   ["Program Architecture", "Participant Deliverables",
                          "Scaling Pathway", "Winter 2026 Pilot Metrics",
                          "Theory of Change", "Illinois Alignment"],
        "Get Involved":  ["Community Impact Dashboard", "Partnership Opportunities"],
    }
    for group_label, pages in evidence_groups.items():
        with st.expander(group_label, expanded=False):
            ev = st.radio(group_label, pages, label_visibility="collapsed", key=f"nav_{group_label}")
            if st.button(f"Go to {ev}", key=f"go_{group_label}", use_container_width=True):
                st.session_state["nav_override"] = ev
                st.rerun()

    if "nav_override" in st.session_state:
        sub_choice = st.session_state.pop("nav_override")

    st.markdown("---")
    st.caption("Data: ACS 2023, CPS 2024, ISTC 2026, BCG/CQE 2024, IBM 2026.")
    st.markdown(
        "[chicagowhpc.org](https://www.chicagowhpc.org) | "
        "[Mentorship](https://forms.gle/2Lnv7LGsN3uUtNuu8) | "
        "[Civic Action Plan](https://drive.google.com/file/d/159AwW3Hso4aAdoUL485qzhfV81VM0IeJ/view)"
    )

tabs = [None] * 20
audience = "Overview"  # kept for backward compat

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────

# PAGE TITLE
st.markdown(
    f"""<div style='background:linear-gradient(135deg,{NAVY},{TEAL});
    padding:32px 32px 24px 32px;border-radius:10px;margin-bottom:24px'>
    <h1 style='color:white;margin:0;font-size:2rem'>Quantum x HPC Pathways</h1>
    <p style='color:#B8D4E8;margin:8px 0 4px 0;font-size:1.1rem'>
    South Side Advanced Technology Workforce Strategy</p>
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




# ══════════════════════════════════════════════════════════════════════════════
# TAB 0: WORKFORCE BRIDGE
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Workforce Bridge":
    section_header("Workforce Bridge",
                   "Illinois has built a world-class quantum ecosystem. The challenge now is connecting residents to it.")

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
if sub_choice == "Why Now?":
    section_header("Why Now?",
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
        fig_hs.update_traces(texttemplate="%{text:.1f}%", textposition="inside", insidetextanchor="end")
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
        fig_coll.update_traces(texttemplate="%{text:.1f}%", textposition="inside", insidetextanchor="end")
        fig_coll.update_layout(height=360, margin=dict(l=10, r=20, t=10, b=10),
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

    st.markdown("---")
    section_header("Existing STEM Workforce",
                   "How many South Side residents already work in STEM and computing fields?")

    st.caption(
        "Source: U.S. Census Bureau, American Community Survey 5-Year Estimates 2019-2023, "
        "Occupation by Sex (S2401). Figures represent employed civilians 16+. "
        "Aggregated from census tract level. Treat as planning estimates with sampling uncertainty."
    )

    stem_df = pd.DataFrame([
        {"area": "South Shore",          "computing_pct": 3.2, "engineering_pct": 1.8, "science_pct": 1.1, "total_stem_pct": 6.1,  "total_employed": 12400},
        {"area": "South Chicago",        "computing_pct": 2.1, "engineering_pct": 2.4, "science_pct": 0.8, "total_stem_pct": 5.3,  "total_employed": 9800},
        {"area": "Woodlawn",             "computing_pct": 3.8, "engineering_pct": 1.4, "science_pct": 1.6, "total_stem_pct": 6.8,  "total_employed": 8200},
        {"area": "Calumet Heights",      "computing_pct": 4.1, "engineering_pct": 2.2, "science_pct": 0.9, "total_stem_pct": 7.2,  "total_employed": 6100},
        {"area": "Greater Grand Crossing","computing_pct": 2.4, "engineering_pct": 1.6, "science_pct": 0.7, "total_stem_pct": 4.7, "total_employed": 11200},
        {"area": "Roseland",             "computing_pct": 2.8, "engineering_pct": 1.9, "science_pct": 0.6, "total_stem_pct": 5.3,  "total_employed": 15800},
        {"area": "Pullman",              "computing_pct": 2.6, "engineering_pct": 2.8, "science_pct": 0.5, "total_stem_pct": 5.9,  "total_employed": 3900},
        {"area": "Auburn Gresham",       "computing_pct": 2.2, "engineering_pct": 1.4, "science_pct": 0.5, "total_stem_pct": 4.1,  "total_employed": 17200},
        {"area": "Chatham",              "computing_pct": 3.6, "engineering_pct": 1.8, "science_pct": 0.8, "total_stem_pct": 6.2,  "total_employed": 12400},
        {"area": "Englewood",            "computing_pct": 1.8, "engineering_pct": 1.2, "science_pct": 0.4, "total_stem_pct": 3.4,  "total_employed": 8100},
    ])
    stem_df["stem_est"] = (stem_df["total_stem_pct"] / 100 * stem_df["total_employed"]).round(0).astype(int)
    CHICAGO_STEM = 12.1

    col_st1, col_st2 = st.columns(2)
    with col_st1:
        fig_stem = px.bar(
            stem_df.sort_values("total_stem_pct"),
            x="total_stem_pct", y="area", orientation="h",
            color="total_stem_pct",
            color_continuous_scale=[[0, "#EEF2F8"], [1, TEAL]],
            labels={"total_stem_pct": "STEM Workers (%)", "area": ""},
            text="total_stem_pct",
            title="STEM workforce concentration (ACS 2023)"
        )
        fig_stem.add_vline(x=CHICAGO_STEM, line_dash="dash", line_color=NAVY,
                           annotation_text=f"Chicago avg: {CHICAGO_STEM}%",
                           annotation_position="top right")
        fig_stem.update_traces(texttemplate="%{text:.1f}%", textposition="inside",
                               insidetextanchor="end", textfont_color="white")
        fig_stem.update_layout(height=360, margin=dict(l=10, r=20, t=40, b=10),
                               coloraxis_showscale=False,
                               plot_bgcolor="white", paper_bgcolor="white", font_color=MGRAY)
        st.plotly_chart(fig_stem, use_container_width=True)

    with col_st2:
        fig_breakdown = px.bar(
            stem_df.sort_values("total_stem_pct", ascending=False),
            x="area", y=["computing_pct", "engineering_pct", "science_pct"],
            barmode="stack",
            color_discrete_map={"computing_pct": TEAL, "engineering_pct": NAVY, "science_pct": GOLD},
            labels={"value": "% of employed", "variable": "Occupation", "area": ""},
            title="Computing, engineering, and science by community"
        )
        fig_breakdown.for_each_trace(lambda t: t.update(
            name={"computing_pct": "Computing", "engineering_pct": "Engineering", "science_pct": "Sciences"}.get(t.name, t.name)
        ))
        fig_breakdown.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=80),
                                    plot_bgcolor="white", paper_bgcolor="white",
                                    font_color=MGRAY, xaxis_tickangle=-35,
                                    legend=dict(orientation="h", y=-0.35))
        st.plotly_chart(fig_breakdown, use_container_width=True)

    total_stem = stem_df["stem_est"].sum()
    callout(
        f"<strong>Key finding:</strong> An estimated {total_stem:,} STEM workers already live in these "
        f"South Side communities (ACS 2023). Average STEM concentration ({stem_df['total_stem_pct'].mean():.1f}%) "
        f"lags the Chicago average ({CHICAGO_STEM}%), confirming structural access barriers rather than "
        f"absence of technical aptitude. These residents are strong candidates for quantum-relevant "
        f"upskilling with targeted support."
    )
    st.caption(
        "Data note: ACS occupation data aggregated from census tracts contains sampling uncertainty. "
        "Computing = Computer and Mathematical occupations; Engineering = Architecture and Engineering; "
        "Sciences = Life, Physical, and Social Science occupations."
    )


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
        "presents component indicators with explicit weight rationale for those who prefer a summary view."
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


if sub_choice == "Opportunity and Vulnerability Analysis":
    section_header("Priority Communities Analysis",
                   "Component indicators shown separately. Note: this page presents a planning heuristic, not a validated index. See Opportunity and Vulnerability Analysis for a non-scored approach.")

    st.markdown("""
    The Community Readiness Profile presents component indicators for each community area. Higher scores reflect greater unmet potential combined with existing strengths. Note: weight rationale is disclosed in the methodology section below. For a non-scored comparison, see the Opportunity and Vulnerability Analysis page.
    in Illinois' emerging quantum economy. Higher scores reflect greater unmet potential -
    communities with strong educational foundations but persistent structural barriers to
    advanced technology careers.

    """)

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
        fig_qoi.update_traces(texttemplate="%{text:.1f}", textposition="inside", insidetextanchor="end", textfont_color="white")
        fig_qoi.update_layout(
            height=380, margin=dict(l=10, r=20, t=40, b=10),
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


    callout(
        "️ <strong>Methodology note:</strong> The QOI is a planning tool, not a causal measure. "
        "It is designed to identify communities where intervention has the greatest potential impact, "
        "not to rank communities by need or deficit. All components are derived from publicly "
        "available ACS 2023 and CPS 2024 data."
    )

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
                text=" ".join(row["area"].split()[:2]).replace(" (comp.)", ""),
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
        "crp": "Opportunity + Vulnerability Matrix",
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
                "crp": "Opportunity + Vulnerability Matrix",
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
                text=" ".join(row["area"].split()[:2]).replace(" (comp.)", ""),
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
                   "Tracking what actually reaches the community - community-level metrics tracking participation in Illinois's emerging advanced technology ecosystem.")

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

    # What we are / what we are not
    col_wn1, col_wn2 = st.columns(2)
    with col_wn1:
        st.markdown(
            f"<div style='background:#F5F5F5;border:2px solid #CCCCCC;border-radius:8px;padding:16px;height:100%'>"
            f"<div style='font-weight:700;color:{MGRAY};font-size:0.95rem;margin-bottom:12px'>What Chicago WHPC Is Not</div>"
            + "".join(f"<div style='font-size:0.85rem;color:{MGRAY};margin:6px 0;padding-left:8px;border-left:2px solid #CCC'>Not {item}</div>"
                      for item in ["a university", "a workforce board", "an employer",
                                   "a research laboratory", "a government agency"])
            + "</div>",
            unsafe_allow_html=True
        )
    with col_wn2:
        st.markdown(
            f"<div style='background:{TEAL}12;border:2px solid {TEAL};border-radius:8px;padding:16px;height:100%'>"
            f"<div style='font-weight:700;color:{TEAL};font-size:0.95rem;margin-bottom:12px'>What Chicago WHPC Is</div>"
            f"<div style='font-size:1.1rem;font-weight:700;color:{NAVY};margin-bottom:10px'>"
            f"A civic workforce intermediary.</div>"
            + "".join(f"<div style='font-size:0.85rem;color:{MGRAY};margin:6px 0;padding-left:8px;border-left:2px solid {TEAL}'>{item}</div>"
                      for item in [
                          "Connects community residents to existing ecosystem assets",
                          "Translates technical content into accessible language",
                          "Builds the mentorship and navigation layer that institutions lack",
                          "Generates community-level participation data",
                          "Owned by and accountable to the South Side community",
                      ])
            + "</div>",
            unsafe_allow_html=True
        )
    st.markdown("")

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




# ══════════════════════════════════════════════════════════════════════════════
# EMERGING WORKFORCE ROLES
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Emerging Workforce Roles":
    section_header("Emerging Workforce Roles",
                   "The quantum ecosystem needs people at every education level — not just PhDs.")

    st.caption("Sources: IBM FutureNow Chicago (2026), IQMP workforce projections, CQE employer analysis 2024, BLS Standard Occupational Classifications.")

    roles = {
        "Computing and Data": {
            "color": TEAL,
            "roles": [
                ("HPC Analyst", "Associate's / BS", "Manage and optimize workloads on high-performance computing clusters. Entry point via certificate or associate's degree.", "City Colleges, research university training"),
                ("AI / ML Engineer", "BS", "Develop and deploy machine learning models using GPU-accelerated infrastructure.", "City Colleges CS pathway, university programs"),
                ("Data Scientist", "BS / MS", "Analyze large datasets for research institutions, tech companies, and national labs.", "University programs, bootcamp + certificate"),
                ("Systems Administrator", "Certificate / AS", "Manage Linux servers, HPC systems, and cloud infrastructure. High demand at national labs.", "Olive Harvey, Kennedy-King, City Colleges"),
                ("Research Computing Staff", "BS / Certificate", "Support researchers using HPC and scientific software. Gateway role at universities and national labs.", "HPC training programs, campus champions"),
            ]
        },
        "Quantum Technology": {
            "color": NAVY,
            "roles": [
                ("Quantum Software Developer", "BS / MS", "Write and optimize quantum circuits using Qiskit, PennyLane, CUDA-Q. Increasingly accessible from BS level.", "University + industry training"),
                ("Quantum Technician", "AS / BS", "Support quantum hardware operation, calibration, and testing. Emerging role as IQMP scales up.", "Technical training, growing at IQMP"),
                ("Quantum Applications Researcher", "MS / PhD", "Develop quantum algorithms for specific industry applications.", "University research programs"),
            ]
        },
        "Semiconductor and Hardware": {
            "color": GOLD,
            "roles": [
                ("Fabrication Technician", "Certificate / AS", "Operate semiconductor manufacturing equipment. High demand as IQMP attracts fabrication tenants.", "City Colleges manufacturing programs"),
                ("Photonics Engineer", "BS", "Design and test optical components for quantum and telecom systems.", "University engineering programs"),
                ("Precision Manufacturing Specialist", "Certificate", "High-accuracy manufacturing for quantum hardware components.", "CTE programs, City Colleges"),
            ]
        },
        "Business and Operations": {
            "color": GREEN,
            "roles": [
                ("Program Manager", "BS", "Coordinate complex research and technology projects across institutions.", "MBA programs, PMP certification"),
                ("Workforce Coordinator", "BS / Certificate", "Connect communities to technology career pathways. Chicago WHPC trains this role directly.", "Chicago WHPC program"),
                ("Technical Sales / Customer Success", "BS", "Bridge technical products and customer needs for quantum and HPC companies.", "Business + technical background"),
            ]
        },
    }

    for category, data in roles.items():
        color = data["color"]
        st.markdown(
            f"<div style='background:{color};color:white;padding:8px 16px;"
            f"border-radius:8px;font-weight:700;margin:20px 0 8px 0'>{category}</div>",
            unsafe_allow_html=True
        )
        role_cols = st.columns(3)
        for i, (title, cred, desc, pathway) in enumerate(data["roles"]):
            with role_cols[i % 3]:
                st.markdown(
                    f"<div style='background:{color}10;border:1.5px solid {color}44;"
                    f"border-radius:8px;padding:12px;margin:4px 0;height:100%'>"
                    f"<div style='font-weight:700;color:{NAVY};font-size:0.88rem'>{title}</div>"
                    f"<div style='background:{color};color:white;display:inline-block;"
                    f"padding:1px 8px;border-radius:10px;font-size:0.72rem;margin:4px 0'>{cred}</div>"
                    f"<div style='font-size:0.8rem;color:{MGRAY};margin-top:4px'>{desc}</div>"
                    f"<div style='font-size:0.75rem;color:{color};margin-top:6px;"
                    f"font-style:italic'>Pathway: {pathway}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

    callout(
        "<strong>Key finding (CQE 2024):</strong> An increasing share of quantum industry positions "
        "require a bachelor's degree rather than a graduate degree - expanding opportunities well "
        "beyond PhD-level research. Certificate and associate's degree holders can enter the "
        "ecosystem through HPC operations, fabrication, and technical support roles."
    )


# ══════════════════════════════════════════════════════════════════════════════
# TALENT RETENTION
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Talent Retention":
    section_header("Talent Retention",
                   "Illinois educates talent. The challenge is keeping it - and ensuring local residents are part of it.")

    col_ret1, col_ret2 = st.columns(2)
    with col_ret1:
        st.markdown("#### The Current Pattern")
        for stage, desc, color in [
            ("Illinois educates talent", "World-class universities, national labs, and research institutions produce quantum-relevant graduates", TEAL),
            ("Talent leaves", "Without local industry density, graduates relocate to established tech hubs - California, New York, Massachusetts", RED),
            ("Economic benefit exits", "Research investment and talent development costs are borne by Illinois; economic returns flow elsewhere", RED),
        ]:
            st.markdown(
                f"<div style='background:{color}12;border-left:4px solid {color};"
                f"padding:10px 14px;margin:6px 0;border-radius:4px'>"
                f"<div style='font-weight:600;color:{NAVY}'>{stage}</div>"
                f"<div style='font-size:0.82rem;color:{MGRAY};margin-top:4px'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
            st.markdown(f"<div style='text-align:center;color:{MGRAY};font-size:1.2rem'>↓</div>", unsafe_allow_html=True)

    with col_ret2:
        st.markdown("#### The IQMP + Chicago WHPC Model")
        for stage, desc, color in [
            ("Illinois educates talent", "Universities, City Colleges, and community programs build quantum-relevant skills at every level", TEAL),
            ("IQMP creates local demand", "750+ jobs announced. Tenant companies need local talent pipelines. Community trust matters for hiring.", GREEN),
            ("Talent stays", "Career opportunities in Chicago match or exceed those in coastal hubs. South Side residents enter the ecosystem.", GREEN),
            ("Economic growth", "Tax base expands, community investment follows, quantum economy distributes benefits locally.", GREEN),
        ]:
            st.markdown(
                f"<div style='background:{color}12;border-left:4px solid {color};"
                f"padding:10px 14px;margin:6px 0;border-radius:4px'>"
                f"<div style='font-weight:600;color:{NAVY}'>{stage}</div>"
                f"<div style='font-size:0.82rem;color:{MGRAY};margin-top:4px'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
            if stage != "Economic growth":
                st.markdown(f"<div style='text-align:center;color:{MGRAY};font-size:1.2rem'>↓</div>", unsafe_allow_html=True)

    st.markdown("---")
    section_header("Workforce Challenges This Program Addresses",
                   "Borrowed from workforce intermediary frameworks.")

    challenges = [
        ("Limited awareness of advanced technology careers",
         "Most South Side residents have never encountered a clear explanation of what quantum computing is, what HPC does, or what jobs exist in these fields.",
         "Community education sessions deliver plain-language career context to 40-60 residents per cohort."),
        ("Fragmented ecosystem navigation",
         "The Illinois quantum ecosystem spans 15+ institutions. No single resource maps pathways from community to career across all of them.",
         "The South Side Quantum Opportunity Guide maps certificates, degrees, programs, and employers in one accessible document."),
        ("Lack of community-level workforce intermediaries",
         "Workforce development in quantum has focused on universities and industry. No organization systematically bridges South Side communities to this ecosystem.",
         "Chicago WHPC is designed specifically to fill this intermediary role."),
        ("Limited mentor access",
         "Mentorship in advanced technology fields typically flows through institutional networks. Community members outside those networks have no equivalent access.",
         "Chicago WHPC's mentorship program creates structured, supported connections between community members and professionals."),
        ("Uneven access to technical training infrastructure",
         "HPC training requires computing resources that most community members cannot access independently.",
         "Chicago WHPC provides access to GPU-accelerated HPC infrastructure through institutional partnerships."),
        ("Talent retention and local pipeline gaps",
         "IQMP employers will need community trust, diverse talent pipelines, and visible local hiring to succeed long-term.",
         "Chicago WHPC builds the community relationships and talent awareness that support long-term IQMP success."),
    ]

    for title, problem, solution in challenges:
        st.markdown(
            f"<div style='background:{LGRAY};border-radius:8px;padding:14px 16px;margin:8px 0'>"
            f"<div style='font-weight:700;color:{NAVY};margin-bottom:8px'>{title}</div>"
            f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px'>"
            f"<div style='background:white;padding:10px;border-radius:6px;border-left:3px solid {RED}'>"
            f"<div style='font-size:0.72rem;font-weight:700;color:{RED};margin-bottom:4px'>CHALLENGE</div>"
            f"<div style='font-size:0.82rem;color:{MGRAY}'>{problem}</div></div>"
            f"<div style='background:white;padding:10px;border-radius:6px;border-left:3px solid {TEAL}'>"
            f"<div style='font-size:0.72rem;font-weight:700;color:{TEAL};margin-bottom:4px'>OUR RESPONSE</div>"
            f"<div style='font-size:0.82rem;color:{MGRAY}'>{solution}</div></div>"
            f"</div></div>",
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# PROGRAM ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Program Architecture":
    section_header("Program Architecture",
                   "A structured, deliverable-based learning pathway for Winter 2026 pilot.")

    callout(
        "Program design is inspired by the Penn State workforce intermediary framework: "
        "each stage has a concrete deliverable, not just a learning outcome. "
        "Participants leave with tangible artifacts that support career navigation."
    )

    stages = [
        {
            "num": "01", "name": "Awareness", "color": TEAL,
            "what": ["Quantum 101 - plain language introduction", "Illinois quantum ecosystem overview",
                     "Career pathways and employer landscape", "Why HPC connects to quantum"],
            "deliverable": "South Side Quantum Ecosystem Guide",
            "deliverable_desc": "A personal copy of the publicly available guide mapping certificates, degrees, employers, and pathways."
        },
        {
            "num": "02", "name": "Preparation", "color": NAVY,
            "what": ["Linux command line fundamentals", "HPC system navigation and job submission",
                     "AI and GPU computing foundations", "Introduction to scientific workflows"],
            "deliverable": "Active HPC Account",
            "deliverable_desc": "Participants receive a working account on institutional HPC infrastructure with documented first job submission."
        },
        {
            "num": "03", "name": "Practice", "color": GOLD,
            "what": ["Hands-on cluster usage projects", "GPU-accelerated workflow exercises",
                     "Introductory quantum simulation (Qiskit or PennyLane)", "Portfolio artifact development"],
            "deliverable": "Portfolio Project",
            "deliverable_desc": "A documented technical project demonstrating HPC skills - shareable with employers and programs."
        },
        {
            "num": "04", "name": "Navigation", "color": GREEN,
            "what": ["Mentorship match and first meeting", "Career pathway mapping to participant goals",
                     "Professional skills (LinkedIn, resume, networking)", "Certificate and degree program review"],
            "deliverable": "Personal Career Roadmap",
            "deliverable_desc": "A documented, named pathway: next program, next credential, next employer contact - specific to each participant."
        },
        {
            "num": "05", "name": "Exposure", "color": "#8E44AD",
            "what": ["Facility tour at Argonne, Fermilab, or IQMP site", "Guest speaker from quantum/HPC employer",
                     "Employer career panel", "Professional network introductions"],
            "deliverable": "Professional Network",
            "deliverable_desc": "At least one documented professional introduction to a person working in the quantum/HPC ecosystem."
        },
        {
            "num": "06", "name": "Outcomes", "color": RED,
            "what": ["Internship or research experience application", "Certificate or degree program enrollment",
                     "Continued mentorship", "Peer facilitation opportunity (returning participants)"],
            "deliverable": "Career Transition",
            "deliverable_desc": "Documented next step: application submitted, program enrolled, interview scheduled, or position obtained."
        },
    ]

    for i, stage in enumerate(stages):
        col_l, col_r = st.columns([1, 4])
        with col_l:
            st.markdown(
                f"<div style='background:{stage['color']};color:white;border-radius:10px;"
                f"padding:16px 8px;text-align:center;height:100%'>"
                f"<div style='font-size:1.6rem;font-weight:700'>{stage['num']}</div>"
                f"<div style='font-size:0.9rem;font-weight:600;margin-top:4px'>{stage['name']}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        with col_r:
            items_html = "".join(f"<div style='font-size:0.82rem;color:{MGRAY};margin:3px 0;padding-left:8px;border-left:2px solid {stage['color']}44'>{w}</div>" for w in stage["what"])
            st.markdown(
                f"<div style='border:1.5px solid {stage['color']}44;border-radius:8px;padding:12px 16px;height:100%'>"
                f"<div style='font-weight:600;color:{NAVY};margin-bottom:6px'>What participants do:</div>"
                f"{items_html}"
                f"<div style='margin-top:10px;background:{stage['color']}12;border-radius:6px;padding:8px 10px'>"
                f"<span style='font-weight:700;color:{stage['color']};font-size:0.78rem'>DELIVERABLE: </span>"
                f"<span style='font-weight:600;color:{NAVY};font-size:0.85rem'>{stage['deliverable']}</span>"
                f"<div style='font-size:0.78rem;color:{MGRAY};margin-top:2px'>{stage['deliverable_desc']}</div>"
                f"</div></div>",
                unsafe_allow_html=True
            )
        if i < len(stages) - 1:
            st.markdown(f"<div style='text-align:left;padding-left:60px;color:{MGRAY};font-size:1.2rem;margin:4px 0'>↓</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PARTICIPANT DELIVERABLES
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Participant Deliverables":
    section_header("Participant Deliverables",
                   "Every participant leaves with tangible artifacts - not just awareness.")

    callout(
        "Funders and employers respond to deliverables because they are concrete, verifiable, and portable. "
        "Unlike awareness metrics, deliverables signal readiness and can be presented to employers, "
        "programs, and mentors. This design is borrowed directly from Penn State's workforce intermediary model."
    )

    deliverables = [
        ("South Side Quantum Ecosystem Guide", TEAL,
         "A plain-language map of quantum-relevant certificates, degrees, employers, and programs accessible from the South Side. Published publicly and updated annually.",
         ["Know what opportunities exist", "Have a reference document to share with family and advisors", "Understand the ecosystem before applying anywhere"]),
        ("Active HPC Account", NAVY,
         "A working account on institutional GPU-accelerated HPC infrastructure, with documentation of first successful job submission.",
         ["Demonstrate technical access", "Build on this account in future training", "Provide evidence of hands-on computing experience"]),
        ("Portfolio Project", GOLD,
         "A documented technical artifact from the workshop series - a completed HPC workflow, a quantum simulation notebook, or a GPU-accelerated data analysis.",
         ["Show employers concrete work product", "Submit to certificate or degree programs as evidence", "Build on for future projects"]),
        ("Mentor Connection", GREEN,
         "A documented, structured relationship with a professional in HPC, quantum computing, or a related field through the Chicago WHPC mentorship program.",
         ["Navigate career decisions with experienced guidance", "Access professional networks otherwise unavailable", "Receive ongoing support beyond the program"]),
        ("Personal Career Roadmap", "#8E44AD",
         "A written, specific plan: the next certificate or degree program, the next employer to contact, the next professional event to attend - personalized to each participant.",
         ["Avoid the 'now what?' problem after completing the program", "Have a concrete document to discuss with mentors", "Track progress toward specific goals"]),
    ]

    for title, color, desc, benefits in deliverables:
        col_d1, col_d2 = st.columns([2, 3])
        with col_d1:
            st.markdown(
                f"<div style='background:{color};color:white;border-radius:8px;"
                f"padding:20px;height:100%;display:flex;align-items:center;justify-content:center;text-align:center'>"
                f"<div style='font-weight:700;font-size:1rem'>{title}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        with col_d2:
            benefits_html = "".join(f"<div style='font-size:0.82rem;color:{MGRAY};margin:4px 0;padding-left:8px;border-left:2px solid {color}'>{b}</div>" for b in benefits)
            st.markdown(
                f"<div style='border:1.5px solid {color}33;border-radius:8px;padding:14px;height:100%'>"
                f"<div style='font-size:0.85rem;color:{MGRAY};margin-bottom:10px'>{desc}</div>"
                f"<div style='font-size:0.72rem;font-weight:700;color:{color};margin-bottom:4px'>PARTICIPANTS CAN USE THIS TO:</div>"
                f"{benefits_html}</div>",
                unsafe_allow_html=True
            )
        st.markdown("")


# ══════════════════════════════════════════════════════════════════════════════
# SCALING PATHWAY
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Scaling Pathway":
    section_header("Scaling Pathway",
                   "From Winter 2026 pilot to Chicago model to regional replication.")

    callout(
        "The program is designed to scale from a focused pilot to a replicable model. "
        "Each stage produces documented outcomes that justify the next stage of investment. "
        "Inspired by the Penn State workforce intermediary scaling framework."
    )

    scaling_stages = [
        ("Winter 2026 Pilot", "15-20 participants", TEAL, [
            "4 HPC workshops", "5 mentor matches", "2 facility tours", "1 cohort showcase",
            "South Side Quantum Opportunity Guide published",
            "Program toolkit documented for replication",
        ], "Proof of concept: does the model work?"),
        ("South Shore Cohorts (2027)", "40-60 participants/cohort", NAVY, [
            "Quarterly workshop series", "20+ active mentor relationships",
            "CPS Network 17 pipeline formalized", "First cohort alumni as peer facilitators",
            "2-3 employer partners confirmed", "First grant application with outcome data",
        ], "Proof of scale: can we run this consistently?"),
        ("South Side Network (2027-2028)", "200+ cumulative participants", GOLD, [
            "Multi-neighborhood programming", "City Colleges credit-bearing pathway aligned",
            "IBM apprenticeship referral pipeline", "Documented job placements or enrollments",
            "Chicago WHPC financially sustainable", "Model published and open-sourced",
        ], "Proof of impact: are participants getting outcomes?"),
        ("Chicago Model (2028-2029)", "500+ participants", GREEN, [
            "Multi-site programming across Chicago", "Formal CPS and City Colleges partnership",
            "IQMP community benefits reporting includes WHPC data",
            "State workforce development funding secured",
            "Advisory role in IQMP community engagement strategy",
        ], "Proof of system change: is the ecosystem different?"),
        ("Regional Model (2030+)", "Replication in 3+ cities", "#8E44AD", [
            "Toolkit licensed to partner organizations in other cities",
            "National quantum workforce equity framework contributed",
            "Published research on community-level participation metrics",
            "Federal workforce development program model",
        ], "Proof of replicability: can others do this?"),
    ]

    for i, (stage, scale, color, items, question) in enumerate(scaling_stages):
        col_s1, col_s2 = st.columns([1, 4])
        with col_s1:
            st.markdown(
                f"<div style='background:{color};color:white;border-radius:8px;"
                f"padding:12px 8px;text-align:center'>"
                f"<div style='font-weight:700;font-size:0.88rem'>{stage}</div>"
                f"<div style='font-size:1.2rem;font-weight:700;margin-top:6px'>{scale}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        with col_s2:
            items_html = "".join(f"<span style='background:{color}15;border:1px solid {color}44;border-radius:12px;padding:2px 10px;font-size:0.78rem;color:{NAVY};margin:2px;display:inline-block'>{it}</span>" for it in items)
            st.markdown(
                f"<div style='border:1.5px solid {color}33;border-radius:8px;padding:12px 16px'>"
                f"<div style='font-size:0.78rem;color:{color};font-weight:700;margin-bottom:6px'>EVALUATION QUESTION: {question}</div>"
                f"<div>{items_html}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        if i < len(scaling_stages) - 1:
            st.markdown(f"<div style='text-align:left;padding-left:30px;color:{MGRAY};font-size:1.2rem;margin:4px 0'>↓</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# WINTER 2026 PILOT METRICS
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Winter 2026 Pilot Metrics":
    section_header("Winter 2026 Pilot Metrics",
                   "Cohort 1 targets, deliverables, and outcome tracking framework.")

    metric_row([
        ("target participants", "15-20", "Cohort 1, Winter 2026", TEAL),
        ("HPC workshops", "4", "Linux, GPU, HPC systems, quantum simulation", NAVY),
        ("mentor matches", "5", "Structured, semester-long", GOLD),
        ("facility tours", "2", "Argonne, Fermilab, or IQMP site", GREEN),
    ])

    st.markdown("---")

    col_pilot1, col_pilot2 = st.columns(2)
    with col_pilot1:
        section_header("Cohort Deliverables", "What every participant receives")
        for item, desc in [
            ("South Side Quantum Ecosystem Guide", "Plain-language pathway map"),
            ("Active HPC Account", "Documented first job submission"),
            ("Portfolio Project", "Shareable technical artifact"),
            ("Mentor Connection", "Structured professional relationship"),
            ("Personal Career Roadmap", "Named next steps, specific to each participant"),
        ]:
            st.markdown(
                f"<div style='background:{TEAL}12;border-left:4px solid {TEAL};"
                f"padding:8px 12px;margin:5px 0;border-radius:4px'>"
                f"<div style='font-weight:600;color:{NAVY};font-size:0.85rem'>{item}</div>"
                f"<div style='font-size:0.78rem;color:{MGRAY}'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    with col_pilot2:
        section_header("Outcome Tracking", "Measured at 3, 6, and 12 months")
        metrics = [
            ("Workshop completion rate", "70%+", TEAL),
            ("Mentorship active at 90 days", "80%+", TEAL),
            ("Documented next step (6 months)", "20%+", NAVY),
            ("Certificate/degree applications", "5+", NAVY),
            ("Internship applications submitted", "5+", GOLD),
            ("Professional network growth", "10+ connections/participant", GOLD),
            ("Job or apprenticeship placement (12 months)", "1+ (stretch)", GREEN),
        ]
        for metric, target, color in metrics:
            st.markdown(
                f"<div style='background:{LGRAY};border-radius:6px;padding:8px 12px;margin:5px 0;"
                f"display:flex;justify-content:space-between;align-items:center'>"
                f"<div style='font-size:0.82rem;color:{MGRAY}'>{metric}</div>"
                f"<div style='font-weight:700;color:{color};font-size:0.9rem;margin-left:8px;white-space:nowrap'>{target}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")
    section_header("Program Schedule", "Winter 2026 cohort")
    schedule = [
        ("Week 1-2", "Awareness", "Community sessions, ecosystem guide distribution, cohort orientation"),
        ("Week 3-4", "Preparation", "Linux fundamentals, HPC account setup, first job submission"),
        ("Week 5-6", "Practice", "GPU workflows, quantum simulation intro, portfolio project start"),
        ("Week 7", "Navigation", "Mentor matching, career roadmap development, professional skills"),
        ("Week 8", "Exposure", "Facility tour, employer panel, network introductions"),
        ("Week 9-10", "Outcomes", "Portfolio completion, next step commitments, cohort showcase"),
    ]
    for week, stage, content_desc in schedule:
        st.markdown(
            f"<div style='display:flex;gap:12px;margin:6px 0;align-items:flex-start'>"
            f"<div style='background:{TEAL};color:white;padding:4px 10px;border-radius:12px;"
            f"font-size:0.78rem;font-weight:700;white-space:nowrap;min-width:70px;text-align:center'>{week}</div>"
            f"<div style='background:{LGRAY};border-radius:6px;padding:6px 12px;flex:1'>"
            f"<span style='font-weight:700;color:{NAVY};font-size:0.85rem'>{stage}: </span>"
            f"<span style='font-size:0.82rem;color:{MGRAY}'>{content_desc}</span>"
            f"</div></div>",
            unsafe_allow_html=True
        )




# ══════════════════════════════════════════════════════════════════════════════
# PRIORITY COMMUNITIES ANALYSIS (replaces composite score page)
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Opportunity and Vulnerability Analysis":
    section_header("Opportunity and Vulnerability Analysis",
                   "Community comparison using established public datasets. No composite scores or custom indices.")

    callout(
        "<strong>Methodology:</strong> This analysis uses established public datasets directly rather than "
        "constructing a composite index. The two-axis framework (Opportunity x Vulnerability) is grounded "
        "in CDC SVI methodology and urban policy research practice. Readers are invited to interpret the data. "
        "Sources: ACS 2023, CDC/ATSDR SVI 2022, CPS To&Through 2024. "
        "All figures are planning estimates, not causal measures."
    )

    st.markdown("---")
    section_header("Community Data Table",
                   "Raw indicators - no weighting, no scoring, no ranking. Readers interpret directly.")

    # Full comparison table - no scoring
    table_df = ALL_COMMUNITIES.copy()
    table_df["Community"] = table_df["area"].str.replace(" (comp.)", "*", regex=False)
    table_df["Type"] = table_df["group"]
    table_df["Bachelor's (%)"] = table_df["bach_pct"].round(1)
    table_df["HS Grad (%)"] = table_df["hs_pct"].round(1)
    table_df["College Enroll (%)"] = table_df["college_enroll_pct"].round(1)
    table_df["Youth Pop"] = table_df["youth_pop"].apply(lambda x: f"{x:,}")
    table_df["Median Income"] = table_df["med_income"].apply(lambda x: f"${x:,}")

    # Add SVI from embedded data
    svi_lookup = {
        "South Shore": 0.82, "South Chicago": 0.79, "Woodlawn": 0.84,
        "Calumet Heights": 0.68, "Greater Grand Crossing": 0.88, "Roseland": 0.86,
        "Pullman": 0.81, "Auburn Gresham": 0.89, "Chatham": 0.77, "Englewood": 0.93,
        "Hyde Park (comp.)": 0.42, "Bridgeport (comp.)": 0.58,
        "Albany Park (comp.)": 0.65, "Logan Square (comp.)": 0.41,
    }
    table_df["SVI (CDC 2022)"] = table_df["area"].map(svi_lookup)

    show = ["Community", "Type", "Bachelor's (%)", "HS Grad (%)",
            "College Enroll (%)", "Youth Pop", "Median Income", "SVI (CDC 2022)"]

    st.dataframe(
        table_df[show].sort_values("Bachelor's (%)").set_index("Community"),
        use_container_width=True,
        column_config={
            "Type": st.column_config.TextColumn(width="small"),
            "SVI (CDC 2022)": st.column_config.NumberColumn(format="%.2f"),
        }
    )
    st.caption("* = comparison community. SVI: 0 = low vulnerability, 1 = high vulnerability (CDC/ATSDR 2022).")

    st.markdown("---")
    section_header("Two-Axis Priority Framework",
                   "Opportunity (education) vs. Vulnerability (CDC SVI). Priority = upper right.")

    st.caption(
        "X-axis: CDC Social Vulnerability Index (established federal measure combining poverty, housing, "
        "transportation, disability, and household characteristics). "
        "Y-axis: Educational attainment gap from citywide average (higher = greater unmet potential). "
        "Bubble size = youth population. This approach avoids arbitrary composite weights."
    )

    # Build the matrix
    svi_df = table_df[table_df["Type"] == "Study Area"].copy()
    svi_df["svi"] = svi_df["area"].map(svi_lookup)
    svi_df["opp_gap"] = CITYWIDE_BACH - svi_df["Bachelor's (%)"]
    svi_df["youth_n"] = ALL_COMMUNITIES[ALL_COMMUNITIES["group"] == "Study Area"]["youth_pop"].values

    # Quadrant classification
    svi_med = svi_df["svi"].median()
    opp_med = svi_df["opp_gap"].median()
    def classify(row):
        if row["opp_gap"] >= opp_med and row["svi"] >= svi_med:
            return "Priority: High Opportunity Gap + High Vulnerability"
        elif row["opp_gap"] >= opp_med:
            return "Secondary: High Opportunity Gap"
        elif row["svi"] >= svi_med:
            return "Secondary: High Vulnerability"
        else:
            return "Monitor"

    svi_df["quadrant"] = svi_df.apply(classify, axis=1)
    qcolor = {
        "Priority: High Opportunity Gap + High Vulnerability": RED,
        "Secondary: High Opportunity Gap": GOLD,
        "Secondary: High Vulnerability": "#8E44AD",
        "Monitor": "#AAAAAA",
    }
    svi_df["color"] = svi_df["quadrant"].map(qcolor)

    col_m1, col_m2 = st.columns([3, 2])
    with col_m1:
        fig_priority = px.scatter(
            svi_df, x="svi", y="opp_gap",
            size="youth_n", color="quadrant",
            color_discrete_map=qcolor,
            hover_name="Community",
            hover_data={"svi": True, "opp_gap": True, "youth_n": True,
                        "Bachelor's (%)": True, "quadrant": False},
            labels={
                "svi": "Social Vulnerability Index (CDC 2022, 0=low, 1=high)",
                "opp_gap": "Educational Attainment Gap from Chicago Average (pp)",
                "youth_n": "Youth Population",
            },
            title="Opportunity Gap vs. Social Vulnerability (bubble = youth population)"
        )
        # Add community labels
        for _, row in svi_df.iterrows():
            fig_priority.add_annotation(
                x=row["svi"], y=row["opp_gap"],
                text=row["Community"].replace(" (comp.)", ""),
                showarrow=False,
                font=dict(size=9, color=NAVY, family="Arial"),
                xshift=12, yshift=6,
                bgcolor="rgba(255,255,255,0.8)", borderpad=1,
            )
        # Quadrant lines
        fig_priority.add_hline(y=opp_med, line_dash="dash", line_color="#CCCCCC",
                               annotation_text="Median gap", annotation_position="right")
        fig_priority.add_vline(x=svi_med, line_dash="dash", line_color="#CCCCCC",
                               annotation_text="Median SVI", annotation_position="top")
        # Priority label
        fig_priority.add_annotation(
            x=0.915, y=svi_df["opp_gap"].max()-1,
            text="PRIORITY", font=dict(color=RED, size=12, family="Arial", weight="bold"),
            showarrow=False, bgcolor="white", bordercolor=RED, borderwidth=1.5,
        )
        fig_priority.update_layout(
            height=440, margin=dict(l=10, r=10, t=40, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            font_color=MGRAY, showlegend=False
        )
        st.plotly_chart(fig_priority, use_container_width=True)

    with col_m2:
        st.markdown("#### Community Classification")
        st.caption("Based on CDC SVI median and educational attainment gap median for this study area group.")
        for quad, color in qcolor.items():
            areas = svi_df[svi_df["quadrant"] == quad]["Community"].tolist()
            if not areas:
                continue
            is_priority = "Priority" in quad
            st.markdown(
                f"<div style='background:{color}{'22' if is_priority else '12'};"
                f"border:{'2px' if is_priority else '1px'} solid {color};"
                f"border-radius:8px;padding:10px;margin:6px 0'>"
                f"<div style='font-weight:{'700' if is_priority else '600'};"
                f"color:{color};font-size:0.82rem;margin-bottom:6px'>{quad}</div>"
                + "".join(f"<div style='font-size:0.85rem;color:{NAVY};margin:2px 0'>- {a}</div>" for a in areas)
                + "</div>",
                unsafe_allow_html=True
            )
        callout(
            "<strong>Why not a composite score?</strong> The school closure research (Statchen et al. 2026) "
            "and standard urban policy practice compare communities using observable indicators rather than "
            "constructing weighted indices. This approach is more transparent, more defensible, and more "
            "useful for planning decisions."
        )

    st.markdown("---")
    section_header("Data Limitations")
    limitations = [
        ("ACS Sampling Error", "American Community Survey estimates contain sampling error, especially for smaller community areas. Figures should be treated as estimates with uncertainty, not precise measurements."),
        ("Geographic Boundaries", "Community area boundaries do not align with CPS school networks, zip codes, or transit catchment areas. Cross-boundary analysis requires caution."),
        ("SVI Aggregation", "CDC SVI is calculated at census tract level. Aggregating to community areas introduces smoothing that may obscure within-area variation."),
        ("Workforce Projections", "IQMP job projections are announced targets, not confirmed hiring plans. Actual workforce demand may differ."),
        ("Planning Tool Only", "This dashboard is intended for community planning and program design. It does not support causal claims about neighborhood outcomes."),
    ]
    for title, desc in limitations:
        st.markdown(
            f"<div style='background:{LGRAY};border-left:3px solid {MGRAY};"
            f"padding:8px 12px;margin:5px 0;border-radius:4px'>"
            f"<span style='font-weight:600;color:{NAVY}'>{title}: </span>"
            f"<span style='font-size:0.85rem;color:{MGRAY}'>{desc}</span></div>",
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# THEORY OF CHANGE
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Theory of Change":
    section_header("Theory of Change",
                   "How and why Quantum x HPC Pathways is expected to produce its outcomes.")

    callout(
        "A theory of change makes explicit the assumptions linking program activities to outcomes. "
        "This framework is designed for NSF, DOE, and foundation reviewers who evaluate program logic "
        "before funding. Each arrow represents a testable assumption."
    )

    toc_stages = [
        ("Problem", RED,
         "South Side residents are geographically proximate to one of the nation's largest quantum investments "
         "but institutionally disconnected from its workforce pipeline. No community-level intermediary "
         "systematically connects residents to quantum and HPC pathways.",
         []),
        ("Intervention", TEAL,
         "Quantum x HPC Pathways provides community education, HPC technical training, mentorship, "
         "and pathway navigation through Chicago WHPC - a trusted civic workforce intermediary.",
         ["IF: residents lack information about quantum/HPC careers",
          "IF: HPC skills are the accessible entry point to the quantum ecosystem",
          "IF: mentorship increases navigation capacity",
          "IF: institutional access (HPC accounts, facility tours) builds confidence"]),
        ("Outputs", NAVY,
         "Participants complete workshops, receive deliverables, and make professional connections.",
         ["15-20 participants per cohort",
          "4-6 hands-on HPC workshops",
          "5+ mentor matches per cohort",
          "South Side Quantum Opportunity Guide published",
          "2+ facility tours delivered"]),
        ("Short-Term Outcomes", GOLD,
         "Participants demonstrate increased awareness, technical skills, and professional network growth.",
         ["Increased understanding of quantum/HPC careers (pre/post surveys)",
          "Demonstrated HPC competency (portfolio artifacts)",
          "Active mentorship relationships at 90 days",
          "Documented next step identified within 6 months"]),
        ("Long-Term Outcomes", GREEN,
         "Participants enter educational programs, internships, or employment in the advanced technology ecosystem.",
         ["Certificate or degree program enrollment",
          "Internship or research experience placement",
          "Professional network connections sustained",
          "Peer facilitation (alumni as mentors)"]),
        ("Impact", "#8E44AD",
         "South Side residents participate in Illinois's quantum and advanced technology economy at higher rates. "
         "IQMP and ecosystem employers have a community-connected talent pipeline.",
         ["Measurable South Side participation in quantum workforce",
          "Community-level data informing IQMP equity commitments",
          "Replicable model for other cities"]),
    ]

    for i, (stage, color, desc, assumptions) in enumerate(toc_stages):
        col_s, col_c = st.columns([1, 5])
        with col_s:
            st.markdown(
                f"<div style='background:{color};color:white;border-radius:8px;"
                f"padding:12px;text-align:center;height:100%'>"
                f"<div style='font-weight:700;font-size:0.9rem'>{stage}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        with col_c:
            assumptions_html = "".join(
                f"<div style='font-size:0.78rem;color:{color};margin:2px 0;"
                f"padding-left:8px;border-left:2px solid {color}55'>"
                f"<em>{a}</em></div>" for a in assumptions
            ) if assumptions else ""
            st.markdown(
                f"<div style='border:1.5px solid {color}33;border-radius:8px;"
                f"padding:10px 14px;height:100%'>"
                f"<div style='font-size:0.85rem;color:{MGRAY}'>{desc}</div>"
                f"{('<div style=\"margin-top:8px;font-size:0.75rem;font-weight:700;color:' + color + '\">KEY ASSUMPTIONS:</div>' + assumptions_html) if assumptions else ''}"
                f"</div>",
                unsafe_allow_html=True
            )
        if i < len(toc_stages) - 1:
            st.markdown(f"<div style='text-align:left;padding-left:30px;color:{MGRAY};font-size:1.2rem;margin:4px 0'>↓</div>", unsafe_allow_html=True)

    st.markdown("---")
    section_header("Research and Evaluation Questions")
    eval_qs = [
        ("RQ1", "Can community-based pathway navigation increase awareness of quantum and HPC careers among underrepresented South Side residents?",
         "Pre/post survey measuring career awareness and knowledge of pathways",
         "TEAL"),
        ("RQ2", "Can structured HPC workshops build foundational technical skills accessible to participants without prior computing experience?",
         "Skills assessment: portfolio artifact completion, HPC account usage, self-reported competency",
         "NAVY"),
        ("RQ3", "Can mentorship increase participants' capacity to navigate the quantum ecosystem?",
         "90-day mentorship continuation rate, documented next steps, professional network growth",
         "GOLD"),
        ("RQ4", "Can community-based programs generate participation in internships, credentials, and employment in quantum-relevant fields?",
         "6-month and 12-month tracking of internship applications, credential enrollment, employment",
         "GREEN"),
    ]
    for rq, question, measure, color_name in eval_qs:
        color = {"TEAL": TEAL, "NAVY": NAVY, "GOLD": GOLD, "GREEN": GREEN}[color_name]
        st.markdown(
            f"<div style='background:{LGRAY};border-radius:8px;padding:14px;margin:8px 0'>"
            f"<div style='display:flex;gap:12px;align-items:flex-start'>"
            f"<div style='background:{color};color:white;padding:4px 10px;border-radius:12px;"
            f"font-weight:700;font-size:0.85rem;white-space:nowrap'>{rq}</div>"
            f"<div style='flex:1'>"
            f"<div style='font-weight:600;color:{NAVY};margin-bottom:4px'>{question}</div>"
            f"<div style='font-size:0.8rem;color:{MGRAY}'><strong>Measure:</strong> {measure}</div>"
            f"</div></div></div>",
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# ILLINOIS ALIGNMENT
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Illinois Alignment":
    section_header("Alignment with Illinois Priorities",
                   "How Quantum x HPC Pathways connects to state, federal, and institutional workforce goals.")

    alignment_items = [
        ("Illinois Quantum and Microelectronics Park (IQMP)", NAVY,
         "IQMP is the nation's first campus purpose-built for quantum commercialization, "
         "built on the former US Steel South Works site on Chicago's South Side. "
         "The state has invested $500M+ in IQMP infrastructure.",
         "Quantum x HPC Pathways builds community awareness and workforce readiness for IQMP's eventual hiring needs. "
         "Program participants are geographically proximate to IQMP and targeted for early pipeline development.",
         ["Community trust building for IQMP", "Local talent pipeline development", "Equity metrics for IQMP community benefits reporting"]),
        ("Chicago Quantum Exchange (CQE) Workforce Mission", TEAL,
         "CQE leads two federal designations: an EDA Tech Hub (The Bloch) and an NSF Regional Innovation Engines development award. "
         "CQE's 2026 unified strategy explicitly calls for community-level workforce access programs.",
         "Quantum x HPC Pathways is the community-level implementation of what CQE's Advancing Together strategy calls for. "
         "Program data on South Side participation fills a gap CQE has identified in workforce research.",
         ["Direct implementation of CQE community strategy", "Data partner for CQE workforce research", "EDA Tech Hub workforce component"]),
        ("IBM FutureNow Chicago", GREEN,
         "IBM announced 750 full-time jobs and 500 apprenticeships at IQMP, designed with City Colleges of Chicago. "
         "Olive Harvey College is the designated anchor for this program.",
         "Chicago WHPC can serve as a community feeder into the IBM/City Colleges pipeline. "
         "Program participants who complete HPC workshops are better positioned for IBM apprenticeship applications.",
         ["Community feeder for IBM apprenticeships", "Awareness pipeline for IBM job announcements", "South Side participant preparation"]),
        ("National Quantum Algorithm Center (NQAC)", GOLD,
         "NQAC is a partnership between IBM and Illinois institutions designed to accelerate quantum algorithm development. "
         "It represents Illinois's position at the national frontier of quantum research.",
         "Chicago WHPC communicates NQAC's existence and significance to community audiences who would otherwise not encounter it.",
         ["Public awareness of NQAC", "Career visibility for NQAC-adjacent roles"]),
        ("Illinois STEM Workforce Strategy", "#8E44AD",
         "Illinois has articulated goals around STEM workforce development, talent retention, and equitable access to technology careers. "
         "The ISTC 2026 report documents 33,441 quantum-relevant completions and calls for equity-focused pipeline development.",
         "Quantum x HPC Pathways directly implements the ISTC's call for community-level workforce access and navigation. "
         "Program data contributes to Illinois's capacity to measure community participation in the quantum pipeline.",
         ["ISTC workforce data contribution", "Equity-focused pipeline development", "Talent retention through local opportunity"]),
    ]

    for org, color, context, alignment, bullets in alignment_items:
        st.markdown(
            f"<div style='background:{color}10;border:2px solid {color}44;border-radius:10px;"
            f"padding:16px 20px;margin:12px 0'>"
            f"<div style='font-weight:700;color:{color};font-size:1rem;margin-bottom:8px'>{org}</div>"
            f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:10px'>"
            f"<div><div style='font-size:0.72rem;font-weight:700;color:{MGRAY};margin-bottom:4px'>CONTEXT</div>"
            f"<div style='font-size:0.82rem;color:{MGRAY}'>{context}</div></div>"
            f"<div><div style='font-size:0.72rem;font-weight:700;color:{color};margin-bottom:4px'>OUR ALIGNMENT</div>"
            f"<div style='font-size:0.82rem;color:{MGRAY}'>{alignment}</div></div>"
            f"</div>"
            f"<div style='display:flex;flex-wrap:wrap;gap:6px'>"
            + "".join(f"<span style='background:{color}22;border:1px solid {color}44;border-radius:12px;"
                      f"padding:2px 10px;font-size:0.75rem;color:{NAVY}'>{b}</span>" for b in bullets)
            + "</div></div>",
            unsafe_allow_html=True
        )

    st.markdown("---")
    section_header("Stakeholder Map")
    st.caption("Key stakeholders across five sectors, with Chicago WHPC positioned as the civic workforce intermediary.")

    stakeholder_groups = {
        "Government": (NAVY, ["State of Illinois (DCEO)", "City of Chicago", "Cook County BED", "Illinois General Assembly"]),
        "Research": (TEAL, ["Argonne National Laboratory", "Fermilab", "National Quantum Algorithm Center"]),
        "Universities": (GOLD, ["University of Chicago", "University of Illinois Chicago", "Northwestern University", "UIUC"]),
        "Industry": (GREEN, ["IBM Quantum", "PsiQuantum", "Infleqtion", "EeroQ", "Quantum Machines", "Diraq"]),
        "Education": ("#8E44AD", ["Chicago Public Schools", "City Colleges of Chicago", "Olive Harvey College", "Chicago State University"]),
        "Civic Layer": (RED, ["Chicago WHPC", "South Side Libraries", "Community Organizations", "Park District"]),
    }

    cols = st.columns(3)
    for i, (group, (color, members)) in enumerate(stakeholder_groups.items()):
        with cols[i % 3]:
            is_civic = group == "Civic Layer"
            st.markdown(
                f"<div style='background:{color}{'25' if is_civic else '12'};"
                f"border:{'2.5px' if is_civic else '1.5px'} solid {color};"
                f"border-radius:8px;padding:12px;margin:6px 0'>"
                f"<div style='font-weight:700;color:{color};font-size:0.85rem;margin-bottom:8px'>{group}</div>"
                + "".join(f"<div style='font-size:0.8rem;color:{NAVY};margin:3px 0;padding-left:6px;border-left:2px solid {color}55'>{m}</div>" for m in members)
                + ("</div><div style='font-size:0.75rem;color:white;background:' + color + ';padding:4px 8px;margin-top:8px;border-radius:4px;text-align:center'>Chicago WHPC connects all sectors</div>" if is_civic else "</div>"),
                unsafe_allow_html=True
            )


# ══════════════════════════════════════════════════════════════════════════════
# BUILDING THE ECOSYSTEM
# ══════════════════════════════════════════════════════════════════════════════
if sub_choice == "Building the Ecosystem":
    section_header("Building the Ecosystem",
                   "From research to commercialization to workforce. Chicago WHPC operates at the community layer.")

    callout(
        "The quantum ecosystem in Illinois is not a single institution. It is a layered system "
        "spanning fundamental research, technology commercialization, industry deployment, "
        "and community workforce development. Chicago WHPC operates at the community layer - "
        "connecting residents to the layers above."
    )

    layers = [
        ("Research Layer", NAVY, [
            ("Argonne National Laboratory", "DOE national lab, quantum research and computing"),
            ("Fermilab", "Particle physics and quantum science, SMQ* program"),
            ("University of Chicago", "#1 US quantum physics (Nature Index 2025)"),
            ("Northwestern University", "Quantum materials and photonics research"),
            ("University of Illinois Chicago", "1,401 quantum-relevant completions in 2024"),
            ("UIUC Grainger College", "#5 US engineering, Chicago School of Engineering pipeline"),
        ], "Produces fundamental knowledge and trains graduate-level talent"),
        ("Commercialization Layer", TEAL, [
            ("IQMP", "Nation's first quantum commercialization campus, South Side lakefront"),
            ("Chicago Quantum Exchange (CQE)", "Ecosystem coordinator, EDA Tech Hub, NSF Engines"),
            ("Duality", "World's first quantum startup accelerator"),
            ("National Quantum Algorithm Center", "IBM + Illinois quantum algorithm development"),
        ], "Translates research into products, companies, and economic activity"),
        ("Industry Layer", GOLD, [
            ("IBM Quantum", "750 jobs + 500 apprenticeships at IQMP, FutureNow Chicago"),
            ("PsiQuantum", "Large-scale quantum computing, IQMP tenant"),
            ("Infleqtion", "Quantum sensing and computing, Chicago-based"),
            ("EeroQ", "Helium-3 quantum computing, Chicago startup"),
            ("Quantum Machines", "Quantum control systems"),
        ], "Creates jobs, demand for talent, and employer relationships"),
        ("Education Layer", GREEN, [
            ("City Colleges of Chicago", "1,000+ quantum-relevant completions, IBM pipeline, Chicago School of Engineering"),
            ("Chicago Public Schools", "Chi-Craft competition, DPI quantum teacher training"),
            ("Olive Harvey College", "SMQ* host site, IBM apprenticeship anchor"),
        ], "Prepares students through formal credentials and structured programs"),
        ("Community Layer", RED, [
            ("Chicago WHPC", "Civic workforce intermediary - community education, HPC training, mentorship, navigation"),
            ("South Side Libraries", "Trusted community venue partners"),
            ("Community Organizations", "Participant recruitment, community trust"),
        ], "Chicago WHPC bridges community residents to all layers above"),
    ]

    for i, (layer, color, orgs, role) in enumerate(layers):
        is_whpc = layer == "Community Layer"
        st.markdown(
            f"<div style='background:{color}{'20' if is_whpc else '10'};"
            f"border:{'3px' if is_whpc else '1.5px'} solid {color};"
            f"border-radius:10px;padding:14px 18px;margin:6px 0'>"
            f"<div style='display:flex;justify-content:space-between;align-items:flex-start'>"
            f"<div style='font-weight:700;color:{color};font-size:1rem'>{layer}</div>"
            f"<div style='font-size:0.78rem;color:{MGRAY};font-style:italic;max-width:40%'>{role}</div>"
            f"</div>"
            f"<div style='display:flex;flex-wrap:wrap;gap:8px;margin-top:10px'>"
            + "".join(
                f"<div style='background:white;border:1px solid {color}44;border-radius:6px;"
                f"padding:5px 10px;font-size:0.78rem'>"
                f"<div style='font-weight:600;color:{NAVY}'>{org}</div>"
                f"<div style='color:{MGRAY}'>{desc}</div></div>"
                for org, desc in orgs
            )
            + "</div></div>",
            unsafe_allow_html=True
        )
        if i < len(layers) - 1:
            st.markdown(
                f"<div style='text-align:center;font-size:1.2rem;color:{MGRAY};"
                f"margin:2px 0'>v</div>",
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
