"""Readable workshop helpers. Metric approximations are explicitly named."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from scipy.ndimage import gaussian_filter1d
from scipy.special import expit

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / '1925299'
COLORS = {1802: '#e87524', 871: '#7761be'}

def load_data():
    from kloppy import skillcorner
    dataset = skillcorner.load(meta_data=DATA/'1925299_match.json',
        raw_data=DATA/'1925299_tracking_extrapolated.jsonl', coordinates='skillcorner')
    wide = dataset.to_df()
    meta = json.loads((DATA/'1925299_match.json').read_text(encoding='utf-8'))
    players = {str(p['id']):p for p in meta['players']}
    records = []
    for pid,p in players.items():
        if f'{pid}_x' not in wide: continue
        part = wide[['frame_id','period_id','timestamp','ball_owning_team_id',f'{pid}_x',f'{pid}_y']].copy()
        part.columns = ['frame_id','period_id','timestamp','team_in_possession','x','y']
        part['player_id'],part['team_id'],part['name'] = pid,p['team_id'],p['short_name']
        records.append(part)
    long = pd.concat(records,ignore_index=True)
    long['seconds'] = long.timestamp.dt.total_seconds()
    # Retain raw visibility information rather than treating extrapolated coordinates as observed.
    raw = [json.loads(s) for s in (DATA/'1925299_tracking_extrapolated.jsonl').read_text().splitlines() if s.strip()]
    possession={r['frame']: str(r.get('possession',{}).get('player_id')) for r in raw}
    observed={(r['frame'],str(p['player_id'])):p.get('is_detected') for r in raw for p in r.get('player_data',[])}
    long['player_in_possession']=long.frame_id.map(possession)
    long['is_detected']=[observed.get((f,p)) for f,p in zip(long.frame_id,long.player_id)]
    events = pd.read_csv(DATA/'1925299_dynamic_events.csv')
    phases = pd.read_csv(DATA/'1925299_phases_of_play.csv')
    return dataset,wide,long,meta,events,phases,raw

def movement(long, sigma=1.5):
    """Smooth within contiguous valid segments; never differentiate across gaps/halves."""
    out = long.copy().sort_values(['player_id','period_id','frame_id'])
    out[['vx','vy','speed_kmh','raw_speed_kmh']] = np.nan
    for _,idx in out.groupby(['player_id','period_id']).groups.items():
        g=out.loc[idx]; valid=g[['x','y']].notna().all(axis=1)
        breaks=(~valid | ~valid.shift(fill_value=False) | g.frame_id.diff().ne(1)).cumsum()
        for _, seg in g[valid].groupby(breaks[valid]):
            if len(seg)<5: continue
            t=seg.seconds.to_numpy(); xy=seg[['x','y']].to_numpy()
            raw_v=np.gradient(xy,t,axis=0)
            smooth=gaussian_filter1d(xy,sigma=sigma,axis=0,mode='nearest')
            v=np.gradient(smooth,t,axis=0)
            # Boundary derivatives are excluded: filters have reduced support there.
            edge=max(1,int(np.ceil(3*sigma)))
            v[:edge]=np.nan; v[-edge:]=np.nan
            out.loc[seg.index,['vx','vy']]=v
            out.loc[seg.index,'speed_kmh']=np.linalg.norm(v,axis=1)*3.6
            out.loc[seg.index,'raw_speed_kmh']=np.linalg.norm(raw_v,axis=1)*3.6
    return out.sort_values(['frame_id','player_id']).reset_index(drop=True)

def physical_summary(long):
    """Teaching estimates at native 10 Hz, with missing coverage reported."""
    rows=[]
    for pid,g in long.groupby('player_id'):
        s=g.speed_kmh; step=s/3.6*0.1
        rows.append(dict(player_id=pid,name=g.name.iloc[0],valid_seconds=s.notna().sum()/10,
            coverage=s.notna().mean(),distance_m=step.sum(min_count=1),
            hsr_m=step.where(s.ge(20)&s.lt(25)).sum(),sprint_m=step.where(s.ge(25)).sum()))
    return pd.DataFrame(rows).sort_values('distance_m',ascending=False)

def efforts(g, threshold=25, min_duration=1.0):
    """Illustrative effort rule: continuous speed >= threshold for >= 1 s; no merging."""
    g=g.sort_values('frame_id').copy()
    active=g.speed_kmh.ge(threshold)
    starts=active.ne(active.shift(fill_value=False)) | g.frame_id.diff().ne(1) | g.period_id.diff().ne(0)
    result=[]
    for _,s in g[active].groupby(starts.cumsum()[active]):
        duration=len(s)*0.1
        if duration>=min_duration:
            result.append({'start':s.seconds.iloc[0],'end':s.seconds.iloc[-1]+.1,'duration_s':duration,'peak_kmh':s.speed_kmh.max()})
    return pd.DataFrame(result,columns=['start','end','duration_s','peak_kmh'])

def pitch(ax=None):
    if ax is None: _,ax=plt.subplots(figsize=(10,6.5))
    ax.set_facecolor('#eef3ed')
    ax.add_patch(Rectangle((-52.5,-34),105,68,fill=False,color='#597063'))
    ax.plot([0,0],[-34,34],color='#597063');ax.add_patch(Circle((0,0),9.15,fill=False,color='#597063'))
    for sign in [-1,1]:
        x=-52.5 if sign<0 else 36
        ax.add_patch(Rectangle((x,-20.16),16.5,40.32,fill=False,color='#597063'))
        ax.plot([sign*52.5,sign*52.5],[-3.66,3.66],lw=4,color='#597063')
    ax.set(xlim=(-55,55),ylim=(-36,36),aspect='equal',xlabel='x (m)',ylabel='y (m)')
    return ax

def frame_plot(long,wide,frame,ax=None,labels=False):
    ax=pitch(ax);g=long[long.frame_id.eq(frame)].dropna(subset=['x','y'])
    for team,s in g.groupby('team_id'):
        ax.scatter(s.x,s.y,c=COLORS.get(team,'gray'),s=65,edgecolors='white',zorder=4,label=str(team))
        if labels:
            for r in s.itertuples(): ax.text(r.x+.5,r.y+.5,r.player_id,fontsize=7)
    b=wide[wide.frame_id.eq(frame)].iloc[0]
    ax.scatter(b.ball_x,b.ball_y,c='black',s=30,zorder=5)
    ax.set_title(f'Brisbane (orange) vs Perth (purple) | frame {frame}')
    return ax

def choose_sequence(long,wide):
    """Find a 10 s segment with strong coverage, a live ball and known possession."""
    counts=long.dropna(subset=['x','y','vx','vy']).groupby('frame_id').size()
    w=wide.copy();w['n']=w.frame_id.map(counts).fillna(0)
    w['ok']=w.n.ge(22)&w.ball_x.notna()&w.ball_y.notna()&w.ball_owning_team_id.notna()&w.ball_state.astype(str).str.lower().eq('alive')
    # Prefer territory near either penalty area; still require continuity across the clip.
    candidates=[]
    for i in range(100,len(w)-100,10):
        clip=w.iloc[i:i+100]
        if clip.ok.mean()>.95 and clip.frame_id.diff().dropna().eq(1).all():
            candidates.append((abs(float(clip.ball_x.median())),i))
    if not candidates: raise ValueError('No suitable clip: inspect tracking coverage.')
    _,i=max(candidates)
    return w.iloc[i:i+100].frame_id.to_numpy()

def surfaces(g, ball, nx=80,ny=52):
    """Baselines, not calibrated pass-success models or exact published reproductions."""
    x=np.linspace(-52.5,52.5,nx);y=np.linspace(-34,34,ny);X,Y=np.meshgrid(x,y)
    points=np.stack([X,Y],axis=-1);pos=g[['x','y']].to_numpy();vel=g[['vx','vy']].to_numpy()
    home=g.team_id.to_numpy()==1802
    d=np.linalg.norm(points[:,:,None,:]-pos,axis=-1)
    vor=home[d.argmin(axis=-1)].astype(float)
    influence=[]
    for p,v in zip(pos,vel):
        speed=np.linalg.norm(v);u=v/(speed+1e-9); perp=np.array([-u[1],u[0]]) if speed>.01 else np.array([0.,1.])
        if speed<.01:u=np.array([1.,0.])
        # Transparent illustrative covariance; not the Fernandez/Bornn parameterization.
        a=4+min(speed,8)*.7;b=4
        delta=points-(p+.5*v)
        influence.append(np.exp(-.5*((delta@u/a)**2+(delta@perp/b)**2)))
    inf=np.stack(influence,axis=-1)
    gaussian=expit(inf[:,:,home].sum(axis=-1)-inf[:,:,~home].sum(axis=-1))
    arrival=.7+np.linalg.norm(points[:,:,None,:]-(pos+.7*vel),axis=-1)/5
    t_home=arrival[:,:,home].min(axis=-1);t_away=arrival[:,:,~home].min(axis=-1)
    tti=expit((t_away-t_home)/.45)
    return X,Y,{'Voronoi':vor,'Gaussian influence':gaussian,'Arrival-time baseline':tti}

def control_plot(long,wide,frame,model='Gaussian influence',ax=None):
    g=long[long.frame_id.eq(frame)].dropna(subset=['x','y','vx','vy'])
    b=wide[wide.frame_id.eq(frame)].iloc[0]
    X,Y,maps=surfaces(g,(b.ball_x,b.ball_y))
    ax=pitch(ax);ax.pcolormesh(X,Y,maps[model],vmin=0,vmax=1,cmap='PuOr_r',alpha=.6,shading='auto')
    frame_plot(long,wide,frame,ax);ax.set_title(model+' | orange = Brisbane advantage')
    return ax

def graph_edges(g,radius=15):
    g=g.dropna(subset=['x','y']).reset_index(drop=True);p=g[['x','y']].to_numpy()
    rows=[]
    for i in range(len(g)):
        for j in range(len(g)):
            if i==j:continue
            delta=p[j]-p[i];d=np.linalg.norm(delta)
            if d<=radius:rows.append((g.player_id[i],g.player_id[j],d,*delta,int(g.team_id[i]==g.team_id[j])))
    return pd.DataFrame(rows,columns=['source','target','distance','dx','dy','same_team'])

def das_input(long,wide,frames):
    """Use explicit attacking direction from the first-half goalkeeper locations."""
    selected=long[long.frame_id.isin(frames)].copy()
    first=long[(long.period_id.eq(1)) & long.frame_id.lt(1000)]
    median_x=first.groupby(['team_id','player_id']).x.median()
    home_x=median_x.loc[1802]
    # Goalkeepers have the most extreme persistent locations; team median is also inspected in notebook.
    home_defends_left=abs(home_x.min())>abs(home_x.max())
    direction={1802:1 if home_defends_left else -1,871:-1 if home_defends_left else 1}
    selected['attacking_direction']=selected.team_in_possession.map(direction)
    ball=wide[wide.frame_id.isin(frames)][['frame_id','period_id','ball_x','ball_y','ball_owning_team_id']].copy()
    ball.columns=['frame_id','period_id','x','y','team_in_possession']
    ball['player_id']='ball';ball['team_id']=None;ball['vx']=0.;ball['vy']=0.
    ball['attacking_direction']=ball.team_in_possession.map(direction)
    ball['player_in_possession']=ball.frame_id.map(selected.groupby('frame_id').player_in_possession.first())
    return pd.concat([selected,ball],ignore_index=True)
