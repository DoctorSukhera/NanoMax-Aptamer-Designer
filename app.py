from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from nanomax_model import AsymmetricDNAAptamerDesigner


APP_DIR = Path(__file__).resolve().parent


def resolve_asset(*names: str) -> Path:
    """Find an asset in the repository root or /assets."""
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


# ---------------------------------------------------------------------
# Premium compact scientific UI
# ---------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root{
        --navy:#0a2342;
        --navy2:#153957;
        --teal:#0d7f87;
        --teal2:#0b6472;
        --cyan:#1aa8bd;
        --gold:#c9922e;
        --gold2:#dfad4f;
        --purple:#6e4bd8;
        --green:#2f907d;
        --ink:#10233d;
        --muted:#64748b;
        --line:#dbe5eb;
        --panel:#ffffff;
        --soft:#f7fafc;
        --pearl:#fbfcfd;
    }

    html, body { color-scheme: light; }

    .stApp{
        background:
          radial-gradient(circle at 9% 5%, rgba(13,127,135,.045), transparent 19%),
          radial-gradient(circle at 91% 7%, rgba(201,146,46,.055), transparent 18%),
          linear-gradient(180deg,#fbfdff 0%,#f5f8fb 100%);
        color:var(--ink);
    }

    /* Main canvas - intentionally compact for one-screen demo */
    .block-container{
        max-width:1600px;
        padding-top:.45rem !important;
        padding-left:1rem !important;
        padding-right:1rem !important;
        padding-bottom:.35rem !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"]{
        min-width:300px !important;
        max-width:300px !important;
        background:linear-gradient(180deg,#ffffff 0%,#f7fafc 100%);
        border-right:1px solid #e1e8ed;
        box-shadow:8px 0 28px rgba(15,35,60,.035);
    }
    [data-testid="stSidebar"] > div:first-child{
        padding:.55rem 1rem .55rem 1rem !important;
    }
    [data-testid="stSidebar"] img{
        background:transparent !important;
        box-shadow:none !important;
        border:none !important;
        object-fit:contain;
    }
    [data-testid="stSidebar"] h3{
        margin:.25rem 0 .65rem 0 !important;
        font-family:Georgia,"Times New Roman",serif;
        color:var(--navy) !important;
        font-size:1.12rem !important;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span{
        color:#18324d !important;
    }

    .brand-block{
        text-align:center;
        margin:-.25rem 0 .55rem 0;
        padding-bottom:.5rem;
        border-bottom:1px solid #e7edf1;
    }
    .brand-main{
        font-family:Georgia,"Times New Roman",serif;
        color:var(--navy);
        font-weight:800;
        letter-spacing:.07em;
        font-size:.85rem;
    }
    .brand-sub{
        margin-top:.1rem;
        color:#728196;
        text-transform:uppercase;
        font-weight:650;
        letter-spacing:.17em;
        font-size:.60rem;
    }

    /* Sliders */
    div[data-baseweb="slider"] [role="slider"]{
        background:#0d7f87 !important;
        border-color:#0d7f87 !important;
        box-shadow:0 0 0 2px rgba(13,127,135,.08) !important;
    }
    div[data-baseweb="slider"] div[style*="background"]{
        border-radius:999px !important;
    }

    /* Compact sidebar widgets */
    [data-testid="stSidebar"] .stSlider{
        padding-bottom:.16rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"]{
        border:1px solid #dce5eb !important;
        border-radius:11px !important;
        background:#fff !important;
        box-shadow:none !important;
        margin-top:.2rem !important;
    }

    /* Primary button */
    .stButton > button[kind="primary"]{
        border:0 !important;
        min-height:2.72rem !important;
        border-radius:10px !important;
        background:linear-gradient(100deg,#0d8f99 0%,#0b3156 100%) !important;
        color:#fff !important;
        font-weight:750 !important;
        box-shadow:0 7px 18px rgba(11,49,86,.16);
    }
    .stButton > button[kind="primary"]:hover{
        transform:translateY(-1px);
        box-shadow:0 10px 22px rgba(11,49,86,.21);
    }
    .stButton > button:not([kind="primary"]){
        min-height:2.45rem !important;
        border-radius:10px !important;
        border-color:#dce5eb !important;
        background:#fff !important;
        color:#1f3650 !important;
    }

    .credit-card{
        border:1px solid #dce5eb;
        border-top:3px solid var(--gold);
        border-radius:14px;
        padding:.72rem .82rem;
        margin-top:.68rem;
        background:linear-gradient(145deg,#fff,#f8fafc);
        box-shadow:0 8px 20px rgba(18,42,68,.045);
        line-height:1.42;
    }
    .credit-card b{color:var(--navy) !important;}
    .credit-card .small{
        color:#7a8797 !important;
        font-size:.71rem;
    }

    /* Hero */
    .hero-shell{
        position:relative;
        overflow:hidden;
        border-radius:19px;
        border:1px solid #d8e4e9;
        padding:.88rem 1.7rem .82rem 1.7rem;
        margin-bottom:.36rem;
        min-height:130px;
        background:
          radial-gradient(circle at 91% 15%,rgba(13,127,135,.08),transparent 23%),
          radial-gradient(circle at 99% 92%,rgba(201,146,46,.065),transparent 18%),
          linear-gradient(110deg,#fff 0%,#f8fcfd 64%,#edf7f9 100%);
        box-shadow:0 12px 30px rgba(18,42,68,.07);
    }
    .hero-shell::before{
        content:"🧬";
        position:absolute;
        right:2.2rem;
        top:-2.1rem;
        font-size:9.5rem;
        opacity:.035;
        transform:rotate(-16deg);
        filter:grayscale(1);
    }
    .hero-shell::after{
        content:"";
        position:absolute;
        width:72px;
        height:2px;
        left:17.5rem;
        top:1.15rem;
        background:linear-gradient(90deg,var(--gold),rgba(201,146,46,.05));
    }
    .eyebrow{
        position:relative;
        z-index:2;
        color:var(--teal2) !important;
        text-transform:uppercase;
        letter-spacing:.19em;
        font-size:.65rem;
        font-weight:800;
        margin-bottom:.26rem;
    }
    .hero-title{
        position:relative;
        z-index:2;
        margin:0;
        color:var(--navy) !important;
        font-family:Georgia,"Times New Roman",serif;
        font-weight:750;
        letter-spacing:-.025em;
        line-height:1;
        font-size:clamp(1.85rem,2.65vw,2.95rem);
        white-space:nowrap;
    }
    .hero-sub{
        position:relative;
        z-index:2;
        margin:.38rem 0 0 0;
        max-width:920px;
        color:#53657b !important;
        font-size:.82rem;
        line-height:1.38;
    }
    .chip-row{
        position:relative;
        z-index:2;
        margin-top:.53rem;
        display:flex;
        gap:.38rem;
        flex-wrap:wrap;
    }
    .chip{
        display:inline-block;
        padding:.22rem .60rem;
        border-radius:999px;
        border:1px solid #d5e5e8;
        background:linear-gradient(180deg,#f4fbfb,#ebf6f6);
        color:#0b6370 !important;
        font-size:.67rem;
        font-weight:650;
    }

    @media(max-width:1100px){
        .hero-title{white-space:normal;font-size:2rem;}
        .hero-shell::after{display:none;}
    }

    /* Streamlit tabs */
    .stTabs [data-baseweb="tab-list"]{
        gap:.25rem;
        border-bottom:1px solid #dce5eb;
        min-height:2.15rem;
    }
    .stTabs [data-baseweb="tab"]{
        height:2.05rem;
        padding:.2rem .58rem;
        font-size:.76rem;
        color:#213a55;
    }
    .stTabs [aria-selected="true"]{
        color:#0d6876 !important;
        font-weight:750 !important;
    }

    /* Main output panel */
    .output-head{
        display:flex;
        align-items:center;
        gap:.55rem;
        margin:.08rem 0 .18rem 0;
    }
    .output-icon{
        font-size:1.45rem;
        color:var(--teal);
    }
    .output-title{
        margin:0;
        font-family:Georgia,"Times New Roman",serif;
        color:var(--navy) !important;
        font-size:1.42rem;
        font-weight:750;
    }
    .output-caption{
        color:#718094 !important;
        font-size:.69rem;
        margin:0 0 .38rem 2rem;
    }
    .seq-label{
        color:#18324d !important;
        font-size:.72rem;
        font-weight:750;
        margin-bottom:.18rem;
    }
    .seq-box{
        width:100%;
        height:38px;
        padding:.58rem .72rem;
        border-radius:9px;
        border:1px solid #d9e3e8;
        background:#f8fafc;
        color:#233d5a !important;
        font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;
        font-size:.71rem;
        line-height:1.1;
        overflow:hidden;
        white-space:nowrap;
        text-overflow:ellipsis;
        box-shadow:inset 0 1px 1px rgba(20,45,70,.025);
    }

    .metric-card{
        height:84px;
        border:1px solid #dce6ec;
        border-top:2px solid var(--metric-accent,#0d7f87);
        border-radius:12px;
        padding:.58rem .72rem;
        background:linear-gradient(180deg,#fff,#fbfcfd);
        box-shadow:0 7px 18px rgba(18,42,68,.045);
    }
    .metric-row{
        display:flex;
        align-items:center;
        gap:.40rem;
    }
    .metric-icon{
        font-size:1.12rem;
        color:var(--metric-accent,#0d7f87) !important;
    }
    .metric-label{
        color:#52657b !important;
        font-size:.66rem;
        font-weight:700;
    }
    .metric-value{
        margin-top:.16rem;
        color:var(--metric-accent,#0a2342) !important;
        font-family:Georgia,"Times New Roman",serif;
        font-size:1.55rem;
        line-height:1;
        font-weight:760;
    }

    /* Visual sub-navigation strip */
    .analysis-strip{
        display:flex;
        gap:1.05rem;
        align-items:center;
        margin:.35rem 0 .22rem 0;
        padding:0 .12rem .26rem .12rem;
        border-bottom:1px solid #dce5eb;
        font-size:.70rem;
        color:#496078;
    }
    .analysis-strip span:first-child{
        color:#0d6876 !important;
        font-weight:800;
        border-bottom:2px solid #0d7f87;
        padding-bottom:.24rem;
    }

    /* Chart cards */
    .chart-title{
        font-family:Georgia,"Times New Roman",serif;
        color:var(--navy) !important;
        font-weight:760;
        font-size:.82rem;
        margin:.06rem 0 -.2rem .12rem;
    }
    div[data-testid="stPlotlyChart"]{
        border:1px solid #e0e7eb;
        border-radius:13px;
        background:#fff;
        box-shadow:0 6px 17px rgba(18,42,68,.038);
        overflow:hidden;
    }

    /* Compact "ready" state */
    .ready-card{
        text-align:center;
        border:1px dashed #ccdce3;
        border-radius:16px;
        background:linear-gradient(180deg,#fff,#f8fbfc);
        padding:1.5rem 1rem;
        margin-top:.25rem;
    }
    .ready-card h3{
        margin:.2rem 0 .3rem 0;
        font-family:Georgia,"Times New Roman",serif;
        color:var(--navy) !important;
    }
    .ready-card p{
        margin:0 auto;
        max-width:720px;
        color:#65758a !important;
        font-size:.82rem;
    }
    .science-card{
        height:100%;
        padding:.78rem .9rem;
        border-radius:13px;
        border:1px solid #e0e7eb;
        background:#fff;
        box-shadow:0 6px 16px rgba(18,42,68,.035);
    }
    .science-card h4{
        margin:0 0 .2rem 0;
        font-family:Georgia,"Times New Roman",serif;
        color:var(--navy) !important;
        font-size:.95rem;
    }
    .science-card p{
        margin:0;
        color:#66778b !important;
        font-size:.72rem;
        line-height:1.4;
    }

    /* Project pages */
    .section-kicker{
        color:var(--teal) !important;
        text-transform:uppercase;
        letter-spacing:.17em;
        font-weight:800;
        font-size:.68rem;
    }
    .section-title{
        margin:.08rem 0 .38rem 0;
        font-family:Georgia,"Times New Roman",serif;
        font-size:1.45rem;
        color:var(--navy) !important;
    }
    .project-note{
        border-left:3px solid var(--gold);
        background:#fbf8f0;
        color:#5f6670 !important;
        border-radius:0 9px 9px 0;
        padding:.55rem .75rem;
        margin:.25rem 0 .5rem 0;
        font-size:.78rem;
    }
    .footer-line{
        text-align:center;
        margin-top:.25rem;
        padding-top:.28rem;
        border-top:1px solid #e4eaee;
        color:#8390a0 !important;
        font-size:.60rem;
    }

    /* Reduce Streamlit vertical gaps */
    div[data-testid="stVerticalBlock"]{gap:.42rem !important;}
    div[data-testid="stHorizontalBlock"]{gap:.62rem !important;}

    /* Download button */
    [data-testid="stDownloadButton"] button{
        min-height:2.2rem !important;
        border-radius:9px !important;
    }

    /* Keep native code/data blocks compact elsewhere */
    .stDataFrame{font-size:.72rem;}

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------
with st.sidebar:
    if LOGO_PATH.exists():
        c1, c2, c3 = st.columns([0.28, 0.44, 0.28])
        with c2:
            st.image(str(LOGO_PATH), use_container_width=True)

    st.markdown(
        """
        <div class="brand-block">
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

    with st.expander("⚙ Advanced / reproducibility"):
        use_seed = st.checkbox("Use fixed random seed", value=True)
        seed = st.number_input("Seed", min_value=0, max_value=999999, value=42, step=1)

    generate = st.button("⚡ Generate DNA aptamer", type="primary", use_container_width=True)

    if st.button("🗑 Clear generated result", use_container_width=True):
        st.session_state.pop("nanomax_result", None)
        st.session_state.pop("nanomax_params", None)
        st.rerun()

    st.markdown(
        """
        <div class="credit-card">
            <div class="small">A Project by</div>
            <b>Prof. Xingyi Ma</b><br>
            <span style="font-size:.76rem">NanoMax Group, HIT Shenzhen</span>
            <div style="height:.48rem"></div>
            <div class="small">Design and Developed by</div>
            <b>Doctor Sukhera (学睿)</b>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------
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


# ---------------------------------------------------------------------
# Generate only after explicit user click
# ---------------------------------------------------------------------
if generate:
    actual_seed = int(seed) if use_seed else None
    with st.spinner("NanoMax is generating an asymmetric DNA aptamer candidate…"):
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
    ["🧬 Designer", "📊 Project overview", "📑 Scientific framework"]
)


# ---------------------------------------------------------------------
# DESIGNER: compact one-screen dashboard
# ---------------------------------------------------------------------
with designer_tab:
    if "nanomax_result" not in st.session_state:
        st.markdown(
            """
            <div class="ready-card">
                <div style="font-size:1.7rem">🧬</div>
                <h3>Ready for inverse design</h3>
                <p>
                    Set the design parameters in the left panel and click
                    <b>Generate DNA aptamer</b>. The candidate sequence and analysis
                    stay hidden until generation is requested.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns(3)
        cards = [
            (c1, "01 · Define", "Set DNA length, branches, loops and GC-content preference."),
            (c2, "02 · Generate", "NanoMax builds an asymmetric target and generates a compatible DNA candidate."),
            (c3, "03 · Inspect", "Review asymmetry, sequence composition, pairing and structural descriptors."),
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

        # Header
        st.markdown(
            """
            <div class="output-head">
                <div class="output-icon">🧬</div>
                <div class="output-title">Generated candidate</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if params:
            seed_label = "random" if params.get("seed") is None else str(params.get("seed"))
            st.markdown(
                f"""
                <div class="output-caption">
                    Generated with length={params.get('length')} nt · branches={params.get('branches')} ·
                    loops={params.get('loops')} · GC target={params.get('gc_target')}% · seed={seed_label}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Sequence / structure in one compact row
        left, right = st.columns([1, 1])
        with left:
            st.markdown('<div class="seq-label">DNA sequence (5′ → 3′)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="seq-box" title="{sequence}">{sequence}</div>', unsafe_allow_html=True)
        with right:
            st.markdown('<div class="seq-label">Target secondary structure (dot-bracket notation)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="seq-box" title="{structure}">{structure}</div>', unsafe_allow_html=True)

        # Five premium compact metric cards
        metric_specs = [
            ("📏", "Length", f"{int(analysis['length'])} nt", "#0b6e91"),
            ("％", "GC content", f"{analysis['gc_content']:.1f}%", "#198765"),
            ("⌘", "Asymmetry", f"{analysis['asymmetry_score']:.1f}%", "#c08317"),
            ("🔗", "Paired bases", f"{analysis['pairing_percent']:.1f}%", "#1468a8"),
            ("♢", "Stability score*", f"{analysis['stability_score']:.1f}", "#6541cf"),
        ]
        metric_cols = st.columns(5)
        for col, (icon, label, value, accent) in zip(metric_cols, metric_specs):
            with col:
                st.markdown(
                    f"""
                    <div class="metric-card" style="--metric-accent:{accent}">
                        <div class="metric-row">
                            <div class="metric-icon">{icon}</div>
                            <div class="metric-label">{label}</div>
                        </div>
                        <div class="metric-value">{value}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Thin analysis strip - intentionally visual, all important analytics stay visible below
        st.markdown(
            """
            <div class="analysis-strip">
                <span>▤ &nbsp;Sequence analysis</span>
                <span>⚒ &nbsp;Structure analysis</span>
                <span>▥ &nbsp;Visualizations</span>
                <span>▧ &nbsp;Method &amp; defense notes</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Data for charts
        composition_df = pd.DataFrame(
            {
                "Base": ["A", "C", "G", "T"],
                "Count": [analysis[f"{b}_count"] for b in ["A", "C", "G", "T"]],
                "Percent": [analysis[f"{b}_percent"] for b in ["A", "C", "G", "T"]],
            }
        )
        pair_df = pd.DataFrame(
            {
                "Pair type": ["GC", "AT"],
                "Count": [analysis["gc_pairs"], analysis["at_pairs"]],
            }
        )

        # Top chart row
        chart1, chart2 = st.columns(2)

        with chart1:
            st.markdown('<div class="chart-title">▥ &nbsp;Base composition</div>', unsafe_allow_html=True)
            fig = px.bar(
                composition_df,
                x="Base",
                y="Percent",
                text="Percent",
                color="Base",
                color_discrete_sequence=["#3488f5", "#2c8f91", "#d5a03a", "#7651df"],
            )
            fig.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
                marker_line_width=0,
            )
            fig.update_layout(
                height=178,
                margin=dict(l=34, r=12, t=18, b=32),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#ffffff",
                font=dict(color="#29425f", size=10),
                xaxis=dict(title="Base", showgrid=False, zeroline=False),
                yaxis=dict(
                    title="Percentage (%)",
                    showgrid=True,
                    gridcolor="#e9eef2",
                    zeroline=False,
                    rangemode="tozero",
                ),
            )
            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False, "responsive": True},
            )

        with chart2:
            st.markdown('<div class="chart-title">🔗 &nbsp;Paired-base composition</div>', unsafe_allow_html=True)
            fig2 = px.bar(
                pair_df,
                x="Pair type",
                y="Count",
                text="Count",
                color="Pair type",
                color_discrete_sequence=["#31b9b5", "#7451e4"],
            )
            fig2.update_traces(textposition="outside", marker_line_width=0)
            fig2.update_layout(
                height=178,
                margin=dict(l=34, r=12, t=18, b=32),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#ffffff",
                font=dict(color="#29425f", size=10),
                xaxis=dict(title="Pair type", showgrid=False, zeroline=False),
                yaxis=dict(
                    title="Count",
                    showgrid=True,
                    gridcolor="#e9eef2",
                    zeroline=False,
                    rangemode="tozero",
                ),
            )
            st.plotly_chart(
                fig2,
                use_container_width=True,
                config={"displayModeBar": False, "responsive": True},
            )

        # Pairing distribution - compact full-width bottom chart
        st.markdown(
            '<div class="chart-title">〰 &nbsp;Pairing distribution along the candidate</div>',
            unsafe_allow_html=True,
        )
        pairing_status = [1 if c in "()" else 0 for c in structure]
        fig3 = go.Figure()
        fig3.add_trace(
            go.Scatter(
                x=list(range(1, len(structure) + 1)),
                y=pairing_status,
                mode="lines",
                line=dict(color="#1976d2", width=2),
                fill="tozeroy",
                fillcolor="rgba(25,118,210,.055)",
                hovertemplate="Position %{x}<br>Paired: %{y}<extra></extra>",
            )
        )
        fig3.update_layout(
            height=145,
            margin=dict(l=38, r=14, t=12, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#ffffff",
            font=dict(color="#29425f", size=10),
            xaxis=dict(
                title="Nucleotide position",
                showgrid=True,
                gridcolor="#edf1f4",
                zeroline=False,
            ),
            yaxis=dict(
                title="Paired (1) / unpaired (0)",
                tickmode="array",
                tickvals=[0, 1],
                range=[-0.05, 1.18],
                showgrid=False,
                zeroline=False,
            ),
        )
        st.plotly_chart(
            fig3,
            use_container_width=True,
            config={"displayModeBar": False, "responsive": True},
        )

        # Tiny footer actions/info so they do not create a second screen
        d1, d2 = st.columns([0.28, 0.72])
        with d1:
            st.download_button(
                "⬇ Download analysis report",
                data=result["report"],
                file_name="NanoMax_DNA_Aptamer_Analysis.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with d2:
            st.caption(
                "Stability score is an internal weighted-pair descriptor for candidate comparison; it is not thermodynamic ΔG."
            )


# ---------------------------------------------------------------------
# PROJECT OVERVIEW
# ---------------------------------------------------------------------
with project_tab:
    st.markdown('<div class="section-kicker">Research concept</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">From desired asymmetry to a candidate DNA architecture</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="project-note">
        NanoMax frames aptamer generation as an inverse-design problem: define the desired
        asymmetric structural characteristics first, then generate and inspect DNA candidates
        that satisfy the computational constraints.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            '<div class="science-card"><h4>Input</h4><p>DNA length, branches, loops and GC-content preference.</p></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="science-card"><h4>Computational core</h4><p>Asymmetric target generation, dot-bracket representation, constrained stochastic sequence generation and descriptor calculation.</p></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            '<div class="science-card"><h4>Output</h4><p>Candidate sequence, target structure, asymmetry index, pairing statistics and downloadable analysis.</p></div>',
            unsafe_allow_html=True,
        )

    if WORKFLOW_FIG.exists():
        st.image(str(WORKFLOW_FIG), use_container_width=True)
        st.caption(
            "NanoMax project workflow: target-feature definition → inverse sequence generation → structural analysis → downstream nanomaterial concept."
        )

    if ASYMMETRY_FIG.exists():
        st.image(str(ASYMMETRY_FIG), use_container_width=True)
        st.caption(
            "Mirror-comparison framework used to quantify asymmetry in the secondary-structure representation."
        )


# ---------------------------------------------------------------------
# SCIENTIFIC FRAMEWORK
# ---------------------------------------------------------------------
with science_tab:
    st.markdown('<div class="section-kicker">Beyond the sequence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">Linking 2D structural asymmetry with 3D nanomaterial morphology</div>',
        unsafe_allow_html=True,
    )

    if NANO_3D_FIG.exists():
        st.image(str(NANO_3D_FIG), use_container_width=True)
        st.caption(
            "Conceptual 3D asymmetry workflow: center of mass → inertia tensor/principal axes → reference symmetry plane → mirrored surface mismatch."
        )

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
        NanoMax Group · Harbin Institute of Technology, Shenzhen · Interactive research prototype
    </div>
    """,
    unsafe_allow_html=True,
)
