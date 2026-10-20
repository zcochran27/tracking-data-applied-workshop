# Reading list and project choices

The standalone xG comparison uses [StatsBomb Open Data](https://github.com/hudl/open-data), with [official event specifications](https://github.com/hudl/open-data/tree/master/doc) and [StatsBomb's discussion of goalkeeper/defender context](https://statsbomb.com/articles/soccer/upgrading-expected-goals/). It fits two transparent workshop models rather than reproducing the provider's production xG model. The data source and logo are credited in the notebook and ROC export.

References checked during workshop preparation, 19 October 2026. Foundational methods remain useful alongside recent work.

- **skillcorner** — [SkillCorner open data and schema](https://github.com/SkillCorner/opendata)
- **kloppy** — [kloppy SkillCorner loader](https://kloppy.pysport.org/reference/providers/skillcorner/)
- **physical** — [SkillCorner physical thresholds and time-to metrics](https://skillcorner.com/us/articles/scouted-brazilian-centre-backs)
- **peak** — [SkillCorner PSV-99 and Peak Velocity](https://skillcorner.com/articles/skillcorner-releases-new-peak-velocity-metric)
- **distance** — [DataBallPy covered distance](https://databallpy.readthedocs.io/en/main/features/covered_distance_page.html)
- **preprocess** — [DataBallPy preprocessing](https://databallpy.readthedocs.io/en/main/getting_started/preprocessing_options.html)
- **space** — [DataBallPy space occupation](https://databallpy.readthedocs.io/en/main/features/space_occupation.html)
- **pressure** — [DataBallPy pressure](https://databallpy.readthedocs.io/en/main/features/pressure_page.html)
- **das** — [DataBallPy DAS and expected completion](https://databallpy.readthedocs.io/en/main/features/dangerous_accessible_space.html)
- **accessible** — [Dangerous Accessible Space: paper and implementation](https://github.com/jonas-bischofberger/accessible-space)
- **gaussian** — [Wide Open Spaces, Fernández & Bornn (2018)](https://static.capabiliaserver.com/frontend/clients/barca/wp_prod/wp-content/uploads/2018/05/Wide-Open-Spaces.pdf)
- **movement** — [Space and Control in Soccer (2021)](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2021.676179/full)
- **spearman** — [Beyond Expected Goals, Spearman (2018)](https://static.hudl.com/craft/downloads/SSAC2018_Beyond_Expected_Goals.pdf?mtime=20180327111214)
- **epv** — [Fine-grained expected possession value (2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8570314/)
- **soccermap** — [SoccerMap (2020)](https://arxiv.org/abs/2010.10202)
- **xg** — [StatsBomb: Upgrading Expected Goals](https://blogarchive.statsbomb.com/articles/soccer/upgrading-expected-goals/)
- **runs** — [SkillCorner: Expected Threat for off-ball runs](https://www.linkedin.com/posts/skillcorner_game-intelligence-expected-threat-activity-7057009275247689728-NVPh)
- **formation** — [Shaw & Glickman: Dynamic Analysis of Team Strategy](https://static.capabiliaserver.com/frontend/clients/barca/wp_prod/wp-content/uploads/2020/01/83c87dfe-barca_poster_shaw.pdf)
- **pathcrf** — [PathCRF: player trajectories to events (2026)](https://github.com/hyunsungkim-ds/pathcrf)
- **phases** — [Augmented possession and phases framework (2025)](https://doi.org/10.1177/22150218241290988)
- **defcon** — [DEFCON: GNN-based defensive EPV (2026)](https://github.com/hyunsungkim-ds/defcon)
- **ussf** — [U.S. Soccer: counterattack GNNs with SkillCorner (2023)](https://github.com/USSoccerFederation/ussf_ssac_23_soccer_gnn)
- **tacticai** — [TacticAI (2024)](https://www.nature.com/articles/s41467-024-45965-x)
- **gat** — [Graph attention for defensive influence](https://github.com/Sentient-Sports/EvaluatingDefensiveInfluenceUsingGATs)
- **gentac** — [GenTac: trajectory forecasting (2026 preprint)](https://arxiv.org/abs/2604.11786)
- **fot** — [Friends of Tracking: pitch control and EPV tutorials](https://github.com/Friends-of-Tracking-Data-FoTD/LaurieOnTracking)
- **xt** — [Karun Singh: Expected Threat](https://karun.in/blog/expected-threat.html)
- **dbxt** — [DataBallPy fitted xT methodology](https://databallpy.readthedocs.io/en/main/features/xt_models.html)
- **explosive** — [SkillCorner explosive accelerations](https://skillcorner.com/articles/new-feature-explosive-accelerations)
- **dbmodel** — [DataBallPy source and fitted model](https://github.com/Alek050/databallpy)

## Which projects to walk through?
| Project | What to show | Advantage | Limitation |
|---|---|---|---|
| DataBallPy physical metrics | Speed and distance calculation | Readable pandas foundation | Must handle gaps and define thresholds |
| Gaussian space influence | One player and team surfaces | Visual link from velocity to space | Influence is not calibrated completion |
| Accessible Space / DAS | Actual package inference and three options | Connects risk and danger without training | Physical assumptions and calibration matter |
| Fernández EPV / SoccerMap | Component diagram and supplied value examples | Explains full decision value | Large training pipeline; no pretrained artifact supplied here |
| DEFCON | GNN components and opponent EPV | Direct defensive value connection | Research model and attribution assumptions |
| U.S. Soccer GNN | Tracking graph and counterattack target | Uses SkillCorner data | Training task differs from general EPV |
| TacticAI | Corner tracking context and architecture schematic | Intuitive prediction and intervention example | Task-specific code/data not public; corners only |
| SkillCorner run threat | Definition and supplied event fields | Values unserved movement | Provider model is not reproduced |

DataBallPy is a methodological reference; the live DAS cells call `accessible-space` directly. The slides' cited GNN systems remain research references. The standalone graph-EPV notebook additionally trains its own small real-data GNN, with held-out possession predictions and an animation; it is not a reproduction of those published systems. Read source licenses before reusing project code.
- **temporal** — [PyTorch Geometric Temporal architectures](https://pytorch-geometric-temporal.readthedocs.io/en/latest/modules/root.html)

- **tcn** — [Temporal convolution for sequence modeling](https://arxiv.org/abs/1803.01271)

- **attention** — [Attention Is All You Need](https://arxiv.org/abs/1706.03762)

- **pleuler** — [Devin Pleuler: Fixed to Fluid (2024)](https://github.com/devinpleuler/research/blob/master/frame-by-frame-position.md)

- **efpi** — [Joris Bekkers: Elastic Formation and Position Identification](https://arxiv.org/abs/2506.23843)

- **efpidocs** — [UnravelSports EFPI tutorial](https://unravelsports.readthedocs.io/en/latest/tutorials/formation_detection.html)

- **graphepv** — [Joris Bekkers: GraphEPV, PyData London 2025](https://rawcdn.githack.com/UnravelSports/keynotes/main/html/20250607-PyData-London.html)

- **unravel** — [UnravelSports soccer GNN tutorial](https://unravelsports.readthedocs.io/en/latest/tutorials/soccer_gnn.html)
