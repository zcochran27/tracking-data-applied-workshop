# Method notebooks

Explore soccer tracking analytics through calculations, plots and animations. Follow the [setup instructions](../../README.md#setup), open a notebook in JupyterLab and run its cells in order.

## Methods

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

## Explore another example

After a complete run, edit the example-selection cell and run it again, then rerun the final exploration cell. Use the displayed catalogs to find valid identifiers.

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

`DURATION_S` controls clip length. `FRAME_STRIDE = 1` uses every native 10 Hz frame; larger values render faster. Event IDs are strings, such as `'8_4'`. `DATA_ROOT` can point to an existing SkillCorner data cache; xG uses its StatsBomb `CACHE`.

See each notebook's assumptions and interpretation notes before drawing conclusions. Pitch-control, pass-survival and space baselines include uncalibrated teaching estimates. Role metadata are not frame-level role ground truth. The graph model's small dataset and sparse goals limit its reliability.
