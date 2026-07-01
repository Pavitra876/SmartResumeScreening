"""
theme.py
Custom visual styling for the Smart Resume Screening dashboard.
Injects CSS and provides reusable HTML components (score gauge, cards)
so the app feels like a designed product rather than a default Streamlit page.
"""

import streamlit as st

# ---- Design tokens ----
NAVY = "#0F1729"
NAVY_LIGHT = "#1E293B"
TEAL = "#10B981"
TEAL_DARK = "#059669"
AMBER = "#F59E0B"
SLATE = "#64748B"
BG = "#F8FAFC"
CARD_BG = "#FFFFFF"
BORDER = "#E2E8F0"


def inject_custom_css():
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {BG};
        }}

        /* Hide default Streamlit chrome for a cleaner custom look */
        header[data-testid="stHeader"] {{
            background: transparent;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {NAVY} 0%, {NAVY_LIGHT} 100%);
        }}
        section[data-testid="stSidebar"] * {{
            color: #E2E8F0 !important;
        }}
        section[data-testid="stSidebar"] button {{
            background-color: rgba(255,255,255,0.06) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            color: #F8FAFC !important;
        }}
        section[data-testid="stSidebar"] button:hover {{
            background-color: {TEAL} !important;
            border-color: {TEAL} !important;
        }}

        /* Headings */
        h1 {{
            font-weight: 800 !important;
            color: {NAVY} !important;
            letter-spacing: -0.02em;
        }}
        h2, h3 {{
            font-weight: 700 !important;
            color: {NAVY} !important;
        }}

        /* Card container */
        .src-card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 1.5rem 1.75rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04);
        }}

        .src-eyebrow {{
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.72rem;
            font-weight: 700;
            color: {TEAL_DARK};
            margin-bottom: 0.25rem;
        }}

        .src-pill {{
            display: inline-block;
            padding: 0.2rem 0.7rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
        }}
        .src-pill-match {{
            background-color: #ECFDF5;
            color: {TEAL_DARK};
            border: 1px solid #A7F3D0;
        }}
        .src-pill-gap {{
            background-color: #FFFBEB;
            color: #B45309;
            border: 1px solid #FDE68A;
        }}

        /* Skill chips */
        .src-chip-row {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }}
        .src-chip {{
            padding: 0.35rem 0.85rem;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 500;
        }}
        .src-chip-match {{ background-color: #ECFDF5; color: {TEAL_DARK}; border: 1px solid #A7F3D0; }}
        .src-chip-gap {{ background-color: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }}

        /* Buttons */
        .stButton button {{
            border-radius: 10px;
            font-weight: 600;
            transition: transform 0.1s ease;
        }}
        .stButton button[kind="primary"] {{
            background-color: {TEAL};
            border-color: {TEAL};
        }}
        .stButton button[kind="primary"]:hover {{
            background-color: {TEAL_DARK};
            border-color: {TEAL_DARK};
            transform: translateY(-1px);
        }}

        /* Metric tweak */
        div[data-testid="stMetricValue"] {{
            font-family: 'Courier New', monospace;
            color: {NAVY};
        }}

        /* File uploader */
        section[data-testid="stFileUploaderDropzone"] {{
            background-color: {BG};
            border: 2px dashed {BORDER};
            border-radius: 12px;
        }}

        /* Tabs */
        button[data-baseweb="tab"] {{
            font-weight: 600;
        }}
    </style>
    """, unsafe_allow_html=True)


def render_score_gauge(score: float, label: str = "ATS Score") -> str:
    """
    Returns an SVG radial gauge as an HTML string, showing the score
    as a circular progress ring with the percentage in the center.
    Color shifts from amber (low) to teal (high) based on score.
    """
    radius = 70
    stroke_width = 14
    circumference = 2 * 3.14159 * radius
    progress = max(0, min(score, 100)) / 100
    dash_offset = circumference * (1 - progress)

    color = TEAL if score >= 60 else (AMBER if score >= 35 else "#EF4444")

    svg = f"""
    <div style="display:flex; align-items:center; justify-content:center; flex-direction:column;">
      <svg width="180" height="180" viewBox="0 0 180 180">
        <circle cx="90" cy="90" r="{radius}" fill="none" stroke="#E2E8F0" stroke-width="{stroke_width}" />
        <circle cx="90" cy="90" r="{radius}" fill="none" stroke="{color}" stroke-width="{stroke_width}"
          stroke-dasharray="{circumference}" stroke-dashoffset="{dash_offset}"
          stroke-linecap="round" transform="rotate(-90 90 90)" />
        <text x="90" y="85" text-anchor="middle" font-size="34" font-weight="800"
          font-family="Courier New, monospace" fill="{NAVY}">{score:.0f}%</text>
        <text x="90" y="110" text-anchor="middle" font-size="12" font-weight="600"
          letter-spacing="1" fill="{SLATE}">{label.upper()}</text>
      </svg>
    </div>
    """
    return svg


def card_open(eyebrow: str = "", title: str = ""):
    """Open a styled card div. Must be paired with card_close()."""
    html = '<div class="src-card">'
    if eyebrow:
        html += f'<div class="src-eyebrow">{eyebrow}</div>'
    if title:
        html += f'<h3 style="margin-top:0;">{title}</h3>'
    st.markdown(html, unsafe_allow_html=True)


def card_close():
    st.markdown('</div>', unsafe_allow_html=True)


def render_skill_chips(skills: list[str], kind: str = "match"):
    """Render a row of pill-shaped skill chips. kind = 'match' or 'gap'."""
    css_class = "src-chip-match" if kind == "match" else "src-chip-gap"
    if not skills:
        st.markdown(
            f'<span style="color:{SLATE}; font-size:0.9rem;">'
            f'{"No matches found." if kind == "match" else "No gaps — great fit!"}</span>',
            unsafe_allow_html=True,
        )
        return
    chips_html = "".join(f'<span class="src-chip {css_class}">{s}</span>' for s in skills)
    st.markdown(f'<div class="src-chip-row">{chips_html}</div>', unsafe_allow_html=True)