from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from nanomax_model import AsymmetricDNAAptamerDesigner


APP_DIR = Path(__file__).resolve().parent

def resolve_asset(*names: str) -> Path:
    """Find an asset whether it is stored in the repository root or /assets."""
    for name in names:
        for candidate in (APP_DIR / name, APP_DIR / "assets" / name):
            if candidate.exists():
                return candidate
    return APP_DIR / names[0]

LOGO_PATH = resolve_asset("hitsz-logo-transparent.png", "hitsz-logo.jpg")
ASYMMETRY_FIG = resolve_asset("nanomax_asymmetry_index.png")
WORKFLOW_FIG = resolve_asset("nanomax_workflow.png")
NANO_3D_FIG = resolve_asset("nanoparticle_3d_asymmetry.png")


st.set_page_config(
    page_title="NanoMax Aptamer Inverse Folding Model",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium light scientific interface styling.
st.markdown(
    """
    <style>
    :root {
        --ink: #0B1F3A;
        --ink-2: #243A55;
        --teal: #0B7A83;
        --teal-2: #0E6174;
        --teal-soft: #EAF6F5;
        --gold: #C49335;
        --gold-soft: #FBF5E8;
        --pearl: #FBFCFD;
        --warm: #F7F6F2;
        --panel: #FFFFFF;
        --line: #DDE5EA;
        --muted: #65758A;
        --shadow: 0 14px 38px rgba(28,49,74,.08);
    }

    html, body { color-scheme: light; }

    .stApp {
        background:
            radial-gradient(circle at 8% 3%, rgba(11,122,131,.035), transparent 23%),
            radial-gradient(circle at 93% 7%, rgba(196,147,53,.045), transparent 20%),
            linear-gradient(180deg, #FCFDFE 0%, #F7F9FA 62%, #F1F5F7 100%);
        color: var(--ink);
    }

    .stApp p, .stApp span, .stApp label, .stApp li,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: var(--ink);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F7F9FA 100%);
        border-right: 1px solid #E3E9ED;
        box-shadow: 8px 0 32px rgba(26,49,75,.035);
    }

    [data-testid="stSidebar"] > div:first-child { padding-top: .9rem; }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 { color: #172A43 !important; }

    [data-testid="stSidebar"] img {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
        object-fit: contain;
    }

    .sidebar-brand {
        text-align: center;
        margin: -.15rem 0 1rem 0;
        padding-bottom: .9rem;
        border-bottom: 1px solid #E6EBEF;
    }
    .sidebar-brand .brand-main {
        font-family: Georgia, 'Times New Roman', serif;
        font-size: .92rem;
        letter-spacing: .075em;
        font-weight: 700;
        color: var(--ink) !important;
    }
    .sidebar-brand .brand-sub {
        margin-top: .16rem;
        color: #738297 !important;
        font-size: .67rem;
        letter-spacing: .18em;
        text-transform: uppercase;
    }

    .block-container {
        max-width: 1420px;
        padding-top: 1.2rem;
        padding-bottom: 3.5rem;
    }

    .hero-shell {
        position: relative;
        overflow: hidden;
        padding: 1.8rem 2.15rem 1.65rem 2.15rem;
        margin-bottom: 1rem;
        border-radius: 22px;
        border: 1px solid #D8E4E9;
        background:
            radial-gradient(circle at 91% 12%, rgba(11,122,131,.085), transparent 21%),
            radial-gradient(circle at 98% 92%, rgba(196,147,53,.07), transparent 18%),
            linear-gradient(115deg, #FFFFFF 0%, #F8FCFD 66%, #EEF7F9 100%);
        box-shadow: var(--shadow), inset 0 1px 0 rgba(255,255,255,.98);
    }

    .hero-shell::before {
        content: "";
        position: absolute;
        width: 310px;
        height: 310px;
        right: -120px;
        top: -155px;
        border-radius: 50%;
        border: 1px solid rgba(11,122,131,.11);
        box-shadow: inset 0 0 0 34px rgba(11,122,131,.015);
    }

    .hero-shell::after {
        content: "";
        position: absolute;
        width: 76px;
        height: 2px;
        top: 1.55rem;
        left: 17.3rem;
        background: linear-gradient(90deg, var(--gold), rgba(196,147,53,.15));
    }

    .eyebrow {
        color: var(--teal-2) !important;
        text-transform: uppercase;
        letter-spacing: .19em;
        font-size: .73rem;
        font-weight: 780;
        margin-bottom: .65rem;
    }

    .hero-title {
        margin: 0;
        max-width: 1100px;
        font-family: Georgia, 'Times New Roman', serif;
        font-size: clamp(2.0rem, 3vw, 3.15rem);
        line-height: 1.03;
        font-weight: 700;
        letter-spacing: -.027em;
        white-space: nowrap;
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink);
    }

    @media (max-width: 1100px) {
        .hero-title {white-space: normal; font-size: 2.15rem;}
        .hero-shell::after {display:none;}
    }

    .hero-sub {
        margin-top: .75rem;
        color: #53657A !important;
        font-size: 1rem;
        max-width: 930px;
        line-height: 1.55;
    }

    .chip-row {margin-top: 1rem; display: flex; gap: .5rem; flex-wrap: wrap;}
    .chip {
        display: inline-block;
        padding: .32rem .72rem;
        border-radius: 999px;
        border: 1px solid #D4E4E7;
        color: #125F68 !important;
        background: linear-gradient(180deg, #F3FBFA, #EAF5F5);
        font-size: .75rem;
        font-weight: 620;
        box-shadow: inset 0 1px 0 #FFFFFF;
    }

    .credit-card {
        border: 1px solid #DDE5EA;
        border-top: 3px solid var(--gold);
        border-radius: 16px;
        padding: 1rem 1rem .95rem 1rem;
        margin-top: 1.1rem;
        background: linear-gradient(145deg, #FFFFFF 0%, #F8FAFB 100%);
        box-shadow: 0 10px 26px rgba(28,49,74,.055);
        line-height: 1.55;
    }
    .sidebar-divider {
        height: 1px;
        margin: 1.15rem 0 .2rem 0;
        background: linear-gradient(90deg, transparent, rgba(196,147,53,.45), transparent);
    }
    .credit-card b {color: var(--ink) !important;}
    .credit-card .small {color: #798699 !important; font-size: .79rem;}

    .section-kicker {
        color: var(--teal) !important;
        font-size: .72rem;
        letter-spacing: .18em;
        text-transform: uppercase;
        font-weight: 800;
        margin-bottom: .16rem;
    }
    .section-title {
        color: var(--ink) !important;
        font-family: Georgia, 'Times New Roman', serif;
        font-size: 1.72rem;
        font-weight: 700;
        margin: 0 0 .45rem 0;
    }

    .science-card {
        height: 100%;
        padding: 1.05rem 1.15rem;
        border-radius: 16px;
        border: 1px solid #E0E6EA;
        background: linear-gradient(180deg, #FFFFFF 0%, #FBFCFD 100%);
        box-shadow: 0 9px 24px rgba(28,49,74,.05), inset 0 1px 0 #FFFFFF;
    }
    .science-card h4 {margin: 0 0 .42rem 0; color: var(--ink) !important; font-family: Georgia, serif;}
    .science-card p {margin: 0; color: #66768A !important; font-size: .89rem; line-height: 1.55;}

    .ready-card {
        text-align: center;
        padding: 2.2rem 1.4rem;
        margin-top: .8rem;
        border-radius: 20px;
        border: 1px solid #DDE6EA;
        background: radial-gradient(circle at 50% 0%, rgba(11,122,131,.055), transparent 29%), linear-gradient(180deg, #FFFFFF, #F9FBFC);
        box-shadow: 0 12px 32px rgba(28,49,74,.05);
    }
    .ready-icon {font-size: 2rem; margin-bottom: .45rem;}
    .ready-card h3 {margin: .2rem 0 .35rem 0; color: var(--ink) !important; font-family: Georgia, serif;}
    .ready-card p {color: #68788B !important; margin: 0 auto; max-width: 720px;}

    .result-heading {display:flex;align-items:center;gap:.6rem;margin-bottom:.1rem;}
    .result-heading .dna-mark {
        width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center;
        background:var(--teal-soft);color:var(--teal) !important;font-weight:800;border:1px solid #D3E8E7;font-size:.68rem;
    }
    .result-heading .result-title {font-family:Georgia,'Times New Roman',serif;font-size:1.55rem;font-weight:700;color:var(--ink) !important;}

    .sequence-box {
        padding: .72rem .9rem;border:1px solid #DEE6EA;border-radius:11px;
        background:linear-gradient(180deg,#FAFBFC,#F4F7F8);color:#23364C !important;
        font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;font-size:.82rem;
        white-space:nowrap;overflow-x:auto;box-shadow:inset 0 1px 2px rgba(28,49,74,.025);
    }

    .metric-card {
        min-height:102px;padding:.82rem .95rem;border-radius:15px;border:1px solid #DDE5EA;
        background:linear-gradient(180deg,#FFFFFF,#FBFCFD);box-shadow:0 8px 22px rgba(28,49,74,.05);
        display:flex;gap:.72rem;align-items:center;
    }
    .metric-card .metric-icon {
        flex:0 0 auto;width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;
        font-weight:800;font-size:.8rem;background:#EEF7F7;color:var(--teal) !important;border:1px solid #D5E9E8;
    }
    .metric-card.gold .metric-icon {background:var(--gold-soft);color:#A56E0C !important;border-color:#EFE0BF;}
    .metric-card.purple .metric-icon {background:#F2EEFF;color:#6C4BD3 !important;border-color:#E1D7FF;}
    .metric-card .metric-label {font-size:.78rem;font-weight:650;color:#526277 !important;margin-bottom:.08rem;}
    .metric-card .metric-value {font-family:Georgia,serif;font-size:1.65rem;font-weight:700;color:var(--ink) !important;line-height:1.05;}
    .metric-card.teal .metric-value {color:#087A63 !important;}
    .metric-card.gold .metric-value {color:#B37512 !important;}
    .metric-card.blue .metric-value {color:#17689B !important;}
    .metric-card.purple .metric-value {color:#6641C2 !important;}

    [data-testid="stVerticalBlockBorderWrapper"] {
        border:1px solid #DFE6EA !important;border-radius:17px !important;background:rgba(255,255,255,.94) !important;
        box-shadow:0 10px 28px rgba(28,49,74,.055);
    }

    .chart-card-title {display:flex;align-items:center;gap:.48rem;font-family:Georgia,serif;font-weight:700;color:var(--ink) !important;font-size:1rem;margin:.05rem 0 -.35rem 0;}
    .chart-dot {width:9px;height:9px;border-radius:50%;background:var(--teal);display:inline-block;}

    .stButton > button[kind="primary"] {
        border:0 !important;background:linear-gradient(105deg,#0A8B8B 0%,#0B4D6C 55%,#0B2947 100%) !important;
        color:white !important;font-weight:740 !important;min-height:3.2rem;border-radius:11px !important;
        box-shadow:0 11px 26px rgba(11,53,76,.20);
    }
    .stButton > button[kind="primary"]:hover {transform:translateY(-1px);box-shadow:0 15px 34px rgba(11,53,76,.25);filter:brightness(1.025);}
    .stButton > button:not([kind="primary"]) {background:#FFFFFF !important;color:#26384E !important;border:1px solid #D6DEE4 !important;border-radius:10px !important;box-shadow:0 3px 10px rgba(28,49,74,.025);}

    .stTabs [data-baseweb="tab-list"] {gap:.25rem;border-bottom:1px solid #DDE4E8;}
    .stTabs [data-baseweb="tab"] {border-radius:8px 8px 0 0;padding-left:.78rem;padding-right:.78rem;color:#415269 !important;font-weight:580;}
    .stTabs [aria-selected="true"] {color:#0B6E77 !important;font-weight:760;background:linear-gradient(180deg,#F8FEFD,#EEF8F7) !important;}

    [data-testid="stSlider"] [role="slider"], div[data-baseweb="slider"] [role="slider"] {
        background:#0B7A83 !important;border-color:#0B7A83 !important;box-shadow:0 0 0 3px rgba(11,122,131,.10) !important;
    }
    [data-testid="stSlider"] div[data-baseweb="slider"] > div > div, div[data-baseweb="slider"] > div > div > div {background-color:#0B7A83 !important;}

    [data-testid="stExpander"] {border-color:#DCE4E9 !important;border-radius:12px !important;background:rgba(255,255,255,.92);box-shadow:0 4px 14px rgba(28,49,74,.025);}
    [data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {color:#26384E !important;}

    .project-note {border-left:3px solid var(--gold);padding:.75rem .95rem;color:#405269 !important;background:#FBF7ED;border-radius:0 12px 12px 0;margin:.65rem 0 1rem 0;}
    div[data-testid="stCodeBlock"] pre, div[data-testid="stCodeBlock"] code {background:#F4F7F8 !important;color:#14263C !important;border-color:#DEE5EA !important;}
    [data-testid="stDataFrame"] {background:#FFFFFF !important;border-radius:12px;box-shadow:0 6px 18px rgba(28,49,74,.035);}
    [data-testid="stAlert"] {background:#EEF7F7 !important;color:#26384E !important;border-color:#D4E8E7 !important;}
    .footer-line {margin-top:1.9rem;padding-top:.9rem;border-top:1px solid #E1E7EA;color:#7B8898 !important;font-size:.76rem;text-align:center;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- Sidebar ----------------
with st.sidebar:
    if LOGO_PATH.exists():
        logo_left, logo_mid, logo_right = st.columns([0.24, 0.52, 0.24])
        with logo_mid:
            st.image(str(LOGO_PATH), use_container_width=True)
    st.markdown(
        """
        <div class="sidebar-brand">
          <div class="brand-main">NANOMAX GROUP</div>
          <div class="brand-sub">HIT Shenzhen</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### ⚙ Design parameters")
    length = st.slider("DNA length (nt)", 100, 200, 150, 5)
    branches = st.slider("Target branches", 2, 5, 3, 1)
    loops = st.slider("Target loops", 3, 8, 5, 1)
    gc_target_percent = st.slider("GC target (%)", 40, 80, 60, 1)

    with st.expander("Advanced / reproducibility"):
        use_seed = st.checkbox("Use fixed random seed", value=True)
        seed = st.number_input("Seed", min_value=0, max_value=999999, value=42, step=1)

    generate = st.button("⚡ Generate DNA aptamer", type="primary", use_container_width=True)

    if st.button("Clear generated result", use_container_width=True):
        st.session_state.pop("nanomax_result", None)
        st.session_state.pop("nanomax_params", None)
        st.rerun()

    # Project attribution deliberately sits at the bottom of the control panel.
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="credit-card">
          <div class="small">A Project by</div>
          <b>Prof. Xingyi Ma</b><br>
          <span>NanoMax Group, HIT Shenzhen</span>
          <div style="height:.75rem"></div>
          <div class="small">Design and Developed by</div>
          <b>Doctor Sukhera (学睿)</b>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------- Hero ----------------
st.markdown(
    """
    <div class="hero-shell">
      <div class="eyebrow">NanoMax Group · HIT Shenzhen</div>
      <h1 class="hero-title">NanoMax Aptamer Inverse Folding Model</h1>
      <p class="hero-sub">
        Interactive inverse design of asymmetric DNA aptamer candidates from user-defined structural constraints.
        Explore target architecture, sequence composition, structural asymmetry and computational descriptors in one interface.
      </p>
      <div class="chip-row">
        <span class="chip">Asymmetric DNA design</span>
        <span class="chip">Inverse folding</span>
        <span class="chip">Dot-bracket structure</span>
        <span class="chip">Asymmetry quantification</span>
        <span class="chip">Interactive analytics</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# Generate only after an explicit click. No candidate sequence/analysis is shown on first load.
if generate:
    actual_seed = int(seed) if use_seed else None
    with st.spinner("NanoMax is constructing an asymmetric target and generating a candidate sequence…"):
        designer = AsymmetricDNAAptamerDesigner(seed=actual_seed)
        structure = designer.generate_asymmetric_multibranch(length, branches, loops)
        sequence = designer.generate_sequence(structure, gc_target_percent / 100)
        analysis = designer.analyze_aptamer(structure, sequence)
        report = designer.create_analysis_report(structure, sequence, analysis)

    st.session_state["nanomax_result"] = {
        "structure": structure,
        "sequence": sequence,
        "analysis": analysis,
        "report": report,
    }
    st.session_state["nanomax_params"] = {
        "length": length,
        "branches": branches,
        "loops": loops,
        "gc_target": gc_target_percent,
        "seed": actual_seed,
    }


designer_tab, project_tab, science_tab = st.tabs(
    ["⚡ Designer", "🧬 Project overview", "🔬 Scientific framework"]
)


# ---------------- Designer ----------------
with designer_tab:
    if "nanomax_result" not in st.session_state:
        st.markdown(
            """
            <div class="ready-card">
              <div class="ready-icon">⌁🧬⌁</div>
              <h3>Ready for inverse design</h3>
              <p>
                Set the structural parameters in the left panel and click <b>Generate DNA aptamer</b>.
                The candidate DNA sequence and all analytical results will remain hidden until generation is requested.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        cards = [
            (c1, "01 · Define", "Specify DNA length, target branches, loops and GC-content preference."),
            (c2, "02 · Generate", "NanoMax constructs an asymmetric target structure and produces a compatible candidate sequence."),
            (c3, "03 · Inspect", "Review asymmetry, base composition, pairing, structural descriptors and visual analytics."),
        ]
        for col, title, text in cards:
            with col:
                st.markdown(
                    f'<div class="science-card"><h4>{title}</h4><p>{text}</p></div>',
                    unsafe_allow_html=True,
                )
    else:
        result = st.session_state["nanomax_result"]
        structure = result["structure"]
        sequence = result["sequence"]
        analysis = result["analysis"]
        params = st.session_state.get("nanomax_params", {})

        with st.container(border=True):
            st.markdown(
                '<div class="result-heading"><div class="dna-mark">DNA</div><div class="result-title">Generated candidate</div></div>',
                unsafe_allow_html=True,
            )
            if params:
                seed_label = "random" if params.get("seed") is None else str(params.get("seed"))
                st.caption(
                    f"Generated with length={params.get('length')} nt · branches={params.get('branches')} · "
                    f"loops={params.get('loops')} · GC target={params.get('gc_target')}% · seed={seed_label}"
                )

            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("**DNA sequence (5′ → 3′)**")
                st.markdown(f'<div class="sequence-box">{sequence}</div>', unsafe_allow_html=True)
            with col2:
                st.markdown("**Target secondary structure (dot-bracket notation)**")
                st.markdown(f'<div class="sequence-box">{structure}</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:.25rem'></div>", unsafe_allow_html=True)
            m1, m2, m3, m4, m5 = st.columns(5)
            metric_specs = [
                (m1, "↔", "Length", f"{int(analysis['length'])} nt", ""),
                (m2, "%", "GC content", f"{analysis['gc_content']:.1f}%", "teal"),
                (m3, "◇", "Asymmetry", f"{analysis['asymmetry_score']:.1f}%", "gold"),
                (m4, "⌁", "Paired bases", f"{analysis['pairing_percent']:.1f}%", "blue"),
                (m5, "◈", "Stability score*", f"{analysis['stability_score']:.1f}", "purple"),
            ]
            for col, icon, label, value, cls in metric_specs:
                with col:
                    st.markdown(
                        f"""<div class="metric-card {cls}">
                              <div class="metric-icon">{icon}</div>
                              <div><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>
                            </div>""",
                        unsafe_allow_html=True,
                    )

        sequence_tab, structure_tab, plots_tab, method_tab = st.tabs(
            ["Sequence analysis", "Structure analysis", "Visualizations", "Method & defense notes"]
        )

        composition_df = pd.DataFrame(
            {
                "Base": ["A", "C", "G", "T"],
                "Count": [analysis[f"{b}_count"] for b in ["A", "C", "G", "T"]],
                "Percent": [analysis[f"{b}_percent"] for b in ["A", "C", "G", "T"]],
            }
        )

        with sequence_tab:
            left, right = st.columns(2)
            with left:
                st.dataframe(composition_df, hide_index=True, use_container_width=True)
            with right:
                st.write(f"**Shannon entropy:** {analysis['sequence_complexity']:.3f}")
                st.write(f"**Purine:pyrimidine ratio:** {analysis['purine_pyrimidine_ratio']:.2f}")
                st.write(f"**GC base pairs:** {int(analysis['gc_pairs'])}")
                st.write(f"**AT base pairs:** {int(analysis['at_pairs'])}")

        with structure_tab:
            descriptors = pd.DataFrame(
                {
                    "Descriptor": [
                        "Hairpin loops",
                        "Bulges",
                        "Internal loops",
                        "Detected branch points",
                        "Paired bases",
                        "Unpaired bases",
                    ],
                    "Value": [
                        int(analysis["hairpins"]),
                        int(analysis["bulges"]),
                        int(analysis["internal_loops"]),
                        int(analysis["branches"]),
                        int(analysis["paired_bases"]),
                        int(analysis["unpaired_bases"]),
                    ],
                }
            )
            st.dataframe(descriptors, hide_index=True, use_container_width=True)
            st.info("Dot-bracket notation uses '(' and ')' for paired positions and '.' for unpaired positions.")

        with plots_tab:
            chart1, chart2 = st.columns(2)
            with chart1:
                with st.container(border=True):
                    st.markdown('<div class="chart-card-title"><span class="chart-dot"></span>Base composition</div>', unsafe_allow_html=True)
                    fig = px.bar(
                        composition_df,
                        x="Base",
                        y="Percent",
                        text="Percent",
                        color="Base",
                        color_discrete_sequence=["#35B9B1", "#356A8C", "#D6A13D", "#8C7BEA"],
                    )
                    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", marker_line_width=0)
                    fig.update_layout(
                        yaxis_title="Percentage", showlegend=False, template="plotly_white", height=285,
                        margin=dict(l=36, r=12, t=20, b=34), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF",
                        font=dict(color="#405269", size=12),
                        xaxis=dict(gridcolor="#EDF1F3", linecolor="#CCD6DC", zeroline=False),
                        yaxis=dict(gridcolor="#EDF1F3", linecolor="#CCD6DC", zeroline=False),
                    )
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            with chart2:
                with st.container(border=True):
                    st.markdown('<div class="chart-card-title"><span class="chart-dot"></span>Paired-base composition</div>', unsafe_allow_html=True)
                    pair_df = pd.DataFrame({"Pair type": ["GC", "AT"], "Count": [analysis["gc_pairs"], analysis["at_pairs"]]})
                    fig2 = px.bar(
                        pair_df, x="Pair type", y="Count", text="Count", color="Pair type",
                        color_discrete_sequence=["#24B8B3", "#C49335"],
                    )
                    fig2.update_traces(marker_line_width=0)
                    fig2.update_layout(
                        showlegend=False, template="plotly_white", height=285,
                        margin=dict(l=36, r=12, t=20, b=34), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF",
                        font=dict(color="#405269", size=12),
                        xaxis=dict(gridcolor="#EDF1F3", linecolor="#CCD6DC", zeroline=False),
                        yaxis=dict(gridcolor="#EDF1F3", linecolor="#CCD6DC", zeroline=False),
                    )
                    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

            pairing_status = [1 if c in "()" else 0 for c in structure]
            with st.container(border=True):
                st.markdown('<div class="chart-card-title"><span class="chart-dot"></span>Pairing distribution along the candidate</div>', unsafe_allow_html=True)
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(
                    x=list(range(1, len(structure) + 1)), y=pairing_status, mode="lines", name="Pairing status",
                    line=dict(color="#0B7A83", width=2), fill="tozeroy", fillcolor="rgba(11,122,131,.08)",
                ))
                fig3.update_layout(
                    template="plotly_white", height=285, margin=dict(l=44, r=14, t=20, b=42),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF", font=dict(color="#405269", size=12),
                    xaxis=dict(title="Nucleotide position", gridcolor="#EDF1F3", linecolor="#CCD6DC", zeroline=False),
                    yaxis=dict(title="Paired (1) / unpaired (0)", tickmode="array", tickvals=[0, 1], gridcolor="#EDF1F3", linecolor="#CCD6DC", zeroline=False),
                )
                st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

        with method_tab:
            st.markdown(
                """
**Algorithm:** constraint-guided stochastic inverse design.

**Core technologies:** Python, NumPy probabilistic sampling, DNA base-pairing constraints (A–T and G–C), dot-bracket secondary-structure representation, Shannon-entropy sequence analysis, structural-asymmetry scoring, heuristic pair-weight stability scoring, Plotly visualization, and Streamlit web deployment.

**Short defense explanation:** NanoMax starts from desired structural constraints, builds an asymmetric target secondary structure, and then generates a DNA sequence intended to satisfy that structure while favoring stable base pairing and a selected GC-content range.

**Validation pathway:** generated candidates can be taken forward to established secondary-structure/thermodynamic tools and experimental assessment before biological interpretation.
                """
            )

        st.download_button(
            "⬇️ Download analysis report",
            data=result["report"],
            file_name="NanoMax_DNA_Aptamer_Analysis.md",
            mime="text/markdown",
        )
        st.caption(
            "*The displayed stability score is an internal weighted-pair descriptor for candidate comparison; it is not thermodynamic ΔG."
        )


# ---------------- Project overview ----------------
with project_tab:
    st.markdown('<div class="section-kicker">Research concept</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">From desired asymmetry to a candidate DNA architecture</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="project-note">
        NanoMax frames aptamer design as an inverse problem: define the desired asymmetric structural characteristics first,
        then generate and inspect candidate DNA sequences that satisfy the computational constraints.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="science-card"><h4>Input</h4><p>DNA length, target branches, loops and GC-content preference.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="science-card"><h4>Computational core</h4><p>Asymmetric target generation, dot-bracket representation, constrained stochastic sequence generation and descriptor calculation.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="science-card"><h4>Output</h4><p>Candidate DNA sequence, target secondary structure, asymmetry index, pairing statistics and downloadable analysis.</p></div>', unsafe_allow_html=True)

    st.markdown("### NanoMax inverse-design workflow")
    st.write("This figure summarizes the project route from desired asymmetric structural features to sequence generation, secondary-structure analysis and downstream nanomaterial design.")
    if WORKFLOW_FIG.exists():
        st.image(str(WORKFLOW_FIG), use_container_width=True)
        st.caption("NanoMax project workflow: target-feature definition → inverse sequence generation → structural analysis → downstream nanomaterial concept.")
    else:
        st.warning("Workflow figure was not found in the repository.")

    st.markdown("### Secondary-structure asymmetry quantification")
    st.write("The asymmetry index compares the two halves of the dot-bracket representation after mirroring/reversing one side, providing a quantitative secondary-structure asymmetry score.")
    if ASYMMETRY_FIG.exists():
        st.image(str(ASYMMETRY_FIG), use_container_width=True)
        st.caption("Mirror-comparison framework used to quantify asymmetry in the secondary-structure representation.")
    else:
        st.warning("Asymmetry-index figure was not found in the repository.")


# ---------------- Scientific framework ----------------
with science_tab:
    st.markdown('<div class="section-kicker">Beyond the sequence</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Linking 2D structural asymmetry with 3D nanomaterial morphology</div>', unsafe_allow_html=True)
    st.write(
        "The broader project includes a geometric framework for quantifying asymmetry in a three-dimensional gold nanoparticle. "
        "The illustrated workflow uses the center of mass, the inertia tensor and principal axes to define a reference frame, "
        "followed by a symmetry-plane cut and mirrored surface comparison to obtain a normalized mismatch measure."
    )
    if NANO_3D_FIG.exists():
        st.image(str(NANO_3D_FIG), use_container_width=True)
        st.caption("Conceptual 3D asymmetry workflow: center of mass → inertia tensor/principal axes → reference symmetry plane → mirrored surface mismatch.")
    else:
        st.warning("Three-dimensional asymmetry figure was not found in the repository.")

    st.markdown("### Defense quick facts")
    q1, q2 = st.columns(2)
    with q1:
        st.markdown(
            """
- **Problem type:** inverse design / inverse folding
- **Primary representation:** DNA sequence + dot-bracket secondary structure
- **Main inputs:** length, branches, loops and GC target
- **Main output:** asymmetric DNA aptamer candidate
            """
        )
    with q2:
        st.markdown(
            """
- **Core algorithm:** constraint-guided stochastic generation
- **Key analyses:** GC content, pairing, asymmetry and sequence diversity
- **Implementation:** Python + NumPy + Streamlit + Plotly
- **Next-stage validation:** structure prediction/thermodynamics and experimental testing
            """
        )


st.markdown(
    """
    <div class="footer-line">
    NanoMax Group · Harbin Institute of Technology, Shenzhen · Computational Aptamer Design Platform
    </div>
    """,
    unsafe_allow_html=True,
)
