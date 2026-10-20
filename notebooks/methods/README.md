# Standalone notebooks by analytical method

A notebook covers a complete analytical question, not each helper operation. For example, graph features, adjacency, message passing, pooling, labels and training live together in the graph-EPV workflow. Formation centering, assignment and change detection likewise form one notebook.

Every notebook includes **all code inline**, including data loading and drawing helpers, and runs in a fresh kernel. No local `.py` imports or previous notebook session are required. Intermediate tables and staged plots explain each transformation. Set `DATA_ROOT` to reuse a SkillCorner cache; the xG comparison uses its own StatsBomb `CACHE`. Install the repository requirements before running.

Read each notebook from top to bottom: inputs and assumptions, helper functions, intermediate calculations and visuals, final results, then interpretation. Diagnostics appear at the point where the calculation is introduced. The final pipeline reuses the inspected helpers rather than adding a separate explanation after its output.

| Notebook | Included stages |
|---|---|
| [Loading, quality, plotting and animation](01_data_exploration.ipynb) | Download and load; reshape; inspect quality; plot; animate |
| [Possession and pass-event detection](02_event_detection.ipynb) | Player–ball vectors; proximity; stable possession; release/transit/reception; timing evaluation |
| [Formation prediction and change detection](03_formation_analysis.ipynb) | Centroid distributions; exploratory line clustering; fixed-template assignment; persistence |
| [Player-viewpoint role classification](04_role_classification.ipynb) | Relative bearings; sector membership; teammate/opponent counts; softmax training |
| [Phase-of-play segmentation](05_match_segmentation.ipynb) | Features; rule gates; confirmation; interval construction; provider-label joins |
| [Physical-metric calculation pipeline](06_physical_metrics.ipynb) | Smooth positions; velocity; acceleration; distance integration; intensity bands; efforts; crossing times; sample peaks |
| [xG: location only versus goalkeeper/defender context](07_expected_goals.ipynb) | Real StatsBomb shots; two nested models; identical match-held-out folds; ROC/AUC for each; paired match-bootstrap intervals |
| [Expected Threat: fitting and action valuation](08_expected_threat.ipynb) | Action counts; reward; transition matrix; iterative solution; endpoint gain |
| [Voronoi pitch-control baseline](09_voronoi_control.ipynb) | Pairwise distance; nearest-player regions; team aggregation |
| [Gaussian influence and team control](10_gaussian_control.ipynb) | Projected centers; directional coordinates; covariance scale; player influence; team aggregation |
| [Arrival-time pitch-control baseline](11_arrival_time_control.ipynb) | Reaction; projected position; travel time; earliest arrival; bounded comparison |
| [Pass-interception survival model](12_pass_completion.ipynb) | Ball path and timing; player arrival; interception hazard; survival integration |
| [Accessible and dangerous space proxies](13_space_and_danger.ipynb) | Control surface; grid-cell area; danger weight; per-cell contributions; totals |
| [Off-ball run option-value proxy](14_run_threat.ipynb) | Completion component; destination value; product; before/after comparison |
| [Action-decomposed possession value](15_epv_decomposition.ipynb) | Selection probabilities; success/failure values; expected contribution; sum |
| [Graph-based EPV modeling pipeline](16_graph_epv.ipynb) | Real SkillCorner training; audited ten-second labels; match-level holdout; calibration; actual possession predictions; synchronized EPV animation |
| [Temporal graph modeling](17_temporal_graph_models.ipynb) | Lagged features; identity edges; graph embeddings; recurrent, convolutional and masked-attention alternatives |

The original presenter notebook and avenue notebooks remain available. Browser-readable copies of this set are in `outputs/methods/`.

Teaching boundaries: fixed-template formation fitting does not reproduce elastic EFPI. Gaussian, arrival-time, AS/DAS and run-threat examples are explicit proxies/baselines. Synthetic checks verify derivatives; the graph notebook then trains a separate real-data teaching GNN and shows its held-out results. Its reconstructed labels, few matches and sparse positive states limit reliability. It is not Bekkers' released model or a production system. The temporal notebook compares encoder choices inside the same modeling pipeline.
