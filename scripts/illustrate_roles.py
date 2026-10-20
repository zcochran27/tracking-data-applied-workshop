"""Real SkillCorner position distributions, angular features and formation baseline."""
import sys, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Wedge
from workshop import load_data, pitch, choose_sequence, movement
from role_methods import *

plt.rcParams.update({'font.size':12,'axes.titlesize':15})
_,wide,long,meta,events,phases,raw=load_data()
keepers={str(p['id']) for p in meta['players'] if 'goalkeeper' in p['player_role']['name'].lower()}
roles={str(p['id']):p['player_role']['acronym'] for p in meta['players']}
out=ROOT/'assets/methods'; manifest=json.loads((ROOT/'resources/visual_manifest.json').read_text())
def save(name,description):
    plt.tight_layout();plt.savefig(out/(name+'.png'),dpi=145,bbox_inches='tight');plt.close()
    manifest[name]={'description':description,'match_id':1925299,'kind':'Independent teaching implementation / real tracking'}
    print(name,flush=True)

team=long[long.team_id.eq(1802)&~long.player_id.isin(keepers)].dropna(subset=['x','y']).copy()
team=center_positions(team)
fig,axs=plt.subplots(1,2,figsize=(12,5))
for ax,cols,title in zip(axs,[['x','y'],['cx','cy']],['Raw average positions','Team-centroid normalized']):
    pitch(ax);ax.set_title(title)
    for i,(pid,g) in enumerate(team.groupby('player_id')):
        a=g[cols].to_numpy();mean=a.mean(axis=0);values,vectors=np.linalg.eigh(np.cov(a.T));v=vectors[:,-1]
        ax.add_patch(Ellipse(mean,*(4*np.sqrt(values[::-1])),angle=np.degrees(np.arctan2(v[1],v[0])),fill=False,color=plt.cm.tab10(i%10),lw=1.5))
        ax.text(*mean,roles.get(pid,pid),fontsize=10,ha='center',weight='bold')
fig.suptitle('Real sample: mean and 2-standard-deviation covariance ellipses')
fig.text(.12,.01,'Metadata role labels. Ellipses describe dispersion, not a Gaussian fit or confidence interval.',fontsize=10)
save('role_distributions','Raw and centroid-normalized bivariate position distributions; metadata role labels')

motion=movement(long);frames=choose_sequence(motion,wide);f=int(frames[50]);nodes=long[long.frame_id.eq(f)].dropna(subset=['x','y'])
fig,axs=plt.subplots(1,2,figsize=(12,5))
for ax,t in zip(axs,[1802,871]):
    pitch(ax);g=nodes[nodes.team_id.eq(t)];ax.scatter(g.x,g.y,s=140,c='#ccc',edgecolors='#444');ax.set_title(f'Team {t} • frame {f}')
fig.suptitle('Guess the current roles from geometry');save('role_quiz','Unlabeled real simultaneous team snapshots')

pid=nodes[nodes.team_id.eq(1802)&~nodes.player_id.isin(keepers)].player_id.iloc[0]
p=nodes[nodes.player_id.eq(pid)].iloc[0];counts=viewpoint_counts(nodes,pid,attack_sign=-1)
fig,(ax,bx)=plt.subplots(1,2,figsize=(12,5));pitch(ax)
for t,g in nodes.groupby('team_id'):ax.scatter(g.x,g.y,c='#e87524' if t==1802 else '#7050a0',s=80)
ax.add_patch(Wedge((p.x,p.y),35,135,225,alpha=.18,color='#147d68'))
ax.scatter(p.x,p.y,s=250,facecolors='none',edgecolors='black',lw=2);ax.set_title('One 90° viewpoint, facing upfield (left)')
bx.plot(np.degrees(counts.angle),counts.teammates,label='Teammates');bx.plot(np.degrees(counts.angle),counts.opponents,label='Opponents (extension)');bx.set(xlabel='Heading relative to attack (degrees)',ylabel='Count within 90°',title='Sweep through 24 headings');bx.legend()
save('angular_view','Pleuler-inspired rotating geometric viewpoint; 24 headings / 90-degree field selected here')

features=[];ids=[]
for _,player in nodes[nodes.team_id.eq(1802)&~nodes.player_id.isin(keepers)].iterrows():
    c=viewpoint_counts(nodes,player.player_id,attack_sign=-1);features.append(c.teammates);ids.append(f'{player.player_id} ({roles[player.player_id]})')
fig,ax=plt.subplots(figsize=(10,5.5));im=ax.imshow(features,aspect='auto',cmap='YlGnBu');ax.set(yticks=range(len(ids)),yticklabels=ids,xlabel='Heading bin (24 per full turn)',title='One player–frame becomes one feature row');fig.colorbar(im,ax=ax,label='Teammate count')
save('role_features','Actual teammate-count feature matrix; role labels come from match metadata, not frame-level truth')

g=team[team.frame_id.eq(f)].sort_values('player_id');fits=fit_formation(-g[['cx','cy']].to_numpy());best=fits[0]
fig,(ax,bx)=plt.subplots(1,2,figsize=(12,5));pitch(ax);a=-g[['cx','cy']].to_numpy();b=best['template']
ax.scatter(a[:,0],a[:,1],label='Centered observations',s=75);ax.scatter(b[:,0],b[:,1],marker='x',s=90,label='Template slots')
for i,j in enumerate(best['assignment']):ax.plot([a[i,0],b[j,0]],[a[i,1],b[j,1]],c='#888',lw=1)
ax.set_title('Best candidate: '+best['formation']);ax.legend(fontsize=10)
bx.barh([z['formation'] for z in fits],[z['rms_m'] for z in fits],color='#147d68');bx.set(xlabel='Assigned RMS distance (m), lower is better',title='Compare four fixed templates')
save('formation_assignment','Attack-normalized fixed-template Hungarian assignment; no ground-truth formation claim')

records=[]
# Non-overlapping 30-second windows, same team and defensive context only.
defensive=team.merge(wide[['frame_id','ball_owning_team_id']],on='frame_id',validate='many_to_one')
defensive=defensive[defensive.ball_owning_team_id.eq(871)].copy();defensive['window']=(defensive.frame_id//300).astype(int)
for window,s in defensive.groupby('window'):
    shape=s.groupby('player_id')[['cx','cy']].median()
    if len(shape)!=10 or s.frame_id.nunique()<50:continue
    fit=fit_formation(-shape.to_numpy());records.append({'window':int(window),'minute':window*.5,'formation':fit[0]['formation'],'rms_m':fit[0]['rms_m'],'margin_m':fit[1]['rms_m']-fit[0]['rms_m']})
timeline=pd.DataFrame(records).set_index('window').reindex(range(min(r['window'] for r in records),max(r['window'] for r in records)+1))
timeline['minute']=timeline.index*.5
timeline['confirmed']=persistent_labels([v if isinstance(v,str) else None for v in timeline.formation])
timeline.to_csv(ROOT/'outputs/formation_candidates.csv',index=False)
fig,(ax,bx)=plt.subplots(2,1,figsize=(11,6),sharex=True);labels=list(formation_templates());mapping={v:i for i,v in enumerate(labels)}
ax.scatter(timeline.minute,timeline.formation.map(mapping),label='Candidate');ax.plot(timeline.minute,timeline.confirmed.map(mapping),c='#e87524',label='Confirmed after 3 available windows');ax.set(yticks=range(4),yticklabels=labels,title='Defensive-window template candidates (not verified tactical changes)');ax.legend(fontsize=10)
bx.plot(timeline.minute,timeline.rms_m,label='Best fit RMS');bx.plot(timeline.minute,timeline.margin_m,label='Runner-up margin');bx.set(xlabel='Sample time (minutes)',ylabel='Metres');bx.legend()
save('formation_changes','Real defensive-window candidates and persistence filter; no tactical ground truth; missing windows not bridged in revised code')

fig,ax=plt.subplots(figsize=(11,6));pitch(ax)
ball=wide[wide.frame_id.eq(f)].iloc[0]
for t,s in nodes.groupby('team_id'):
    a=s[['x','y']].to_numpy();color='#e87524' if t==1802 else '#7050a0'
    for i in range(len(a)):
        for j in range(i):ax.plot(a[[i,j],0],a[[i,j],1],c=color,alpha=.12,lw=.7)
    for x,y in a:ax.plot([x,ball.ball_x],[y,ball.ball_y],c='#147d68',alpha=.25,lw=.8)
    ax.scatter(a[:,0],a[:,1],c=color,s=70)
ax.scatter(ball.ball_x,ball.ball_y,c='black',s=100,marker='*');ax.set_title('UnravelSports example topology: team graphs linked through ball')
save('bekkers_graph','Real tracking coordinates with split-by-team plus ball topology; independently built, not library inference')

fig,ax=plt.subplots(figsize=(11,6));ax.axis('off')
steps=[('Tracking + events','Align frames and goal timestamps'),('One graph per frame','Nodes, edge features, global context'),('Graph encoder + readout','Learn interactions and aggregate state'),('Binary scoring head','P(possession team scores in next 10 s)')]
for i,(title,detail) in enumerate(steps):
    y=.88-i*.23;ax.text(.5,y,title,ha='center',fontsize=19,bbox=dict(boxstyle='round,pad=.5',fc='#dfede6',ec='#147d68'));ax.text(.5,y-.09,detail,ha='center',fontsize=12)
    if i<3:ax.annotate('',xy=(.5,y-.17),xytext=(.5,y-.11),arrowprops=dict(arrowstyle='->'))
ax.set_title('Joris Bekkers: GraphEPV (PyData London 2025)',fontsize=19);fig.text(.12,.01,'Schematic, no trained inference. Historical talk uses Keras/Spektral; current docs recommend PyG.',fontsize=11)
save('bekkers_epv','GraphEPV target and general graph-classification pipeline attributed to PyData London 2025')
(ROOT/'resources/visual_manifest.json').write_text(json.dumps(manifest,indent=2))
