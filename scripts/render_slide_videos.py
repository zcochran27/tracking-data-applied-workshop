"""Render slide-only MP4 assets from cached SkillCorner data; notebooks stay standalone."""
from pathlib import Path
import json, subprocess, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from scipy.optimize import linear_sum_assignment
from scipy.ndimage import gaussian_filter1d

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/videos'; OUT.mkdir(exist_ok=True)
POST=ROOT/'assets/methods'; META=json.loads((ROOT/'data/1925299/1925299_match.json').read_text(encoding='utf-8'))
RAW=[json.loads(s) for s in (ROOT/'data/1925299/1925299_tracking_extrapolated.jsonl').read_text().splitlines()]
PLAYERS={p['id']:p for p in META['players']}; HOME=META['home_team']['id']
COLORS={HOME:'#e87524',META['away_team']['id']:'#7959b5'}
VALID=[r for r in RAW if r['period']==1 and len(r['player_data'])==22 and r['ball_data']['x'] is not None]
BYFRAME={r['frame']:r for r in VALID}
plt.rcParams.update({'font.size':12,'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})

def pitch(ax, centered=False):
    ax.set_facecolor('#eef3ed')
    if not centered:
        ax.add_patch(Rectangle((-52.5,-34),105,68,fill=False,color='#597063'))
        ax.plot([0,0],[-34,34],color='#597063');ax.add_patch(Circle((0,0),9.15,fill=False,color='#597063'))
        for x in [-52.5,36]:ax.add_patch(Rectangle((x,-20.16),16.5,40.32,fill=False,color='#597063'))
    ax.set(xlim=(-55,55),ylim=(-36,36),aspect='equal',xlabel='x (m)',ylabel='y (m)')

def positions(r):
    ids=np.array([p['player_id'] for p in r['player_data']]); xy=np.array([[p['x'],p['y']] for p in r['player_data']],float)
    return ids,xy,np.array([PLAYERS[i]['team_id'] for i in ids])

def draw_players(ax,r, labels=False):
    ids,xy,teams=positions(r)
    for t,col in COLORS.items():
        q=xy[teams==t];ax.scatter(*q.T,c=col,s=65,edgecolors='white',zorder=4)
    ax.scatter(r['ball_data']['x'],r['ball_data']['y'],c='black',s=38,zorder=5)
    if labels:
        for pid,q in zip(ids,xy):ax.annotate(str(PLAYERS[pid]['number']),q,xytext=(4,4),textcoords='offset points',fontsize=9)
    return ids,xy,teams

def nearest(r):
    ids,xy,t=positions(r); b=np.array([r['ball_data']['x'],r['ball_data']['y']]);d=np.linalg.norm(xy-b,axis=1);j=d.argmin()
    z=r['ball_data'].get('z'); candidate=int(ids[j]) if d[j]<=2 and z is not None and z<=2 else None
    return candidate,float(d[j])

# Same transparent pass-candidate gates as notebook 02; no provider event endpoints.
segments=[]
for r in VALID:
    pid,_=nearest(r)
    if segments and segments[-1]['player']==pid and r['frame']==segments[-1]['end']+1:segments[-1]['end']=r['frame']
    else:segments.append(dict(player=pid,start=r['frame'],end=r['frame']))
stable=[s for s in segments if s['player'] is not None and s['end']-s['start']+1>=3]
pairs=[]
for a,b in zip(stable,stable[1:]):
    if a['player']==b['player'] or PLAYERS[a['player']]['team_id']!=PLAYERS[b['player']]['team_id']:continue
    if not 1<=b['start']-a['end']<=40:continue
    path=[BYFRAME.get(f) for f in range(a['end'],b['start']+1)]
    if not all(path):continue
    disp=np.linalg.norm(np.array([path[0]['ball_data'][k] for k in ['x','y']])-np.array([path[-1]['ball_data'][k] for k in ['x','y']]))
    if disp>=3:pairs.append((a,b))
assert pairs,'No valid pass candidates in sample'
a,b=pairs[0];start=max(a['start'],a['end']-20);end=min(b['end'],b['start']+20)
CLIP=[BYFRAME[f] for f in range(start,end+1) if f in BYFRAME]
GENERAL=next(([BYFRAME[f] for f in range(s,s+150)] for s in sorted(BYFRAME) if all(f in BYFRAME for f in range(s,s+150))),None)
assert GENERAL
only=set(sys.argv[1:])
manifest=json.loads((OUT/'manifest.json').read_text()) if (OUT/'manifest.json').exists() else []

def movie(name,records,draw,fps=10,subtitle='',repeat=1):
    if only and name not in only:return
    dest=OUT/(name+'.mp4');w,h=1280,720
    args=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-c:v','libx264','-crf','21','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
    proc=subprocess.Popen(args,stdin=subprocess.PIPE)
    for i,r in enumerate(records):
        fig=plt.figure(figsize=(12.8,7.2),dpi=100,facecolor='#fbfcf8');draw(fig,r,i)
        fig.text(.5,.025,subtitle,ha='center',fontsize=12,color='#43594f')
        fig.subplots_adjust(left=.07,right=.97,bottom=.12,top=.86,wspace=.25)
        fig.canvas.draw();rgb=np.asarray(fig.canvas.buffer_rgba())[:,:,:3].copy()
        if i==0:plt.imsave(POST/('video_'+name+'.png'),rgb)
        for _ in range(repeat):proc.stdin.write(rgb.tobytes())
        plt.close(fig)
    proc.stdin.close();assert proc.wait()==0
    manifest.append(dict(file='assets/videos/'+name+'.mp4',poster='methods/video_'+name+'.png',frames=len(records)*repeat,fps=fps,source='SkillCorner match 1925299',description=subtitle))
    print('Rendered',name,flush=True)

def tracking(fig,r,i):
    ax=fig.add_subplot();pitch(ax);draw_players(ax,r,True);ax.set_title(f"Real tracking playback · frame {r['frame']} · {(r['frame']-GENERAL[0]['frame'])/10:.1f} s elapsed",fontsize=19)
movie('tracking_playback',GENERAL,tracking,subtitle='Real SkillCorner coordinates · native 10 Hz · no inferred future motion')

def event(fig,r,i):
    ax=fig.add_subplot(121);pitch(ax);ids,xy,t=draw_players(ax,r,True)
    ball=[r['ball_data']['x'],r['ball_data']['y']];ax.add_patch(Circle(ball,2,color='#147d68',fill=False,lw=2))
    candidate,d=nearest(r)
    state='RELEASE / TRANSIT' if a['end']<r['frame']<b['start'] else ('STABLE PASSER' if r['frame']<=a['end'] else 'RECEPTION CANDIDATE')
    ax.set_title(state,fontsize=16)
    if candidate is not None:
        q=xy[ids==candidate][0];ax.scatter(*q,s=250,facecolors='none',edgecolors='#147d68',linewidths=2,zorder=6)
    path=CLIP[:i+1];ax.plot([p['ball_data']['x'] for p in path],[p['ball_data']['y'] for p in path],c='black',lw=1.5)
    ax2=fig.add_subplot(122);times=np.array([(p['frame']-start)/10 for p in CLIP]);dist=np.array([nearest(p)[1] for p in CLIP])
    ax2.plot(times,dist,color='#147d68');ax2.axhline(2,color='#e87524',ls='--',label='2 m gate');ax2.axvline((r['frame']-start)/10,c='black');ax2.set(xlabel='Elapsed time (s)',ylabel='Nearest-player distance (m)',title='Proximity gate and stable-control segments');ax2.legend()
    fig.suptitle(f"Pass candidate · #{PLAYERS[a['player']]['number']} → #{PLAYERS[b['player']]['number']} · frame {r['frame']}",fontsize=20)
movie('event_detection',CLIP,event,subtitle='Heuristic candidate: distance ≤2 m, ball height ≤2 m, stable control ≥0.3 s · not a verified pass',repeat=2)

# Result-focused redesign assets. Keep original clips intact for pinned notebook playback.
times=np.array([(r['frame']-start)/10 for r in CLIP])
stable_owner={f:s['player'] for s in stable for f in range(s['start'],s['end']+1)}
def possession_result(fig,r,i):
    gs=fig.add_gridspec(3,2,width_ratios=[1.45,1],height_ratios=[1,1,.4])
    ax=fig.add_subplot(gs[:2,0]);pitch(ax);ids,xy,_=draw_players(ax,r,True)
    owner=stable_owner.get(r['frame'])
    if owner in ids:
        q=xy[ids==owner][0];ax.scatter(*q,s=320,facecolors='none',edgecolors='#147d68',lw=3,zorder=7)
    ax.set_title('Inferred carrier: '+(f"#{PLAYERS[owner]['number']}" if owner else 'unassigned'),fontsize=18)
    trace=fig.add_subplot(gs[:2,1]);dist=[nearest(q)[1] for q in CLIP]
    trace.plot(times,dist,c='#147d68');trace.axhline(2,c='#e87524',ls='--',label='2 m gate');trace.axvline(times[i],c='black',lw=1.5)
    trace.set(xlabel='Sequence time (s)',ylabel='Distance to closest player (m)',title='Distance explains ambiguous moments');trace.legend(fontsize=10)
    timeline=fig.add_subplot(gs[2,:]);owners=list(dict.fromkeys(stable_owner.get(q['frame']) for q in CLIP)); palette={p:plt.get_cmap('Set2')(j) for j,p in enumerate(owners)}
    for q,t in zip(CLIP,times):
        p=stable_owner.get(q['frame']);timeline.broken_barh([(t,.1)],(0,1),facecolors=palette[p] if p else '#ddd')
    for p in owners:
        if p:
            inds=[j for j,q in enumerate(CLIP) if stable_owner.get(q['frame'])==p];timeline.text(np.mean(times[inds]),.5,f"#{PLAYERS[p]['number']}",ha='center',va='center',fontsize=11)
    timeline.axvline(times[i],c='black');timeline.set(xlim=(times[0],times[-1]+.1),yticks=[],xlabel='Sequence time (s)',title='Stable possession timeline · gray = unassigned')
    fig.suptitle('Who controls the ball?',fontsize=22)
movie('possession_result',CLIP,possession_result,repeat=2,subtitle='Offline heuristic result · proximity + ball-height gate + ≥0.3 s stable control · half-speed playback')

def distance_to(r,pid):
    ids,xy,_=positions(r);return np.linalg.norm(xy[ids==pid][0]-[r['ball_data']['x'],r['ball_data']['y']])
passer_dist=np.array([distance_to(r,a['player']) for r in CLIP]);receiver_dist=np.array([distance_to(r,b['player']) for r in CLIP])
ball_speed=[]
for r in CLIP:
    prev=BYFRAME.get(r['frame']-1)
    ball_speed.append(np.linalg.norm(np.array([r['ball_data'][k]-prev['ball_data'][k] for k in ['x','y']]))/.1 if prev else np.nan)
height=np.array([r['ball_data'].get('z',np.nan) for r in CLIP],float)
release_t=(a['end']-start)/10;reception_t=(b['start']-start)/10
def pass_physics(fig,r,i):
    gs=fig.add_gridspec(3,2,width_ratios=[1.15,1.1],hspace=.45)
    ax=fig.add_subplot(gs[:,0]);pitch(ax);ids,xy,_=draw_players(ax,r,True)
    path=CLIP[:i+1];ax.plot([q['ball_data']['x'] for q in path],[q['ball_data']['y'] for q in path],c='black',lw=1.6)
    origin=[BYFRAME[a['end']]['ball_data'][k] for k in ['x','y']];dest=[BYFRAME[b['start']]['ball_data'][k] for k in ['x','y']]
    ax.annotate('',xy=dest,xytext=origin,arrowprops=dict(arrowstyle='->',color='#147d68',lw=2,ls='--'))
    state='Passer control' if r['frame']<=a['end'] else ('Ball transit' if r['frame']<b['start'] else 'Reception candidate')
    ax.set_title(f"{state} · #{PLAYERS[a['player']]['number']} → #{PLAYERS[b['player']]['number']}",fontsize=17)
    for j in range(3):
        trace=fig.add_subplot(gs[j,1]);trace.axvspan(release_t,reception_t,color='#147d68',alpha=.09)
        if j==0:
            trace.plot(times,passer_dist,label='To passer',c='#e87524');trace.plot(times,receiver_dist,label='To receiver',c='#7959b5');trace.axhline(2,c='#777',ls='--',lw=1);trace.set_ylabel('Distance (m)');trace.legend(fontsize=9,ncol=2)
        elif j==1:trace.plot(times,ball_speed,c='#147d68');trace.set_ylabel('Ball speed (m/s)');trace.set_title('Horizontal speed · diagnostic, not a fitted threshold',fontsize=10)
        else:trace.plot(times,height,c='#51645c');trace.axhline(2,c='#777',ls='--',lw=1);trace.set(ylabel='Ball height (m)',xlabel='Sequence time (s)')
        trace.axvline(release_t,c='#147d68',ls='--',lw=1);trace.axvline(reception_t,c='#7959b5',ls='--',lw=1);trace.axvline(times[i],c='black',lw=1.5);trace.set_xlim(times[0],times[-1])
        if j==0:
            trace.text(release_t,1.05,'Release',transform=trace.get_xaxis_transform(),ha='center',fontsize=10,color='#147d68');trace.text(reception_t,1.05,'Reception',transform=trace.get_xaxis_transform(),ha='center',fontsize=10,color='#7959b5')
    fig.suptitle('When does a pass occur?',fontsize=22)
movie('pass_physics',CLIP,pass_physics,repeat=2,subtitle='Actual tracking diagnostics · heuristic candidate, not verified ground truth · speed from consecutive 0.1 s intervals')

def centered(fig,r,i):
    ids,xy,teams=positions(r);mask=teams==HOME; q=xy[mask];centroid=q.mean(0)
    for k,(pts,title) in enumerate([(q,'Raw team positions'),(q-centroid,'Subtract the current team centroid')]):
        ax=fig.add_subplot(1,2,k+1);pitch(ax,centered=k==1);ax.scatter(*pts.T,c='#e87524',s=80)
        for pid,p in zip(ids[mask],pts):ax.annotate(str(PLAYERS[pid]['number']),p,xytext=(4,4),textcoords='offset points')
        ax.scatter(*(centroid if k==0 else [0,0]),marker='x',s=130,c='#147d68');ax.set_title(title,fontsize=17)
    fig.suptitle('Team movement versus relative shape',fontsize=21)
movie('formation_centering',GENERAL,centered,subtitle='Same players and frames in both panels · centering removes translation, not rotations or phase changes')

# Window-level fixed-template assignment, followed by causal persistence.
templates={}
for name,lines in {'4-4-2':[4,4,2],'4-3-3':[4,3,3],'4-2-3-1':[4,2,3,1],'3-5-2':[3,5,2]}.items():
    t=np.array([(x,y) for x,n in zip(np.linspace(-18,18,len(lines)),lines) for y in (np.linspace(-23,23,n) if n>1 else [0])]);templates[name]=t-t.mean(0)
windows=[]; current=None;candidate=None;count=0
for k in range((VALID[-1]['frame']-10)//300+1):
    samples={}
    for r in VALID:
        if (r['frame']-10)//300!=k:continue
        owner=r['possession'].get('player_id')
        if not (r['possession'].get('group')=='away team' or (owner in PLAYERS and PLAYERS[owner]['team_id']!=HOME)):continue
        ids,xy,teams=positions(r);mask=np.array([t==HOME and 'goalkeeper' not in PLAYERS[p]['player_role']['name'].lower() for p,t in zip(ids,teams)])
        if mask.sum()!=10:continue
        points=-xy[mask];points-=points.mean(0)
        for pid,q in zip(ids[mask],points):samples.setdefault(int(pid),[]).append(q)
    fits=[];points=None
    if len(samples)==10 and min(map(len,samples.values()))>=50:
        points=np.array([np.median(samples[pid],axis=0) for pid in sorted(samples)])
        for name,t in templates.items():
            costs=((points[:,None]-t[None])**2).sum(-1);rr,cc=linear_sum_assignment(costs);fits.append((np.sqrt(costs[rr,cc].mean()),name,cc))
        fits.sort();label=fits[0][1];count=count+1 if label==candidate else 1;candidate=label
        if count>=3:current=candidate
    else:label=None;candidate=None;count=0
    windows.append(dict(window=k,points=points,fits=fits,label=label,confirmed=current))
def formation(fig,r,i):
    ax=fig.add_subplot(121);pitch(ax,True);ax.set_title('Defensive-window median shape',fontsize=16)
    if r['points'] is not None:
        q=r['points'];t=templates[r['label']];costs=((q[:,None]-t[None])**2).sum(-1);rr,cc=linear_sum_assignment(costs)
        ax.scatter(*q.T,c='#e87524',s=80,label='Centered medians');ax.scatter(*t.T,marker='x',c='#147d68',s=90,label=r['label']+' slots')
        for a0,b0 in zip(rr,cc):ax.plot([q[a0,0],t[b0,0]],[q[a0,1],t[b0,1]],color='gray',alpha=.6)
        ax.legend(fontsize=10)
    else:ax.text(0,0,'Insufficient qualifying frames',ha='center',fontsize=14)
    ax2=fig.add_subplot(122);names=list(templates);ticks=np.arange(len(names))
    for key,color,offset in [('label','#e87524',0),('confirmed','#147d68',.08)]:
        vals=[names.index(w[key])+offset if w[key] is not None else np.nan for w in windows[:i+1]]
        ax2.step([w['window']*.5 for w in windows[:i+1]],vals,where='post',label='Raw candidate' if key=='label' else 'Confirmed after 3 bins',c=color,lw=2)
    ax2.set(yticks=ticks,yticklabels=names,xlim=(0,max(1,len(windows)*.5)),ylim=(-.4,3.6),xlabel='Match time (minutes)',title='Candidate versus persistent label');ax2.legend(fontsize=10)
    fig.suptitle(f"Formation-change candidates · window {r['window']*.5:.1f}–{(r['window']+1)*.5:.1f} min",fontsize=20)
first_valid=next(i for i,w in enumerate(windows) if w['points'] is not None)
def formation_offset(fig,r,i):formation(fig,r,i+first_valid)
movie('formation_candidates',windows[first_valid:],formation_offset,fps=6,repeat=3,subtitle='30-second defensive windows · fixed templates · 3-bin confirmation · missing bins reset evidence · 60× playback')

def control(fig,r,i):
    ids,xy,teams=positions(r);gx,gy=np.meshgrid(np.linspace(-52.5,52.5,80),np.linspace(-34,34,52));target=np.stack([gx,gy],axis=-1)
    dist=np.linalg.norm(target[:,:,None,:]-xy,axis=-1)
    prev=BYFRAME.get(r['frame']-1,r);pids,pxy,_=positions(prev);lookup=dict(zip(pids,pxy));v=np.array([(q-lookup.get(pid,q))*10 for pid,q in zip(ids,xy)])
    h=teams==HOME; near=teams[dist.argmin(axis=-1)]==HOME
    centers=xy+.5*v;delta=target[:,:,None,:]-centers
    angle=np.arctan2(v[:,1],v[:,0]);long=delta[:,:,:,0]*np.cos(angle)+delta[:,:,:,1]*np.sin(angle);lat=-delta[:,:,:,0]*np.sin(angle)+delta[:,:,:,1]*np.cos(angle)
    influence=np.exp(-.5*((long/7)**2+(lat/4)**2));gauss=1/(1+np.exp(-(influence[:,:,h].sum(-1)-influence[:,:,~h].sum(-1))*3))
    arrival=np.linalg.norm(target[:,:,None,:]-(xy+.7*v),axis=-1)/5+.7;score=1/(1+np.exp(np.clip((arrival[:,:,h].min(-1)-arrival[:,:,~h].min(-1))/.5,-50,50)))
    for j,(surface,title) in enumerate([(near,'Voronoi: nearest player'),(gauss,'Directional Gaussian influence'),(score,'Arrival-time score')]):
        ax=fig.add_subplot(1,3,j+1);pitch(ax);ax.imshow(surface,origin='lower',extent=[-52.5,52.5,-34,34],cmap='PuOr_r',vmin=0,vmax=1,alpha=.6);draw_players(ax,r);ax.set_title(title,fontsize=13);ax.set_xlabel('Purple: Perth · Orange: Brisbane',fontsize=10)
    fig.suptitle(f"Same frame, three spatial models · frame {r['frame']}",fontsize=21)
movie('control_comparison',GENERAL[::2],control,fps=5,subtitle='Teaching baselines · Gaussian and arrival scores are not calibrated possession probabilities')

def graph(fig,r,i):
    ax=fig.add_subplot();pitch(ax);ids,xy,teams=draw_players(ax,r,True);d=np.linalg.norm(xy[:,None]-xy[None,:],axis=-1)
    for j,k in zip(*np.where(np.triu(d<20,1))):ax.plot(xy[[j,k],0],xy[[j,k],1],color='#147d68',alpha=.35,lw=1,zorder=1)
    ax.set_title(f"Dynamic spatial graph · 20 m radius · frame {r['frame']}",fontsize=20)
movie('dynamic_graph',GENERAL,graph,subtitle='Actual moving players · edges are recomputed each frame · topology illustration, not learned attention')

# Compare the existing notebook's rule estimates with supplied provider phases.
phase_rows=[];last_team=None;seg_start=None;last_x=None;past=[];pending=None;confirmed='unknown';pending_n=0;last_frame=None
for r in VALID:
    group=r['possession'].get('group');team=HOME if group=='home team' else (META['away_team']['id'] if group=='away team' else None)
    new=team!=last_team or last_frame is None or r['frame']!=last_frame+1
    sec=(r['frame']-10)/10;attack_x=r['ball_data']['x']*(-1 if team==HOME else 1)
    if new:seg_start=sec;past=[];pending=None;pending_n=0;confirmed='unknown'
    if not new and last_x is not None:past.append((attack_x-last_x)*10)
    progress=np.mean(past[-10:]) if len(past)>=5 else np.nan
    if team is None:label='unknown'
    elif sec-seg_start<8 and progress>3:label='transition candidate'
    elif attack_x<-17.5:label='deep circulation'
    elif attack_x<17.5:label='middle progression'
    else:label='advanced possession'
    pending_n=pending_n+1 if label==pending else 1;pending=label
    if pending_n>=3:confirmed=label
    phase_rows.append(dict(frame=r['frame'],seconds=sec,team=team,phase=confirmed,provider='unlabeled'))
    last_team=team;last_x=attack_x;last_frame=r['frame']
phase_frame=pd.DataFrame(phase_rows)
for row in pd.read_csv(ROOT/'data/1925299/1925299_phases_of_play.csv').itertuples():
    mask=phase_frame.frame.between(row.frame_start,row.frame_end)&phase_frame.team.eq(row.team_in_possession_id)
    if row.period==1:phase_frame.loc[mask,'provider']=row.team_in_possession_phase_type
phase_by_frame=phase_frame.set_index('frame');candidates=phase_frame[phase_frame.phase.eq('transition candidate')&phase_frame.frame.gt(100)].frame
phase_clip=None
for f in candidates:
    lo=max(10,int(f)-60);hi=int(f)+80
    if all(k in BYFRAME for k in range(lo,hi+1)):
        phase_clip=[BYFRAME[k] for k in range(lo,hi+1,2)];break
assert phase_clip
phase_lo=phase_clip[0]['frame'];phase_hi=phase_clip[-1]['frame'];phase_sample=phase_frame[phase_frame.frame.between(phase_lo,phase_hi)]
phase_names=list(dict.fromkeys(list(phase_sample.phase)+list(phase_sample.provider)));phase_colors={label:plt.get_cmap('tab20')(i) for i,label in enumerate(phase_names)}
def phase_comparison(fig,r,i):
    gs=fig.add_gridspec(3,1,height_ratios=[3.8,1,1]);ax=fig.add_subplot(gs[0]);pitch(ax);draw_players(ax,r,True);current=phase_by_frame.loc[r['frame']]
    ax.set_title(f"Rule: {current.phase}  |  Supplied: {current.provider}",fontsize=16)
    for j,(col,title) in enumerate([('phase','Rule-based estimate'),('provider','Supplied SkillCorner phase')],1):
        trace=fig.add_subplot(gs[j]);
        for row in phase_sample.itertuples():trace.broken_barh([((row.frame-phase_lo)/10,.1)],(0,1),facecolors=phase_colors[getattr(row,col)])
        for label in dict.fromkeys(phase_sample[col]):
            indices=phase_sample[phase_sample[col].eq(label)];trace.text(((indices.frame.iloc[0]+indices.frame.iloc[-1])/2-phase_lo)/10,.5,label.replace(' ','\n'),ha='center',va='center',fontsize=9)
        trace.axvline((r['frame']-phase_lo)/10,c='black',lw=2);trace.set(xlim=(0,(phase_hi-phase_lo)/10+.1),yticks=[],title=title)
        if j==2:trace.set_xlabel('Clip time (s)')
    fig.suptitle('Where does one phase end and another begin?',fontsize=21)
movie('phase_comparison',phase_clip,phase_comparison,fps=5,subtitle='Rule estimates and provider labels use different taxonomies · disagreement is not a measured classification error')

# Two selected provider-valued runs, independently synchronized to their own run start.
events=pd.read_csv(ROOT/'data/1925299/1925299_dynamic_events.csv')
runs=events[events.event_type.eq('off_ball_run')&events.period.eq(1)&events.xthreat.notna()&events.frame_start.ge(10)&events.frame_end.lt(max(BYFRAME))].copy()
runs=runs[(runs.frame_end-runs.frame_start).between(20,100)]
runs=runs[[all(f in BYFRAME for f in range(int(row.frame_start),int(row.frame_end)+1)) for row in runs.itertuples()]]
low=runs.sort_values('xthreat').iloc[0];high=runs.sort_values('xthreat',ascending=False).iloc[0];selected_runs=[low,high]
run_length=max(int(x.frame_end-x.frame_start+1) for x in selected_runs)
def run_comparison(fig,unused,i):
    for j,row in enumerate(selected_runs):
        frame=min(int(row.frame_start)+i,int(row.frame_end));r=BYFRAME[frame];ax=fig.add_subplot(1,2,j+1);pitch(ax);ids,xy,teams=draw_players(ax,r,True);pid=int(row.player_id);q=xy[ids==pid][0];ax.scatter(*q,s=300,facecolors='none',edgecolors='#147d68',lw=3,zorder=7)
        path=[BYFRAME[f] for f in range(int(row.frame_start),frame+1)];trail=[next((p['x'],p['y']) for p in x['player_data'] if p['player_id']==pid) for x in path];trail=np.array(trail);ax.plot(*trail.T,c='#147d68',lw=2)
        ball=[r['ball_data']['x'],r['ball_data']['y']];ax.plot([ball[0],q[0]],[ball[1],q[1]],c='#147d68',ls='--',lw=1)
        carrier=r['possession'].get('player_id')
        if carrier in ids:ax.scatter(*xy[ids==carrier][0],s=180,marker='s',facecolors='none',edgecolors='black',lw=1.5,zorder=7)
        value=float(row.xthreat);ax.set_title(f"#{PLAYERS[pid]['number']} {PLAYERS[pid]['short_name']}\nSupplied run xThreat: {value:.4f}",fontsize=15);ax.text(.02,.02,f"{(frame-int(row.frame_start))/10:.1f} s into run",transform=ax.transAxes,fontsize=11)
    fig.suptitle('Two off-ball runs, different supplied threat values',fontsize=20)
movie('run_comparison',range(run_length),run_comparison,repeat=2,subtitle='Selected low/high examples, not controlled counterfactuals · dashed lane is hypothetical · shorter run freezes at its end')

# Re-encode actual held-out model predictions already rendered by notebook 16.
epv=ROOT/'assets/methods/graph_epv_real_goal.gif';dest=OUT/'graph_epv_possession.mp4'
if not only or 'graph_epv_possession' in only:
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(epv),'-an','-vf','scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0xfbfcf8,setsar=1','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)],check=True)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(dest),'-frames:v','1',str(POST/'video_graph_epv_possession.png')],check=True)
manifest.append(dict(file='assets/videos/graph_epv_possession.mp4',poster='methods/video_graph_epv_possession.png',source='Notebook 16 held-out SkillCorner match 1925299',description='Actual frozen-model ten-second scoring predictions, synchronized with real tracking; independent workshop GNN, not Bekkers weights'))
merged={}
for item in manifest:merged.setdefault(item['file'],{}).update(item)
manifest=list(merged.values())
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Saved',len(manifest),'MP4 assets',flush=True)
