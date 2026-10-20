# Presenter guide

Notebook bands in the slides link directly to the corresponding standalone method notebook. Research-only slides have no notebook link.

## 1. Tracking Data Applied

Introduce the match and the distinction between observed tracking, extrapolated tracking and derived labels.

## 2. Data and documentation

The opening entries are linked. Full sources are in the reading list. Real sample: Brisbane vs Perth, 21 December 2024, match 1925299.

[Open method notebook](../notebooks/methods/01_data_exploration.ipynb)

## 3. Loading tracking data

The figure contains actual dataframe values; velocity columns are derived after loading.

[Open method notebook](../notebooks/methods/01_data_exploration.ipynb)

## 4. Tracking quality and visibility

Red rings mark extrapolated players according to raw is_detected. Coordinates can exist without a direct camera observation. All subsequent models inherit this uncertainty.

[Open method notebook](../notebooks/methods/01_data_exploration.ipynb)

## 5. Plotting a tracking frame

Use actual pitch dimensions. A visually plausible frame is a useful first check, but does not prove identity or position accuracy.

[Open method notebook](../notebooks/methods/01_data_exploration.ipynb)

## 6. Animating a sequence

Three snapshots are from the real selected clip. The notebook contains a full embedded animation.

[Open method notebook](../notebooks/methods/01_data_exploration.ipynb)

## 7. Possession detection

Figure is an actual 2 m proximity heuristic, not the full Vidal-Codina or PathCRF method. Pros: transparent and quick. Cons: aerial balls, duels and tracking uncertainty. Compare with supplied possession labels; evaluate timing-aware accuracy.

[Open method notebook](../notebooks/methods/02_event_detection.ipynb)

## 8. Pass-event detection

The real ball path is annotated at supplied possession endpoints. This is an explanatory candidate sequence, not a validated recovered pass. Pros: converts continuous signals to actionable events. Cons: missing ball data and multi-touch ambiguity.

[Open method notebook](../notebooks/methods/02_event_detection.ipynb)

## 9. Guess the current player roles

Audience prompt inspired by the supplied reference. These are actual SkillCorner frames, with identities hidden. A single snapshot is ambiguous; metadata positions are not frame-level role truth.

[Open method notebook](../notebooks/methods/03_formation_analysis.ipynb)

## 10. Position distributions and centering

Independently generated from SkillCorner. Two-standard-deviation covariance ellipses, not confidence regions. Labels are metadata roles. Pros: removes team translation. Cons: averaging still mixes phases and rotations; covariance can hide multimodal behavior. Use identical qualifying samples in both panels.

[Open method notebook](../notebooks/methods/03_formation_analysis.ipynb)

## 11. Pleuler: rotating player viewpoints

Pleuler (June 2024), independently implemented. Our choices: 24 headings and overlapping 90-degree sectors. This is geometric context, not observed head orientation, actual sight or occlusion. Attack-normalize both axes. Opponent-count channel is our extension. Pros: translation-invariant and intuitive. Cons: angular resolution, orientation and missing players affect features.

[Open method notebook](../notebooks/methods/04_role_classification.ipynb)

## 12. From angular features to role labels

Pleuler used XGBoost. This notebook manufactures features but does not train or claim accuracy from a single match. Assigned-position metadata gives weak labels during rotations. For credible evaluation use manually reviewed frame roles and held-out matches/players. Add opponent counts as a separate tested extension. Pros: flexible nonlinear classification. Cons: label noise and domain shift.

[Open method notebook](../notebooks/methods/04_role_classification.ipynb)

## 13. Formation prediction by assignment

Teaching baseline: four fixed templates, Hungarian minimum squared-distance assignment, attack-right orientation. RMS residual is not a probability. Unlike EFPI, this implementation has no elastic template optimization. Pros: interpretable assignments and no player-order dependence. Cons: template inventory, scale and asymmetry determine results.

[Open method notebook](../notebooks/methods/03_formation_analysis.ipynb)

## 14. Bekkers: elastic formation identification

EFPI is the published extension using elastic templates and linear assignment. The displayed visualization is our simpler fixed-template baseline, not an EFPI result. Follow the linked tutorial for package inference. Pros: formation and role assignment together. Cons: parameter choices, substitutions, partial tracking and tactical ambiguity. Compare output to video-reviewed labels.

## 15. Detecting formation-change candidates

Plot uses real defensive-context windows with at least 50 qualifying frames. Three consecutive available 30-second bins confirm a label; missing bins reset the candidate count. Existing confirmed state is retained through missing bins, not evidence of ongoing stability. This is an educational rule, not EFPI change logic. Pleuler explicitly proposed change detection without testing it. No tactical ground truth is available here. Role swaps alone need not imply formation changes.

[Open method notebook](../notebooks/methods/03_formation_analysis.ipynb)

## 16. Formation detection

Real median outfield positions are shown separately by possession. Pros: summarizes organization beyond a team sheet. Cons: averaging mixes roles and game states; these are not asserted formation labels.

[Open method notebook](../notebooks/methods/03_formation_analysis.ipynb)

## 17. Player-role and line detection

Ward clustering of real centered x positions into three groups is a teaching baseline. It is not a validated named-formation classifier. Pros: interpretable. Cons: fixed line counts, overlaps and rotations.

[Open method notebook](../notebooks/methods/03_formation_analysis.ipynb)

## 18. Phase-of-play segmentation

The plot shows supplied SkillCorner labels, not predictions from a classifier trained here. Pros: makes context explicit. Cons: taxonomy-dependent and sensitive to boundary definitions.

[Open method notebook](../notebooks/methods/05_match_segmentation.ipynb)

## 19. Estimating player speed

Actual speed curves are shown. Pros: foundation for physical and tactical features. Cons: derivatives amplify noise; smoothing removes some short peaks.

[Open method notebook](../notebooks/methods/06_physical_metrics.ipynb)

## 20. Distance covered

The real sample’s cumulative distance excludes missing derivatives. No full-match extrapolation. Pros: simple workload volume measure. Cons: incomplete and extrapolated tracking affect accuracy.

[Open method notebook](../notebooks/methods/06_physical_metrics.ipynb)

## 21. High-speed and sprint distance

Our code uses [20,25) and [25,infinity) to avoid overlap; exact equality handling is a teaching convention. Pros: distinguishes intensity from volume. Cons: thresholds and exposure affect comparisons.

[Open method notebook](../notebooks/methods/06_physical_metrics.ipynb)

## 22. Sprint-effort counts

Shaded segments are our >=1 s, no-merging teaching rule. They are not exact SkillCorner production sprint counts. Pros: repeated-effort view. Cons: sensitive to thresholds, smoothing and merging rules.

[Open method notebook](../notebooks/methods/06_physical_metrics.ipynb)

## 23. Acceleration and deceleration

The plot uses real signed speed derivatives. A direction change can produce acceleration-vector magnitude without increasing scalar speed. Pros: captures bursts and braking. Cons: highly noise-sensitive; threshold crossing alone does not qualify a production explosive effort.

[Open method notebook](../notebooks/methods/06_physical_metrics.ipynb)

## 24. Time to high-speed running

The real crossing is illustrative, not production-qualified. The published metric is the minimum interval within qualifying explosive accelerations. Start detection, >0.7 s high-acceleration qualification and filtering matter.

[Open method notebook](../notebooks/methods/06_physical_metrics.ipynb)

## 25. Time to sprint

Real observed crossing shown. No official Time to Sprint or Top 3 value is reconstructed. Pros: explosiveness/capacity. Cons: limited opportunities, sample size and qualification rules.

[Open method notebook](../notebooks/methods/06_physical_metrics.ipynb)

## 26. PSV-99: activity-based speed capacity

The real frame-speed distribution illustrates why populations matter. SkillCorner describes PSV-99 over physical activities above 15 km/h. This histogram is not the official PSV-99 calculation.

[Open method notebook](../notebooks/methods/06_physical_metrics.ipynb)

## 27. Peak Velocity: absolute top speed

The figure uses our smoothed sample-speed estimates. It does not reproduce SkillCorner’s validated production Peak Velocity. Pros: interpretable capacity measure. Cons: noisy spikes, short exposure and preprocessing dependence.

[Open method notebook](../notebooks/methods/06_physical_metrics.ipynb)

## 28. Expected goals: shot quality

Hypothetical shot rays at a real ball location; no xG prediction is invented. Pros: familiar target and interpretable features. Cons: sparse shots, outcome imbalance and contextual bias.

[Open method notebook](../notebooks/methods/07_expected_goals.ipynb)

## 29. Expected Threat: location value

Actual fitted DataBallPy open-play grid, not trained on this small sample. V(s)=P(shot|s)P(goal|shot,s)+sum P(successful move to s'|s)V(s'). Classic location xT does not use defender positions. State the model target and training domain.

[Open method notebook](../notebooks/methods/08_expected_threat.ipynb)

## 30. Expected Threat gained

The arrow is real ball displacement in the selected clip, not an assertion of a single completed pass. Attack direction is normalized and 105 m scaled to the model’s 106 m convention. Pros: simple action valuation. Cons: path-independent, no defender context or causal attribution.

[Open method notebook](../notebooks/methods/08_expected_threat.ipynb)

## 31. Voronoi space control

Actual frame, grid approximation to a Voronoi partition. Pros: quick and interpretable. Cons: hard boundaries and no movement, ball-flight or uncertainty.

[Open method notebook](../notebooks/methods/09_voronoi_control.ipynb)

## 32. Gaussian player influence

Real player velocity with an illustrative ellipse. The covariance is not the exact Fernández/Bornn parameterization. Pros: smooth and motion-aware. Cons: hand-set influence scale and simplified movement ability.

[Open method notebook](../notebooks/methods/10_gaussian_control.ipynb)

## 33. Gaussian team control

Our logistic transformation bounds the team difference; it is not a calibrated possession probability. Pros: contested-space view. Cons: aggregation and covariance assumptions affect the surface.

[Open method notebook](../notebooks/methods/10_gaussian_control.ipynb)

## 34. Arrival-time control

Actual frame with a simple 0.7 s projection and 5 m/s travel speed baseline. Pros: interpretable timing. Cons: no ball flight, acceleration optimization or interception-rate integration; not Spearman’s full model.

[Open method notebook](../notebooks/methods/11_arrival_time_control.ipynb)

## 35. Ball-aware pitch control

Architecture schematic on actual tracking context, not a computed Spearman surface. Pros: physical link to passing. Cons: uncertain reactions, speed and ball parameters. Separate from the arrival-time teaching baseline.

## 36. Expected pass completion

Actual accessible-space xC inference on hypothetical endpoints at real teammate positions. Pros: interpretable risk. Cons: model calibration, ball speed and offside conventions; candidates are not observed choices.

[Open method notebook](../notebooks/methods/12_pass_completion.ipynb)

## 37. Accessible space

Actual public-model output. Pros: incorporates ball and player movement. Cons: simulation assumptions and resolution; individual access can overlap.

[Open method notebook](../notebooks/methods/13_space_and_danger.ipynb)

## 38. Dangerous accessible space

Actual public-model dangerous surface. Pros: links access and useful territory. Cons: danger definition and physical assumptions; DAS units are danger-weighted square metres.

[Open method notebook](../notebooks/methods/13_space_and_danger.ipynb)

## 39. Changes in dangerous space

Actual model values on three frames. Pros: connects movement to changing opportunity. Cons: different team possession states and model noise must be checked; before/after changes alone are not causal credit.

[Open method notebook](../notebooks/methods/13_space_and_danger.ipynb)

## 40. Off-ball run threat

Actual supplied xthreat values for off-ball runs. The provider model is not reconstructed. Pros: visible unserved contributions. Cons: counterfactual assumptions, context and selection bias.

## 41. Tracking as a spatial graph

Real radius graph. Pros: models relationships directly. Cons: radius edges miss distant tactical relationships; fully connected and learned connectivity are alternatives.

[Open method notebook](../notebooks/methods/16_graph_epv.ipynb)

## 42. Node and edge features

Actual edge-feature rows. Edge direction controls the sign of relative position. Team IDs should be encoded meaningfully rather than treated as numeric magnitudes.

[Open method notebook](../notebooks/methods/16_graph_epv.ipynb)

## 43. Graph neural message passing

Architecture schematic, not a trained result. Pros: relational inductive bias and shared updates. Cons: oversmoothing, connectivity choices and training requirements. Attention alone is not causal importance.

[Open method notebook](../notebooks/methods/16_graph_epv.ipynb)

## 44. Temporal node features

Actual one-second lag and speed change on a real player. Explicit lag frame checks prevent bridging gaps. Instantaneous velocity adds motion information but is not a substitute for full history.

## 45. Dynamic graphs over time

Actual snapshots and a player trail. A sequence of spatial graphs retains team interactions that change with time; a static aggregate passing network does not.

## 46. Temporal edges between snapshots

Schematic topology with real player IDs. The notebook creates actual spatial and temporal edge records. Do not connect across substitutions or tracking gaps without an explicit rule; labels cannot leak future frames.

## 47. Recurrent temporal graph models

Architecture schematic rather than a claim about a specific cited model’s GRU implementation. Pros: sequential processing with a compact state. Cons: long-history retention and sequence alignment. No trained inference is shown.

## 48. Temporal convolution on graph history

Architecture schematic. Pros: parallel computation and explicit receptive field. Cons: window length, dilation and sampling-rate choices. Filters must not access future frames at prediction time.

## 49. Causal temporal attention

Architecture schematic. Pros: flexible history selection and long-range dependencies. Cons: data/computation requirements, masking and leakage; attention weights do not establish causal importance.

## 50. Spatiotemporal message passing

General architecture schematic, not a reproduction of PathCRF. Pros: joint relational/time structure. Cons: graph size, identity errors and edge construction choices.

## 51. SoccerMap: spatial neural prediction

Architecture schematic. SoccerMap is a convolutional approach, not a GNN. Pros: field-wide outputs. Cons: rasterization and training data requirements; no pretrained inference is claimed.

## 52. Bekkers: building a football graph

Real SkillCorner frame with one documented UnravelSports configuration: split-by-team connections plus ball links. This is not asserted as the unique GraphEPV topology. Pros: permutation-invariant aggregation and relational features. Cons: edges determine which interactions can be learned. Current documentation recommends PyTorch Geometric; the 2025 talk used Keras/Spektral.

## 53. Bekkers: GraphEPV scoring target

PyData London, 7 June 2025. Talk uses World Cup 2022 PFF data across 64 matches, with labels respecting team and period. This is a ten-second scoring target, not automatically the complete action-decomposed Fernández EPV framework. Schematic only: no pretrained model inference here. Strength: includes off-ball context. Limitation: rare correlated labels, calibration and transfer to another competition.

[Open method notebook](../notebooks/methods/16_graph_epv.ipynb)

## 54. GraphEPV and temporal extensions

Our extension discussion, not a claim that the 2025 GraphEPV presentation trained a temporal GNN. Use the existing lagged features, GRU, TCN and attention slides as alternative temporal encoders. Keep whole matches/possessions together when splitting; account for the ten-second outcome window. Compare against location xT and non-graph models on the same target.

## 55. Expected possession value

Conceptual decomposition: sum over actions P(action|state) times outcome-conditional value, including failure. EPV is a framework/target, not a synonym for GNN. Different EPV definitions must not be mixed.

## 56. Observed passes and supplied EPV

Actual pass_epv_delta_for fields in SkillCorner dynamic events. This is the provider’s model output; not a reconstructed Fernández or DEFCON prediction. The field name is shown rather than assuming undocumented equivalence.

## 57. DEFCON: defensive contribution

Architecture schematic only. Explain attribution assumptions before interpreting defensive credits. Actual frame is context, not DEFCON inference.

## 58. U.S. Soccer: counterattack graphs

Architecture schematic. The published balanced event-frame study uses reaching the penalty area as success; the repository’s additional all-frame dataset has different goal labels. Do not mix those datasets or quote them as equivalent.

## 59. TacticAI: corner-kick modeling

Architecture schematic. The input illustration uses real tracking near a supplied corner-reception event; it is not the original TacticAI input or trained inference. Complete task-specific code/weights and licensed data are not released. Model-generated suggestions are not guarantees.

## 60. Trajectory forecasting

Architecture schematic; no invented future trajectories are shown as learned output. GenTac is a recent preprint example. Distinguish forecasting and causal intervention.

## 61. Validating tracking models

Schematic split only, not measured performance. Event detection needs timing tolerances; probability models need calibration; tactical labels need a clear taxonomy.
