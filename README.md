# Tracking Data Applied

An illustrated soccer analytics workshop using SkillCorner open tracking data, with a dedicated slide for each method and reproducible visual examples.

The standalone xG notebook additionally uses StatsBomb Open Data shot freeze frames to compare a distance/angle model with a model adding goalkeeper and defender context. It includes real match-held-out ROC/AUC results and uncertainty intervals; the other tracking walkthroughs continue to use SkillCorner.

The standalone graph-EPV notebook trains a small real-data GNN on SkillCorner tracking, evaluates unseen matches, and ends with actual model predictions over possessions. It includes a synchronized [EPV animation](outputs/methods/graph_epv_goal_animation.html), a [GIF](assets/methods/graph_epv_real_goal.gif), training code, a saved teaching checkpoint and a `RETRAIN` switch. The model is exploratory and has sparse positive labels; the notebook reports precision–recall and probability metrics alongside ROC/AUC.

## Materials

- [PowerPoint deck](slides/tracking-data-applied.pptx)
- [Interactive notebook with saved outputs](notebooks/tracking_data_applied.ipynb)
- [Standalone notebook for each method, including inline helpers and intermediate visuals](notebooks/methods/README.md)
- [From-scratch notebooks for every avenue](notebooks/avenues/README.md)
- [Browser-readable notebook with animation](outputs/tracking-data-applied.html)
- [Reading list and research projects](resources/READING_LIST.md)
- [Presenter guide](resources/PRESENTER_GUIDE.md)
- [Methodology and approximation boundaries](resources/METHODOLOGY.md)
- [Readable Python helpers](workshop.py)

## Run locally

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/download_data.py
jupyter lab notebooks/tracking_data_applied.ipynb
```

Run all cells in order. Internet is required to install packages and fetch the initial public data sample. Once cached, the notebook runs locally. Saved outputs support presentation without running the expensive cells; widget controls require a live Jupyter kernel. The HTML animation works without ffmpeg.

## Workshop flow

Data and visualization → event and formation detection → phases → physical metrics → xG and xThreat → pitch control → passing risk and dangerous space → off-ball threat → spatial and temporal graphs → neural models and EPV.

Each method has its own visual, assumptions and interpretation. Temporal graph examples include lagged features, dynamic spatial edges and forward identity edges. The standalone xG notebook trains two explicit logistic models on StatsBomb shots. Full production EPV/GNN models are not trained.

## Data and credit

Data: [SkillCorner/opendata](https://github.com/SkillCorner/opendata), released with PySport. Example match: Brisbane Roar vs Perth Glory, 21 December 2024, ID 1925299. The downloader caches only the first 9000 tracking records and associated metadata/labels; raw downloads are excluded from this repository. Derived figures and notebook outputs use that real sample.

The downloader pins upstream revision `4340d274572876239c154c90bc507a9b3250a656`. The upstream license notice is retained in `resources/SKILLCORNER_LICENSE.txt`. GitHub renders notebook figures, but download the HTML to play its embedded animation; widget sliders require Jupyter.

SkillCorner definitions anchor the physical metrics; DataBallPy documentation supports methodology. Workshop estimates are not exact reproductions of proprietary SkillCorner processing. Detailed research references and code availability are in the reading list. External projects and source data retain their own licenses.

## Rebuild and verify

```sh
python scripts/build_materials.py
python scripts/render_figures.py
python scripts/illustrate_methods.py
python scripts/illustrate_roles.py
python scripts/execute_notebook.py
python -m unittest discover -s tests
```

For the independent method notebooks, run `python scripts/build_avenue_notebooks.py`, then `python scripts/execute_avenue_notebooks.py`. This creates seven notebooks (foundations plus six avenues) with code, explanations and saved results, and standalone HTML copies under `outputs/avenues/`. Each notebook implements its calculations directly; shared helpers only load data and draw the pitch. Training code uses explicitly labeled synthetic checks when the partial match lacks reliable training labels.

The slide authoring source is `scripts/build_slides.mjs`; it uses OpenAI's bundled artifact-tool runtime (not a public npm dependency). Edit `slides/content.json` or the authoring script for slide content and layout. The exported PPTX is editable in PowerPoint. `build_materials.py` regenerates an unexecuted notebook, so execute it afterward.

## Figure and model provenance

The 17 method notebooks under `notebooks/methods/` each cover a complete analytical workflow. Formation centering, assignment and change detection are together; graph construction, message passing, pooling, labels and training are together. Each notebook includes data downloading, kloppy ingestion, reshaping, pitch drawing, helper functions, prerequisite calculations and intermediate visual diagnostics inline. Read in order from inputs through each inspected transformation to final results and interpretation. They import no local Python helper files and require no previous notebook session. Set `DATA_ROOT` in the first code cell if using another cache. Each method has a saved HTML counterpart under `outputs/methods/`. The earlier presenter and avenue notebooks remain available as broader walkthroughs.

`assets/methods/` contains generated method illustrations. `resources/visual_manifest.json` describes their provenance. Real tracking and supplied provider values are distinguished from architecture schematics and teaching baselines. The DataBallPy fitted open-play xT grid is retained with its license and SHA-256 provenance in `resources/models/`. It is an external event-trained model, not a grid fitted on this tracking sample.

Role and formation walkthroughs include centroid-normalized covariance ellipses, Devin Pleuler's angular teammate-count idea (with an explicitly added opponent channel), fixed-template assignment and persistence-filtered change candidates. Joris Bekkers' GraphEPV talk anchors the graph-model discussion, including its ten-second scoring target. The standalone graph notebook now trains an independent teaching GNN on real SkillCorner data; it does not reproduce Bekkers' architecture or weights. Our fixed-template formation example is distinct from Bekkers' elastic EFPI algorithm. See `resources/ROLE_AND_GRAPHEPV.md` for sources and limitations.
