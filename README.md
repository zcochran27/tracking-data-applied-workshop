# Tracking Data Applied

Illustrated soccer analytics methods using SkillCorner open tracking data. The slide deck links directly to the corresponding standalone method notebooks and embeds ten playable MP4 tracking/model videos. Click a video in PowerPoint slideshow view to play it. [Standalone video files](assets/videos/README.md) are also included.

## Materials

- [PowerPoint deck](slides/tracking-data-applied-updated.pptx)
- [14 standalone method notebooks](notebooks/methods/README.md)
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

Choose a method notebook and run its cells in order. Internet is required for the initial data download. Change the `selection` variables near the top to choose frames, possessions, events, players, formation windows or shots, then rerun the exploration cell. Tracking animations are generated in the notebook from coordinates and method calculations. No notebook downloads a video or requires widgets; separate HTML exports are not provided. Each notebook manages its own cache. Raw downloads are excluded from Git.

## Slide structure

The 51-slide deck opens with the five avenues, then organizes examples into event detection, formation/position identification, match segmentation, physical metrics and game modeling. Each avenue has a purpose-and-ideas opener. Method slides focus on the problem, a concise description of the methods and a dominant result visual; numbered implementation steps live in the notebooks.

General graph concepts use attributed Joris Bekkers keynote figures and a real dynamic-graph video. Standalone temporal-model architecture slides have been removed. Five full research examples use published figures: SoccerMap, DEFCON, counterattack GNNs, TacticAI and GenTac.

## Models and examples

The xG notebook uses StatsBomb Open Data shot freeze frames to compare location-only and goalkeeper/defender-context models on identical match-held-out folds, with ROC/AUC curves and uncertainty intervals.

The graph-EPV notebook includes real SkillCorner training code, a saved teaching checkpoint, held-out match results, possession-value curves and a synchronized animation generated directly inside the notebook. Set `RETRAIN=True` to retrain. Its reconstructed goal labels, limited matches and sparse positives constrain reliability; it does not reproduce Bekkers' architecture or weights.

Formation centering, template assignment and change detection form one workflow. Pleuler-inspired angular features and role classification form another. Pitch-control and space examples label their assumptions and teaching approximations. The slide deck also discusses research methods with no accompanying implementation; those slides have no notebook link.

## Sources and credit

Tracking: [SkillCorner/opendata](https://github.com/SkillCorner/opendata), released with PySport. Notebook downloaders pin upstream revisions. The SkillCorner license notice is retained in `resources/SKILLCORNER_LICENSE.txt`. SkillCorner definitions anchor physical metrics; DataBallPy documentation supports methodology. Teaching estimates do not reproduce proprietary processing.

The xG notebook additionally uses [StatsBomb Open Data](https://github.com/hudl/open-data). External projects and datasets retain their own usage terms. See the reading list, model cards and notebook source links for attribution and limitations.

## Slide source and assets

Edit `slides/content.json` for slide text and notebook mappings. `scripts/build_slides.mjs` builds the deck using OpenAI's bundled artifact-tool runtime; `scripts/add_source_links.py` adds source and notebook hyperlinks, and `scripts/publish_previews.py` publishes rendered previews. These scripts support the slide deck only. The `render_result_figures.py`, `render_space_results.py` and `render_xt_result.py` scripts create slide figures from notebook calculations, published-model inference and the licensed xT grid. `scripts/render_slide_videos.py` renders MP4 assets using cached tracking data, NumPy/SciPy/Matplotlib and an installed ffmpeg executable; it does not supply code to any notebook.

`assets/methods/` retains slide illustrations. `resources/visual_manifest.json` records provenance. `resources/models/` retains the graph teaching checkpoint/history/model card and the licensed external DataBallPy xT grid used by slide illustrations. Execution reports and derived data tables are under `outputs/methods/`.

On Windows with Microsoft PowerPoint installed, run `powershell -File scripts/verify_powerpoint_media.ps1` after rebuilding to verify that the native application resolves every embedded movie and its click-to-play action. The latest native check and playback-probe results are recorded in [PowerPoint media validation](resources/POWERPOINT_BALL_MEDIA_VALIDATION.json).

## Select another example

First run the notebook top to bottom. For another example, edit and run its selection cell, then rerun the final exploration cell; model refitting is not required. For example, set `FRAME_ID = 181` for a tracking frame, `PASS_INDEX = 1` for another detected pass, `FORMATION_WINDOW = 4` for a qualifying defensive window, or `SHOT_INDEX = 1` for another StatsBomb shot. Inspect the displayed catalogs for valid identifiers. Frame overrides take priority over event/possession starts. `FRAME_STRIDE = 1` uses every 10 Hz tracking frame; larger values speed rendering. Clips stop at missing coverage. xG has freeze-frame selection rather than fabricated motion.
