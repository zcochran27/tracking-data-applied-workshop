"""Render slide-only MP4 assets from cached SkillCorner data; notebooks stay standalone."""
from pathlib import Path
import json, subprocess, sys
import numpy as np
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
manifest=json.loads((OUT/'manifest.json').read_text()) if only and (OUT/'manifest.json').exists() else []

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

# Re-encode actual held-out model predictions already rendered by notebook 16.
epv=ROOT/'assets/methods/graph_epv_real_goal.gif';dest=OUT/'graph_epv_possession.mp4'
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(epv),'-an','-vf','scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0xfbfcf8,setsar=1','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)],check=True)
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(dest),'-frames:v','1',str(POST/'video_graph_epv_possession.png')],check=True)
manifest.append(dict(file='assets/videos/graph_epv_possession.mp4',poster='methods/video_graph_epv_possession.png',source='Notebook 16 held-out SkillCorner match 1925299',description='Actual frozen-model ten-second scoring predictions, synchronized with real tracking; independent workshop GNN, not Bekkers weights'))
manifest=list({x['file']:x for x in manifest}.values())
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Saved',len(manifest),'MP4 assets',flush=True)
