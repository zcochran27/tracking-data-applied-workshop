# Tracking Data Applied

Illustrated soccer analytics methods using SkillCorner open tracking data. The slide deck links directly to the corresponding standalone method notebooks.

## Materials

- [PowerPoint deck](slides/tracking-data-applied.pptx)
- [14 standalone method notebooks](notebooks/methods/README.md)
- [Browser-readable method notebooks](outputs/methods/README.md)
- [Reading list and research projects](resources/READING_LIST.md)
- [Presenter guide with slide-to-notebook links](resources/PRESENTER_GUIDE.md)
- [Methodology and approximation boundaries](resources/METHODOLOGY.md)
- [Validation and model results](resources/VALIDATION.md)

Each method notebook contains all its code inline: downloading, loading, helper functions, intermediate calculations, visuals and final results. Read and run it from beginning to end in a fresh kernel. No local Python helper modules or previous notebook session are needed.

## Run locally

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter lab notebooks/methods
```

Choose a method notebook and run its cells in order. Internet is required for the initial data download. Saved outputs and HTML copies support viewing without execution; live widgets require Jupyter. Each notebook manages its own cache. Raw downloads are excluded from Git.

## Models and examples

The xG notebook uses StatsBomb Open Data shot freeze frames to compare location-only and goalkeeper/defender-context models on identical match-held-out folds, with ROC/AUC curves and uncertainty intervals.

The graph-EPV notebook includes real SkillCorner training code, a saved teaching checkpoint, held-out match results, possession-value curves and a synchronized [EPV animation](outputs/methods/graph_epv_goal_animation.html). Set `RETRAIN=True` to retrain. Its reconstructed goal labels, limited matches and sparse positives constrain reliability; it does not reproduce Bekkers' architecture or weights.

Formation centering, template assignment and change detection form one workflow. Pleuler-inspired angular features and role classification form another. Pitch-control and space examples label their assumptions and teaching approximations. The slide deck also discusses research methods with no accompanying implementation; those slides have no notebook band.

## Sources and credit

Tracking: [SkillCorner/opendata](https://github.com/SkillCorner/opendata), released with PySport. Notebook downloaders pin upstream revisions. The SkillCorner license notice is retained in `resources/SKILLCORNER_LICENSE.txt`. SkillCorner definitions anchor physical metrics; DataBallPy documentation supports methodology. Teaching estimates do not reproduce proprietary processing.

The xG notebook additionally uses [StatsBomb Open Data](https://github.com/hudl/open-data). External projects and datasets retain their own usage terms. See the reading list, model cards and notebook source links for attribution and limitations.

## Slide source and assets

Edit `slides/content.json` for slide text and notebook mappings. `scripts/build_slides.mjs` builds the deck using OpenAI's bundled artifact-tool runtime; `scripts/add_source_links.py` adds source and notebook hyperlinks, and `scripts/publish_previews.py` publishes rendered previews. These three scripts support the slide deck only.

`assets/methods/` retains slide illustrations. `resources/visual_manifest.json` records provenance. `resources/models/` retains the graph teaching checkpoint/history/model card and the licensed external DataBallPy xT grid used by slide illustrations. Method HTML exports are under `outputs/methods/`.
