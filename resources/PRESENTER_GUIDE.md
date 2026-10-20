# Presenter guide

Total: 60 minutes. Notebook outputs are saved; practice switching before presenting.

## 1. Tracking Data Applied (1 min slides)
Open with the football problem: who has a useful passing option, and what created it? Ask students to watch the same sequence before looking at model outputs.



## 2. Data and documentation (2 min slides)
Open the links in resources/READING_LIST.md. Tracking and derived labels are different products. The sample is Brisbane vs Perth, match 1925299; do not imply all files in the current manifest are downloaded.



## 3. The hour (1 min slides)
Timing includes notebook visits: A=7, B=4, C=5, graph=1, D=7 minutes. Slides total 31 minutes; questions 5 minutes. Avoid running full-match simulations live.



## 4. Coordinates are measurements (2 min slides)
Native sample is 10 Hz. Inspect raw is_detected fields where present. Keep contiguous segments; never differentiate across a half or a gap. Dynamic-event coordinates may use different orientation from tracking.

NOTEBOOK A · load → inspect → animate · 7 min

## 5. Six avenues for tracking analysis (1 min slides)
Defense/off-ball movement are cross-cutting applications. Keep the core taxonomy of five avenues while making those questions visible.



## 6. Event detection (2 min slides)
Simple proximity is a candidate detector, not ground truth. Loose balls, aerial passes and duels create ambiguity. PathCRF (2026) models dynamic graphs and possession-path inference. Validate event precision/recall with timing tolerances and hand-reviewed clips.



## 7. Formation, roles and phases (3 min slides)
Shaw & Glickman show dynamic formations by game state. Mean positions alone hide role switches and transition periods. Phase definitions depend on the taxonomy. Notebook appendix demonstrates interval joins and shape summaries, not a trained formation classifier.



## 8. SkillCorner physical metrics (2 min slides)
Thresholds here refer to the documented men’s context. Use half-open bins [20,25) and [25,∞) in our teaching code to avoid overlap; this boundary convention is ours. SkillCorner describes PSV-99 over physical activities above 15 km/h; do not replace it with a percentile of all frames. Exact production smoothing and effort rules are not fully reproduced.



## 9. From positions to physical output (1 min slides)
Distance estimate = sum(speed in m/s × dt). Our effort rule uses >=1 second and no merging. It is an educational approximation, not an exact SkillCorner count. Do not extrapolate the 15-minute sample into a full-match total or compare it directly with player-season aggregates.

NOTEBOOK B · speed → efforts → distance · 4 min

## 10. Pitch control: three assumptions (2 min slides)
Ask which model notices a player running away from the ball. Gaussian does not automatically mean calibrated probability. Our arrival-time baseline is not Spearman’s ball-aware control model.



## 11. Choosing a control model (1 min slides)
Use the same frame across panels. Our Gaussian uses a transparent illustrative covariance rather than exactly reproducing Fernández/Bornn. Control is not value: safe space behind your goal need not be valuable. Transition to pass simulation later.

NOTEBOOK C · compare surfaces · 5 min

## 12. Tracking as a graph (1 min slides)
Distinguish a frame-level interaction graph from an aggregate passing network. The radius graph is an example, not a claim that only nearby players interact. Fully connected graphs can capture distant tactical relationships.



## 13. What a graph neural network learns (2 min slides)
Explain message passing verbally: the receiver representation changes when a defender closes the lane. Permutation-aware architectures avoid arbitrary player ordering. Temporal context needs a recurrent, temporal-attention or spatiotemporal design. Graph construction, data quality and calibration still matter.

NOTEBOOK · inspect node and edge features · 1 min

## 14. Graph models in soccer (2 min slides)
Open the project comparison in resources/READING_LIST.md. TacticAI is a set-piece study, not a general open-play EPV model. Its task-specific code and licensed tracking data were not released. Do not interpret attention weights as causal defensive credit.



## 15. EPV: value the situation (2 min slides)
A schematic decomposition is sum over actions P(action|state) × E(value after action|state,action). Include failure/turnover branches. EPV definitions vary: expected net next-goal outcome, possession scoring probability, or fixed-horizon scoring are not interchangeable. GNNs can estimate components; EPV does not require GNNs. Fernández et al use convolutional pass surfaces.



## 16. Passing risk and dangerous space (1 min slides)
DAS uses physical pass simulation. The notebook calls the public accessible-space implementation and plots its actual output; it does not relabel a Gaussian map as pass completion. Ball speed assumptions, direction and offside treatment affect results. DAS is danger-weighted area, not calibrated goal probability.

NOTEBOOK D · options → AS/DAS · 7 min

## 17. xG and off-ball scoring opportunities (1 min slides)
Use StatsBomb’s xG discussion for features and Spearman for OBSO. Never train an xG model on a handful of shots from this sample. A location-danger heuristic is not a fitted xG model.



## 18. Value runs that never receive the ball (1 min slides)
SkillCorner describes run xT as the chance of a goal within 10 seconds if the run is served. Distinguish this counterfactual target from location-based event xT and observed EPV change. Supplied provider values may be explored without claiming to reproduce the model.



## 19. Where research goes next (1 min slides)
DEFCON is a direct defense/EPV example. GenTac is recent preprint research: present it as emerging work, not settled operational evidence. More realistic simulated outcomes still require out-of-sample validation.



## 20. Validate the football answer (1 min slides)
Close on the same sequence. Ask: which option became available, which player helped create it, and what would you need to establish that contribution reliably? Save 5 minutes for questions.



## 21. Questions and next steps (5 min slides)
Questions: 5 minutes. Optional appendix code is for after the workshop. All research references are in slide notes and resources/READING_LIST.md.



## Timing guardrails
Notebook A 7 min, B 4 min, C 5 min, graph 1 min, D 7 min. Optional phase cells are homework. If behind, shorten graph project examples and show saved DAS outputs; keep the final five minutes for questions.