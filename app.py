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

# Futuristic, scientific interface styling.
st.markdown(
    """
    <style>
    :root {
        --cyan: #35e7ff;
        --cyan2: #00a7c7;
        --violet: #8b5cf6;
        --bg: #060b12;
        --panel: rgba(13, 23, 34, 0.80);
        --line: rgba(53, 231, 255, 0.18);
        --muted: #91a4b7;
    }

    .stApp {
        background:
            radial-gradient(circle at 16% 12%, rgba(0, 198, 255, .10), transparent 26%),
            radial-gradient(circle at 88% 8%, rgba(139, 92, 246, .10), transparent 25%),
            linear-gradient(180deg, #071019 0%, #05090f 65%, #03070b 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(11,17,27,.98), rgba(17,23,36,.98));
        border-right: 1px solid rgba(53,231,255,.13);
    }

    [data-testid="stSidebar"] img {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
        object-fit: contain;
    }

    .block-container {
        max-width: 1380px;
        padding-top: 1.5rem;
        padding-bottom: 4rem;
    }

    .hero-shell {
        position: relative;
        overflow: hidden;
        padding: 2.05rem 2.15rem;
        margin-bottom: 1.25rem;
        border-radius: 24px;
        border: 1px solid rgba(53,231,255,.20);
        background:
          linear-gradient(120deg, rgba(8,26,40,.94), rgba(10,16,30,.88)),
          radial-gradient(circle at 90% 20%, rgba(139,92,246,.18), transparent 35%);
        box-shadow: 0 22px 60px rgba(0,0,0,.26), inset 0 0 50px rgba(53,231,255,.03);
    }

    .hero-shell::after {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        right: -80px;
        top: -110px;
        border-radius: 50%;
        border: 1px solid rgba(53,231,255,.18);
        box-shadow: 0 0 70px rgba(53,231,255,.08);
    }

    .eyebrow {
        color: var(--cyan);
        text-transform: uppercase;
        letter-spacing: .18em;
        font-size: .76rem;
        font-weight: 700;
        margin-bottom: .55rem;
    }

    .hero-title {
        margin: 0;
        font-size: clamp(2.0rem, 3.25vw, 3.45rem);
        line-height: 1.04;
        font-weight: 780;
        letter-spacing: -.035em;
        white-space: nowrap;
        background: linear-gradient(90deg, #ffffff, #bcefff 55%, #c6b7ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    @media (max-width: 900px) {
        .hero-title {white-space: normal; font-size: 2.15rem;}
    }

    .hero-sub {
        margin-top: .9rem;
        color: #b9c8d7;
        font-size: 1.04rem;
        max-width: 850px;
    }

    .chip-row {margin-top: 1.15rem; display: flex; gap: .55rem; flex-wrap: wrap;}
    .chip {
        display: inline-block;
        padding: .35rem .72rem;
        border-radius: 999px;
        border: 1px solid rgba(53,231,255,.20);
        color: #bdeffc;
        background: rgba(53,231,255,.055);
        font-size: .78rem;
    }

    .credit-card {
        border: 1px solid rgba(53,231,255,.14);
        border-radius: 16px;
        padding: .95rem 1rem;
        margin-top: 1.25rem;
        background: linear-gradient(145deg, rgba(53,231,255,.045), rgba(139,92,246,.035));
        line-height: 1.55;
    }
    .sidebar-divider {
        height: 1px;
        margin: 1.25rem 0 .2rem 0;
        background: linear-gradient(90deg, transparent, rgba(53,231,255,.23), transparent);
    }
    .credit-card b {color: #f6fbff;}
    .credit-card .small {color: #9fb0bf; font-size: .82rem;}

    .section-kicker {
        color: var(--cyan);
        font-size: .76rem;
        letter-spacing: .15em;
        text-transform: uppercase;
        font-weight: 700;
        margin-bottom: .2rem;
    }

    .section-title {
        font-size: 1.65rem;
        font-weight: 760;
        margin: 0 0 .5rem 0;
    }

    .science-card {
        height: 100%;
        padding: 1.1rem 1.15rem;
        border-radius: 17px;
        border: 1px solid rgba(53,231,255,.13);
        background: linear-gradient(145deg, rgba(15,27,41,.82), rgba(10,16,26,.72));
        box-shadow: inset 0 1px 0 rgba(255,255,255,.025);
    }
    .science-card h4 {margin: 0 0 .45rem 0; color: #eefaff;}
    .science-card p {margin: 0; color: #9fb2c4; font-size: .9rem; line-height: 1.55;}

    .ready-card {
        text-align: center;
        padding: 2.2rem 1.4rem;
        margin-top: .8rem;
        border-radius: 20px;
        border: 1px dashed rgba(53,231,255,.28);
        background: linear-gradient(180deg, rgba(53,231,255,.035), rgba(139,92,246,.025));
    }
    .ready-icon {font-size: 2.1rem; margin-bottom: .45rem;}
    .ready-card h3 {margin: .2rem 0 .35rem 0;}
    .ready-card p {color: #95a8b9; margin: 0 auto; max-width: 720px;}

    div[data-testid="stMetric"] {
        border: 1px solid rgba(53,231,255,.13);
        background: rgba(11,21,32,.68);
        padding: .8rem .95rem;
        border-radius: 15px;
    }

    div[data-testid="stMetricValue"] {color: #eafcff;}

    .stButton > button[kind="primary"] {
        border: 0 !important;
        background: linear-gradient(100deg, #00b7d8, #6866ff) !important;
        color: white !important;
        font-weight: 730 !important;
        min-height: 3.15rem;
        border-radius: 12px !important;
        box-shadow: 0 10px 28px rgba(0,183,216,.20);
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 34px rgba(0,183,216,.28);
    }

    .stTabs [data-baseweb="tab-list"] {gap: .45rem;}
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding-left: .8rem;
        padding-right: .8rem;
    }

    [data-testid="stExpander"] {
        border-color: rgba(53,231,255,.12) !important;
        border-radius: 14px !important;
        background: rgba(11,20,30,.32);
    }

    .project-note {
        border-left: 3px solid var(--cyan);
        padding: .7rem .9rem;
        color: #aabaca;
        background: rgba(53,231,255,.035);
        border-radius: 0 12px 12px 0;
        margin: .65rem 0 1rem 0;
    }

    .footer-line {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(53,231,255,.09);
        color: #748697;
        font-size: .78rem;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- Sidebar ----------------
with st.sidebar:
    if LOGO_PATH.exists():
        logo_left, logo_mid, logo_right = st.columns([0.40, 0.120, 0.40])
        with logo_mid:
            st.image(str(LOGO_PATH), use_container_width=True)

    st.markdown("### Design parameters")
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

        st.markdown('<div class="section-kicker">NanoMax output</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Generated candidate</div>', unsafe_allow_html=True)
        if params:
            seed_label = "random" if params.get("seed") is None else str(params.get("seed"))
            st.caption(
                f"Generated with length={params.get('length')} nt · branches={params.get('branches')} · "
                f"loops={params.get('loops')} · GC target={params.get('gc_target')}% · seed={seed_label}"
            )

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("**DNA sequence (5′ → 3′)**")
            st.code(sequence, language=None)
        with col2:
            st.markdown("**Target secondary structure (dot-bracket notation)**")
            st.code(structure, language=None)

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Length", f"{int(analysis['length'])} nt")
        m2.metric("GC content", f"{analysis['gc_content']:.1f}%")
        m3.metric("Asymmetry", f"{analysis['asymmetry_score']:.1f}%")
        m4.metric("Paired bases", f"{analysis['pairing_percent']:.1f}%")
        m5.metric("Stability score*", f"{analysis['stability_score']:.1f}")

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
                fig = px.bar(
                    composition_df,
                    x="Base",
                    y="Percent",
                    text="Percent",
                    title="Base composition",
                    color="Base",
                    color_discrete_sequence=["#35e7ff", "#6f7dff", "#b987ff", "#69ffc9"],
                )
                fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                fig.update_layout(yaxis_title="Percentage", showlegend=False, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

            with chart2:
                pair_df = pd.DataFrame(
                    {
                        "Pair type": ["GC", "AT"],
                        "Count": [analysis["gc_pairs"], analysis["at_pairs"]],
                    }
                )
                fig2 = px.bar(
                    pair_df,
                    x="Pair type",
                    y="Count",
                    text="Count",
                    title="Paired-base composition",
                    color="Pair type",
                    color_discrete_sequence=["#35e7ff", "#8b5cf6"],
                )
                fig2.update_layout(showlegend=False, template="plotly_dark")
                st.plotly_chart(fig2, use_container_width=True)

            pairing_status = [1 if c in "()" else 0 for c in structure]
            fig3 = go.Figure()
            fig3.add_trace(
                go.Scatter(
                    x=list(range(1, len(structure) + 1)),
                    y=pairing_status,
                    mode="lines",
                    name="Pairing status",
                    line=dict(color="#35e7ff", width=2),
                    fill="tozeroy",
                    fillcolor="rgba(53,231,255,.10)",
                )
            )
            fig3.update_layout(
                title="Pairing distribution along the candidate",
                xaxis_title="Nucleotide position",
                yaxis_title="Paired (1) / unpaired (0)",
                yaxis=dict(tickmode="array", tickvals=[0, 1]),
                template="plotly_dark",
            )
            st.plotly_chart(fig3, use_container_width=True)

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
    NanoMax Group · Harbin Institute of Technology, Shenzhen · Interactive research prototype
    </div>
    """,
    unsafe_allow_html=True,
)
