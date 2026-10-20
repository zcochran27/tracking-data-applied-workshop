# Tracking Data Applied

An illustrated soccer analytics workshop using SkillCorner open tracking data, with a dedicated slide for each method and reproducible visual examples.

## Materials

- [PowerPoint deck](slides/tracking-data-applied.pptx)
- [Interactive notebook with saved outputs](notebooks/tracking_data_applied.ipynb)
- [Browser-readable notebook with animation](outputs/tracking-data-applied.html)
- [Reading list and research projects](resources/READING_LIST.md)
- [Presenter guide and timings](resources/PRESENTER_GUIDE.md)
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

Each method has its own visual, assumptions and interpretation. Temporal graph examples include lagged features, dynamic spatial edges and forward identity edges. No training of full EPV, xG or GNN models is implied.

## Data and credit

Data: [SkillCorner/opendata](https://github.com/SkillCorner/opendata), released with PySport. Example match: Brisbane Roar vs Perth Glory, 21 December 2024, ID 1925299. The downloader caches only the first 9000 tracking records and associated metadata/labels; raw downloads are excluded from this repository. Derived figures and notebook outputs use that real sample.

The downloader pins upstream revision `4340d274572876239c154c90bc507a9b3250a656`. The upstream license notice is retained in `resources/SKILLCORNER_LICENSE.txt`. GitHub renders notebook figures, but download the HTML to play its embedded animation; widget sliders require Jupyter.

SkillCorner definitions anchor the physical metrics; DataBallPy documentation supports methodology. Workshop estimates are not exact reproductions of proprietary SkillCorner processing. Detailed research references and code availability are in the reading list. External projects and source data retain their own licenses.

## Rebuild and verify

```sh
python scripts/build_materials.py
python scripts/render_figures.py
python scripts/illustrate_methods.py
python scripts/execute_notebook.py
python -m unittest discover -s tests
```

The slide authoring source is `scripts/build_slides.mjs`; it uses OpenAI's bundled artifact-tool runtime (not a public npm dependency). Edit `slides/content.json` or the authoring script for slide content and layout. The exported PPTX is editable in PowerPoint. `build_materials.py` regenerates an unexecuted notebook, so execute it afterward.

## Figure and model provenance

`assets/methods/` contains generated method illustrations. `resources/visual_manifest.json` describes their provenance. Real tracking and supplied provider values are distinguished from architecture schematics and teaching baselines. The DataBallPy fitted open-play xT grid is retained with its license and SHA-256 provenance in `resources/models/`. It is an external event-trained model, not a grid fitted on this tracking sample.
