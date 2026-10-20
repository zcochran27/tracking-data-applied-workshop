"""Author self-contained method notebooks; only ingestion/pitch drawing are shared.

Run from the repository root. Scientific calculations appear inside each notebook.
"""
from pathlib import Path
import textwrap
import nbformat as nb

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'notebooks/avenues';OUT.mkdir(exist_ok=True)
BOOKS={}
COMMON='''
from pathlib import Path
import sys
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'workshop.py').exists())
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
from workshop import load_data, pitch  # ingestion and drawing only; methods below are explicit
dataset, wide, tracking, metadata, events, phases, raw = load_data()
tracking = tracking.sort_values(['player_id','period_id','frame_id']).copy()
assert not tracking.duplicated(['period_id','frame_id','player_id']).any()
observed = tracking.dropna(subset=['x','y'])
frame_id = int(observed.groupby(['period_id','frame_id']).size().loc[lambda s:s.eq(22)].index[20][1])
snapshot = observed[observed.frame_id.eq(frame_id)].copy()
keepers = {str(p['id']) for p in metadata['players'] if 'goalkeeper' in p['player_role']['name'].lower()}
role_labels = {str(p['id']):p['player_role']['acronym'] for p in metadata['players']}
print('Real match 1925299; loaded frames:', wide.shape[0], '| illustrative frame:', frame_id)
'''
def book(name,title,description,sections):
    cells=[nb.v4.new_markdown_cell('# '+title+'\n\n'+description+'''

Download the bounded real sample first with `python scripts/download_data.py` from the repository root. Run cells in order. Each notebook can start a fresh kernel. Only data ingestion and pitch drawing use shared helpers; calculations below use NumPy/pandas/SciPy directly. Raw files remain excluded from Git. The sample contains one partial first half, so supervised-model training requires additional labeled matches for meaningful evaluation.
'''),nb.v4.new_code_cell(textwrap.dedent(COMMON).strip())]
    for kind,source in sections:
        cells.append((nb.v4.new_code_cell if kind=='code' else nb.v4.new_markdown_cell)(textwrap.dedent(source).strip()))
    n=nb.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}})
    nb.write(n,OUT/(name+'.ipynb'));BOOKS[name]=title
def md(s):return ('markdown',s)
def code(s):return ('code',s)

book('00_data_foundations','Data foundations: loading, quality and animation','Inspect SkillCorner data and build the representations used in every avenue.',[
md('''## Load with kloppy and inspect the schema
`load_data` wraps `kloppy.skillcorner.load` and reshapes its dataframe. Here is the direct loading operation; no model is involved. Keep native metres, period keys and observed/extrapolated flags. [SkillCorner open data](https://github.com/SkillCorner/opendata), [kloppy](https://kloppy.pysport.org/).'''),
code('''from kloppy import skillcorner
direct=skillcorner.load(meta_data=ROOT/'data/1925299/1925299_match.json',raw_data=ROOT/'data/1925299/1925299_tracking_extrapolated.jsonl',coordinates='skillcorner')
display(direct.to_df().iloc[:5,:8])
display(tracking.groupby('team_id').agg(rows=('player_id','size'),detected_fraction=('is_detected','mean')))
fig,ax=plt.subplots(figsize=(10,6));pitch(ax)
for team,g in snapshot.groupby('team_id'):
    ax.scatter(g.x,g.y,label=str(team))
ax.legend();ax.set_title('Real player coordinates');plt.show()
'''),
md('''## Animate coordinates directly
Use a short sequence with complete player coverage and consecutive frames. The output is embedded HTML; a moving point does not establish that every coordinate was directly observed by the camera.'''),
code('''from matplotlib.animation import FuncAnimation
from IPython.display import HTML
coverage=observed.groupby('frame_id').size()
available=coverage[coverage.eq(22)].index.to_numpy()
start=next(int(f) for f in available if all(f+j in available for j in range(30)))
clip=observed[observed.frame_id.between(start,start+29)]
fig,ax=plt.subplots(figsize=(8,5));pitch(ax)
scat=ax.scatter([],[],s=60)
def update(i):
    g=clip[clip.frame_id.eq(start+i)]
    scat.set_offsets(g[['x','y']].to_numpy())
    scat.set_color(np.where(g.team_id.eq(1802),'#e87524','#7761be'))
    ax.set_title(f'Frame {start+i}');return (scat,)
animation=FuncAnimation(fig,update,frames=30,interval=100,blit=False)
plt.close(fig);display(HTML(animation.to_jshtml()))
'''),
md('''## Checks and interpretation
Inspect missing coordinates, identity continuity, timestamps and visibility before modeling. Retain extrapolated positions as an explicit quality feature rather than silently treating them as measured observations. All following notebooks use a bounded sample, never a full-match workload estimate.''')])

book('01_event_detection','Event detection from continuous tracking','Build possession and pass candidates from player–ball proximity, temporal stability and ball movement.',[
md('''## Nearest-player possession candidates
Compute Euclidean player–ball distance for each frame. A two-metre radius is a chosen teaching threshold. Ball height filters flyovers, but duels and missing observations still require uncertainty. Supplied possession is useful for comparison, not a model input here.'''),
code('''joined=observed.merge(wide[['period_id','frame_id','ball_x','ball_y','ball_z']],on=['period_id','frame_id'],validate='many_to_one')
joined['distance']=np.hypot(joined.x-joined.ball_x,joined.y-joined.ball_y)
valid=joined.dropna(subset=['distance'])
nearest=valid.loc[valid.groupby(['period_id','frame_id']).distance.idxmin()].sort_values(['period_id','frame_id']).copy()
nearest['candidate']=nearest.player_id.where(nearest.distance.le(2)&nearest.ball_z.fillna(0).le(2))
nearest['break']=nearest.period_id.ne(nearest.period_id.shift())|nearest.frame_id.diff().ne(1)|nearest.candidate.ne(nearest.candidate.shift())
nearest['segment']=nearest['break'].cumsum()
segments=nearest.groupby('segment').agg(period=('period_id','first'),start=('frame_id','min'),end=('frame_id','max'),player=('candidate','first'),team=('team_id','first'),frames=('frame_id','size'))
segments['duration_s']=segments.frames/10
stable=segments[segments.player.notna()&segments.duration_s.ge(.3)].copy()
display(stable.head(12))
nearest.head(250).plot(x='seconds',y='distance',title='Nearest player–ball distance');plt.axhline(2,color='orange',ls='--');plt.show()
'''),
md('''## Release, transit and reception
Pair successive stable possession segments. A same-team identity change with finite ball displacement is a pass candidate. Limit the gap and reject missing ball trajectories. Interceptions, dribbles near teammates, deflections and aerial passes can still fool this baseline. Never equate these rows with verified pass events.'''),
code('''candidates=[]
for a,b in zip(stable.itertuples(),list(stable.itertuples())[1:]):
    if a.period!=b.period or a.player==b.player or a.team!=b.team:continue
    gap=b.start-a.end
    path=wide[wide.period_id.eq(a.period)&wide.frame_id.between(a.end,b.start)].sort_values('frame_id')
    if not 1<=gap<=40 or len(path)!=gap+1 or path[['ball_x','ball_y']].isna().any().any():continue
    displacement=np.linalg.norm(path[['ball_x','ball_y']].iloc[-1]-path[['ball_x','ball_y']].iloc[0])
    if displacement<3:continue
    candidates.append(dict(period=a.period,release=a.end,reception=b.start,passer=a.player,receiver=b.player,travel_s=gap/10,displacement_m=displacement))
passes=pd.DataFrame(candidates,columns=['period','release','reception','passer','receiver','travel_s','displacement_m'])
display(passes.head(10))
fig,ax=plt.subplots(figsize=(10,6));pitch(ax)
if len(passes):
    p=passes.iloc[0];path=wide[wide.period_id.eq(p.period)&wide.frame_id.between(p.release,p.reception)]
    ax.plot(path.ball_x,path.ball_y,'o-',label='Candidate ball path');ax.legend()
ax.set_title('Pass candidate, not a validated detected event');plt.show()
'''),
md('''## Timing-aware evaluation
For labeled events, a correct type and passer/receiver should also match within an explicit timing tolerance. Use one-to-one matching so multiple candidates cannot all claim the same true event. Tune thresholds only on training/validation matches. The function below measures timing matches, and can be applied within each event type and player pairing.'''),
code('''from scipy.optimize import linear_sum_assignment
def timing_scores(predicted,truth,tolerance_s=.5):
    predicted=np.asarray(predicted);truth=np.asarray(truth)
    if not len(predicted) or not len(truth):return {'tp':0,'fp':len(predicted),'fn':len(truth)}
    delta=np.abs(predicted[:,None]-truth[None,:])
    # A large penalty first maximizes the count of eligible one-to-one matches.
    cost=np.where(delta<=tolerance_s,delta,1e6)
    rows,cols=linear_sum_assignment(cost);tp=int((delta[rows,cols]<=tolerance_s).sum())
    return {'tp':tp,'fp':len(predicted)-tp,'fn':len(truth)-tp}
assert timing_scores([1,1.1],[1],.2)=={'tp':1,'fp':1,'fn':0}
print('Synthetic unit check only:',timing_scores([1,3],[1.1,5],.2))
'''),md('''**Tradeoff:** interpretable and inexpensive, but robust event recovery needs ball dynamics, aerial handling and video-reviewed labels. See [PathCRF](https://github.com/hyunsungkim-ds/pathcrf) for a richer research direction; this notebook does not reproduce it.''')])

book('02_formations_and_roles','Formations, angular role features and change detection','Implement the requested distribution plots, Pleuler-inspired viewpoint counts and fixed-template prediction.',[
md('''## Raw and centroid-normalized distributions
Subtract the outfield team centroid at each frame. Plot means and covariance ellipses using identical samples. Two-standard-deviation axes describe dispersion, not a confidence interval. Metadata role names are assigned positions, not verified frame-level roles. [Pleuler: Fixed to Fluid](https://github.com/devinpleuler/research/blob/master/frame-by-frame-position.md).'''),
code('''from matplotlib.patches import Ellipse
team=observed[observed.team_id.eq(1802)&~observed.player_id.isin(keepers)].copy()
team[['cx','cy']]=team[['x','y']].to_numpy()-team.groupby(['period_id','frame_id'])[['x','y']].transform('mean').to_numpy()
fig,axs=plt.subplots(1,2,figsize=(13,5))
for ax,cols,title in zip(axs,[['x','y'],['cx','cy']],['Raw positions','Centered positions']):
    pitch(ax);ax.set_title(title)
    for i,(pid,g) in enumerate(team.groupby('player_id')):
        points=g[cols].to_numpy();mean=points.mean(axis=0)
        vals,vecs=np.linalg.eigh(np.cov(points.T));v=vecs[:,-1]
        ax.add_patch(Ellipse(mean,4*np.sqrt(vals[-1]),4*np.sqrt(vals[0]),angle=np.degrees(np.arctan2(v[1],v[0])),fill=False,color=plt.cm.tab10(i%10)))
        ax.text(*mean,role_labels[pid],fontsize=9)
plt.show()
'''),
md('''## Manufacture angular count features
For a given player, compute relative angles to every other player. Sweep 24 headings and count objects inside a 90° sector. Rotate both axes for attack-left teams. Pleuler's original method counts teammates; the opponent channel is our extension. This models relative geometry, not gaze or occluded vision.'''),
code('''def angular_counts(nodes,pid,attack_sign=1,bins=24,fov=90):
    p=nodes[nodes.player_id.eq(pid)].iloc[0]
    others=nodes[~nodes.player_id.eq(pid)]
    delta=attack_sign*(others[['x','y']].to_numpy()-p[['x','y']].to_numpy(dtype=float))
    angles=np.arctan2(delta[:,1],delta[:,0]);headings=np.linspace(-np.pi,np.pi,bins,endpoint=False)
    difference=np.angle(np.exp(1j*(angles[:,None]-headings)))
    inside=np.abs(difference)<=np.deg2rad(fov/2)+1e-12
    same=others.team_id.eq(p.team_id).to_numpy()
    return headings,inside[same].sum(axis=0),inside[~same].sum(axis=0)
rows=[]
for _,p in snapshot.iterrows():
    angles,mates,opponents=angular_counts(snapshot,p.player_id,attack_sign=-1 if p.team_id==1802 else 1)
    rows.append(dict(player_id=p.player_id,metadata_role=role_labels[p.player_id],**{f'mate_{i}':v for i,v in enumerate(mates)},**{f'opp_{i}':v for i,v in enumerate(opponents)}))
features=pd.DataFrame(rows);display(features.iloc[:5,:10])
plt.plot(np.degrees(angles),features.filter(like='mate_').iloc[0].to_numpy());plt.xlabel('Heading (degrees)');plt.ylabel('Teammate count');plt.show()
'''),
md('''## Supervised role classification from scratch
Pleuler used XGBoost. To expose the training calculation without adding an ML framework, this cell defines a multinomial linear classifier with softmax and gradient descent. A linear model is less flexible than XGBoost. Train it on **many reviewed matches**, splitting by match/player. We test its numerical mechanics on a labeled synthetic example only. No accuracy against noisy single-match metadata is presented as tactical-role performance.'''),
code('''def softmax(z):
    z=z-z.max(axis=1,keepdims=True);p=np.exp(z);return p/p.sum(axis=1,keepdims=True)
def train_roles(X,y,n_classes,steps=600,lr=.1):
    X=np.c_[np.ones(len(X)),np.asarray(X,float)];W=np.zeros((X.shape[1],n_classes))
    target=np.eye(n_classes)[np.asarray(y,int)]
    for _ in range(steps):W-=lr*X.T@(softmax(X@W)-target)/len(X)
    return W
rng=np.random.default_rng(7);toy_X=np.r_[rng.normal(-2,.3,(20,2)),rng.normal(2,.3,(20,2))];toy_y=np.repeat([0,1],20)
W=train_roles(toy_X,toy_y,2)
assert (softmax(np.c_[np.ones(40),toy_X]@W).argmax(axis=1)==toy_y).all()
print('Synthetic optimizer check passed; real role-model training needs reviewed labels.')
'''),
md('''## Formation prediction with one-to-one assignment
Center ten outfield positions, construct candidate templates and minimize player-to-slot squared distance with the Hungarian algorithm. This uses SciPy's assignment optimizer, with all features and objective shown explicitly. It is a **fixed-template baseline**, not the elastic fitting in [Bekkers' EFPI](https://arxiv.org/abs/2506.23843). Costs and margins are not probabilities.'''),
code('''from scipy.optimize import linear_sum_assignment
templates={}
for name,lines in {'4-4-2':[4,4,2],'4-3-3':[4,3,3],'4-2-3-1':[4,2,3,1],'3-5-2':[3,5,2]}.items():
    t=np.array([(x,y) for x,n in zip(np.linspace(-18,18,len(lines)),lines) for y in (np.linspace(-23,23,n) if n>1 else [0])]);templates[name]=t-t.mean(axis=0)
def score_templates(points):
    points=np.asarray(points,float)
    if points.shape!=(10,2):raise ValueError('Ten outfield players required')
    points=points-points.mean(axis=0);results=[]
    for name,t in templates.items():
        distance2=((points[:,None]-t[None])**2).sum(axis=2)
        r,c=linear_sum_assignment(distance2)
        results.append((name,np.sqrt(distance2[r,c].mean()),c))
    return sorted(results,key=lambda z:z[1])
points=-snapshot[snapshot.team_id.eq(1802)&~snapshot.player_id.isin(keepers)][['x','y']].to_numpy()
scores=score_templates(points);display(pd.DataFrame([(n,c) for n,c,_ in scores],columns=['candidate','RMS metres']))
assert score_templates(templates['4-3-3'][::-1]+20)[0][1]<1e-10
'''),
md('''## Detect persistent change candidates
Use comparable defensive phases, elapsed-time bins and period keys. Require ten players with adequate coverage. Missing bins reset evidence. A three-window confirmation is our illustrative rule, not EFPI's algorithm. Pleuler proposes change detection without testing it in his article. Video review must distinguish tactical changes, phase changes and temporary role swaps.'''),
code('''team['window']=(team.seconds//30).astype(int)
records=[]
for (period,window),g in team[team.team_in_possession.eq(871)].groupby(['period_id','window']):
    per_player=g.groupby('player_id').agg(cx=('cx','median'),cy=('cy','median'),n=('frame_id','size'))
    if len(per_player)!=10 or per_player.n.min()<50:continue
    fits=score_templates(-per_player[['cx','cy']].to_numpy())
    records.append(dict(period=period,window=window,label=fits[0][0],cost=fits[0][1],margin=fits[1][1]-fits[0][1]))
timeline=pd.DataFrame(records)
def confirm(sequence,n=3):
    current=None;candidate=None;count=0;result=[]
    for label in sequence:
        if not isinstance(label,str):candidate=None;count=0
        else:
            count=count+1 if label==candidate else 1;candidate=label
            if count>=n:current=candidate
        result.append(current)
    return result
for period,g in timeline.groupby('period'):
    g=g.set_index('window')
    g=g.reindex(range(int(g.index.min()),int(g.index.max())+1));g['confirmed']=confirm(g.label)
    display(g.head(12))
    labels=list(templates);mapping={v:i for i,v in enumerate(labels)}
    plt.scatter(g.index*30,g.label.map(mapping),label='Candidate');plt.plot(g.index*30,g.confirmed.map(mapping),label='Confirmed')
    plt.yticks(range(4),labels);plt.xlabel('Elapsed period time (s)');plt.title(f'Period {period}: candidates, not tactical ground truth');plt.legend();plt.show()
''')])

book('03_match_segmentation','Match segmentation and phases of play','Build frame features and an explicit tactical-state baseline, then compare with supplied interval labels.',[
md('''## Build interpretable frame-level features
Use team centroids, width, length, possession and a rolling trend in ball progress. Brisbane attacks left in this first-half sample; rotate both axes for its attack-right progress. In a full match derive orientation per period/team from metadata. These features support segmentation but do not uniquely define tactical phases.'''),
code('''shape=observed.groupby(['period_id','frame_id','team_id']).agg(cx=('x','mean'),cy=('y','mean'),xmin=('x','min'),xmax=('x','max'),ymin=('y','min'),ymax=('y','max'))
shape['width']=shape.ymax-shape.ymin;shape['length']=shape.xmax-shape.xmin
frame=wide[['period_id','frame_id','timestamp','ball_x','ball_y','ball_owning_team_id']].copy()
frame['seconds']=frame.timestamp.dt.total_seconds();frame=frame.sort_values(['period_id','frame_id'])
frame['sign']=np.where(frame.ball_owning_team_id.eq(1802),-1,1)
frame['attack_x']=frame.ball_x*frame.sign
new=(frame.period_id.ne(frame.period_id.shift())|frame.frame_id.diff().ne(1)|frame.ball_owning_team_id.ne(frame.ball_owning_team_id.shift()))
frame['possession_segment']=new.cumsum()
frame['possession_age']=frame.seconds-frame.groupby('possession_segment').seconds.transform('first')
frame['progress_speed']=frame.groupby('possession_segment').attack_x.diff()/frame.groupby('possession_segment').seconds.diff()
frame['progress_1s']=frame.groupby('possession_segment').progress_speed.transform(lambda s:s.rolling(10,min_periods=5).mean())
display(frame[['frame_id','attack_x','possession_age','progress_1s']].head(15))
'''),
md('''## A transparent rule-based state classifier
Rules below are deliberately simple: a fast early advance is a transition candidate; otherwise classify by field zone. Values are teaching choices, not SkillCorner's production definitions. Invalid ball position or unknown possession yields an unknown state.'''),
code('''def rule_phase(row):
    if pd.isna(row.attack_x) or row.ball_owning_team_id not in [1802,871]:return 'unknown'
    if row.possession_age<8 and row.progress_1s>3:return 'transition candidate'
    if row.attack_x<-17.5:return 'deep circulation'
    if row.attack_x<17.5:return 'middle progression'
    return 'advanced possession'
frame['raw_phase']=frame.apply(rule_phase,axis=1)
# Confirm three consecutive labels causally; restart when possession/coverage changes.
def smooth_states(g):
    current='unknown';pending=None;n=0;output=[]
    for label in g.raw_phase:
        n=n+1 if label==pending else 1;pending=label
        if n>=3:current=label
        output.append(current)
    return pd.Series(output,index=g.index)
frame['phase']=pd.concat([smooth_states(g) for _,g in frame.groupby('possession_segment')]).sort_index()
breaks=frame.phase.ne(frame.phase.shift())|new
intervals=frame.groupby(breaks.cumsum()).agg(period=('period_id','first'),start=('seconds','min'),end=('seconds','max'),phase=('phase','first'),n=('frame_id','size'))
intervals['duration_s']=intervals.end-intervals.start+.1
display(intervals.head(12))
'''),
md('''## Interval join to provider phases
Keep period and inclusive frame boundaries. Inspect overlaps rather than silently selecting one phase. Our rule taxonomy differs from the provider taxonomy, so a diagonal confusion-matrix interpretation would be misleading without a reviewed mapping.'''),
code('''frame['provider_phase']=None;frame['provider_matches']=0
for r in phases.itertuples():
    mask=frame.period_id.eq(r.period)&frame.frame_id.between(r.frame_start,r.frame_end)&frame.ball_owning_team_id.eq(r.team_in_possession_id)
    frame.loc[mask,'provider_matches']+=1
    frame.loc[mask,'provider_phase']=r.team_in_possession_phase_type
display(frame.provider_matches.value_counts().rename('frames'))
display(pd.crosstab(frame.phase,frame.provider_phase))
fig,ax=plt.subplots(figsize=(12,4))
labels=list(frame.phase.unique());mapping={v:i for i,v in enumerate(labels)}
ax.scatter(frame.seconds,frame.phase.map(mapping),s=2);ax.set(yticks=range(len(labels)),yticklabels=labels,xlabel='Time (s)',title='Rule-based state timeline');plt.show()
'''),md('''**Next step:** learn a classifier or a sequence model on reviewed phases, using match-level splits and boundary-tolerant evaluation. Hysteresis reduces flicker but introduces detection delay. Possession changes, dead-ball states and camera gaps need explicit treatment. [SkillCorner data and labels](https://github.com/SkillCorner/opendata).''')])

book('04_physical_metrics','Physical metrics from coordinates','Differentiate positions, accumulate workload and inspect acceleration efforts using explicit calculations.',[
md('''## Smooth and differentiate within continuous segments
Compute velocity from coordinate gradients and actual timestamps. Split at missing data, gaps and periods. Gaussian smoothing here is retrospective and symmetric: live prediction needs a causal alternative or latency allowance. Exclude filter boundaries. [DataBallPy](https://databallpy.readthedocs.io/en/main/), [SkillCorner acceleration definitions](https://skillcorner.com/articles/new-feature-explosive-accelerations) and [SkillCorner peak-speed definitions](https://skillcorner.com/articles/skillcorner-releases-new-peak-velocity-metric) provide the methodological context; our estimates do not recreate proprietary processing.'''),
code('''from scipy.ndimage import gaussian_filter1d
motion=tracking.copy();motion[['vx','vy','speed_kmh','accel']]=np.nan
for _,g in motion.groupby(['player_id','period_id']):
    valid=g[['x','y']].notna().all(axis=1)
    splits=(~valid|~valid.shift(fill_value=False)|g.frame_id.diff().ne(1)|g.seconds.diff().le(0)).cumsum()
    for _,s in g[valid].groupby(splits[valid]):
        if len(s)<20:continue
        xy=gaussian_filter1d(s[['x','y']].to_numpy(),sigma=1.5,axis=0,mode='nearest')
        v=np.gradient(xy,s.seconds.to_numpy(),axis=0);speed=np.linalg.norm(v,axis=1)
        acceleration=np.gradient(speed,s.seconds.to_numpy())
        v[:5]=np.nan;v[-5:]=np.nan;speed[:5]=np.nan;speed[-5:]=np.nan
        acceleration[:6]=np.nan;acceleration[-6:]=np.nan
        motion.loc[s.index,['vx','vy']]=v;motion.loc[s.index,'speed_kmh']=speed*3.6;motion.loc[s.index,'accel']=acceleration
display(motion[['player_id','frame_id','vx','vy','speed_kmh','accel']].dropna().head())
'''),
md('''## Distance, intensity bands and coverage
Integrate trapezoidally over valid neighboring speed estimates. Allocate intervals to intensity bands by mean interval speed. This differs slightly from frame-rectangle conventions; disclose the convention. The men's HSR and sprint thresholds here are 20 and 25 km/h. Report valid exposure and avoid scaling a partial sample into a full match.'''),
code('''summaries=[]
for pid,g in motion.groupby('player_id'):
    g=g.sort_values(['period_id','frame_id']);dt=g.seconds.diff()
    valid=g.period_id.eq(g.period_id.shift())&g.frame_id.diff().eq(1)&dt.gt(0)&g.speed_kmh.notna()&g.speed_kmh.shift().notna()
    interval_speed=(g.speed_kmh+g.speed_kmh.shift())/2
    distance=interval_speed/3.6*dt
    summaries.append(dict(player_id=pid,valid_s=dt.where(valid).sum(),distance_m=distance.where(valid).sum(),HSR_m=distance.where(valid&interval_speed.ge(20)&interval_speed.lt(25)).sum(),sprint_m=distance.where(valid&interval_speed.ge(25)).sum(),coverage=valid.mean(),sample_peak_kmh=g.speed_kmh.max()))
summary=pd.DataFrame(summaries);display(summary.sort_values('distance_m',ascending=False).head(10))
summary.set_index('player_id')[['HSR_m','sprint_m']].plot.bar(figsize=(12,4),title='Sample distances by intensity');plt.ylabel('Metres');plt.show()
'''),
md('''## Sprint efforts and signed acceleration
Consecutive speed at or above 25 km/h for at least one second defines an effort **in this notebook**. No short-gap merging. Signed scalar acceleration measures speeding up/braking, while vector acceleration also responds to direction changes.'''),
code('''effort_rows=[]
for pid,g in motion.groupby('player_id'):
    g=g.sort_values(['period_id','frame_id']);active=g.speed_kmh.ge(25)
    segment=(active.ne(active.shift(fill_value=False))|g.frame_id.diff().ne(1)|g.period_id.ne(g.period_id.shift())).cumsum()
    for _,s in g[active].groupby(segment[active]):
        duration=s.seconds.iloc[-1]-s.seconds.iloc[0]+.1
        if duration>=1:effort_rows.append(dict(player_id=pid,start_s=s.seconds.iloc[0],duration_s=duration,peak_kmh=s.speed_kmh.max()))
display(pd.DataFrame(effort_rows,columns=['player_id','start_s','duration_s','peak_kmh']).head())
pid=summary.sort_values('sample_peak_kmh',ascending=False).player_id.iloc[0];g=motion[motion.player_id.eq(pid)]
fig,axs=plt.subplots(2,1,figsize=(12,5),sharex=True);axs[0].plot(g.seconds,g.speed_kmh);axs[0].set_ylabel('km/h');axs[1].plot(g.seconds,g.accel);axs[1].set(xlabel='Time (s)',ylabel='Signed m/s²');plt.show()
'''),
md('''## Time from 9 to 20 / 25 km/h
Find consecutive rising-speed episodes, interpolate threshold crossings, and inspect durations. SkillCorner reports these metrics within **qualifying explosive accelerations** with additional production rules; the crossings below are not official Time to HSR / Time to Sprint. PSV-99 uses its specified activity population and cannot be replaced by an all-frame 99th percentile. Our sample peak is also distinct from validated production Peak Velocity.'''),
code('''def crossing_time(t,v,threshold):
    hits=np.flatnonzero((v[:-1]<threshold)&(v[1:]>=threshold))
    if not len(hits):return np.nan
    i=hits[0];return t[i]+(threshold-v[i])/(v[i+1]-v[i])*(t[i+1]-t[i])
crossings=[]
for pid,g in motion.groupby('player_id'):
    g=g.sort_values(['period_id','frame_id']);rising=g.accel.gt(0)&g.speed_kmh.notna()
    segment=(rising.ne(rising.shift(fill_value=False))|g.frame_id.diff().ne(1)|g.period_id.ne(g.period_id.shift())).cumsum()
    for _,s in g[rising].groupby(segment[rising]):
        if len(s)<3:continue
        t=s.seconds.to_numpy();v=s.speed_kmh.to_numpy();t9=crossing_time(t,v,9)
        for threshold in [20,25]:
            end=crossing_time(t,v,threshold)
            if np.isfinite(t9+end) and end>t9:crossings.append(dict(player_id=pid,target_kmh=threshold,seconds=end-t9))
display(pd.DataFrame(crossings,columns=['player_id','target_kmh','seconds']).head(12))
assert np.isclose(crossing_time(np.array([0,1]),np.array([0,20]),9),.45)
''')])

book('05_game_modeling','Game modeling: xG, xT, control, passing and possession value','Implement simple models directly, with explicit targets and boundaries between fitted data, physical assumptions and illustrative calculations.',[
md('''## xG features and a binary classifier
Distance and goal-opening angle are a starting feature set. Tracking adds goalkeeper location and defenders in the shooting corridor. Training needs real shot outcomes over many matches. We expose logistic loss and its gradient, using a synthetic optimizer check rather than inventing xG probabilities on this sample.'''),
code('''def shot_features(x,y):
    dx=52.5-np.asarray(x);y=np.asarray(y)
    distance=np.hypot(dx,y)
    a=np.arctan2(3.66-y,dx);b=np.arctan2(-3.66-y,dx)
    angle=np.abs(np.angle(np.exp(1j*(a-b))))
    return np.c_[distance,angle]
def sigmoid(z):return 1/(1+np.exp(-np.clip(z,-40,40)))
def fit_binary(X,y,steps=1000,lr=.1):
    X=np.c_[np.ones(len(X)),np.asarray(X,float)];w=np.zeros(X.shape[1]);y=np.asarray(y,float)
    for _ in range(steps):w-=lr*X.T@(sigmoid(X@w)-y)/len(y)
    return w
display(pd.DataFrame(shot_features([40,30,45],[0,15,-10]),columns=['distance_m','opening_radians']))
rng=np.random.default_rng(8);toy=rng.normal(size=(100,2));target=(toy[:,0]>0).astype(int);w=fit_binary(toy,target)
assert ((sigmoid(np.c_[np.ones(len(toy)),toy]@w)>.5)==target).mean()>.9
print('Synthetic optimization check only. No real xG fit is claimed.')
'''),
md('''## xT as a Markov reward model, from scratch
For each state, count shots, goals and attempted movements. Estimate `p_shot`, scoring conditional on shooting, and successful transition probability per **all state actions**. Failed moves contribute zero continuation in this formulation. Iterate `V = immediate_goal_reward + successful_transition @ V`. The function accepts an action table and trains the grid; the demonstration uses clearly synthetic actions because the supplied dynamic-event schema is not a complete verified shot/move training corpus. [Karun Singh](https://karun.in/blog/expected-threat.html).'''),
code('''def fit_xt(actions,n_states,tolerance=1e-10,max_iter=10000):
    totals=np.bincount(actions.start,minlength=n_states).astype(float)
    reward=np.zeros(n_states);transitions=np.zeros((n_states,n_states))
    for a in actions.itertuples():
        if a.kind=='shot':reward[a.start]+=float(a.goal)
        elif a.success:transitions[a.start,int(a.end)]+=1
    denominator=np.maximum(totals,1)
    reward/=denominator;transitions/=denominator[:,None]
    V=np.zeros(n_states)
    for _ in range(max_iter):
        next_V=reward+transitions@V
        if np.max(np.abs(next_V-V))<tolerance:return next_V,transitions,reward
        V=next_V
    raise ValueError('xT did not converge; inspect recurrent states and termination')
toy_actions=pd.DataFrame([dict(start=0,end=1,kind='move',success=True,goal=False),dict(start=0,end=1,kind='move',success=False,goal=False),dict(start=1,end=1,kind='shot',success=False,goal=True),dict(start=1,end=1,kind='shot',success=False,goal=False)])
V,T,reward=fit_xt(toy_actions,2);assert np.allclose(V,[.25,.5]);print('Synthetic fitted values:',V)
# Compare with an external event-trained model, explicitly distinct from fitting above.
grid=np.load(ROOT/'resources/models/open_play_xT.npy');plt.imshow(grid.T,origin='lower',extent=(-53,53,-34,34),aspect='auto',cmap='YlOrRd');plt.colorbar(label='External DataBallPy fitted xT');plt.xlabel('Attack-right x (m)');plt.show()
'''),
md('''## Voronoi and Gaussian influence
Voronoi assigns each grid point to its nearest player. Our anisotropic Gaussian is an explicit teaching model: longer influence along velocity and a half-second projected centre. It is not Fernández/Bornn's exact parameterization. A bounded influence difference is a score, not a calibrated probability. Compare sensitivity to scale.'''),
code('''X,Y=np.meshgrid(np.linspace(-52.5,52.5,70),np.linspace(-34,34,46));targets=np.stack([X,Y],axis=-1)
nodes=snapshot.reset_index(drop=True);positions=nodes[['x','y']].to_numpy();home=nodes.team_id.eq(1802).to_numpy()
distance=np.linalg.norm(targets[:,:,None,:]-positions,axis=-1)
voronoi=home[distance.argmin(axis=-1)].astype(float)
# Backward finite difference on consecutive observations; no future velocity features.
previous=observed[observed.frame_id.eq(frame_id-1)][['player_id','x','y','seconds']]
nodes=nodes.merge(previous,on='player_id',suffixes=('','_previous'),how='left')
dt=nodes.seconds-nodes.seconds_previous
velocity=(nodes[['x','y']].to_numpy()-nodes[['x_previous','y_previous']].to_numpy())/dt.to_numpy()[:,None]
velocity=np.nan_to_num(velocity);influence=[]
for p,v in zip(positions,velocity):
    speed=np.linalg.norm(v);u=v/speed if speed>.01 else np.array([1.,0.]);perp=np.array([-u[1],u[0]])
    delta=targets-(p+.5*v);major=4+.7*min(speed,8)
    influence.append(np.exp(-.5*((delta@u/major)**2+(delta@perp/4)**2)))
influence=np.stack(influence,axis=-1);gaussian=sigmoid(influence[:,:,home].sum(axis=-1)-influence[:,:,~home].sum(axis=-1))
fig,axs=plt.subplots(1,2,figsize=(12,4))
for ax,surface,title in zip(axs,[voronoi,gaussian],['Nearest-player team regions','Illustrative Gaussian influence']):
    pitch(ax);ax.imshow(surface,origin='lower',extent=(-52.5,52.5,-34,34),cmap='PuOr',alpha=.6,vmin=0,vmax=1);ax.scatter(positions[:,0],positions[:,1],s=15);ax.set_title(title)
plt.show()
'''),
md('''## Arrival time and pass-interception survival
Start with reaction plus travel time to each target. Then sample a hypothetical pass path, compare player arrival with ball arrival, and integrate interception hazards. The expected receiver and passer are specified. This is our simplified constant-speed hazard model, not exact Spearman or the `accessible-space` implementation. Parameters need fitting and calibration against real passes.'''),
code('''reaction=.7;player_speed=5.
arrival=reaction+np.linalg.norm(targets[:,:,None,:]-(positions+.7*velocity),axis=-1)/player_speed
control=sigmoid((arrival[:,:,~home].min(axis=-1)-arrival[:,:,home].min(axis=-1))/.45)
def pass_survival(start,end,defender_positions,ball_speed=15.,reaction=.7,run_speed=5.,rate=2.):
    duration=np.linalg.norm(end-start)/ball_speed
    if duration<1e-9:return 1.
    times=np.linspace(0,duration,40);path=start+(end-start)*times[:,None]/duration
    arrival=reaction+np.linalg.norm(path[:,None,:]-defender_positions[None,:,:],axis=-1)/run_speed
    hazards=rate*sigmoid((times[:,None]-arrival)/.15)
    # Probability of no defender interception under this independent-hazard approximation.
    return float(np.exp(-np.trapezoid(hazards.sum(axis=1),times)))
ball=wide[wide.frame_id.eq(frame_id)].iloc[0];start=np.array([ball.ball_x,ball.ball_y])
options=nodes[nodes.team_id.eq(1802)].copy()
options['completion_proxy']=[pass_survival(start,np.array([r.x,r.y]),positions[~home]) for r in options.itertuples()]
display(options[['player_id','completion_proxy']]);assert options.completion_proxy.between(0,1).all()
plt.figure(figsize=(8,5));pitch(plt.gca());plt.imshow(control,origin='lower',extent=(-52.5,52.5,-34,34),alpha=.6,cmap='PuOr',vmin=0,vmax=1);plt.title('Arrival-time control baseline');plt.show()
'''),
md('''## Accessible and dangerous space proxies
Integrate a reachability surface over cell area. Danger weighting adds an explicitly chosen goal-distance weight. This illustrative integral explains the mechanics but is not the published AS/DAS metric. The main walkthrough calls the actual `accessible-space` package. Recompute after a run to study change, keeping opponents and context visible.'''),
code('''cell_area=(X[0,1]-X[0,0])*(Y[1,0]-Y[0,0])
# Brisbane attacks left: its target goal is x=-52.5 in this sample.
danger=np.exp(-np.hypot(X+52.5,Y)/25)
accessible_proxy=float(control.sum()*cell_area)
dangerous_proxy=float((control*danger).sum()*cell_area)
print('Reachability integral proxy (m²):',round(accessible_proxy,1))
print('Danger-weighted proxy (weighted m²):',round(dangerous_proxy,1))
fig,ax=plt.subplots(figsize=(8,5));pitch(ax);ax.imshow(control*danger,origin='lower',extent=(-52.5,52.5,-34,34),alpha=.8,cmap='YlOrRd');ax.set_title('Illustrative danger-weighted space');plt.show()
'''),
md('''## Off-ball run threat and EPV decomposition
An unserved run can change options and danger even without an event. A simple proxy uses completion times destination value; compare before and after a run rather than crediting all endpoint value to the runner. SkillCorner's run xthreat is a supplied distinct model.

EPV requires a precisely defined target. A generic action decomposition sums action-selection probabilities times success/failure conditional values. Bekkers' GraphEPV instead predicts a goal within ten seconds directly from a frame graph. The formula below illustrates decomposition with hypothetical inputs, not learned predictions.'''),
code('''def lookup_xt(x,y):
    nx,ny=grid.shape;ix=np.clip(((x+53)/106*nx).astype(int),0,nx-1);iy=np.clip(((y+34)/68*ny).astype(int),0,ny-1)
    return grid[ix,iy]
options['destination_xT']=lookup_xt(-options.x.to_numpy()*106/105,-options.y.to_numpy())
options['option_proxy']=options.completion_proxy*options.destination_xT
display(options[['player_id','completion_proxy','destination_xT','option_proxy']].sort_values('option_proxy',ascending=False))
def decomposed_epv(selection,success,value_success,value_failure):
    selection=np.asarray(selection,float);success=np.asarray(success,float)
    if not np.isclose(selection.sum(),1) or (selection<0).any():raise ValueError('Action selection must be a distribution')
    return float(np.sum(selection*(success*np.asarray(value_success)+(1-success)*np.asarray(value_failure))))
print('Hypothetical decomposition:',decomposed_epv([.6,.4],[.8,.5],[.05,.15],[-.02,-.04]))
'''),md('''## Evaluation and next steps
Hold out matches, not neighboring frames. Assess discrimination **and calibration** for xG, pass completion and GraphEPV. Compare models on the same horizon and target. Use real action labels to fit xT, real shots to fit xG, and synchronized goals to train EPV. The proxy quantities above must not be reported as official provider metrics. Read [Fernández EPV](https://pmc.ncbi.nlm.nih.gov/articles/PMC8570314/), [Bekkers GraphEPV](https://rawcdn.githack.com/UnravelSports/keynotes/main/html/20250607-PyData-London.html) and [DataBallPy](https://databallpy.readthedocs.io/en/main/).''')])

book('06_graphs_and_temporal_models','Graphs and temporal models from scratch','Build node/edge tensors, message passing, a trainable NumPy graph classifier and causal history representations.',[
md('''## Construct graph tensors
Use a radius graph for this transparent baseline. Nodes are players, edge weights indicate spatial neighbors, and features contain normalized position and a home-team indicator. For actual GraphEPV training, orient coordinates to the possession team and encode attacking/defending identity consistently; the home-team indicator here only illustrates tensor construction. Compare this to UnravelSports' split-team/ball topology in the main walkthrough. Graph construction is a modeling decision, not a neutral preprocessing step. [UnravelSports](https://unravelsports.readthedocs.io/en/latest/tutorials/soccer_gnn.html).'''),
code('''def make_graph(nodes,radius=15):
    nodes=nodes.sort_values('player_id');position=nodes[['x','y']].to_numpy()
    X=np.c_[position/np.array([52.5,34]),nodes.team_id.eq(1802).astype(float)]
    distance=np.linalg.norm(position[:,None]-position[None,:],axis=-1)
    A=(distance<=radius).astype(float) # includes self loops
    A=A/A.sum(axis=1,keepdims=True)
    return X,A,nodes.player_id.to_numpy()
X,A,ids=make_graph(snapshot)
display(pd.DataFrame(X,index=ids,columns=['x_scaled','y_scaled','team']))
fig,ax=plt.subplots(figsize=(9,5));pitch(ax);pos=snapshot.set_index('player_id').loc[ids,['x','y']].to_numpy()
for i,j in zip(*np.where(np.triu(A>0,1))):ax.plot(pos[[i,j],0],pos[[i,j],1],c='#aaa',lw=1)
ax.scatter(pos[:,0],pos[:,1],c=X[:,2],cmap='PuOr');ax.set_title('Radius graph from real tracking');plt.show()
'''),
md('''## Message passing and graph readout
Average neighboring features, apply a learned linear map and nonlinearity, then pool player embeddings into a graph vector. Shared weights and symmetric pooling make this classifier invariant to row order when features and edges are permuted together. Distance/relative-velocity edge features and explicit ball nodes would enrich this minimal implementation.'''),
code('''def encode(X,A,W):return np.tanh(A@X@W)
def graph_probability(X,A,W,head,bias=0):
    H=encode(X,A,W);g=H.mean(axis=0);return 1/(1+np.exp(-np.clip(g@head+bias,-40,40)))
rng=np.random.default_rng(4);W=rng.normal(0,.1,(X.shape[1],8));head=rng.normal(0,.1,8)
embedding=encode(X,A,W);display(pd.DataFrame(embedding,index=ids).head())
permutation=rng.permutation(len(X))
assert np.isclose(graph_probability(X,A,W,head),graph_probability(X[permutation],A[np.ix_(permutation,permutation)],W,head))
print('Permutation-invariance check passed. Random weights are not EPV predictions.')
'''),
md('''## Train the small GNN with explicit backpropagation
Binary cross entropy, graph pooling, tanh derivative and neighbor aggregation gradients are shown below. Training uses synthetic graphs with a synthetic feature-sign label to check that optimization works. This does **not** establish soccer performance. The same function can accept real labeled graph samples after creating an appropriate held-out split.'''),
code('''def train_gnn(graphs,labels,hidden=8,steps=400,lr=.1):
    rng=np.random.default_rng(11);W=rng.normal(0,.2,(graphs[0][0].shape[1],hidden));head=rng.normal(0,.2,hidden);bias=0.;losses=[]
    for step in range(steps):
        dW=np.zeros_like(W);dh=np.zeros_like(head);db=0.;loss=0.
        for (X,A),y in zip(graphs,labels):
            aggregated=A@X;H=np.tanh(aggregated@W);g=H.mean(axis=0)
            z=g@head+bias;p=1/(1+np.exp(-np.clip(z,-40,40)));error=p-y
            loss+=np.logaddexp(0,z)-y*z
            dh+=g*error;db+=error
            dH=np.broadcast_to(head*error/len(X),H.shape)
            dW+=aggregated.T@(dH*(1-H**2))
        n=len(graphs);W-=lr*dW/n;head-=lr*dh/n;bias-=lr*db/n;losses.append(loss/n)
    return W,head,bias,losses
rng=np.random.default_rng(10);toy_graphs=[];toy_labels=[]
for i in range(40):
    label=i%2;features=rng.normal(2*label-1,.3,(6,3));adjacency=np.ones((6,6))/6
    toy_graphs.append((features,adjacency));toy_labels.append(label)
trained_W,trained_head,trained_bias,losses=train_gnn(toy_graphs,toy_labels)
assert losses[-1]<losses[0]
plt.plot(losses);plt.xlabel('Gradient step');plt.ylabel('Synthetic training loss');plt.show()
'''),
md('''## Build GraphEPV labels with a declared horizon
Bekkers' 2025 talk labels a frame positive when the team in possession scores within the next ten seconds in the same period. Require known follow-up through the horizon; censored sample endings and unknown possession must not become negative examples. Future outcomes are labels, never input features. A production implementation also needs complete event coverage and explicit period-end handling.'''),
code('''def goal_within_horizon(frames,goals,coverage_end,horizon=10):
    labels=pd.Series(np.nan,index=frames.index,dtype=float)
    for idx,r in frames.iterrows():
        end=coverage_end.get(r.period_id,-np.inf)
        if pd.isna(r.ball_owning_team_id) or r.seconds+horizon>end:continue
        eligible=goals.period.eq(r.period_id)&goals.team_id.eq(r.ball_owning_team_id)&goals.seconds.gt(r.seconds)&goals.seconds.le(r.seconds+horizon)
        labels.loc[idx]=float(eligible.any())
    return labels
toy_frames=pd.DataFrame({'period_id':[1,1,1],'seconds':[0,12,28],'ball_owning_team_id':[1,1,1]})
toy_goals=pd.DataFrame({'period':[1],'seconds':[8.],'team_id':[1]})
toy_labels=goal_within_horizon(toy_frames,toy_goals,{1:30.})
assert toy_labels.iloc[0]==1 and toy_labels.iloc[1]==0 and pd.isna(toy_labels.iloc[2])
display(toy_labels.rename('Synthetic target check'))
'''),
md('''## Historical features and temporal identity edges
Build backward displacement and velocity without future frames. Same-player edges connect consecutive observations within a period. A one-second lag uses ten frames at this sample's native ten Hz, with an elapsed-time check. Never bridge substitutions, missing identity observations or period boundaries.'''),
code('''history=tracking.sort_values(['player_id','period_id','frame_id']).copy()
groups=history.groupby(['player_id','period_id'])
history['lag_frame']=groups.frame_id.shift(10);history['lag_time']=groups.seconds.shift(10)
valid=history.frame_id.sub(history.lag_frame).eq(10)&np.isclose(history.seconds-history.lag_time,1)
history['dx_1s']=(history.x-groups.x.shift(10)).where(valid)
history['dy_1s']=(history.y-groups.y.shift(10)).where(valid)
temporal=[]
for (pid,period),g in observed.groupby(['player_id','period_id']):
    g=g.sort_values('frame_id')
    for a,b in zip(g.itertuples(),list(g.itertuples())[1:]):
        if b.frame_id-a.frame_id==1 and 0<b.seconds-a.seconds<.2:
            temporal.append((pid,period,a.frame_id,b.frame_id,b.seconds-a.seconds))
temporal=pd.DataFrame(temporal,columns=['player_id','period','source_frame','target_frame','dt'])
assert temporal.target_frame.gt(temporal.source_frame).all()
display(history[['player_id','frame_id','dx_1s','dy_1s']].dropna().head());display(temporal.head())
'''),
md('''## Temporal encoders: recurrence, convolution and attention
After encoding each spatial graph, apply a historical sequence model. Below are minimal forward calculations for a recurrent state, causal convolution and masked attention. Random parameters illustrate tensor mechanics only; they are not trained forecasts or EPV. The recurrence is a plain tanh RNN rather than a GRU. Identity-edge message passing is another approach, rather than the same architecture under a different name.'''),
code('''available=observed.groupby('frame_id').size();available=set(available[available.eq(22)].index)
start=next(f for f in sorted(available) if all(f+j in available for j in range(10)))
Z=[]
for f in range(start,start+10):
    Xi,Ai,_=make_graph(observed[observed.frame_id.eq(f)]);Z.append(encode(Xi,Ai,W).mean(axis=0))
Z=np.array(Z);d=Z.shape[1];rng=np.random.default_rng(9)
U=rng.normal(0,.1,(d,d));R=rng.normal(0,.1,(d,d));state=np.zeros(d);states=[]
for z in Z:state=np.tanh(z@U+state@R);states.append(state.copy())
kernel=np.array([.6,.3,.1]);convolution=np.array([sum(kernel[k]*Z[t-k] for k in range(min(3,t+1))) for t in range(len(Z))])
scores=Z@Z.T/np.sqrt(d);mask=np.triu(np.ones_like(scores,dtype=bool),1);scores[mask]=-np.inf
attention=np.exp(scores-scores.max(axis=1,keepdims=True));attention/=attention.sum(axis=1,keepdims=True);context=attention@Z
assert np.allclose(attention[mask],0)
fig,axs=plt.subplots(1,3,figsize=(13,4))
for ax,data,title in zip(axs,[np.array(states),convolution,attention],['Recurrent hidden states','Causal temporal convolution','Masked temporal attention']):ax.imshow(data,aspect='auto');ax.set_title(title);ax.set_ylabel('Historical frame')
plt.show()
'''),md('''## Evaluation and extensions
Split by whole matches or independent possessions, with no overlapping history/outcome windows across splits. Test calibration and compare location-only, tabular, static-graph and temporal baselines on the **same** target. Larger temporal models need far more than this sample. Learned attention is not causal importance. Receiver prediction, defensive attribution, counterattack success and trajectory forecasting need their own targets and losses; the binary scorer above does not reproduce TacticAI, DEFCON or a trajectory generator. Sources: [GraphEPV talk](https://rawcdn.githack.com/UnravelSports/keynotes/main/html/20250607-PyData-London.html), [counterattack GNN](https://arxiv.org/abs/2411.17450), [temporal architectures](https://pytorch-geometric-temporal.readthedocs.io/en/latest/modules/root.html).''')])

index=['# Avenue notebooks','Each notebook starts from a fresh kernel and contains its method implementations. Only loading and pitch drawing are shared. The main walkthrough notebook is unchanged.','']
for name,title in BOOKS.items():index.append(f'- [{title}]({name}.ipynb)')
index+=['','Training routines are implemented explicitly, with synthetic numerical checks where the partial match lacks credible outcome/role labels. These checks are marked and are not model-performance claims. Game-modeling proxies are distinct from published or provider production metrics.','', 'Regenerate: `python scripts/build_avenue_notebooks.py`. Execute and export: `python scripts/execute_avenue_notebooks.py`.']
(OUT/'README.md').write_text('\n'.join(index)+'\n',encoding='utf-8')
print('Created',len(BOOKS),'avenue notebooks')
