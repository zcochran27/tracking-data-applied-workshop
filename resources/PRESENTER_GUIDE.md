# Presenter guide
Each method has a dedicated slide and a reproducible visual. Research architectures are labeled as schematics rather than learned outputs.
## 1. Tracking Data Applied
Introduce the match and the distinction between observed tracking, extrapolated tracking and derived labels.



## 2. Data and documentation
The opening entries are linked. Full sources are in the reading list. Real sample: Brisbane vs Perth, 21 December 2024, match 1925299.



## 3. Loading tracking data
The figure contains actual dataframe values; velocity columns are derived after loading.

NOTEBOOK · load and inspect

## 4. Tracking quality and visibility
Red rings mark extrapolated players according to raw is_detected. Coordinates can exist without a direct camera observation. All subsequent models inherit this uncertainty.



## 5. Plotting a tracking frame
Use actual pitch dimensions. A visually plausible frame is a useful first check, but does not prove identity or position accuracy.



## 6. Animating a sequence
Three snapshots are from the real selected clip. The notebook contains a full embedded animation.

NOTEBOOK · play the sequence

## 7. Possession detection
Figure is an actual 2 m proximity heuristic, not the full Vidal-Codina or PathCRF method. Pros: transparent and quick. Cons: aerial balls, duels and tracking uncertainty. Compare with supplied possession labels; evaluate timing-aware accuracy.

NOTEBOOK · inspect the candidate detector

## 8. Pass-event detection
The real ball path is annotated at supplied possession endpoints. This is an explanatory candidate sequence, not a validated recovered pass. Pros: converts continuous signals to actionable events. Cons: missing ball data and multi-touch ambiguity.



## 9. Formation detection
Real median outfield positions are shown separately by possession. Pros: summarizes organization beyond a team sheet. Cons: averaging mixes roles and game states; these are not asserted formation labels.



## 10. Player-role and line detection
Ward clustering of real centered x positions into three groups is a teaching baseline. It is not a validated named-formation classifier. Pros: interpretable. Cons: fixed line counts, overlaps and rotations.



## 11. Phase-of-play segmentation
The plot shows supplied SkillCorner labels, not predictions from a classifier trained here. Pros: makes context explicit. Cons: taxonomy-dependent and sensitive to boundary definitions.

NOTEBOOK · join phase intervals

## 12. Estimating player speed
Actual speed curves are shown. Pros: foundation for physical and tactical features. Cons: derivatives amplify noise; smoothing removes some short peaks.



## 13. Distance covered
The real sample’s cumulative distance excludes missing derivatives. No full-match extrapolation. Pros: simple workload volume measure. Cons: incomplete and extrapolated tracking affect accuracy.



## 14. High-speed and sprint distance
Our code uses [20,25) and [25,infinity) to avoid overlap; exact equality handling is a teaching convention. Pros: distinguishes intensity from volume. Cons: thresholds and exposure affect comparisons.



## 15. Sprint-effort counts
Shaded segments are our >=1 s, no-merging teaching rule. They are not exact SkillCorner production sprint counts. Pros: repeated-effort view. Cons: sensitive to thresholds, smoothing and merging rules.



## 16. Acceleration and deceleration
The plot uses real signed speed derivatives. A direction change can produce acceleration-vector magnitude without increasing scalar speed. Pros: captures bursts and braking. Cons: highly noise-sensitive; threshold crossing alone does not qualify a production explosive effort.



## 17. Time to high-speed running
The real crossing is illustrative, not production-qualified. The published metric is the minimum interval within qualifying explosive accelerations. Start detection, >0.7 s high-acceleration qualification and filtering matter.



## 18. Time to sprint
Real observed crossing shown. No official Time to Sprint or Top 3 value is reconstructed. Pros: explosiveness/capacity. Cons: limited opportunities, sample size and qualification rules.



## 19. PSV-99: activity-based speed capacity
The real frame-speed distribution illustrates why populations matter. SkillCorner describes PSV-99 over physical activities above 15 km/h. This histogram is not the official PSV-99 calculation.



## 20. Peak Velocity: absolute top speed
The figure uses our smoothed sample-speed estimates. It does not reproduce SkillCorner’s validated production Peak Velocity. Pros: interpretable capacity measure. Cons: noisy spikes, short exposure and preprocessing dependence.



## 21. Expected goals: shot quality
Hypothetical shot rays at a real ball location; no xG prediction is invented. Pros: familiar target and interpretable features. Cons: sparse shots, outcome imbalance and contextual bias.



## 22. Expected Threat: location value
Actual fitted DataBallPy open-play grid, not trained on this small sample. V(s)=P(shot|s)P(goal|shot,s)+sum P(successful move to s'|s)V(s'). Classic location xT does not use defender positions. State the model target and training domain.



## 23. Expected Threat gained
The arrow is real ball displacement in the selected clip, not an assertion of a single completed pass. Attack direction is normalized and 105 m scaled to the model’s 106 m convention. Pros: simple action valuation. Cons: path-independent, no defender context or causal attribution.

NOTEBOOK · xT lookup and endpoint difference

## 24. Voronoi space control
Actual frame, grid approximation to a Voronoi partition. Pros: quick and interpretable. Cons: hard boundaries and no movement, ball-flight or uncertainty.



## 25. Gaussian player influence
Real player velocity with an illustrative ellipse. The covariance is not the exact Fernández/Bornn parameterization. Pros: smooth and motion-aware. Cons: hand-set influence scale and simplified movement ability.



## 26. Gaussian team control
Our logistic transformation bounds the team difference; it is not a calibrated possession probability. Pros: contested-space view. Cons: aggregation and covariance assumptions affect the surface.



## 27. Arrival-time control
Actual frame with a simple 0.7 s projection and 5 m/s travel speed baseline. Pros: interpretable timing. Cons: no ball flight, acceleration optimization or interception-rate integration; not Spearman’s full model.



## 28. Ball-aware pitch control
Architecture schematic on actual tracking context, not a computed Spearman surface. Pros: physical link to passing. Cons: uncertain reactions, speed and ball parameters. Separate from the arrival-time teaching baseline.



## 29. Expected pass completion
Actual accessible-space xC inference on hypothetical endpoints at real teammate positions. Pros: interpretable risk. Cons: model calibration, ball speed and offside conventions; candidates are not observed choices.

NOTEBOOK · candidate-pass risk

## 30. Accessible space
Actual public-model output. Pros: incorporates ball and player movement. Cons: simulation assumptions and resolution; individual access can overlap.



## 31. Dangerous accessible space
Actual public-model dangerous surface. Pros: links access and useful territory. Cons: danger definition and physical assumptions; DAS units are danger-weighted square metres.



## 32. Changes in dangerous space
Actual model values on three frames. Pros: connects movement to changing opportunity. Cons: different team possession states and model noise must be checked; before/after changes alone are not causal credit.



## 33. Off-ball run threat
Actual supplied xthreat values for off-ball runs. The provider model is not reconstructed. Pros: visible unserved contributions. Cons: counterfactual assumptions, context and selection bias.



## 34. Tracking as a spatial graph
Real radius graph. Pros: models relationships directly. Cons: radius edges miss distant tactical relationships; fully connected and learned connectivity are alternatives.



## 35. Node and edge features
Actual edge-feature rows. Edge direction controls the sign of relative position. Team IDs should be encoded meaningfully rather than treated as numeric magnitudes.



## 36. Graph neural message passing
Architecture schematic, not a trained result. Pros: relational inductive bias and shared updates. Cons: oversmoothing, connectivity choices and training requirements. Attention alone is not causal importance.



## 37. Temporal node features
Actual one-second lag and speed change on a real player. Explicit lag frame checks prevent bridging gaps. Instantaneous velocity adds motion information but is not a substitute for full history.

NOTEBOOK · lagged features and masks

## 38. Dynamic graphs over time
Actual snapshots and a player trail. A sequence of spatial graphs retains team interactions that change with time; a static aggregate passing network does not.



## 39. Temporal edges between snapshots
Schematic topology with real player IDs. The notebook creates actual spatial and temporal edge records. Do not connect across substitutions or tracking gaps without an explicit rule; labels cannot leak future frames.



## 40. Recurrent temporal graph models
Architecture schematic rather than a claim about a specific cited model’s GRU implementation. Pros: sequential processing with a compact state. Cons: long-history retention and sequence alignment. No trained inference is shown.



## 41. Temporal convolution on graph history
Architecture schematic. Pros: parallel computation and explicit receptive field. Cons: window length, dilation and sampling-rate choices. Filters must not access future frames at prediction time.



## 42. Causal temporal attention
Architecture schematic. Pros: flexible history selection and long-range dependencies. Cons: data/computation requirements, masking and leakage; attention weights do not establish causal importance.



## 43. Spatiotemporal message passing
General architecture schematic, not a reproduction of PathCRF. Pros: joint relational/time structure. Cons: graph size, identity errors and edge construction choices.



## 44. SoccerMap: spatial neural prediction
Architecture schematic. SoccerMap is a convolutional approach, not a GNN. Pros: field-wide outputs. Cons: rasterization and training data requirements; no pretrained inference is claimed.



## 45. Expected possession value
Conceptual decomposition: sum over actions P(action|state) times outcome-conditional value, including failure. EPV is a framework/target, not a synonym for GNN. Different EPV definitions must not be mixed.



## 46. Observed passes and supplied EPV
Actual pass_epv_delta_for fields in SkillCorner dynamic events. This is the provider’s model output; not a reconstructed Fernández or DEFCON prediction. The field name is shown rather than assuming undocumented equivalence.

NOTEBOOK · supplied event-value fields

## 47. DEFCON: defensive contribution
Architecture schematic only. Explain attribution assumptions before interpreting defensive credits. Actual frame is context, not DEFCON inference.



## 48. U.S. Soccer: counterattack graphs
Architecture schematic. The published balanced event-frame study uses reaching the penalty area as success; the repository’s additional all-frame dataset has different goal labels. Do not mix those datasets or quote them as equivalent.



## 49. TacticAI: corner-kick modeling
Architecture schematic. The input illustration uses real tracking near a supplied corner-reception event; it is not the original TacticAI input or trained inference. Complete task-specific code/weights and licensed data are not released. Model-generated suggestions are not guarantees.



## 50. Trajectory forecasting
Architecture schematic; no invented future trajectories are shown as learned output. GenTac is a recent preprint example. Distinguish forecasting and causal intervention.



## 51. Validating tracking models
Schematic split only, not measured performance. Event detection needs timing tolerances; probability models need calibration; tactical labels need a clear taxonomy.
