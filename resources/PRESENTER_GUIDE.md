# Presenter guide

The deck is organized into five analytical avenues. Each section introduces its scope and ideas; method slides pair a concise problem/method description with a dominant result visual. Numbered implementation steps remain in the standalone notebooks.

Movies are native embedded MP4s. Click a movie in slideshow view. Posters remain visible when stopped. Research figures retain their authors’ results and source links.

## 1. Tracking Data Applied

SkillCorner open tracking, StatsBomb shot freeze frames, published research and independent teaching models are identified throughout.

[SkillCorner open data and schema](https://github.com/SkillCorner/opendata)

## 2. What can tracking data answer?

User-requested introduction to all avenues. Graphs and GNNs are general modeling tools introduced within game modeling, with applications beyond EPV. No duration or audience-level framing.

[SkillCorner open data and schema](https://github.com/SkillCorner/opendata)

## 3. Data and documentation

The opening entries are linked. Full sources are in the reading list. Real sample: Brisbane vs Perth, 21 December 2024, match 1925299.

**Problem:** Where do coordinates, labels and metric definitions come from?

**Methods:** SkillCorner open data; kloppy ingestion; DataBallPy metric documentation.

**Result:** Keep coordinates, supplied labels and our derived estimates distinct.

[Method notebook](../notebooks/methods/01_data_exploration.ipynb)

[SkillCorner open data and schema](https://github.com/SkillCorner/opendata)
[kloppy SkillCorner loader](https://kloppy.pysport.org/reference/providers/skillcorner/)
[DataBallPy covered distance](https://databallpy.readthedocs.io/en/main/features/covered_distance_page.html)

## 4. Tracking quality and visibility

Actual SkillCorner frame 163. The green polygon connects top-left, bottom-left, bottom-right and top-right image_corners_projection in native metric coordinates; its fill is clipped to the pitch, while the boundary retains the actual projected corners. Green shading shows the camera footprint, gray pitch lies outside it. Player marker style comes directly from is_detected: filled detections, hollow extrapolations; orange Brisbane, purple Perth. This illustrative frame has 11 players inside/detected and 11 outside/extrapolated. Polygon membership is not substituted for detection status: occlusion or missed detections can occur inside the camera footprint. Coordinates outside camera coverage may still be supplied by extrapolation.

**Problem:** Which positions were observed on screen?

**Methods:** Project image corners; read each player’s is_detected flag.

**Result:** Camera coverage and detection status are related, separate fields.

[Method notebook](../notebooks/methods/01_data_exploration.ipynb)

[SkillCorner open data and schema](https://github.com/SkillCorner/opendata)
[DataBallPy preprocessing](https://databallpy.readthedocs.io/en/main/getting_started/preprocessing_options.html)

## 5. Read movement in context

Embedded native-rate MP4 of actual SkillCorner player and ball positions with shirt numbers. Click the movie in slideshow view. Tracking visualization, not broadcast footage.

**Problem:** What does a tracking sequence reveal that one frame misses?

**Methods:** Animate the same player identities and ball through time.

**Result:** Motion, team structure and tracking uncertainty become visible.

[Method notebook](../notebooks/methods/01_data_exploration.ipynb)

[Standalone MP4](../assets/videos/tracking_playback.mp4)

[SkillCorner open data and schema](https://github.com/SkillCorner/opendata)
[kloppy SkillCorner loader](https://kloppy.pysport.org/reference/providers/skillcorner/)

## 6. Event detection

Can continuous coordinates recover the events we want to analyze?
Ideas: Ball control and possession; Pass release and reception; Shots, carries and duels; Pressure and defensive engagements; Timing-aware validation; Ambiguity and missing ball tracking


## 7. Who controls the ball?

Result video highlights stable-control candidates, with a possession timeline and player–ball distance plot. Candidate uses distance ≤2 m, ball height ≤2 m and ≥0.3 s stable control. This is an offline heuristic, not a validated event detector or PathCRF implementation. Half-speed playback.

**Problem:** Identify the likely ball carrier between recorded events.

**Methods:** Proximity and ball-height gates; require stable control.

**Result:** Highlighted carrier states; uncertain intervals remain unassigned.

[Method notebook](../notebooks/methods/02_event_detection.ipynb)

[Standalone MP4](../assets/videos/possession_result.mp4)

[SkillCorner open data and schema](https://github.com/SkillCorner/opendata)
[PathCRF: player trajectories to events (2026)](https://github.com/hyunsungkim-ds/pathcrf)

## 8. When does a pass occur?

Actual player–ball distances, horizontal ball speed and ball height share the same clip time axis. Release/reception gates follow notebook 02; speed is diagnostic, not a learned or fitted threshold. Dashed target arrow is the retrospectively identified candidate. No precision/recall claim.

**Problem:** Separate a pass from touches, ball transit and reception.

**Methods:** Link same-team control segments; inspect distance and ball motion.

**Result:** Release and reception candidates align with the physics traces.

[Method notebook](../notebooks/methods/02_event_detection.ipynb)

[Standalone MP4](../assets/videos/pass_physics.mp4)

[SkillCorner open data and schema](https://github.com/SkillCorner/opendata)
[PathCRF: player trajectories to events (2026)](https://github.com/hyunsungkim-ds/pathcrf)

## 9. Formation and position identification

How can we describe team organization while players move and rotate?
Ideas: Team shape and phase-conditioned averages; Formation-template identification; Player roles and positional rotations; Role signatures from relative geometry; Persistent formation-change candidates; Substitutions and asymmetric shapes


## 10. Which formation best fits this shape?

Best residual example from defensive 30-second windows; ten outfield players, at least 50 qualifying frames each. Four fixed templates and Hungarian squared-distance assignment. Player labels are assigned template slots, not reviewed role truth. Raw versus centered covariance ellipses appear as a small inset. RMS error is not a formation probability; not elastic EFPI inference.

**Problem:** Infer organization from positions rather than the team sheet.

**Methods:** Centroid normalization and minimum-cost template assignment.

**Result:** A best-fitting formation, assigned slots and competing scores.

[Method notebook](../notebooks/methods/03_formation_analysis.ipynb)

[Shaw & Glickman: Dynamic Analysis of Team Strategy](https://static.capabiliaserver.com/frontend/clients/barca/wp_prod/wp-content/uploads/2020/01/83c87dfe-barca_poster_shaw.pdf)
[Joris Bekkers: Elastic Formation and Position Identification](https://arxiv.org/abs/2506.23843)
[Devin Pleuler: Fixed to Fluid (2024)](https://github.com/devinpleuler/research/blob/master/frame-by-frame-position.md)

## 11. Which spatial signature describes a role?

Twenty-four attack-normalized headings; teammates only in the comparison. Sector geometry is not observed gaze or occlusion. Metadata roles label the examples, not frame-level ground truth. No real role-classifier performance is claimed; the notebook’s classifier training check remains synthetic.

**Problem:** Distinguish players by where their teammates lie around them.

**Methods:** Pleuler-inspired teammate counts across rotating 90° sectors.

**Result:** Contrasting angular signatures for wide, central and attacking roles.

[Method notebook](../notebooks/methods/04_role_classification.ipynb)

[Devin Pleuler: Fixed to Fluid (2024)](https://github.com/devinpleuler/research/blob/master/frame-by-frame-position.md)

## 12. Did the formation actually change?

Dominant timeline and before/after pitch views. Three consecutive available 30-second bins confirm a candidate; missing bins reset evidence, while the last confirmed state is retained. Gray windows are insufficient samples. No substitutions fall in this bounded sample. Differing candidates are not claimed to be verified formation changes.

**Problem:** Separate persistent reorganization from transient shape changes.

**Methods:** Compare defensive windows; confirm only persistent candidates.

**Result:** The timeline distinguishes raw candidates, confirmed labels and gaps.

[Method notebook](../notebooks/methods/03_formation_analysis.ipynb)

[Shaw & Glickman: Dynamic Analysis of Team Strategy](https://static.capabiliaserver.com/frontend/clients/barca/wp_prod/wp-content/uploads/2020/01/83c87dfe-barca_poster_shaw.pdf)
[Joris Bekkers: Elastic Formation and Position Identification](https://arxiv.org/abs/2506.23843)
[Devin Pleuler: Fixed to Fluid (2024)](https://github.com/devinpleuler/research/blob/master/frame-by-frame-position.md)

## 13. Match segmentation and phases

What tactical context should an event, shape or workload be compared within?
Ideas: Possession and transition phases; Build-up, progression and advanced play; Defensive blocks and pressing phases; Set pieces and interruptions; Phase duration and boundary detection; Context-conditioned physical/tactical summaries


## 14. Where does one phase end and another begin?

Rule-based estimates use possession age, attack-normalized ball location and past progression speed, with three-frame confirmation. Provider labels use SkillCorner’s taxonomy. Compare interval behavior, not exact label accuracy without a reviewed mapping. The video shows actual transition context.

**Problem:** Assign context to continuous tracking intervals.

**Methods:** Causal rule estimates versus supplied SkillCorner phase intervals.

**Result:** The synchronized timelines expose boundaries and disagreements.

[Method notebook](../notebooks/methods/05_match_segmentation.ipynb)

[Standalone MP4](../assets/videos/phase_comparison.mp4)

[Augmented possession and phases framework (2025)](https://doi.org/10.1177/22150218241290988)
[SkillCorner open data and schema](https://github.com/SkillCorner/opendata)

## 15. Physical metrics

How much did players move, and what physical capacities did they demonstrate?
Ideas: Distance and valid tracking exposure; High-speed and sprint distance; Sprint efforts and repeated intensity; Acceleration and braking; Time to high-speed running / sprint; PSV-99 and Peak Velocity


## 16. How much ground did one player cover?

Same smoothing and contiguous-segment derivative rules as notebook 06. Cumulative distance uses mean endpoint speeds and observed elapsed time. Coverage is valid integration seconds divided by bounded sample duration. Extrapolated positions may still contribute; no full-match extrapolation.

**Problem:** Measure movement volume without hiding missing intervals.

**Methods:** Integrate speed only across valid consecutive intervals.

**Result:** Cumulative distance is reported alongside the valid sample coverage.

[Method notebook](../notebooks/methods/06_physical_metrics.ipynb)

[DataBallPy covered distance](https://databallpy.readthedocs.io/en/main/features/covered_distance_page.html)
[DataBallPy preprocessing](https://databallpy.readthedocs.io/en/main/getting_started/preprocessing_options.html)

## 17. Who accumulated high-intensity distance?

Main bars: HSR [20,25) and sprint [25,infinity) km/h. Small speed trace illustrates threshold-qualified intervals. Exact equality handling is a teaching convention. Compare exposure/coverage before interpreting player rankings; these are not full-match or official production totals.

**Problem:** Separate high-speed running from total movement volume.

**Methods:** Integrate distances within explicitly defined speed bands.

**Result:** Player comparison bars show HSR and sprint contributions.

[Method notebook](../notebooks/methods/06_physical_metrics.ipynb)

[SkillCorner physical thresholds and time-to metrics](https://skillcorner.com/us/articles/scouted-brazilian-centre-backs)
[DataBallPy covered distance](https://databallpy.readthedocs.io/en/main/features/covered_distance_page.html)

## 18. How many sprint efforts qualified?

Uses ≥25 km/h for at least one second, with no merging across gaps. Efforts are numbered on the trace; count comes from notebook 06. These are not exact SkillCorner production effort counts.

**Problem:** Distinguish sustained sprint efforts from brief speed spikes.

**Methods:** Threshold speed, minimum duration and an explicit gap rule.

**Result:** Qualifying efforts are shaded and counted on the speed trace.

[Method notebook](../notebooks/methods/06_physical_metrics.ipynb)

[SkillCorner physical thresholds and time-to metrics](https://skillcorner.com/us/articles/scouted-brazilian-centre-backs)
[DataBallPy preprocessing](https://databallpy.readthedocs.io/en/main/getting_started/preprocessing_options.html)

## 19. When does the player accelerate or brake?

Large signed acceleration trace; small synchronized speed trace. This is not acceleration-vector magnitude, and highlighted positive/negative samples are not automatically production-qualified explosive efforts. Derivatives amplify noise; smoothing changes peaks.

**Problem:** Describe speeding up and slowing down around an effort.

**Methods:** Differentiate smoothed scalar speed within valid segments.

**Result:** Positive bursts and braking intervals align with the speed trace.

[Method notebook](../notebooks/methods/06_physical_metrics.ipynb)

[SkillCorner explosive accelerations](https://skillcorner.com/articles/new-feature-explosive-accelerations)
[DataBallPy preprocessing](https://databallpy.readthedocs.io/en/main/getting_started/preprocessing_options.html)

## 20. How quickly does the player reach HSR?

Separate slide for 9→20 km/h. Shows fastest qualifying monotone crossing found by the notebook’s sample rule. Official SkillCorner Time to HSR uses additional explosive-acceleration qualification; this slide does not reproduce that production metric.

**Problem:** Measure the elapsed time from 9 to 20 km/h.

**Methods:** Inspect and interpolate one continuous rising-speed trajectory.

**Result:** The observed threshold-crossing interval is visible and labeled.

[Method notebook](../notebooks/methods/06_physical_metrics.ipynb)

[SkillCorner physical thresholds and time-to metrics](https://skillcorner.com/us/articles/scouted-brazilian-centre-backs)
[SkillCorner explosive accelerations](https://skillcorner.com/articles/new-feature-explosive-accelerations)

## 21. How quickly does the player reach sprint speed?

Separate slide for 9→25 km/h with its own actual trajectory. No official Time to Sprint or Top-3 metric is reconstructed; opportunity, qualification and filtering matter.

**Problem:** Measure the elapsed time from 9 to 25 km/h.

**Methods:** Inspect and interpolate one continuous rising-speed trajectory.

**Result:** Time to sprint is distinct from the maximum speed reached.

[Method notebook](../notebooks/methods/06_physical_metrics.ipynb)

[SkillCorner physical thresholds and time-to metrics](https://skillcorner.com/us/articles/scouted-brazilian-centre-backs)
[SkillCorner explosive accelerations](https://skillcorner.com/articles/new-feature-explosive-accelerations)

## 22. PSV-99: a robust speed-capacity proxy

Original chart from SkillCorner, Peak Velocity article, 11 June 2026. PSV-99 is described as the 99th percentile of physical activities over 15 km/h, not all frame speeds. This figure is supplied research/product communication, not our sample calculation. Retain original legend and axes.

**Problem:** How can speed capacity be summarized without one noisy maximum?

**Methods:** SkillCorner’s 99th percentile of physical activities above 15 km/h.

**Result:** The published example contrasts an activity-based proxy with peak speed.

[SkillCorner PSV-99 and Peak Velocity](https://skillcorner.com/articles/skillcorner-releases-new-peak-velocity-metric)

## 23. Peak Velocity: absolute top-end speed

Original SkillCorner figure. Article reports correlation 0.96 / R² 0.92 when averaging each player’s top three metric values in the displayed validation. Do not generalize this validation to our smoothed sample maxima or to every competition.

**Problem:** What is the highest speed a player reliably reaches?

**Methods:** SkillCorner’s validated maximum-speed processing.

**Result:** The provider’s published validation compares Peak Velocity with ground truth.

[SkillCorner PSV-99 and Peak Velocity](https://skillcorner.com/articles/skillcorner-releases-new-peak-velocity-metric)

## 24. Game modeling

Which locations, options and game states create or prevent scoring opportunities?
Ideas: Shot quality and location value; Control, interception and completion; Accessible and dangerous space; Off-ball options and run threat; Graphs and learned relational models; Possession value and tactical applications


## 25. How does context change a shot estimate?

Actual out-of-fold predictions from notebook 07; no model used the example match during that fold’s training. Context includes goalkeeper distance/offset and defender geometry. Selected for model disagreement, not as evidence of aggregate improvement. Freeze-frame coverage is not continuous full tracking.

**Problem:** Location alone cannot describe the goalkeeper and defenders.

**Methods:** Compare location-only and contextual logistic xG on the same shot.

**Result:** The same real freeze frame receives two different held-out estimates.

[Method notebook](../notebooks/methods/07_expected_goals.ipynb)

[StatsBomb: Upgrading Expected Goals](https://blogarchive.statsbomb.com/articles/soccer/upgrading-expected-goals/)

## 26. Does context improve xG discrimination?

Location AUC 0.743879, 95% match-bootstrap interval [0.713895,0.774165]; contextual 0.779870 [0.749411,0.809066]. Paired difference 0.035990 [0.021778,0.051104]. 1,000 match resamples of existing out-of-fold predictions, without refitting. Training-only scaling. ROC is discrimination, not calibration.

**Problem:** Test contextual features across held-out matches, not one example.

**Methods:** Same five match-grouped folds for both logistic models.

**Result:** ROC AUC rises from 0.744 to 0.780 on the shared eligible cohort.

[Method notebook](../notebooks/methods/07_expected_goals.ipynb)

[StatsBomb: Upgrading Expected Goals](https://blogarchive.statsbomb.com/articles/soccer/upgrading-expected-goals/)

## 27. Which completed moves increase location value?

Main map: licensed fitted DataBallPy open-play grid; SkillCorner successful player-possession passes use release coordinates x_end/y_end and supplied reception coordinates. Attack-normalized 105 m x scaled to the model 106 m convention. Two highest positive and one highest negative gains are selected examples. Small inset: synthetic two-state fitting mechanics from notebook 08; not training the full grid on this sample. Source provenance JSON stores event IDs.

**Problem:** Value progression before a shot is taken.

**Methods:** Fitted location xT; value a completed move by V(end)−V(start).

**Result:** Actual completed passes gain or lose value on the fitted map.

[Method notebook](../notebooks/methods/08_expected_threat.ipynb)

[Karun Singh: Expected Threat](https://karun.in/blog/expected-threat.html)
[DataBallPy fitted xT methodology](https://databallpy.readthedocs.io/en/main/features/xt_models.html)

## 28. Who is closest to each patch of space?

Grid approximation to Voronoi on a real frame. Strength: simple and interpretable. Limitation: ignores player movement, ball travel and uncertainty.

**Problem:** Build a transparent geometric control baseline.

**Methods:** Voronoi regions from nearest-player distance.

**Result:** Hard boundaries partition the pitch into nearest-player regions.

[Method notebook](../notebooks/methods/09_voronoi_control.ipynb)

[Space and Control in Soccer (2021)](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2021.676179/full)
[Wide Open Spaces, Fernández & Bornn (2018)](https://static.capabiliaserver.com/frontend/clients/barca/wp_prod/wp-content/uploads/2018/05/Wide-Open-Spaces.pdf)

## 29. How does movement shape spatial influence?

Directional Gaussian teaching parameterization, not exact Fernández/Bornn covariance. Bounded team comparison is not calibrated possession probability. Velocity and covariance affect the surface; contribution is not causal importance.

**Problem:** Replace hard boundaries with smooth directional influence.

**Methods:** Projected Gaussian player influence, aggregated by team.

**Result:** A continuous team-influence surface reflects movement direction.

[Method notebook](../notebooks/methods/10_gaussian_control.ipynb)

[Wide Open Spaces, Fernández & Bornn (2018)](https://static.capabiliaserver.com/frontend/clients/barca/wp_prod/wp-content/uploads/2018/05/Wide-Open-Spaces.pdf)

## 30. Which team reaches a target sooner?

0.7 s projection/reaction and 5 m/s travel baseline. No full ball-flight, acceleration optimization or competing interception-rate integration. Not the full Spearman model.

**Problem:** Model the race to space rather than only proximity.

**Methods:** Reaction/projection time and earliest team travel time.

**Result:** The arrival-time score exposes contested and reachable regions.

[Method notebook](../notebooks/methods/11_arrival_time_control.ipynb)

[Beyond Expected Goals, Spearman (2018)](https://static.hudl.com/craft/downloads/SSAC2018_Beyond_Expected_Goals.pdf?mtime=20180327111214)
[Space and Control in Soccer (2021)](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2021.676179/full)

## 31. How do the control assumptions change the answer?

Original synchronized comparison video. Scores are teaching outputs, not calibrated possession probabilities; parameter choices are stated in assets/videos/README.md. Sampled at 5 Hz with real-time playback.

**Problem:** Compare methods without changing the tracking situation.

**Methods:** Voronoi, Gaussian and arrival-time baselines on identical frames.

**Result:** The moving comparison makes each model’s different boundaries visible.

[Method notebook](../notebooks/methods/11_arrival_time_control.ipynb)

[Standalone MP4](../assets/videos/control_comparison.mp4)

[Wide Open Spaces, Fernández & Bornn (2018)](https://static.capabiliaserver.com/frontend/clients/barca/wp_prod/wp-content/uploads/2018/05/Wide-Open-Spaces.pdf)
[Beyond Expected Goals, Spearman (2018)](https://static.hudl.com/craft/downloads/SSAC2018_Beyond_Expected_Goals.pdf?mtime=20180327111214)

## 32. Which passing targets are more likely to succeed?

Main surface: actual accessible-space 2.0.13 expected-completion inference on real SkillCorner tracking, respecting offside. Inset: independently parameterized uncalibrated teaching survival example. Notebook 12 implements a teaching model, not the published fitted parameters. Targets are hypothetical, not observed choices; no SkillCorner-domain calibration claim.

**Problem:** Assess a receiver before the pass is attempted.

**Methods:** Published accessible-space completion model; survival-proxy illustration.

**Result:** A field-wide completion map ranks hypothetical target locations.

[Method notebook](../notebooks/methods/12_pass_completion.ipynb)

[Dangerous Accessible Space: paper and implementation](https://github.com/jonas-bischofberger/accessible-space)
[DataBallPy DAS and expected completion](https://databallpy.readthedocs.io/en/main/features/dangerous_accessible_space.html)
[Beyond Expected Goals, Spearman (2018)](https://static.hudl.com/craft/downloads/SSAC2018_Beyond_Expected_Goals.pdf?mtime=20180327111214)

## 33. Where can the attacking team receive?

Actual accessible-space inference. Public model simulation settings and frame provenance are recorded in assets/results/space_result_provenance.json. Notebook 13 demonstrates a simpler area-integral proxy; it is not this published output. AS is an area quantity; individual accessible regions may overlap.

**Problem:** Measure space that is accessible through potential passes.

**Methods:** Published pass-flight and player-interception simulation.

**Result:** The accessible-space surface identifies receiving opportunity.

[Method notebook](../notebooks/methods/13_space_and_danger.ipynb)

[Dangerous Accessible Space: paper and implementation](https://github.com/jonas-bischofberger/accessible-space)
[DataBallPy DAS and expected completion](https://databallpy.readthedocs.io/en/main/features/dangerous_accessible_space.html)

## 34. Which accessible space is dangerous?

Published dangerous-accessible-space output on the same frame as AS. DAS units are danger-weighted square metres, not scoring probability. The notebook’s chosen distance-based danger proxy is separate.

**Problem:** Separate available territory from valuable territory.

**Methods:** Weight published accessibility by the model’s danger definition.

**Result:** Danger weighting concentrates attention on useful receiving space.

[Method notebook](../notebooks/methods/13_space_and_danger.ipynb)

[Dangerous Accessible Space: paper and implementation](https://github.com/jonas-bischofberger/accessible-space)
[DataBallPy DAS and expected completion](https://databallpy.readthedocs.io/en/main/features/dangerous_accessible_space.html)

## 35. How does useful space change during play?

Published accessible-space outputs at 5 Hz; traces show AS m² and DAS danger-weighted m² separately. Team/possession context must be read with the clip. Before/after movement does not establish causal player credit.

**Problem:** Connect movement to changing options over time.

**Methods:** Recompute published AS and DAS on successive real frames.

**Result:** The video links changing surfaces with their own value traces.

[Method notebook](../notebooks/methods/13_space_and_danger.ipynb)

[Standalone MP4](../assets/videos/dangerous_space_result.mp4)

[Dangerous Accessible Space: paper and implementation](https://github.com/jonas-bischofberger/accessible-space)
[DataBallPy DAS and expected completion](https://databallpy.readthedocs.io/en/main/features/dangerous_accessible_space.html)

## 36. Which off-ball run offers more threat?

Selected low/high off-ball-run events fully covered by the sample. Each panel is synchronized to its own run start; the shorter run freezes at the end. A square marks supplied ball carrier when available; dashed lane is hypothetical. Values are supplied event-level xthreat fields, not locally fitted or controlled causal effects.

**Problem:** Recognize useful runs even when a pass is not played.

**Methods:** Compare supplied SkillCorner run-threat estimates in context.

**Result:** Two actual runs receive contrasting supplied threat values.

[Standalone MP4](../assets/videos/run_comparison.mp4)

[SkillCorner: Expected Threat for off-ball runs](https://www.linkedin.com/posts/skillcorner_game-intelligence-expected-threat-activity-7057009275247689728-NVPh)
[SkillCorner open data and schema](https://github.com/SkillCorner/opendata)

## 37. Why represent football as a graph?

Original graph illustration from Bekkers, PyData London 2025. General representation explanation before EPV: player/ball nodes, player-player and player-ball relations, adjacency and global context. The picture is conceptual, not a trained prediction. Source URL and attribution in assets/references/bekkers/attribution.json.

**Problem:** Positions alone hide who relates to whom.

**Methods:** Players and ball as nodes; relationships as edges.

**Result:** A graph encodes interactions without relying on player row order.

[Method notebook](../notebooks/methods/16_graph_epv.ipynb)

[Joris Bekkers: GraphEPV, PyData London 2025](https://rawcdn.githack.com/UnravelSports/keynotes/main/html/20250607-PyData-London.html)

## 38. What information should a graph carry?

Original node/global-feature matrix from the linked keynote. This is a general feature menu; do not imply our independent workshop GNN includes every displayed velocity, acceleration or global feature. Its actual features are current-frame geometry and identity/context indicators, specified in notebook 16.

**Problem:** Describe players and game context in machine-readable form.

**Methods:** Node feature vectors plus global match-state features.

**Result:** The feature matrix captures geometry and context for every node.

[Method notebook](../notebooks/methods/16_graph_epv.ipynb)

[Joris Bekkers: GraphEPV, PyData London 2025](https://rawcdn.githack.com/UnravelSports/keynotes/main/html/20250607-PyData-London.html)
[UnravelSports soccer GNN tutorial](https://unravelsports.readthedocs.io/en/latest/tutorials/soccer_gnn.html)

## 39. Which relationships can the model exchange information over?

Keynote adjacency matrix shows one documented team/ball connection configuration, not a unique universal GraphEPV topology. Edge features can describe distance, relative geometry and team relations; the actual workshop model uses 20 m radius edges plus ball links, not this matrix. The main visual combines original edge-feature and adjacency illustrations from the same keynote; both source files are retained and credited.

**Problem:** Choose which interactions a graph can represent.

**Methods:** Edge attributes and an explicit adjacency structure.

**Result:** Connectivity defines the available routes for relational information.

[Method notebook](../notebooks/methods/16_graph_epv.ipynb)

[Joris Bekkers: GraphEPV, PyData London 2025](https://rawcdn.githack.com/UnravelSports/keynotes/main/html/20250607-PyData-London.html)
[UnravelSports soccer GNN tutorial](https://unravelsports.readthedocs.io/en/latest/tutorials/soccer_gnn.html)

## 40. What does a graph neural network learn?

Original Sahasrabudhe & Bekkers architecture image reused in the keynote, attributed to its authors. General GNN explanation: shared updates, permutation-invariant aggregation and task-specific output. This is not our independent 353-parameter teaching architecture. No standalone temporal-network/encoder slides are included.

**Problem:** Use player relationships to predict a task outcome.

**Methods:** Shared message passing, graph pooling and a task-specific readout.

**Result:** Relational representations become a prediction for the chosen task.

[Method notebook](../notebooks/methods/16_graph_epv.ipynb)

[Joris Bekkers: GraphEPV, PyData London 2025](https://rawcdn.githack.com/UnravelSports/keynotes/main/html/20250607-PyData-London.html)
[U.S. Soccer: counterattack GNNs with SkillCorner (2023)](https://github.com/USSoccerFederation/ussf_ssac_23_soccer_gnn)

## 41. How does the graph change as players move?

Player-only real radius graph at native 10 Hz. The trained workshop graph additionally includes a ball node and ball links. Recomputing spatial edges over time is not itself a trained temporal network or learned attention.

**Problem:** A useful relationship at one instant may disappear at the next.

**Methods:** Recompute 20 m player-radius edges on real tracking frames.

**Result:** The video reveals changing spatial neighborhoods in actual play.

[Method notebook](../notebooks/methods/16_graph_epv.ipynb)

[Standalone MP4](../assets/videos/dynamic_graph.mp4)

[Joris Bekkers: GraphEPV, PyData London 2025](https://rawcdn.githack.com/UnravelSports/keynotes/main/html/20250607-PyData-London.html)
[UnravelSports soccer GNN tutorial](https://unravelsports.readthedocs.io/en/latest/tutorials/soccer_gnn.html)

## 42. Graph EPV: what exactly are we predicting?

Published PyData London 2025 target uses World Cup PFF tracking and event-aligned goals, respecting team and period. Our notebook trains an independent frame GNN on SkillCorner with reconstructed, score-audited goal timing. It is not Bekkers’ CrystalGraph architecture/weights or a full action-decomposed EPV reproduction.

**Problem:** Turn a tracking state into a clearly defined future outcome.

**Methods:** Bekkers: one frame graph; goal by the possession team within 10 s.

**Result:** A scoring probability belongs to a stated team and time horizon.

[Method notebook](../notebooks/methods/16_graph_epv.ipynb)

[Joris Bekkers: GraphEPV, PyData London 2025](https://rawcdn.githack.com/UnravelSports/keynotes/main/html/20250607-PyData-London.html)

## 43. Does our graph model generalize to unseen matches?

16 included matches total: 10 train, 3 validation, 3 test. Test has 4,846 sampled states and 16 positives, not 16 independent goals. AP baseline prevalence 0.00330. Log loss improves 0.02363→0.02158; Brier worsens 0.003308→0.003335. Model mean prediction 0.00858 versus test prevalence 0.00330. Goal timing is reconstructed and not video-verified. ROC and PR are actual saved notebook results; no temporal model was trained.

**Problem:** Evaluate predictions beyond the training matches.

**Methods:** Match-level holdout; validation-only model selection and calibration.

**Result:** AUC 0.843; AP 0.020—ranking improves, probability reliability is limited.

[Method notebook](../notebooks/methods/16_graph_epv.ipynb)

[SkillCorner open data and schema](https://github.com/SkillCorner/opendata)
[Joris Bekkers: GraphEPV, PyData London 2025](https://rawcdn.githack.com/UnravelSports/keynotes/main/html/20250607-PyData-London.html)

## 44. What does EPV look like during a possession?

Actual independent trained model output from notebook 16. Display case is selected by goal context, not high prediction; not a performance sample. Shading indicates retrospective target window, not an input. Model features use the current frame only. User requested goal buildup plus separate performance results; non-goal example stays in the notebook.

**Problem:** Read a predicted scoring probability alongside the actual play.

**Methods:** Frozen workshop GNN evaluated frame by frame on an unseen match.

**Result:** The goal buildup’s predicted value evolves with player and ball positions.

[Method notebook](../notebooks/methods/16_graph_epv.ipynb)

[Standalone MP4](../assets/videos/graph_epv_possession.mp4)

[SkillCorner open data and schema](https://github.com/SkillCorner/opendata)
[Joris Bekkers: GraphEPV, PyData London 2025](https://rawcdn.githack.com/UnravelSports/keynotes/main/html/20250607-PyData-London.html)

## 45. How do supplied pass values differ across events?

Actual pass_epv_delta_for event fields. Provider output is separate from our ten-second scoring model, classic location xT and Fernández’s action-decomposed EPV framework. Show original field name, target/horizon distinctions and source documentation; no reconstruction or cross-model numerical equivalence is asserted.

**Problem:** Inspect provider estimates without mixing model definitions.

**Methods:** Join supplied event-value fields to their tracking context.

**Result:** Pass EPV changes identify events worth examining in context.

[SkillCorner open data and schema](https://github.com/SkillCorner/opendata)
[Fine-grained expected possession value (2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8570314/)

## 46. SoccerMap: score every possible passing location

Original SoccerMap Figure 3, arXiv 2010.10202v1. Yellow/blue attacking/defending players, arrows are velocity, white circle is ball; original probability color scale retained. A CNN, not a GNN. This result is from the paper’s data/model, not our SkillCorner inference. Other heads can address pass selection and expected pass value.

**Problem:** Predict a surface rather than one chosen pass endpoint.

**Methods:** Fully convolutional network over spatial tracking feature channels.

**Result:** The published model produces a field-wide pass-success surface.

[SoccerMap (2020)](https://arxiv.org/abs/2010.10202)

## 47. DEFCON: credit defensive positioning

Original DEFCON paper Figure 3, page 7. Two intercepted passes; color is defender responsibility and numeric text is assigned defensive credit. Credit follows the framework’s assumptions, not causal proof. Cropped figure only, no values changed. Not model inference on our sample; authors’ underlying club dataset is not public.

**Problem:** Value prevention beyond tackles and interceptions.

**Methods:** Graph-based action values and defender responsibility estimates.

**Result:** Published defensive credits distribute value among involved defenders.

[DEFCON: GNN-based defensive EPV (2026)](https://github.com/hyunsungkim-ds/defcon)

## 48. Counterattacks: will this attack reach the box?

Original Figure 5a from A Graph Neural Network deep-dive into successful counterattacks. Women’s-model example predicts ending in the opponent penalty box with probability 49.5%. This is the published event-frame task; do not mix with additional all-frame goal-label datasets in the repository. Not our local model output.

**Problem:** Predict counterattack success from team interactions.

**Methods:** Graph classifiers trained on synchronized tracking and events.

**Result:** The published example shows a 49.5% model estimate for box entry.

[U.S. Soccer: counterattack GNNs with SkillCorner (2023)](https://github.com/USSoccerFederation/ussf_ssac_23_soccer_gnn)

## 49. TacticAI: improve a corner-kick setup

Original TacticAI Figure 3 from arXiv 2310.10553v1. Corner adjustment and predicted receiver probabilities are authors’ results, not interventions proven to improve match outcomes. Pre/post tactical suggestions are not locally generated or trained on SkillCorner. Retain original figure labels and legend.

**Problem:** Support decisions about receivers and player positioning.

**Methods:** Geometric graph learning with predictive and generative components.

**Result:** The published example compares receiver probabilities before and after adjustment.

[TacticAI (2024)](https://www.nature.com/articles/s41467-024-45965-x)

## 50. GenTac: forecast multiple plausible continuations

Original GenTac Figure 5 panel a, arXiv 2604.11786v1. Four-second history, 20 generated rollouts and resulting event distribution are from the paper. Cropped original panel, no probabilities changed. Not a workshop-trained forecast, not a standalone temporal-network architecture slide and not causal intervention evidence.

**Problem:** Represent uncertainty about how play may develop.

**Methods:** Diffusion-based multi-player trajectory generation and event prediction.

**Result:** Published forecast samples imply a distribution of possible tactical outcomes.

[GenTac: trajectory forecasting (2026 preprint)](https://arxiv.org/abs/2604.11786)

## 51. What would make these results trustworthy?

Event detection needs reviewed timing-tolerant matching. Formation/role labels require tactical ground truth. Physical comparisons require exposure and preprocessing definitions. Probability models need calibration and rare-event baselines. Stress-test extrapolated tracking, missing data, attack direction and domain shift. Current slide diagram is conceptual, not an extra experiment.

**Problem:** Distinguish an explanatory example from a reliable model.

**Methods:** Independent match splits; task-specific error and probability checks.

**Result:** A useful result states its target, evidence, uncertainty and failure modes.

[SkillCorner open data and schema](https://github.com/SkillCorner/opendata)
[Fine-grained expected possession value (2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8570314/)

## Formation visualization alternatives and ball markers

`slides/formation-options.pptx` contains four editable alternatives for slide 10: A role board, B candidate-template comparison, C raw/normalized ellipses beside the result, D assignment residuals. All use the same real window and fixed-template assignment; option C is now selected for main slide 10, with an additional matching panel and template RMS scores. Formation boards show schematic role slots, not observed coordinates.

The completion/accessible-space/dangerous-space maps and moving AS/DAS comparison now explicitly mark the ball. Because the original presentation was open in PowerPoint, this revision was saved as `slides/tracking-data-applied-updated.pptx`; the open file was preserved.

Slide 10 links centroid normalization to formation assignment: summarize normalized positions by coordinate-wise medians, optimize a one-to-one player-to-slot assignment for each template with the Hungarian algorithm, and rank the candidates by RMS distance. The plotted assignment shows the winning template; the final role board uses schematic slots.
