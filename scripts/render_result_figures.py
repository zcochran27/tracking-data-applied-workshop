"""Slide figures from standalone notebook calculations; not imported by notebooks."""
from pathlib import Path
import json,io,contextlib,base64
import numpy as np
import pandas as pd
import nbformat
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from scipy.optimize import linear_sum_assignment
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/results';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':14,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#fbfcf8','savefig.facecolor':'#fbfcf8'})
def finish(fig,name,note=''):
    if note:fig.text(.5,.015,note,ha='center',fontsize=10,color='#51645c')
    fig.tight_layout(rect=(0,.045,1,.98));fig.savefig(OUT/(name+'.png'),dpi=140);plt.close(fig);print('Figure',name,flush=True)
def notebook(stem,stop=None):
    n=nbformat.read(ROOT/'notebooks/methods'/f'{stem}.ipynb',as_version=4);ns={}
    show=plt.show;plt.show=lambda:plt.close('all')
    with contextlib.redirect_stdout(io.StringIO()):
        for i,c in enumerate(n.cells):
            if stop is not None and i>stop:break
            if c.cell_type!='code' or 'embedded-mp4' in c.metadata.get('tags',[]):continue
            ns['display']=lambda *args,**kwargs:None
            # Initial imports can rebind display; no cell computations depend on its return.
            exec(c.source,ns)
    plt.show=show;return ns

n=notebook('06_physical_metrics');motion=n['motion'];summary=n['summary'];meta=n['metadata'];lookup={str(p['id']):p for p in meta['players']}
motion.to_pickle(ROOT/'.build/slide_motion.pkl');n['wide'].to_pickle(ROOT/'.build/slide_wide.pkl')
player=summary.sort_values(['effort_count','sprint_m'],ascending=False).iloc[0].player_id
g=motion[motion.player_id.eq(player)].sort_values('frame_id');work=n['interval_workload'](g);efforts=n['sprint_efforts'](g)
name=lookup[player]['short_name'];valid=work.metres.notna();valid_s=work.dt.where(valid).sum();elapsed=g.seconds.max()-g.seconds.min()
fig,ax=plt.subplots(figsize=(13,6.5));ax.plot(work.seconds/60,work.cumulative_m,c='#147d68',lw=3);ax.set(xlabel='Sample time (minutes)',ylabel='Cumulative distance (m)',title=f'{name}: {work.metres.sum():,.0f} m across {valid_s:.0f} valid seconds')
ax.text(.02,.95,f'Valid intervals: {valid_s/elapsed:.1%} of sample duration',transform=ax.transAxes,va='top');finish(fig,'distance', 'Bounded sample, not a full match · missing derivative intervals add no distance · extrapolated coordinates remain included')
fig,(ax,small)=plt.subplots(1,2,figsize=(14,6.5),gridspec_kw={'width_ratios':[2.5,1]});s=summary.sort_values('HSR_m',ascending=False).head(10).copy();labels=[lookup[p]['short_name'] for p in s.player_id]
ax.barh(labels,s.HSR_m,color='#147d68',label='HSR 20–25 km/h');ax.barh(labels,s.sprint_m,left=s.HSR_m,color='#e87524',label='Sprint ≥25 km/h');ax.invert_yaxis();ax.set(xlabel='Distance (m)',title='High-intensity distance in the same bounded sample');ax.legend(fontsize=11)
peak=g.loc[g.speed_kmh.idxmax()];win=g[g.frame_id.between(peak.frame_id-60,peak.frame_id+60)];small.plot(win.seconds,win.speed_kmh,c='#51645c');small.axhline(20,c='#147d68',ls='--');small.axhline(25,c='#e87524',ls='--');small.set(title='How intervals qualify',xlabel='Sample time (s)',ylabel='Speed (km/h)');finish(fig,'intensity','Comparisons require exposure/coverage checks · teaching convention uses [20,25) and [25,∞) km/h')
fig,ax=plt.subplots(figsize=(13,6.5));ax.plot(g.seconds/60,g.speed_kmh,color='#51645c',lw=1);ax.axhline(25,c='#e87524',ls='--',label='25 km/h threshold')
for i,r in enumerate(efforts.itertuples(),1):ax.axvspan(r.start_s/60,(r.start_s+r.duration_s)/60,color='#147d68',alpha=.3);ax.text((r.start_s+r.duration_s/2)/60,32,str(i),ha='center',fontsize=12)
ax.set(title=f'{name}: {len(efforts)} qualifying sprint efforts',xlabel='Sample time (minutes)',ylabel='Speed (km/h)');ax.legend();finish(fig,'efforts','Teaching rule: ≥25 km/h for ≥1 second, no gap merging · counts are not official SkillCorner production outputs')
fig,(ax,speedax)=plt.subplots(2,1,figsize=(13,6.5),sharex=True,gridspec_kw={'height_ratios':[2.2,1]});local=g[g.frame_id.between(peak.frame_id-100,peak.frame_id+100)]
ax.plot(local.seconds,local.accel,c='#51645c');ax.fill_between(local.seconds,0,local.accel,where=local.accel>0,color='#147d68',alpha=.3);ax.fill_between(local.seconds,0,local.accel,where=local.accel<0,color='#e87524',alpha=.3);ax.axhline(0,c='#888',lw=.8);ax.set(ylabel='Signed acceleration (m/s²)',title=f'{name}: acceleration and braking around one effort');speedax.plot(local.seconds,local.speed_kmh,c='#7959b5');speedax.set(ylabel='Speed (km/h)',xlabel='Sample time (s)');finish(fig,'acceleration','Derivative of scalar speed · signed acceleration differs from acceleration-vector magnitude · smoothing affects peaks')
for target in [20,25]:
    candidates=[]
    for pid,q in motion.groupby('player_id'):
        rising=q.accel.gt(0)&q.speed_kmh.notna();splits=(rising.ne(rising.shift(fill_value=False))|q.frame_id.diff().ne(1)|q.period_id.ne(q.period_id.shift())).cumsum()
        for _,seg in q[rising].groupby(splits[rising]):
            if len(seg)<3:continue
            t=seg.seconds.to_numpy();v=seg.speed_kmh.to_numpy();t9=n['crossing_time'](t,v,9);end=n['crossing_time'](t,v,target)
            if np.isfinite(t9+end) and end>t9:candidates.append((end-t9,pid,seg,t9,end))
    duration,pid,seg,t9,end=sorted(candidates,key=lambda x:x[0])[0]
    fig,ax=plt.subplots(figsize=(13,6.5));ax.plot(seg.seconds-t9,seg.speed_kmh,'o-',c='#147d68',lw=2);ax.axhline(9,c='#888',ls='--');ax.axhline(target,c='#e87524',ls='--');ax.axvspan(0,duration,color='#147d68',alpha=.12);ax.scatter([0,duration],[9,target],c='#e87524',s=120,zorder=5);ax.annotate(f'{duration:.2f} s',xy=(duration/2,(9+target)/2),ha='center',fontsize=24,color='#147d68');ax.set(title=f"{lookup[pid]['short_name']}: illustrative 9 → {target} km/h crossing",xlabel='Time from 9 km/h crossing (s)',ylabel='Speed (km/h)');finish(fig,'time_'+str(target),'Fastest observed monotone crossing in bounded sample · not production-qualified SkillCorner Time to HSR/Sprint')

# Formation geometry, distributions and causal candidate timeline from the same source sample.
raw=n['raw'];templates={}
for label,lines in {'4-4-2':[4,4,2],'4-3-3':[4,3,3],'4-2-3-1':[4,2,3,1],'3-5-2':[3,5,2]}.items():
    t=np.array([(x,y) for x,k in zip(np.linspace(-18,18,len(lines)),lines) for y in (np.linspace(-23,23,k) if k>1 else [0])]);templates[label]=t-t.mean(0)
team=n['tracking'];team=team[team.team_id.eq(1802)&~team.player_id.isin(n['keepers'])].dropna(subset=['x','y']).copy();team['cx']=team.x-team.groupby('frame_id').x.transform('mean');team['cy']=team.y-team.groupby('frame_id').y.transform('mean');team['window']=(team.seconds//30).astype(int)
records=[]
for window,q in team[team.team_in_possession.eq(871)].groupby('window'):
    med=q.groupby('player_id').agg(cx=('cx','median'),cy=('cy','median'),n=('frame_id','size'))
    if len(med)!=10 or med.n.min()<50:continue
    points=-med[['cx','cy']].to_numpy();fits=[]
    for label,t in templates.items():
        cost=((points[:,None]-t[None])**2).sum(2);rr,cc=linear_sum_assignment(cost);fits.append((np.sqrt(cost[rr,cc].mean()),label,cc))
    fits.sort();records.append({'window':window,'label':fits[0][1],'cost':fits[0][0],'points':points,'ids':list(med.index),'fits':fits})
chosen=min(records,key=lambda q:q['cost']);points=chosen['points'];template=templates[chosen['label']];cc=chosen['fits'][0][2]
slotroles={'4-4-2':['RB','RCB','LCB','LB','RW','RCM','LCM','LW','RCF','LCF'],'4-3-3':['RB','RCB','LCB','LB','RCM','CM','LCM','RW','CF','LW'],'4-2-3-1':['RB','RCB','LCB','LB','RDM','LDM','RW','AM','LW','CF'],'3-5-2':['RCB','CB','LCB','RWB','RCM','CM','LCM','LWB','RCF','LCF']}
fig=plt.figure(figsize=(14,7));gs=fig.add_gridspec(2,3,width_ratios=[1,1,.9],height_ratios=[1.5,1]);ax=fig.add_subplot(gs[:,0:2]);n['pitch'](ax);ax.set(xlim=(-35,35),ylim=(-35,35));ax.scatter(*points.T,s=135,c='#e87524',zorder=4)
for pid,q,slot in zip(chosen['ids'],points,cc):
    ax.annotate(f"#{lookup[pid]['number']} {slotroles[chosen['label']][slot]}",q,xytext=(5,6),textcoords='offset points',fontsize=11);ax.plot([q[0],template[slot,0]],[q[1],template[slot,1]],c='#147d68',alpha=.3)
ax.scatter(*template.T,marker='x',s=80,c='#147d68');ax.set_title('Best fixed template: '+chosen['label'],fontsize=20)
bar=fig.add_subplot(gs[0,2]);bar.barh([f[1] for f in chosen['fits']],[f[0] for f in chosen['fits']],color='#147d68');bar.invert_yaxis();bar.set(xlabel='RMS assignment error (m)',title='Competing templates',xlim=(0,max(f[0] for f in chosen['fits'])*1.15))
from PIL import Image
ellipse='methods/role_distributions.png';inset=fig.add_subplot(gs[1,2]);inset.imshow(Image.open(ROOT/'assets'/ellipse));inset.axis('off');inset.set_title('Raw → centroid-normalized',fontsize=11);finish(fig,'formation_result',f"Defensive window {chosen['window']*.5:.1f}–{(chosen['window']+1)*.5:.1f} min · role labels are assigned slots, not reviewed role truth · selected lowest-residual example")
allwindows=pd.DataFrame([{'window':r['window'],'label':r['label']} for r in records]).set_index('window').reindex(range(min(r['window'] for r in records),max(r['window'] for r in records)+1));current=None;pending=None;count=0;confirmed=[]
for label in allwindows.label:
    if not isinstance(label,str):pending=None;count=0
    else:
        count=count+1 if label==pending else 1;pending=label
        if count>=3:current=label
    confirmed.append(current)
allwindows['confirmed']=confirmed;mapping={v:i for i,v in enumerate(templates)}
fig=plt.figure(figsize=(14,7));gs=fig.add_gridspec(2,2,height_ratios=[1.7,1]);ax=fig.add_subplot(gs[0,:]);ax.scatter(allwindows.index*.5,allwindows.label.map(mapping),c='#e87524',label='Window candidate',s=40);ax.step(allwindows.index*.5,allwindows.confirmed.map(mapping),where='post',c='#147d68',lw=2.5,label='Persistence-confirmed')
for window,row in allwindows.iterrows():
    if not isinstance(row.label,str):ax.axvspan(window*.5,(window+1)*.5,color='#ddd',alpha=.5)
ax.set(yticks=list(mapping.values()),yticklabels=list(mapping),xlabel='Sample time (minutes)',title='Raw candidates versus persistent formation labels');ax.legend(loc='upper left',fontsize=11)
first=records[0];other=next((r for r in records if r['label']!=first['label']),records[-1])
for j,r in enumerate([first,other]):
    ax=fig.add_subplot(gs[1,j]);ax.scatter(*r['points'].T,c='#e87524',s=70);ax.set(xlim=(-35,35),ylim=(-30,30),aspect='equal',title=f"{r['window']*.5:.1f} min · candidate {r['label']}",xlabel='Centered x (m)',ylabel='Centered y (m)')
finish(fig,'formation_timeline','Gray windows: insufficient qualifying frames · 3 consecutive bins confirm · not verified tactical changes · no substitutions in this sample')

snap=n['snapshot'];home=snap[snap.team_id.eq(1802)].copy();home['role']=home.player_id.map({p:lookup[p]['player_role']['acronym'] for p in home.player_id});chosen_players=[]
for roles in [['RB','LB'],['LDM','RDM','CDM'],['CF','LW','RW']]:
    match=home[home.role.isin(roles)];chosen_players.append(match.iloc[0] if len(match) else home.iloc[len(chosen_players)])
fig=plt.figure(figsize=(14,7));gs=fig.add_gridspec(1,4,width_ratios=[1,1,1,.85]);angles=np.linspace(-np.pi,np.pi,24,endpoint=False)
for j,p in enumerate(chosen_players):
    delta=-(home[home.player_id.ne(p.player_id)][['x','y']].to_numpy()-p[['x','y']].to_numpy(float));bearing=np.arctan2(delta[:,1],delta[:,0]);diff=np.angle(np.exp(1j*(bearing[:,None]-angles)));counts=(abs(diff)<=np.pi/4+1e-12).sum(0);ax=fig.add_subplot(gs[0,j],projection='polar');ax.plot(np.r_[angles,angles[0]],np.r_[counts,counts[0]],c=['#147d68','#e87524','#7959b5'][j],lw=2);ax.fill(np.r_[angles,angles[0]],np.r_[counts,counts[0]],alpha=.15);ax.set(ylim=(0,10),title=f"{p.role}\n{lookup[p.player_id]['short_name']}");ax.set_xticks([0,np.pi/2,np.pi,3*np.pi/2],['Forward','Left','Back','Right']);ax.tick_params(labelsize=9)
p=chosen_players[0];ax=fig.add_subplot(gs[0,3]);delta=-(home[['x','y']].to_numpy()-p[['x','y']].to_numpy(float));ax.scatter(*delta.T,c='#e87524');ax.scatter(0,0,s=100,c='#147d68');ax.add_patch(Polygon([[0,0],[35,-35],[35,35]],facecolor='#147d68',alpha=.12));ax.set(xlim=(-40,45),ylim=(-45,45),aspect='equal',title='90° viewing sector',xlabel='Relative forward (m)',ylabel='Relative lateral (m)');finish(fig,'angular_signatures','Teammate counts at 24 headings from one actual frame · metadata roles label examples, not current-role ground truth · geometry, not measured gaze')

# Real xG predictions: same functions and same grouped folds as notebook 07, without redoing bootstrap.
x=notebook('07_expected_goals',stop=22);data=x['data'];pred=x['predictions'];names=list(pred);difference=abs(pred[names[1]]-pred[names[0]]);eligible=np.flatnonzero((difference>.08)&(difference<.18));index=int(eligible[len(eligible)//2]) if len(eligible) else int(np.argmax(difference));shot=data.iloc[index]
fig,(ax,bar)=plt.subplots(1,2,figsize=(14,7),gridspec_kw={'width_ratios':[2,1]});x['draw_pitch'](ax);ax.set(xlim=(20,63),ylim=(-27,27));defenders=np.array(shot.defender_positions);ax.add_patch(Polygon([[shot.x,shot.y],[60,-4],[60,4]],facecolor='#e87524',alpha=.13));ax.scatter(*defenders.T,c='#7959b5',s=85,label='Visible defenders');ax.scatter(shot.gk_x,shot.gk_y,c='#147d68',marker='*',s=200,label='Goalkeeper');ax.scatter(shot.x,shot.y,c='#e87524',s=130,label='Shooter');ax.legend(fontsize=10,loc='upper left');ax.set_title('Same real shot, more context');values=[pred[k][index] for k in names];bar.bar(['Location\nonly','+ GK and\ndefenders'],values,color=['#e87524','#147d68']);bar.set(ylim=(0,min(1,max(values)*1.4+.04)),ylabel='Out-of-fold scoring probability',title='Workshop model estimates')
for j,value in enumerate(values):bar.text(j,value+.01,f'{value:.1%}',ha='center',fontsize=20)
finish(fig,'xg_example',f'Match {shot.match_id} · {shot.event_id} · selected for model disagreement, not evidence of overall improvement · StatsBomb native units')
fig,ax=plt.subplots(figsize=(12,7));metrics=json.loads((ROOT/'outputs/methods/xg_model_comparison.json').read_text())
for key,color in zip(names,['#e87524','#147d68']):
    fpr,tpr,_,auc=x['curves'][key];ax.plot(fpr,tpr,c=color,lw=2.5,label=f'{key}: AUC {auc:.3f}')
ax.plot([0,1],[0,1],c='#aaa',ls='--');ax.set(xlabel='False-positive rate',ylabel='True-positive rate',title='Location-only versus goalkeeper/defender-context xG');ax.legend(loc='lower right',fontsize=14);finish(fig,'xg_roc','3,066 non-penalty shots · 287 goals · 128 matches · identical 5 match-grouped folds; scaling fitted only on training folds')
for cell in nbformat.read(ROOT/'notebooks/methods/16_graph_epv.ipynb',as_version=4).cells:
    if cell.cell_type=='code' and 'Held-out matches: precision' in cell.source:
        png=next(o.data['image/png'] for o in cell.outputs if 'image/png' in o.get('data',{}));(OUT/'graph_epv_performance.png').write_bytes(base64.b64decode(png));print('Figure graph_epv_performance')
(OUT/'result_provenance.json').write_text(json.dumps({'physical_player_id':player,'physical_name':name,'xg_example_match':int(shot.match_id),'xg_example_event':shot.event_id,'xg_example_probabilities':dict(zip(names,map(float,values))),'formation_window':int(chosen['window']),'formation_label':chosen['label'],'source':'Existing standalone notebooks and pinned cached data; slide authoring only'},indent=2)+'\n')
