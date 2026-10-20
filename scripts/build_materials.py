"""Author notebook, slide content and resources from one workshop outline."""
from pathlib import Path
import json, textwrap
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]
for d in ['notebooks','slides','resources','assets','outputs','.build']:(ROOT/d).mkdir(exist_ok=True)

SOURCES={
'skillcorner':('SkillCorner open data and schema','https://github.com/SkillCorner/opendata'),
'kloppy':('kloppy SkillCorner loader','https://kloppy.pysport.org/reference/providers/skillcorner/'),
'physical':('SkillCorner physical thresholds and time-to metrics','https://skillcorner.com/us/articles/scouted-brazilian-centre-backs'),
'peak':('SkillCorner PSV-99 and Peak Velocity','https://skillcorner.com/articles/skillcorner-releases-new-peak-velocity-metric'),
'distance':('DataBallPy covered distance','https://databallpy.readthedocs.io/en/main/features/covered_distance_page.html'),
'preprocess':('DataBallPy preprocessing','https://databallpy.readthedocs.io/en/main/getting_started/preprocessing_options.html'),
'space':('DataBallPy space occupation','https://databallpy.readthedocs.io/en/main/features/space_occupation.html'),
'pressure':('DataBallPy pressure','https://databallpy.readthedocs.io/en/main/features/pressure_page.html'),
'das':('DataBallPy DAS and expected completion','https://databallpy.readthedocs.io/en/main/features/dangerous_accessible_space.html'),
'accessible':('Dangerous Accessible Space: paper and implementation','https://github.com/jonas-bischofberger/accessible-space'),
'gaussian':('Wide Open Spaces, Fernández & Bornn (2018)','https://static.capabiliaserver.com/frontend/clients/barca/wp_prod/wp-content/uploads/2018/05/Wide-Open-Spaces.pdf'),
'movement':('Space and Control in Soccer (2021)','https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2021.676179/full'),
'spearman':('Beyond Expected Goals, Spearman (2018)','https://static.hudl.com/craft/downloads/SSAC2018_Beyond_Expected_Goals.pdf?mtime=20180327111214'),
'epv':('Fine-grained expected possession value (2021)','https://pmc.ncbi.nlm.nih.gov/articles/PMC8570314/'),
'soccermap':('SoccerMap (2020)','https://arxiv.org/abs/2010.10202'),
'xg':('StatsBomb: Upgrading Expected Goals','https://blogarchive.statsbomb.com/articles/soccer/upgrading-expected-goals/'),
'runs':('SkillCorner: Expected Threat for off-ball runs','https://www.linkedin.com/posts/skillcorner_game-intelligence-expected-threat-activity-7057009275247689728-NVPh'),
'formation':('Shaw & Glickman: Dynamic Analysis of Team Strategy','https://static.capabiliaserver.com/frontend/clients/barca/wp_prod/wp-content/uploads/2020/01/83c87dfe-barca_poster_shaw.pdf'),
'pathcrf':('PathCRF: player trajectories to events (2026)','https://github.com/hyunsungkim-ds/pathcrf'),
'phases':('Augmented possession and phases framework (2025)','https://doi.org/10.1177/22150218241290988'),
'defcon':('DEFCON: GNN-based defensive EPV (2026)','https://github.com/hyunsungkim-ds/defcon'),
'ussf':('U.S. Soccer: counterattack GNNs with SkillCorner (2023)','https://github.com/USSoccerFederation/ussf_ssac_23_soccer_gnn'),
'tacticai':('TacticAI (2024)','https://www.nature.com/articles/s41467-024-45965-x'),
'gat':('Graph attention for defensive influence','https://github.com/Sentient-Sports/EvaluatingDefensiveInfluenceUsingGATs'),
'gentac':('GenTac: trajectory forecasting (2026 preprint)','https://arxiv.org/abs/2604.11786'),
'fot':('Friends of Tracking: pitch control and EPV tutorials','https://github.com/Friends-of-Tracking-Data-FoTD/LaurieOnTracking')}
from expanded_content import EXTRA_SOURCES, make_slides, extend_notebook
SOURCES.update(EXTRA_SOURCES)
(ROOT/'resources/sources.json').write_text(json.dumps(SOURCES,indent=2),encoding='utf-8')

slides=make_slides()
(ROOT/'slides/content.json').write_text(json.dumps(slides,indent=2),encoding='utf-8')

cells=[]
def md(s):cells.append(nbf.v4.new_markdown_cell(textwrap.dedent(s).strip()))
def code(s):cells.append(nbf.v4.new_code_cell(textwrap.dedent(s).strip()))
md('''# Tracking Data Applied
Soccer analytics with **SkillCorner**

Use the saved outputs for presenting, then run cells to explore. **Real data:** Brisbane Roar vs Perth Glory, 21 December 2024, match 1925299. Only the first 9000 source records are cached. This is not a full-match physical report.

Explore each method through code, visual output, assumptions and interpretation.

Sources and definitions: [reading list](../resources/READING_LIST.md) · [methodology](../resources/METHODOLOGY.md). Credit SkillCorner and PySport for the open-data initiative.''')
md('''## Setup
From the repository root: `python -m pip install -r requirements.txt`, then `python scripts/download_data.py` and `jupyter lab`.
The downloader caches actual public data in an ignored folder. It fails visibly if unavailable; no synthetic fallback is substituted. Restart and Run All after installing dependencies.''')
code('''from pathlib import Path
import sys, json
ROOT = Path.cwd() if (Path.cwd() / 'workshop.py').exists() else Path.cwd().parent
sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, HTML
import ipywidgets as widgets
from workshop import *
plt.rcParams.update({'figure.dpi':100, 'axes.spines.top':False, 'axes.spines.right':False})
assert DATA.exists(), 'Run python scripts/download_data.py from the repository root.'
''')
md('''## A. Load SkillCorner with kloppy
`load_data()` calls `skillcorner.load(meta_data=..., raw_data=..., coordinates="skillcorner")` on cached files. For a full remote match kloppy also offers `skillcorner.load_open_data(match_id="1925299")`.

We preserve native metres and frame IDs so dynamic events/phases can be joined using frame intervals. Loading is separate from model computation.''')
code('''dataset, wide, long, meta, events, phases, raw = load_data()
print(meta['home_team']['name'], 'vs', meta['away_team']['name'])
print(dataset.metadata.pitch_dimensions)
display(wide[['frame_id','period_id','timestamp','ball_x','ball_y','ball_owning_team_id']].head())
print('Rows:', len(wide), '| player coordinate coverage:', long.x.notna().mean())
print('Raw frame keys:', list(raw[0]))
print('One raw player record:', raw[0].get('player_data', [])[:1])
display(events.event_type.value_counts().to_frame('supplied events'))
''')
md('''### Derive motion without bridging gaps
Smooth coordinates within valid contiguous segments, then differentiate using timestamps. Exclude filter boundaries. The helper retains missing values and reports valid coverage. This is a teaching preprocessing pipeline, not SkillCorner's proprietary production processing.

See `workshop.movement` for the implementation and DataBallPy's [preprocessing documentation](https://databallpy.readthedocs.io/en/main/getting_started/preprocessing_options.html).''')
code('''motion = movement(long)
frames = choose_sequence(motion, wide)
frame = int(frames[len(frames)//2])
print('Selected contiguous clip:', int(frames[0]), 'to', int(frames[-1]))
print('Tracking time:', wide.loc[wide.frame_id.eq(frame),'timestamp'].iloc[0])
frame_plot(motion, wide, frame)
plt.show()
''')
md('''### Animate the same sequence
The embedded HTML animation works without ffmpeg. Colors identify teams, not possession. Native coordinates retain stadium orientation; check attacking direction before any goal-value calculation.''')
code('''from matplotlib.animation import FuncAnimation
fig, ax = plt.subplots(figsize=(9,6))
def draw(i):
    ax.clear()
    frame_plot(motion, wide, int(frames[i]), ax)
anim = FuncAnimation(fig, draw, frames=len(frames), interval=100)
html_animation = anim.to_jshtml()
plt.close(fig)
display(HTML(html_animation))
''')
md('''## B. Physical metrics: SkillCorner definitions, transparent estimates
In the documented men's context, HSR is 20–25 km/h and sprinting is above 25 km/h. Our code assigns [20,25) to HSR and [25,∞) to sprint to avoid double counting. This exact boundary convention is a teaching choice.

Distance ≈ Σ speed(m/s) × Δt. Missing data are excluded, never interpreted as zero exertion. Results describe the sample, not a match. Do not compare these estimates directly with official player-season aggregates.

**Effort rule here:** at least 1 s continuously above threshold; no gap merging. SkillCorner's exact production effort/filter rules are not reproduced. PSV-99 is defined over physical activities above 15 km/h; a 99th percentile over all tracking rows is not a faithful reproduction. Peak Velocity is a separate metric.''')
code('''summary = physical_summary(motion)
display(summary.head(10).round(2))
player_id = summary.iloc[0].player_id
g = motion[motion.player_id.eq(player_id)].sort_values('frame_id')
fig,ax=plt.subplots(figsize=(11,3.5))
ax.plot(g.seconds,g.raw_speed_kmh,alpha=.3,label='raw derivative')
ax.plot(g.seconds,g.speed_kmh,label='smoothed estimate')
for v,label in [(20,'HSR'),(25,'Sprint')]: ax.axhline(v,ls='--',label=label)
ax.set(xlabel='Tracking time (s)',ylabel='Speed (km/h)',title=g.name.iloc[0])
ax.legend(ncol=4); plt.show()
display(efforts(g))
''')
md('''### Interactive effort threshold
Change the duration or threshold to see why run counts depend on definitions. Time-to-HSR/sprint also needs a qualified starting state, start-time rule, and minimum data coverage; we explain those metrics in slides without claiming to reconstruct the official output.''')
code('''@widgets.interact(threshold=(18.,30.,1.), min_duration=(.5,3.,.5))
def inspect_efforts(threshold=25.,min_duration=1.):
    display(efforts(g,threshold,min_duration))
''')
md('''## C. Pitch-control notions: compare assumptions
**Voronoi:** nearest player owns each grid location. Fast, interpretable, but ignores velocity and ball travel.

**Gaussian influence:** aggregate smooth directional influence. Our covariance is illustrative, inspired by the family of methods, and does not reproduce Fernández/Bornn's exact parameterization. Team influence is converted to a bounded score; it is not a calibrated probability.

**Arrival-time baseline:** reaction delay + distance from a projected position / assumed speed. No ball-flight or interception integration; this is not a full Spearman pitch-control implementation.

Review the helper `surfaces` to inspect all assumptions.''')
code('''fig,axs=plt.subplots(1,3,figsize=(17,5))
for ax,model in zip(axs,['Voronoi','Gaussian influence','Arrival-time baseline']):
    control_plot(motion,wide,frame,model,ax)
plt.tight_layout();plt.show()
''')
code('''@widgets.interact(i=(0,len(frames)-1,1),model=['Voronoi','Gaussian influence','Arrival-time baseline'])
def inspect_control(i=len(frames)//2,model='Gaussian influence'):
    control_plot(motion,wide,int(frames[i]),model)
    plt.show()
''')
md('''## Graphs: build the representation before discussing the network
Nodes are players; directed edges connect players within 15 m. Node features include position, velocity and team. Edge features include distance, relative position and team relationship. Changing the radius changes the graph; fully connected alternatives can model distant relationships.

A GNN learns shared message/update functions and task-specific readouts. This cell constructs inputs only: it does not train a GNN or claim EPV predictions. Reordering nodes should not change graph-level predictions when the architecture is designed appropriately.''')
code('''nodes=motion[motion.frame_id.eq(frame)].dropna(subset=['x','y','vx','vy']).reset_index(drop=True)
edges=graph_edges(nodes)
display(nodes[['player_id','team_id','x','y','vx','vy']].head())
display(edges.head())
ax=frame_plot(motion,wide,frame)
for e in edges.itertuples():
    if e.source > e.target: continue
    a=nodes[nodes.player_id.eq(e.source)].iloc[0]; b=nodes[nodes.player_id.eq(e.target)].iloc[0]
    ax.plot([a.x,b.x],[a.y,b.y],color='gray',alpha=.35,lw=1)
ax.set_title('Example radius graph: 15 m');plt.show()
''')
md('''## D. Accessible space, dangerous space and passing options
We now use the **actual public `accessible-space` implementation**, referenced by DataBallPy. It simulates passes across angles and speeds with potential receivers/interceptors. This differs from comparing Gaussian influence at the destination.

Explicitly inspect the first-half attacking direction, ball location, possession team, and velocity units. A goalkeeper-location heuristic supplies direction below; confirm it visually. The model's DAS is danger-weighted area, not EPV or calibrated goal probability. We use a modest grid for workshop speed.

The package respects offside by default. Its constraints, default parameters and treatment of simultaneous team access should be read alongside the [documentation](https://github.com/jonas-bischofberger/accessible-space).''')
code('''import accessible_space
import inspect
print('Implementation:', inspect.signature(accessible_space.get_dangerous_accessible_space))
selected_frames = [int(frames[20]),int(frames[50]),int(frames[80])]
tracking_for_das = das_input(motion,wide,selected_frames)
display(tracking_for_das[['frame_id','player_id','team_id','team_in_possession','attacking_direction']].head())
print('Check goalkeeper positions against the plot:')
display(motion[motion.frame_id.eq(frame)].groupby('team_id').x.agg(['min','max','median']))
das_result = accessible_space.get_dangerous_accessible_space(
    tracking_for_das,period_col='period_id',attacking_direction_col='attacking_direction',
    infer_attacking_direction=False,player_in_possession_col='player_in_possession',n_angles=30,n_v0=8,radial_gridsize=3,
    use_progress_bar=False,additional_fields_to_return=['attack_poss_density'])
metrics=tracking_for_das[['frame_id']].copy()
metrics['AS_m2']=das_result.acc_space
metrics['DAS_weighted_m2']=das_result.das
display(metrics.drop_duplicates().round(2))
''')
md('''### Compare simulated passing surfaces
The surface shows modeled attacking accessibility. This surface is not an observed-pass outcome. Explain why risk, danger and actual decision selection are different targets.''')
code('''fig,axs=plt.subplots(1,3,figsize=(17,5))
for ax,k in zip(axs,range(3)):
    frame_plot(motion,wide,selected_frames[k],ax)
    plt.sca(ax)
    accessible_space.plot_expected_completion_surface(das_result.simulation_result,frame_index=k)
    ax.set_title(f'Accessible passing surface | frame {selected_frames[k]}')
plt.tight_layout();plt.show()
''')
md('''### Completion estimates for specified options
Take three teammate locations as hypothetical pass targets in one frame. These are **candidate options, not observed attempts or evidence of intent**. The model marginalizes over its ball-speed assumptions; calibration must be evaluated on labeled passes before interpreting values as reliable probabilities.''')
code('''print(inspect.signature(accessible_space.get_expected_pass_completion))
poss_team = int(wide.loc[wide.frame_id.eq(selected_frames[1]),'ball_owning_team_id'].iloc[0])
ball_row = wide[wide.frame_id.eq(selected_frames[1])].iloc[0]
receivers = motion[motion.frame_id.eq(selected_frames[1]) & motion.team_id.eq(poss_team)].dropna(subset=['x','y','vx','vy']).copy()
receivers['distance_to_ball']=np.hypot(receivers.x-ball_row.ball_x,receivers.y-ball_row.ball_y)
passer=receivers.player_in_possession.iloc[0]
assert passer in set(receivers.player_id), 'Supplied ball carrier is not in the eligible player set.'
targets=receivers[receivers.player_id.ne(passer)].sort_values('distance_to_ball').iloc[[0,2,4]]
options=pd.DataFrame({'frame_id':selected_frames[1],'player_id':passer,'team_id':poss_team,
    'x':ball_row.ball_x,'y':ball_row.ball_y,'x_target':targets.x.to_numpy(),'y_target':targets.y.to_numpy()})
xc=accessible_space.get_expected_pass_completion(options,tracking_for_das,
    event_frame_col='frame_id',event_player_col='player_id',event_team_col='team_id',
    event_start_x_col='x',event_start_y_col='y',event_end_x_col='x_target',event_end_y_col='y_target',
    tracking_period_col='period_id',use_progress_bar=False)
options['xC_model']=xc.xc
display(options.round(3))
ax=frame_plot(motion,wide,selected_frames[1])
for r in options.itertuples():
    ax.annotate('',xy=(r.x_target,r.y_target),xytext=(r.x,r.y),arrowprops={'arrowstyle':'->','color':'black'})
    ax.text(r.x_target,r.y_target+2,f'{r.xC_model:.2f}',fontsize=10)
ax.set_title('Hypothetical passing options | model completion estimates');plt.show()
''')
md('''## Supplied events and phase context
The following optional cells demonstrate supplied-label inspection, interval joins and shape summaries. They do not train an event detector, formation model, phase classifier, xG model or EPV model.''')
code('''# Interval join within a period. Inspect phase taxonomy before interpreting summaries.
phase_rows=[]
for p in phases.itertuples():
    s=motion[(motion.period_id.eq(p.period)) & motion.frame_id.between(p.frame_start,p.frame_end)]
    if s.empty: continue
    shape=s.groupby(['frame_id','team_id']).agg(width=('y',lambda x:x.max()-x.min()),length=('x',lambda x:x.max()-x.min())).reset_index()
    shape['phase']=p.team_in_possession_phase_type
    shape['in_possession']=shape.team_id.eq(p.team_in_possession_id)
    phase_rows.append(shape)
phase_shapes=pd.concat(phase_rows,ignore_index=True)
display(phase_shapes.groupby(['phase','in_possession'])[['width','length']].median().round(1))
print('Shape includes goalkeepers; filter them before interpreting outfield compactness.')
display(events.loc[events.frame_start.between(wide.frame_id.min(),wide.frame_id.max()), ['event_type','event_subtype','player_name','frame_start']].head(15))
''')
md('''## Discussion and extensions
- What changes if the same player is moving in the opposite direction?
- Does a larger area imply a more dangerous attack?
- How would you validate completion estimates, phase labels or event detection?
- What data would you need to distinguish run quality from teammate support?

**Further projects:** [DEFCON](https://github.com/hyunsungkim-ds/defcon), [U.S. Soccer counterattack GNN](https://github.com/USSoccerFederation/ussf_ssac_23_soccer_gnn), [TacticAI](https://www.nature.com/articles/s41467-024-45965-x), [SoccerMap](https://arxiv.org/abs/2010.10202).

Avoid random frame-level train/test splits: adjacent frames leak near-identical situations. Split by match/sequence, evaluate calibration and test coverage sensitivity. No trained EPV, xG or GNN artifact is included in this introductory workshop.''')
cells=extend_notebook(cells)
nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.13'}})
nbf.write(nb,ROOT/'notebooks/tracking_data_applied.ipynb')

reading=['# Reading list and project choices','\nReferences checked during workshop preparation, 19 October 2026. Foundational methods remain useful alongside recent work.\n']
for key,(title,url) in SOURCES.items():reading.append(f'- **{key}** — [{title}]({url})')
reading += ['\n## Which projects to walk through?',
'| Project | What to show | Advantage | Limitation |',
'|---|---|---|---|',
'| DataBallPy physical metrics | Speed and distance calculation | Readable pandas foundation | Must handle gaps and define thresholds |',
'| Gaussian space influence | One player and team surfaces | Visual link from velocity to space | Influence is not calibrated completion |',
'| Accessible Space / DAS | Actual package inference and three options | Connects risk and danger without training | Physical assumptions and calibration matter |',
'| Fernández EPV / SoccerMap | Component diagram and research figures | Explains full decision value | Large training pipeline; no pretrained artifact supplied here |',
'| DEFCON | GNN components and opponent EPV | Direct defensive value connection | Research model and attribution assumptions |',
'| U.S. Soccer GNN | Tracking graph and counterattack target | Uses SkillCorner data | Training task differs from general EPV |',
'| TacticAI | Published graph diagram and corner use case | Intuitive prediction and intervention example | Task-specific code/data not public; corners only |',
'| SkillCorner run threat | Definition and supplied event fields | Values unserved movement | Provider model is not reproduced |',
'\nDataBallPy is a methodological reference; the live DAS cells call `accessible-space` directly. GNN examples are references, not trained workshop models. Read source licenses before reusing project code.']
(ROOT/'resources/READING_LIST.md').write_text('\n'.join(reading),encoding='utf-8')
guide=['# Presenter guide','\nEach method has a dedicated slide and a reproducible visual. Figures derived from model architecture are labeled as schematics rather than learned predictions.\n']
for i,s in enumerate(slides,1):guide.append(f"## {i}. {s['title']}\n{s['notes']}\n\n{s['cue']}\n")
(ROOT/'resources/PRESENTER_GUIDE.md').write_text('\n'.join(guide),encoding='utf-8')
print('Created',len(slides),'slides of content and',len(cells),'notebook cells')
