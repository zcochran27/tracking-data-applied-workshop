from pathlib import Path
import json,subprocess
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
ROOT=Path(__file__).resolve().parents[1]
from pathlib import Path
import json, urllib.request
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from IPython.display import display
from kloppy import skillcorner

# Change DATA_ROOT to use an existing cache elsewhere. No local Python modules are imported.
candidates=[Path.cwd(),*Path.cwd().parents]
ROOT=next((p for p in candidates if (p/'data/1925299/1925299_match.json').exists()),Path.cwd())
DATA_ROOT=ROOT/'data/1925299'

def ensure_sample(destination):
    """Download only missing data files. Tracking is bounded to 9000 source records."""
    destination.mkdir(parents=True,exist_ok=True)
    revision='4340d274572876239c154c90bc507a9b3250a656'
    base=f'https://raw.githubusercontent.com/SkillCorner/opendata/{revision}/data/matches/1925299/'
    for suffix in ['match.json','dynamic_events.csv','phases_of_play.csv']:
        name='1925299_'+suffix;target=destination/name
        if not target.exists():
            with urllib.request.urlopen(base+name,timeout=90) as response:target.write_bytes(response.read())
    name='1925299_tracking_extrapolated.jsonl';target=destination/name
    if not target.exists():
        url=base.replace('raw.githubusercontent.com/','media.githubusercontent.com/media/')+name
        temporary=destination/(name+'.partial')
        with urllib.request.urlopen(url,timeout=90) as response,temporary.open('wb') as output:
            count=0
            for line in response:
                if line.strip():
                    json.loads(line);output.write(line);count+=1
                if count>=9000:break
        temporary.replace(target)

def read_tracking(destination):
    """Load kloppy coordinates and explicitly reshape player columns to rows."""
    dataset=skillcorner.load(meta_data=destination/'1925299_match.json',raw_data=destination/'1925299_tracking_extrapolated.jsonl',coordinates='skillcorner')
    wide=dataset.to_df()
    metadata=json.loads((destination/'1925299_match.json').read_text(encoding='utf-8'))
    raw=[json.loads(line) for line in (destination/'1925299_tracking_extrapolated.jsonl').read_text().splitlines() if line.strip()]
    player_possession={r['frame']:str(r.get('possession',{}).get('player_id')) for r in raw}
    visibility={(r['frame'],str(p['player_id'])):p.get('is_detected') for r in raw for p in r.get('player_data',[])}
    parts=[]
    for p in metadata['players']:
        pid=str(p['id'])
        if f'{pid}_x' not in wide:continue
        part=wide[['period_id','frame_id','timestamp','ball_owning_team_id',f'{pid}_x',f'{pid}_y']].copy()
        part.columns=['period_id','frame_id','timestamp','team_in_possession','x','y']
        part['player_id']=pid;part['team_id']=p['team_id'];part['name']=p['short_name'];parts.append(part)
    tracking=pd.concat(parts,ignore_index=True)
    tracking['seconds']=tracking.timestamp.dt.total_seconds()
    tracking['player_in_possession']=tracking.frame_id.map(player_possession)
    tracking['is_detected']=[visibility.get((f,p)) for f,p in zip(tracking.frame_id,tracking.player_id)]
    tracking=tracking.sort_values(['player_id','period_id','frame_id'])
    return dataset,wide,tracking,metadata,raw

def pitch(ax=None):
    """Draw a 105 by 68 metre pitch in native centered coordinates."""
    if ax is None:_,ax=plt.subplots(figsize=(9,5.5))
    ax.set_facecolor('#eef3ed')
    ax.add_patch(Rectangle((-52.5,-34),105,68,fill=False,color='#597063'))
    ax.plot([0,0],[-34,34],c='#597063');ax.add_patch(Circle((0,0),9.15,fill=False,color='#597063'))
    for x in [-52.5,36]:ax.add_patch(Rectangle((x,-20.16),16.5,40.32,fill=False,color='#597063'))
    ax.set(xlim=(-55,55),ylim=(-36,36),aspect='equal',xlabel='x (m)',ylabel='y (m)')
    return ax

ensure_sample(DATA_ROOT)
dataset,wide,tracking,metadata,raw=read_tracking(DATA_ROOT)
def sigmoid(z):
    return 1/(1+np.exp(-np.clip(z,-40,40)))

def interception_components(start,end,defenders,ball_speed=15.,reaction=.7,run_speed=5.,rate=2.):
    duration=np.linalg.norm(end-start)/ball_speed
    times=np.linspace(0,max(duration,1e-6),40)
    path=start+(end-start)*np.linspace(0,1,40)[:,None]
    player_arrival=reaction+np.linalg.norm(path[:,None,:]-defenders[None,:,:],axis=-1)/run_speed
    hazard=rate*sigmoid((times[:,None]-player_arrival)/.15)
    increments=(hazard.sum(axis=1)[1:]+hazard.sum(axis=1)[:-1])/2*np.diff(times)
    survival=np.exp(-np.r_[0,np.cumsum(increments)])
    return times,player_arrival,hazard,survival


lookup={str(p['id']):p for p in metadata['players']}
raw_lookup={r['frame']:r for r in raw if r['period']==1}
observed=tracking.dropna(subset=['x','y'])
complete=observed.groupby(['period_id','frame_id']).size();valid=set(complete[complete.eq(22)].index.get_level_values('frame_id'))
candidates=[]
for frame_id in sorted(valid)[::10]:
    r=raw_lookup.get(frame_id);carrier=str(r.get('possession',{}).get('player_id')) if r else None
    if carrier not in lookup or r['ball_data'].get('z') is None or r['ball_data']['z']>2:continue
    nodes=observed[observed.frame_id.eq(frame_id)].copy();start=np.array([r['ball_data']['x'],r['ball_data']['y']],float)
    owner=nodes[nodes.player_id.eq(carrier)]
    if len(owner)!=1 or np.linalg.norm(owner[['x','y']].to_numpy()[0]-start)>2:continue
    team=int(owner.team_id.iloc[0]);defenders=nodes[nodes.team_id.ne(team)].copy();targets=nodes[nodes.team_id.eq(team)&nodes.player_id.ne(carrier)].copy()
    for target in targets.itertuples():
        end=np.array([target.x,target.y]);length=np.linalg.norm(end-start)
        if not 25<length<60:continue
        times,arrival,hazard,survival=interception_components(start,end,defenders[['x','y']].to_numpy())
        risk=(hazard.max(axis=0)>.9).sum()
        if .15<survival[-1]<.8 and risk>=2:
            candidates.append((abs(survival[-1]-.5),frame_id,carrier,str(target.player_id)))
assert candidates,'No illustrative interception example found'
_,frame_id,carrier,receiver=min(candidates)
r=raw_lookup[frame_id];nodes=observed[observed.frame_id.eq(frame_id)].copy();team=int(lookup[carrier]['team_id']);start=np.array([r['ball_data']['x'],r['ball_data']['y']],float)
defenders=nodes[nodes.team_id.ne(team)].reset_index(drop=True);targets=nodes[nodes.team_id.eq(team)&nodes.player_id.ne(carrier)].copy()
def_xy=defenders[['x','y']].to_numpy();end=targets[targets.player_id.eq(receiver)][['x','y']].to_numpy()[0]
times,arrival,hazard,survival=interception_components(start,end,def_xy);path=start+(end-start)*np.linspace(0,1,40)[:,None]
targets['survival_score']=[interception_components(start,np.array([q.x,q.y]),def_xy)[-1][-1] for q in targets.itertuples()]
# Two defenders with the strongest interception hazards at any path point.
selected=np.argsort(hazard.max(axis=0))[-2:][::-1]
peaks=sorted(int(np.argmax(hazard[:,d])) for d in selected)
indices=sorted(set([max(10,peaks[0]-6),peaks[0],min(39,peaks[-1])]))
assert len(indices)==3
probes=[]
for k,index in enumerate(indices):
    d=int(selected[np.argmax(hazard[index,selected])]);h=float(hazard[index,d]);conditional=1-np.exp(-h*.2)
    probes.append(dict(marker='ABC'[k],index=int(index),defender_id=str(defenders.iloc[d].player_id),defender_number=int(lookup[str(defenders.iloc[d].player_id)]['number']),ball_s=float(times[index]),defender_s=float(arrival[index,d]),hazard_per_s=h,conditional_02s=float(conditional)))
OUT=ROOT/'assets/results';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#fbfcf8','savefig.facecolor':'#fbfcf8'})
cmap=plt.get_cmap('RdYlGn')

def draw_pass_example(cursor=None):
    fig=plt.figure(figsize=(12.8,7.2),dpi=100);gs=fig.add_gridspec(2,2,height_ratios=[4.1,1.4],hspace=.38,wspace=.3)
    ax=fig.add_subplot(gs[0,0]);pitch(ax)
    ax.scatter(def_xy[:,0],def_xy[:,1],c='#7959b5',s=35,zorder=4,label='Defenders')
    occupied=[]
    for q in targets.itertuples():
        ax.plot([start[0],q.x],[start[1],q.y],color=cmap(q.survival_score),lw=1.8,alpha=.85,zorder=2)
        ax.scatter(q.x,q.y,c='#e87524',edgecolors='white',s=55,zorder=5)
        tx,ty=q.x,q.y+4
        while any(abs(tx-x)<13 and abs(ty-y)<7 for x,y in occupied):ty+=7
        if ty>34:ty=q.y-6
        occupied.append((tx,ty));ax.annotate(f"#{lookup[str(q.player_id)]['number']}  {q.survival_score:.0%}",(q.x,q.y),xytext=(tx,ty),textcoords='data',ha='center',fontsize=9,bbox={'facecolor':'white','alpha':.9,'edgecolor':'none','pad':1},arrowprops={'arrowstyle':'-','color':'#999','lw':.6},zorder=10)
    ax.scatter(*start,s=130,c='black',edgecolors='white',zorder=8,label='Carrier / ball')
    ax.set_title(f"From carrier #{lookup[carrier]['number']} to each teammate",fontsize=15);ax.set_xlabel('');ax.set_ylabel('');ax.legend(loc='lower left',fontsize=8)
    ax=fig.add_subplot(gs[0,1]);pitch(ax)
    ax.scatter(def_xy[:,0],def_xy[:,1],c='#7959b5',alpha=.25,s=30,zorder=2)
    ax.plot(*path.T,c='#147d68',lw=2,label='Ball path');ax.scatter(*start,c='black',s=60,zorder=5);ax.scatter(*end,c='#e87524',s=100,zorder=5)
    for j,d in enumerate(selected):
        q=def_xy[d];ax.scatter(*q,c='#7959b5',edgecolors='white',s=110,zorder=5);ax.annotate('#'+str(lookup[str(defenders.iloc[d].player_id)]['number']),q,xytext=(4,5),textcoords='offset points',fontsize=11)
    for probe in probes:
        point=path[probe['index']];dxy=def_xy[defenders.player_id.eq(probe['defender_id'])][0]
        ax.plot([dxy[0],point[0]],[dxy[1],point[1]],ls='--',c='#7959b5',lw=1.3,alpha=1 if cursor is None or cursor>=probe['index'] else .25)
        ax.scatter(*point,s=100,facecolors='white',edgecolors='#147d68',zorder=7);ax.text(*point,probe['marker'],ha='center',va='center',fontsize=9,zorder=8)
    if cursor is not None:ax.scatter(*path[cursor],s=130,c='black',edgecolors='white',zorder=10)
    extent=np.vstack([start,end,def_xy[selected]]);ax.set(xlim=(max(-55,extent[:,0].min()-10),min(55,extent[:,0].max()+10)),ylim=(max(-36,extent[:,1].min()-12),min(36,extent[:,1].max()+12)),xlabel='',ylabel='')
    ax.set_title(f"Selected pass to #{lookup[receiver]['number']}: {survival[-1]:.0%} survival",fontsize=15)
    left=fig.add_subplot(gs[1,0]);left.axis('off');left.text(0,.95,'Same model as notebook 12',weight='bold',fontsize=13,va='top');left.text(0,.66,'Ball: 15 m/s. Defender: 0.7 s reaction + distance / 5 m/s.\nSum interception hazards, then integrate ball survival.\nPercentages are uncalibrated survival estimates.',fontsize=11,va='top',linespacing=1.5)
    table=fig.add_subplot(gs[1,1]);table.axis('off')
    cells=[[p['marker'],f"#{p['defender_number']}",f"{p['ball_s']:.2f}s",f"{p['defender_s']:.2f}s",f"{p['conditional_02s']:.0%}"] for p in probes]
    tb=table.table(cellText=cells,colLabels=['Point','Def.','Ball ETA','Def. ETA','P / 0.2s*'],loc='upper center',cellLoc='center');tb.auto_set_font_size(False);tb.set_fontsize(10);tb.scale(1,1.6)
    table.text(0,-.03,'*Conditional interception chance over 0.2 s at this hazard,\nassuming the ball is still free; not endpoint completion.',fontsize=9,va='top')
    fig.suptitle(f'Which passes survive interception?  Real frame {frame_id}',fontsize=20)
    fig.subplots_adjust(left=.055,right=.975,top=.87,bottom=.13)
    return fig
fig=draw_pass_example();fig.savefig(OUT/'pass_survival_options.png',dpi=140);plt.close(fig)
provenance={'frame':int(frame_id),'carrier':carrier,'receiver':receiver,'target_count':len(targets),'survival_score':float(survival[-1]),'ball_speed_mps':15,'reaction_s':.7,'run_speed_mps':5,'rate_per_s':2,'sigmoid_scale_s':.15,'probes':probes,'note':'Same interception_components as notebook 12; hypothetical ground passes, not calibrated completion or observed attempts.'}
(OUT/'pass_survival_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
video=ROOT/'assets/videos/pass_survival_options.mp4';proc=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','10','-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],stdin=subprocess.PIPE)
for i in range(40):
    fig=draw_pass_example(i);fig.canvas.draw();rgb=np.asarray(fig.canvas.buffer_rgba())[:,:,:3].copy()
    for _ in range(2):proc.stdin.write(rgb.tobytes())
    plt.close(fig)
proc.stdin.close();assert proc.wait()==0
print('Selected real example:',provenance,flush=True)
