# Validation

- Executed all 19 notebook code cells in order on the real SkillCorner sample; no error outputs.
- Saved player plots, embedded animation, widget state, pitch-control comparisons, graph features, AS/DAS summaries and hypothetical-pass completion estimates.
- Ran nine numerical tests covering motion/gap handling, effort segmentation, control bounds, graph construction, temporal-edge direction and continuity, lag masking, and fitted xT lookup orientation.
- Rendered and visually inspected all 61 slides. Every method has a dedicated visual. No duration, audience-skill or agenda slide is included.
- PowerPoint package integrity, slide geometry/font policy and first-party import checks completed through the presentation finalizer.
- Exported the executed notebook as standalone HTML for browser viewing. Jupyter is required for live Python widgets.

Limitations: Gaussian/arrival-time surfaces and physical effort rules are teaching baselines. No full EPV, xG or GNN model is trained here. Source data are a bounded first-half sample, not a full match. See METHODOLOGY.md for definitions and reproduction boundaries. PowerPoint was validated through rendering/import tools, not opened in the Microsoft PowerPoint application.

Role update: executed notebook with angular features and assignment outputs; nine tests pass, including translation/rotation invariance, Hungarian assignment and causal persistence with gap reset. Rendered all 61 slides and inspected the new figures and deck contact sheet. GraphEPV target checked against the primary PyData London 2025 slides.

Avenue notebooks: executed all seven independently from fresh kernels (36 code cells, zero notebook error outputs) and saved seven standalone HTML exports. Reviewed a figure from every notebook. Inline checks cover timing matching, fixed-template assignment, softmax/logistic optimization, xT convergence, threshold interpolation, graph permutation invariance, decreasing synthetic GNN loss, horizon censoring and causal attention. The original walkthrough notebook and slide deck are unchanged by this addition. Training checks use explicitly labeled synthetic data when the sample lacks sufficient reviewed labels; no research-model performance is asserted. Execution details are in `outputs/avenues/execution_report.json`.

Complete-method notebooks: consolidated helper operations into 17 analytical workflows under `notebooks/methods/`. Every notebook contains its downloader, loader, reshaping, drawing helpers and method code inline, with intermediate tables and staged visualizations. All 202 code cells executed in fresh kernels without notebook error outputs. AST checks confirm no imports of local workshop/helper modules. The graph workflow includes a finite-difference gradient check; temporal attention checks its causal mask and row normalization. Saved corresponding HTML exports and an execution report under `outputs/methods/`. The original walkthrough and avenue notebooks are retained unchanged. Synthetic examples and proxy methods remain explicitly labeled.
