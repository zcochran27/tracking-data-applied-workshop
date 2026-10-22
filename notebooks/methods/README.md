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
| [Phase-of-play segmentation](05_match_segmentation.ipynb) | Features; priority rules; offline short-run suppression; phase intervals and timelines |
| [Physical-metric calculation pipeline](06_physical_metrics.ipynb) | Smooth positions; velocity; acceleration; distance integration; intensity bands; efforts; crossing times; sample peaks |
| [xG: location only versus goalkeeper/defender context](07_expected_goals.ipynb) | Real StatsBomb shots; two nested models; identical match-held-out folds; ROC/AUC for each; paired match-bootstrap intervals |
| [Expected Threat: fitting and action valuation](08_expected_threat.ipynb) | Action counts; reward; transition matrix; iterative solution; endpoint gain |
| [Voronoi pitch-control baseline](09_voronoi_control.ipynb) | Pairwise distance; nearest-player regions; team aggregation |
| [Gaussian influence and team control](10_gaussian_control.ipynb) | Projected centers; directional coordinates; covariance scale; player influence; team aggregation |
| [Arrival-time pitch-control baseline](11_arrival_time_control.ipynb) | Reaction; projected position; travel time; earliest arrival; bounded comparison |
| [Pass-interception survival model](12_pass_completion.ipynb) | Ball path and timing; player arrival; interception hazard; survival integration |
| [Accessible and dangerous space proxies](13_space_and_danger.ipynb) | Control surface; grid-cell area; danger weight; per-cell contributions; totals |
| [Graph-based EPV modeling pipeline](16_graph_epv.ipynb) | Real SkillCorner training; audited ten-second labels; match-level holdout; calibration; actual possession predictions; synchronized EPV animation |


Teaching boundaries: fixed-template formation fitting does not reproduce elastic EFPI. Gaussian, arrival-time, AS/DAS and run-threat examples are explicit proxies/baselines. Synthetic checks verify derivatives; the graph notebook then trains a separate real-data teaching GNN and shows its held-out results. Its reconstructed labels, few matches and sparse positive states limit reliability. It is not Bekkers' released model or a production system.

## Example controls

Each notebook has an editable example-selection cell near the top. After the first complete run, edit and run its variables, then rerun the final exploration cell. All animation drawing and method-overlay calculations are inline; no downloaded MP4, local helper module, widget or separate HTML file is needed. The saved notebook embeds its default animation as generated image frames.

| Method | Relevant selections |
|---|---|
| Tracking and visibility | `FRAME_ID`, `POSSESSION_INDEX`, `EVENT_ID` |
| Possession/pass detection | `PASS_INDEX`, frame or possession override |
| Formation | `FORMATION_WINDOW` (qualifying defensive windows are listed) |
| Player spatial signatures | `PLAYER_ID`, `FRAME_ID`, `FOV_DEGREES`, `HEADING_DEGREES` |
| Phases | `POSSESSION_INDEX`, frame/event selection; raw and smoothed predictions |
| Physical metrics | `PLAYER_ID`, `METRIC` (`speed`, `acceleration`, `distance`, `sprints`) |
| xG | `SHOT_INDEX`: real StatsBomb freeze frame and held-out estimates; no continuous tracking exists for these shots |
| xT | `EVENT_ID`: supplied completed-action ID, with actual tracking and the embedded licensed fitted grid |
| Control and space | `FRAME_ID`, `TEAM_ID`, possession/event selection |
| Pass survival | `FRAME_ID`, `RECEIVER_ID`; scores recomputed as players move |
| Graph EPV | `SEQUENCE` (`goal`, `non_goal`, `sample`), frame or possession override, optional period/team |

`DURATION_S` limits continuous tracking clips; `FRAME_STRIDE=1` uses every native 10 Hz frame. Larger strides make rendering faster. Unknown states and missing coverage remain visible or stop the clip; no player trajectories are interpolated. `available_possessions` lists uninterrupted supplied team-possession spans, while the event-detection notebook independently infers player control. Supplied event IDs are strings such as `'8_4'`; use the catalog rather than converting them to integers.

The explorer recomputes the notebook’s method rather than silently switching to another model. AS/DAS animations here show the independent area-integral proxies; the published outputs on the slides are a separate implementation. Pass-survival scores remain uncalibrated. Role examples use metadata labels, not validated frame-role truth.
