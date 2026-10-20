# Roles, formations and GraphEPV

## Primary sources

- [Devin Pleuler, Fixed to Fluid: Frame-by-Frame Role Classification (June 2024)](https://github.com/devinpleuler/research/blob/master/frame-by-frame-position.md): geometric teammate counts around a rotating viewpoint, with XGBoost role classification. Formation-change detection is proposed but untested in that article.
- [Joris Bekkers, EFPI (2025)](https://arxiv.org/abs/2506.23843) and [package tutorial](https://unravelsports.readthedocs.io/en/latest/tutorials/formation_detection.html): elastic formation templates and linear assignment.
- [Joris Bekkers, GraphEPV, PyData London (7 June 2025)](https://rawcdn.githack.com/UnravelSports/keynotes/main/html/20250607-PyData-London.html): frame graphs trained with a possession-team goal-within-ten-seconds label, using PFF World Cup 2022 data. This target differs from full action-decomposed EPV.
- [Current UnravelSports GNN tutorial](https://unravelsports.readthedocs.io/en/latest/tutorials/soccer_gnn.html): conversion, labeling, grouped splits and training. Current recommendation is PyTorch Geometric; the historical talk uses Keras/Spektral.

## What the workshop implements

Figures independently calculated from SkillCorner tracking recreate the requested *types* of visualization rather than reuse the supplied screenshots. Raw and team-centered distributions use the same sample. Ellipses have axes of two standard deviations; they describe covariance, not Gaussian probability coverage or confidence intervals. Role labels on those figures are assigned metadata roles.

The viewpoint example uses 24 headings with overlapping 90-degree sectors, no range cutoff and no occlusion. This is geometric context rather than measured vision. Opponent counts extend the original teammate-count idea. Attack-left normalization rotates both axes, retaining left/right distinctions. The notebook manufactures features without claiming a trained classifier or out-of-sample performance. Training needs many labeled matches, reviewed frame roles and held-out players/matches.

Formation prediction uses four fixed outfield templates and minimum squared-distance Hungarian assignment. This does not reproduce EFPI's elastic optimization. RMS costs and runner-up margins are not probabilities. Candidate timelines use defensive-context, non-overlapping 30-second windows with at least 50 qualifying frames and ten player medians. These are frame-index windows in a ten-Hz sample; production work should use elapsed time and period keys. Three consecutive populated bins confirm a candidate, missing bins reset candidate evidence, and the last confirmed state is retained. This persistence rule is our teaching choice, not EFPI logic. No tactical changes are asserted as ground truth. Phase shifts, set pieces, rotations, coverage and template choice can change the inferred label.

The graph topology illustration independently builds team subgraphs linked through the ball, one documented UnravelSports option. The GraphEPV diagram explains its target and general workflow without claiming trained inference or an exact layer-by-layer implementation. Temporal features, identity edges, recurrent models, convolutions and attention are additional architecture choices. They are not attributed as tested additions in the 2025 frame-model talk.

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
