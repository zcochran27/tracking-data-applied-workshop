"""Additional reproducible methods used by the illustrated slides and notebook."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from workshop import ROOT, graph_edges

def nearest_possession(motion,wide,max_distance=2.0):
    joined=motion.merge(wide[['frame_id','ball_x','ball_y']],on='frame_id',validate='many_to_one')
    joined['ball_distance']=np.hypot(joined.x-joined.ball_x,joined.y-joined.ball_y)
    valid=joined.dropna(subset=['ball_distance'])
    nearest=valid.loc[valid.groupby('frame_id').ball_distance.idxmin(),['frame_id','period_id','player_id','ball_distance','player_in_possession']].sort_values('frame_id')
    nearest['candidate']=nearest.player_id.where(nearest.ball_distance.le(max_distance),'unassigned')
    nearest['change']=nearest.candidate.ne(nearest.candidate.shift()) & nearest.frame_id.diff().eq(1)
    return nearest.reset_index(drop=True)

def centered_shape(motion,team=1802,in_possession=True):
    s=motion[motion.team_id.eq(team) & motion.team_in_possession.eq(team).eq(in_possession)].copy()
    # Role maps use outfield players; caller excludes metadata-identified goalkeepers first.
    centers=s.groupby('frame_id')[['x','y']].transform('mean')
    s[['cx','cy']]=s[['x','y']].to_numpy()-centers.to_numpy()
    return s.groupby('player_id').agg(x=('cx','median'),y=('cy','median'),n=('frame_id','size')).reset_index()

def line_clusters(shape,n_lines=3):
    """Exploratory 1D longitudinal clusters, not a validated formation classifier."""
    result=shape.copy()
    z=linkage(result[['x']].to_numpy(),method='ward')
    result['line']=fcluster(z,n_lines,criterion='maxclust')
    return result

def temporal_features(motion,frames):
    s=motion[motion.frame_id.isin(frames)].sort_values(['player_id','period_id','frame_id']).copy()
    for feature in ['x','y','vx','vy','speed_kmh']:
        s[feature+'_lag10']=s.groupby(['player_id','period_id'])[feature].shift(10)
    lagframe=s.groupby(['player_id','period_id']).frame_id.shift(10)
    valid=s.frame_id.sub(lagframe).eq(10)
    cols=[c for c in s if c.endswith('_lag10')]
    s.loc[~valid,cols]=np.nan
    s['speed_change_1s']=s.speed_kmh-s.speed_kmh_lag10
    return s

def temporal_edges(motion,frames,radius=15):
    """Spatial edges plus causal identity edges from one observed frame to the next."""
    s=motion[motion.frame_id.isin(frames)].dropna(subset=['x','y']).sort_values(['player_id','period_id','frame_id'])
    spatial=[]
    for frame,g in s.groupby('frame_id'):
        e=graph_edges(g,radius);e['source_frame']=frame;e['target_frame']=frame;e['edge_type']='spatial';spatial.append(e)
    time=[]
    for (_,period),g in s.groupby(['player_id','period_id']):
        for a,b in zip(g.itertuples(),list(g.itertuples())[1:]):
            if b.frame_id-a.frame_id!=1:continue
            time.append(dict(source=a.player_id,target=b.player_id,source_frame=a.frame_id,target_frame=b.frame_id,edge_type='temporal',dt=.1))
    return pd.concat(spatial+[pd.DataFrame(time)],ignore_index=True)

def xt_grid():
    return np.load(ROOT/'resources/models/open_play_xT.npy',allow_pickle=False)

def xt_value(x,y):
    """DataBallPy grid convention: centred 106 × 68 m pitch, attacking right."""
    grid=xt_grid();nx,ny=grid.shape
    xi=np.clip((np.asarray(x)+53)*nx/106,0,nx-1).astype(int)
    yi=np.clip((np.asarray(y)+34)*ny/68,0,ny-1).astype(int)
    return grid[xi,yi]
