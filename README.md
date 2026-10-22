# Tracking Data Applied

A soccer analytics workshop on using player and ball tracking data to study events, team shape, phases of play, physical performance and game value. The materials combine SkillCorner open tracking data, StatsBomb shot data, practical Python examples and published research.

## Workshop materials

- [Slides](slides/tracking-data-applied-updated.pptx): PowerPoint presentation with embedded videos and links to notebooks. Click a video in slideshow view to play it.
- [Method notebooks](notebooks/methods/README.md): code, intermediate calculations, visualizations and examples for each method.
- [Reading list](resources/READING_LIST.md): documentation, papers and related projects.
- [Methodology](resources/METHODOLOGY.md): assumptions, formulas and interpretation of the examples.
- [Roles, formations and graph EPV](resources/ROLE_AND_GRAPHEPV.md): methods and primary sources.

## Setup

Use Python 3.11 or newer. Clone the repository and create a virtual environment:

```sh
git clone https://github.com/zcochran27/tracking-data-applied-workshop.git
cd tracking-data-applied-workshop
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```sh
source .venv/bin/activate
```

Install the packages and launch JupyterLab:

```sh
python -m pip install -r requirements.txt
jupyter lab notebooks/methods
```

Open a notebook and run its cells from top to bottom. An internet connection is needed for the initial data download. Data are cached locally in `data/`.

To explore another example, change the variables in the example-selection cell and rerun that cell and the final exploration cell. Depending on the method, you can select a frame, possession, event, player, formation window or shot. The notebooks display available identifiers. `DURATION_S` controls clip length and `FRAME_STRIDE` controls animation sampling.

## Methods

The [notebook guide](notebooks/methods/README.md) lists all fourteen notebooks: data exploration, event detection, formation analysis, role classification, phase segmentation, physical metrics, xG, xT, Voronoi control, Gaussian control, arrival-time control, pass completion, accessible/dangerous space and graph EPV.

The xG example compares location-only and goalkeeper/defender-context models using StatsBomb shot freeze frames. The graph EPV example trains on SkillCorner data and includes held-out results and possession predictions; set `RETRAIN = True` to train it again. Model assumptions and limitations are documented in the notebooks and [model card](resources/models/graph_epv_model_card.json).

## Data and credit

- [SkillCorner open data and documentation](https://github.com/SkillCorner/opendata), released with PySport. [License](resources/SKILLCORNER_LICENSE.txt).
- [StatsBomb Open Data](https://github.com/hudl/open-data) for shot events and freeze frames.
- [kloppy documentation](https://kloppy.pysport.org/) for loading tracking data.
- [DataBallPy documentation](https://databallpy.readthedocs.io/en/main/) for metrics and the fitted xT model. [License](resources/DATABALLPY_LICENSE.txt).

Published figures and models retain their original credits and usage terms. Source links are included in the slides, notebooks and [reference guide](assets/references/README.md).
