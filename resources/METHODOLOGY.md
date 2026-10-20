# Methodology and reproduction boundaries

## Data
SkillCorner match 1925299: Brisbane Roar FC vs Perth Glory, 21 December 2024. Tracking is broadcast-derived and includes extrapolated positions. The downloader caches the first 9000 JSONL records plus full metadata, dynamic events and phases. A bounded sample is not a complete match. Source data remain outside Git; rerun the downloader for execution. Credit SkillCorner and PySport. See the upstream repository's MIT license and documentation.

Use the original frame IDs and period IDs. Tracking uses native metric coordinates; dynamic event coordinates may be attack-normalized. Do not draw event coordinates on tracking without checking direction and dimensions. Phase joins use frame intervals within period and avoid the coordinate issue.

## Physical metrics
Compute derivatives separately within contiguous valid player/period segments. Smooth positions with a Gaussian kernel (sigma 1.5 frames); exclude three-sigma boundary support before estimating speed. These are explicit teaching choices, not SkillCorner's production filters. Derive speed in m/s then multiply by 3.6. Distance integrates speed over native 0.1-second intervals. Report valid seconds and sample coverage. Extrapolated coordinates can remain in these estimates; coordinate coverage is not camera-observed coverage.

The documented men's bands are HSR 20–25 km/h and sprint above 25 km/h. Our half-open code uses [20,25), [25,infinity) to avoid boundary double counting. Effort examples require 1 continuous second and do not merge gaps. Exact production effort rules are not asserted. Threshold sensitivity is interactive. No PSV-99 reconstruction is claimed: SkillCorner defines its activity population above 15 km/h, which differs from all raw frame speeds. Peak Velocity is distinct. Time-to-HSR/sprint requires a qualified start rule and is discussed rather than reconstructed. Acceleration vector magnitude and the signed derivative of scalar speed answer different questions.

## Pitch control
Voronoi assigns each grid point to its nearest player. Gaussian influence uses projected means, directional covariance and a logistic transformation of team influence differences. It illustrates the method family, not the exact Wide Open Spaces parameterization. The score is not a calibrated probability. The arrival-time baseline uses a 0.7-second reaction/projected-position assumption and 5 m/s travel speed; it does not integrate ball trajectories or reproduce Spearman. Source helpers expose all parameters.

## Accessible space and completion
Actual `accessible-space` package inference is used. Explicit first-half direction is inferred from persistent extreme player positions and must be checked against goalkeeper locations before changing matches. AS and DAS are computed on three selected frames. The coarse angular/ball-speed sampling supports workshop latency, not maximum-resolution analysis. A ball row with zero current velocity marks the launch position; the simulator supplies hypothetical pass velocities. Synthetic candidate pass endpoints are real teammate locations, not observed decisions. The supplied player-possession label determines the hypothetical passer; its correctness should still be checked against the clip. DAS is danger-weighted area, not a goal probability. AS/DAS and xC use different task defaults in the package; inspect parameter signatures rather than equating them.

## Graphs and value models
The radius graph is directed, with distance, dx/dy and same-team features. No GNN is trained. Graph construction is not evidence of learned tactical relationships. Full EPV, xG, run-threat and counterfactual models are explained using cited research. A model's prediction target, horizon, calibration and failure/turnover branches must be stated. Attention weights and before/after value differences are not causal attribution by themselves.

## Evaluation
Use held-out matches or sequences, not random neighboring frames. Validate preprocessing with clips; evaluate event detection with timing tolerances, probabilities with calibration/proper scores, and tactical labels with explicit taxonomies. Test sensitivity to missing/extrapolated positions, smoothing, thresholds, directions and physical parameters. The notebook is an educational analysis, not a production scouting or medical/load-monitoring system.
