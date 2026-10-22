# Roles, formations and GraphEPV

## Primary sources

- [Devin Pleuler, Fixed to Fluid: Frame-by-Frame Role Classification (June 2024)](https://github.com/devinpleuler/research/blob/master/frame-by-frame-position.md): geometric teammate counts around a rotating viewpoint, with XGBoost role classification. Formation-change detection is proposed but untested in that article.
- [Joris Bekkers, EFPI (2025)](https://arxiv.org/abs/2506.23843) and [package tutorial](https://unravelsports.readthedocs.io/en/latest/tutorials/formation_detection.html): elastic formation templates and linear assignment.
- [Joris Bekkers, GraphEPV, PyData London (7 June 2025)](https://rawcdn.githack.com/UnravelSports/keynotes/main/html/20250607-PyData-London.html): frame graphs trained with a possession-team goal-within-ten-seconds label, using PFF World Cup 2022 data. This target differs from full action-decomposed EPV.
- [Current UnravelSports GNN tutorial](https://unravelsports.readthedocs.io/en/latest/tutorials/soccer_gnn.html): conversion, labeling, grouped splits and training. Current recommendation is PyTorch Geometric; the historical talk uses Keras/Spektral.

## What the workshop implements

Figures calculated from SkillCorner tracking show player distributions and role features. Raw and team-centered distributions use the same sample. Ellipses have axes of two standard deviations; they describe covariance, not Gaussian probability coverage or confidence intervals. Role labels on those figures are assigned metadata roles.

The viewpoint example uses 24 headings with overlapping 90-degree sectors, no range cutoff and no occlusion. This is geometric context rather than measured vision. Opponent counts extend the original teammate-count idea. Attack-left normalization rotates both axes, retaining left/right distinctions. The notebook manufactures features without claiming a trained classifier or out-of-sample performance. Training needs many labeled matches, reviewed frame roles and held-out players/matches.

Formation prediction uses four fixed outfield templates and minimum squared-distance Hungarian assignment. This does not reproduce EFPI's elastic optimization. RMS costs and runner-up margins are not probabilities. Candidate timelines use defensive-context, non-overlapping 30-second windows with at least 50 qualifying frames and ten player medians. These are frame-index windows in a ten-Hz sample; production work should use elapsed time and period keys. Three consecutive populated bins confirm a candidate, missing bins reset candidate evidence, and the last confirmed state is retained. This persistence rule is specific to the workshop baseline. No tactical changes are asserted as ground truth. Phase shifts, set pieces, rotations, coverage and template choice can change the inferred label.

The graph topology illustration independently builds team subgraphs linked through the ball, one documented UnravelSports option. The GraphEPV diagram explains its target and general workflow without claiming trained inference or an exact layer-by-layer implementation. Temporal features, identity edges, recurrent models, convolutions and attention are additional architecture choices. They are not attributed as tested additions in the 2025 frame-model talk.

The standalone graph notebook now extends that explanation with an independent real-trained GNN: normalized 20 m edges plus ball links, self-feature and neighborhood transforms, and separate attacking/defending/ball readouts. It trains on ten SkillCorner matches, uses three validation matches for checkpoint selection/calibration, and reserves three test matches including the animated example. The input is current geometry, not future outcomes or supplied provider EPV. Its target is a same-team goal-shot event in the next ten seconds, reconstructed by aligning goal markers to nearby shots and reconciling final scores. Four of twenty source matches fail that audit and are excluded. Timing is not video-verified.

Final notebook curves and animation are actual predictions from this teaching model, with missing possession/coverage left as gaps. The saved checkpoint is for quick playback; `RETRAIN=True` executes the included real-data training loop. The held-out set has only sixteen positive sampled states, so it does not demonstrate production reliability or an advantage over a strong location baseline. It is not the provider's thirty-second EPV model or Bekkers' CrystalGraph implementation. See `outputs/methods/graph_epv_real_results.json` and `resources/models/graph_epv_model_card.json`.

## Walkthrough tradeoffs

| Walkthrough | Benefit | Limitation |
|---|---|---|
| Raw versus centered distributions | Makes team translation and dispersion visible | Averages can conceal role rotations and mixed phases |
| Angular counts | Transparent relational features without a neural network | Depends on orientation, sector width and complete player coverage |
| Supervised role classifier | Flexible role probabilities and embeddings | Requires credible frame labels; metadata roles are weak labels |
| Fixed-template assignment | Easy to inspect player-slot matches and candidate costs | Restricted templates and hand-set scale; not elastic EFPI |
| Formation-change timeline | Explains persistence and phase-conditioned comparison | Needs video-reviewed changes and uncertainty thresholds |
| GraphEPV | Relates off-ball interactions to a clear scoring target | Rare correlated goals, calibration, domain shift and training volume |
| Temporal graph extension | Captures runs and changing pressure | Extra computation, history alignment and leakage risks |
