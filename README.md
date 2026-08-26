# 🧬 NanoMax Aptamer Inverse Folding Model

<p align="center">
  <img src="assets/hitsz-logo.jpg" alt="Harbin Institute of Technology, Shenzhen" width="300">
</p>

<p align="center">
  <b>Interactive computational inverse design of asymmetric DNA aptamer candidates</b>
</p>

<p align="center">
  <b>A Project by Prof. Xingyi Ma</b><br>
  NanoMax Group, HIT Shenzhen<br><br>
  <b>Design and Developed by Doctor Sukhera (学睿)</b>
</p>

---

## Project overview

NanoMax is a Python-based interactive platform for **asymmetric DNA aptamer inverse design**. Rather than starting only from a DNA sequence and asking what structure it may form, the workflow starts from desired structural constraints and generates a candidate sequence for that target architecture.

The current web prototype allows the user to specify:

- DNA sequence length
- target number of branches
- target number of loops
- GC-content preference
- optional random seed for reproducibility

The generated candidate is then characterized using sequence composition, base-pairing statistics, a secondary-structure asymmetry index, Shannon-entropy sequence diversity, structural descriptors and an internal weighted-pair stability descriptor.

## NanoMax inverse-design workflow

<p align="center">
  <img src="assets/nanomax_workflow.png" alt="NanoMax inverse design workflow" width="100%">
</p>

The broader project workflow connects desired asymmetric structural features with target secondary-structure generation, candidate sequence generation, structural analysis and subsequent nanomaterial-design concepts.

## Secondary-structure asymmetry quantification

<p align="center">
  <img src="assets/nanomax_asymmetry_index.png" alt="Secondary structure asymmetry index" width="100%">
</p>

The secondary-structure asymmetry framework uses a mirror comparison of the dot-bracket representation. The structure is divided into two halves, the right half is reversed, and positional agreement is compared to derive symmetry and asymmetry percentages.

## Three-dimensional nanomaterial asymmetry concept

<p align="center">
  <img src="assets/nanoparticle_3d_asymmetry.png" alt="Three-dimensional nanoparticle asymmetry framework" width="100%">
</p>

The project also explores a geometric route for quantifying asymmetry in three-dimensional gold nanoparticle morphologies. The conceptual workflow uses the **center of mass**, **inertia tensor/principal axes**, a reference symmetry plane and a mirrored surface-mismatch comparison.

## Core computational approach

**Algorithm:** constraint-guided stochastic inverse design.

**Core technologies:**

- Python
- NumPy probabilistic sampling
- A–T and G–C DNA base-pairing constraints
- dot-bracket secondary-structure representation
- structural-asymmetry scoring
- Shannon entropy for sequence-diversity analysis
- heuristic weighted-pair stability scoring
- Plotly for interactive visualization
- Streamlit for web deployment

### Conceptual flow

```text
Desired asymmetric DNA features
            ↓
Target secondary structure
            ↓
Dot-bracket representation
            ↓
Constrained candidate sequence generation
            ↓
Sequence + structure analysis
            ↓
Candidate for downstream computational / experimental validation
```

## Web interface

The Streamlit interface is designed for demonstration and research prototyping. On first load, **no candidate sequence or analysis is displayed**. Results appear only after the user selects the design parameters and clicks **Generate DNA aptamer**.

The application includes:

- futuristic dark scientific UI
- HIT Shenzhen project branding
- interactive parameter controls
- on-demand candidate generation
- DNA sequence and dot-bracket structure output
- GC content, asymmetry, pairing and stability descriptors
- sequence-composition analysis
- structure-analysis table
- interactive plots
- project/scientific-framework galleries
- downloadable analysis report

## Repository structure

```text
NanoMax_Streamlit_Deployment/
├── app.py
├── nanomax_model.py
├── requirements.txt
├── README.md
├── assets/
│   ├── hitsz-logo.jpg
│   ├── nanomax_workflow.png
│   ├── nanomax_asymmetry_index.png
│   └── nanoparticle_3d_asymmetry.png
└── .streamlit/
    └── config.toml
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create or open your GitHub repository.
2. Upload the contents of this folder to the repository root.
3. Make sure the `assets` folder and `.streamlit/config.toml` are included.
4. Open Streamlit Community Cloud and connect the GitHub repository.
5. Set the main file path to `app.py`.
6. Deploy the application.

If the app is already connected to GitHub, pushing these updated files to the same repository will normally trigger a new deployment automatically.

## Defense-ready description

> **NanoMax uses a constraint-guided stochastic inverse-design algorithm. We first define the desired asymmetric DNA structural characteristics, and the program generates a candidate sequence under base-pairing, GC-content and structural constraints. It then calculates sequence and structural descriptors, including an asymmetry index, to support candidate selection for downstream validation.**

## Research-use note

NanoMax is an interactive computational research prototype. Generated candidate sequences and structural descriptors should be taken forward to established structure-prediction/thermodynamic tools and experimental validation before biological or materials-performance conclusions are drawn.
