"""Four alternative slide-10 result visuals from the same real formation window."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,Ellipse
from scipy.optimize import linear_sum_assignment

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/formation-options';OUT.mkdir(exist_ok=True)
meta=json.loads((ROOT/'data/1925299/1925299_match.json').read_text(encoding='utf-8'));lookup={str(p['id']):p for p in meta['players']}
keepers={p for p,v in lookup.items() if 'goalkeeper' in v['player_role']['name'].lower()}
motion=pd.read_pickle(ROOT/'.build/slide_motion.pkl');team=motion[motion.team_id.eq(1802)&motion.period_id.eq(1)&~motion.player_id.isin(keepers)].dropna(subset=['x','y']).copy()
team['cx']=team.x-team.groupby('frame_id').x.transform('mean');team['cy']=team.y-team.groupby('frame_id').y.transform('mean');team['window']=(team.seconds//30).astype(int)
window=json.loads((ROOT/'assets/results/result_provenance.json').read_text())['formation_window']
sample=team[team.window.eq(window)&team.team_in_possession.eq(871)].copy();med=sample.groupby('player_id').agg(cx=('cx','median'),cy=('cy','median'),n=('frame_id','size'));assert len(med)==10 and med.n.min()>=50
points=-med[['cx','cy']].to_numpy();ids=list(med.index);templates={};line_counts={'4-4-2':[4,4,2],'4-3-3':[4,3,3],'4-2-3-1':[4,2,3,1],'3-5-2':[3,5,2]}
roles={'4-4-2':['RB','RCB','LCB','LB','RW','RCM','LCM','LW','RCF','LCF'],'4-3-3':['RB','RCB','LCB','LB','RCM','CM','LCM','RW','CF','LW'],'4-2-3-1':['RB','RCB','LCB','LB','RDM','LDM','RW','AM','LW','CF'],'3-5-2':['RCB','CB','LCB','RWB','RCM','CM','LCM','LWB','RCF','LCF']}
fits=[]
for label,lines in line_counts.items():
    t=np.array([(x,y) for x,n in zip(np.linspace(-18,18,len(lines)),lines) for y in (np.linspace(-23,23,n) if n>1 else [0])]);t-=t.mean(0);templates[label]=t
    cost=((points[:,None]-t[None])**2).sum(2);rr,cc=linear_sum_assignment(cost);fits.append({'label':label,'rms':float(np.sqrt(cost[rr,cc].mean())),'assignment':cc,'residuals':np.sqrt(cost[rr,cc])})
fits.sort(key=lambda q:q['rms']);best=fits[0];label=best['label'];t=templates[label];cc=best['assignment']
BG='#fbfcf8';INK='#183a35';GREEN='#147d68';ORANGE='#e87524'
plt.rcParams.update({'font.size':13,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':BG,'savefig.facecolor':BG})
def pitch(ax,vertical=False):
    ax.set_facecolor('#eef3ed')
    if vertical:
        ax.add_patch(Rectangle((-34,-52.5),68,105,fill=False,edgecolor='#718479'));ax.plot([-34,34],[0,0],c='#718479');ax.add_patch(Circle((0,0),9.15,fill=False,edgecolor='#718479'))
        for y in [-52.5,36]:ax.add_patch(Rectangle((-20.16,y),40.32,16.5,fill=False,edgecolor='#718479'))
        ax.set(xlim=(-36,36),ylim=(-54,54),aspect='equal');ax.axis('off')
    else:
        ax.axhline(0,c='#c5d1c9',lw=.8);ax.axvline(0,c='#c5d1c9',lw=.8);ax.set(xlim=(-35,35),ylim=(-32,32),aspect='equal',xlabel='Centered forward (m)',ylabel='Centered lateral (m)')
def save(fig,name,note):
    fig.text(.5,.018,note,ha='center',fontsize=10,color='#51645c');fig.tight_layout(rect=(0,.055,1,.96));fig.savefig(OUT/(name+'.png'),dpi=150);plt.close(fig)
def board(ax):
    pitch(ax,True);lines=line_counts[label];display_slots=np.array([(y,x) for x,n in zip(np.linspace(-31,31,len(lines)),lines) for y in (np.linspace(-24,24,n) if n>1 else [0])]);colors=plt.get_cmap('Set2')
    for j,(pid,slot) in enumerate(zip(ids,cc)):
        q=display_slots[slot];ax.scatter(*q,s=550,facecolors=GREEN,edgecolors='white',lw=2,zorder=4);ax.text(*q,str(lookup[pid]['number']),ha='center',va='center',color='white',weight='bold',fontsize=13,zorder=5);ax.text(q[0],q[1]-6,roles[label][slot],ha='center',fontsize=12,color=INK)
    ax.annotate('Attack',xy=(31,45),xytext=(31,30),arrowprops={'arrowstyle':'->','color':GREEN},ha='center',fontsize=11,color=GREEN)

# A: a familiar role board, intentionally schematic rather than raw positions.
fig=plt.figure(figsize=(14,7));gs=fig.add_gridspec(1,2,width_ratios=[1.3,1]);ax=fig.add_subplot(gs[0]);board(ax);ax.set_title('Assigned formation: '+label,fontsize=23,color=INK)
ax=fig.add_subplot(gs[1]);ax.axis('off');ax.text(.02,.85,label,fontsize=60,color=GREEN,weight='bold');ax.text(.02,.67,'Ten players assigned to ten roles',fontsize=17,color=INK);ax.text(.02,.48,f"Lowest RMS error: {best['rms']:.2f} m",fontsize=20,color=INK);ax.text(.02,.35,f"Next candidate: {fits[1]['label']} ({fits[1]['rms']:.2f} m)",fontsize=16,color='#607066');ax.text(.02,.14,'Best among four fixed templates.\nRole assignments are model estimates.',fontsize=16,color='#607066')
save(fig,'A_role_board','Schematic template-slot display, not observed player coordinates · shirt numbers reflect the actual assignment')

# B: compare every candidate on exactly the same spatial sample and axes.
fig,axs=plt.subplots(2,2,figsize=(14,7),sharex=True,sharey=True)
for ax,fit in zip(axs.flat,fits):
    pitch(ax);template=templates[fit['label']];ax.scatter(*points.T,c=ORANGE,s=65,zorder=4,label='Observed median');ax.scatter(*template.T,c=GREEN,marker='x',s=70,label='Template slot')
    for p,slot in zip(points,fit['assignment']):ax.plot([p[0],template[slot,0]],[p[1],template[slot,1]],c=GREEN,alpha=.35,lw=1)
    ax.set_title(f"{fit['label']} · RMS {fit['rms']:.2f} m"+(' · best fit' if fit is best else ''),color=GREEN if fit is best else INK,fontsize=17)
    ax.set_xlabel('');ax.set_ylabel('');ax.tick_params(labelsize=9)
axs[0,0].legend(fontsize=10,loc='lower left');save(fig,'B_template_comparison','Same centered medians and coordinate scales in every panel · lower assignment error ranks the fixed templates')

# C: show only enough normalization process to support the result.
fig=plt.figure(figsize=(14,7));gs=fig.add_gridspec(2,2,width_ratios=[1.25,1.35]);rawax=fig.add_subplot(gs[0,0]);centerax=fig.add_subplot(gs[1,0]);resultax=fig.add_subplot(gs[:,1]);palette=plt.get_cmap('tab10')
for index,(pid,g) in enumerate(sample.groupby('player_id')):
    for ax,cols in [(rawax,['x','y']),(centerax,['cx','cy'])]:
        q=-g[cols].to_numpy();mean=q.mean(0);cov=np.cov(q.T);eig,vec=np.linalg.eigh(cov);angle=np.degrees(np.arctan2(vec[1,-1],vec[0,-1]));ax.add_patch(Ellipse(mean,4*np.sqrt(max(eig[-1],0)),4*np.sqrt(max(eig[0],0)),angle=angle,fill=False,edgecolor=palette(index),lw=1.5));ax.scatter(*mean,s=20,c=[palette(index)])
rawax.set(xlim=(-55,55),ylim=(-34,34),aspect='equal',title='Raw position distributions');centerax.set(xlim=(-35,35),ylim=(-34,34),aspect='equal',title='Team-centroid normalized');board(resultax);resultax.set_title('Assigned formation: '+label,fontsize=21,color=GREEN)
save(fig,'C_normalization_and_result','Identical qualifying frames in both distribution panels · ellipses show dispersion, not confidence · board is schematic')

# D: keep the observed shape, but make model misfit visible instead of hiding it.
fig,(ax,bar)=plt.subplots(1,2,figsize=(14,7),gridspec_kw={'width_ratios':[1.6,1]});pitch(ax);res=best['residuals'];im=ax.scatter(*points.T,c=res,cmap='YlOrRd',s=150,vmin=0,vmax=max(res),edgecolors='#51645c',zorder=4);ax.scatter(*t.T,marker='x',c=GREEN,s=90,zorder=3)
labels=[]
for j,(pid,q,slot) in enumerate(zip(ids,points,cc)):
    ax.plot([q[0],t[slot,0]],[q[1],t[slot,1]],c='#82958b',lw=1.1,alpha=.7);name=f"#{lookup[pid]['number']} {roles[label][slot]}";labels.append(name);offset=(5,8 if j%2==0 else -14);ax.annotate(name,q,xytext=offset,textcoords='offset points',fontsize=10)
ax.set_title(label+' assignment: where does the template fit poorly?',fontsize=17);fig.colorbar(im,ax=ax,shrink=.7,label='Player-to-slot residual (m)');order=np.argsort(res)[::-1];bar.barh(np.array(labels)[order],res[order],color=plt.cm.YlOrRd(res[order]/max(res)));bar.invert_yaxis();bar.set(xlabel='Assignment residual (m)',title='Largest mismatches');save(fig,'D_fit_diagnostics','Residuals are geometric model error, not role confidence or a calibrated probability · lower error does not verify a formation')

current=json.loads((ROOT/'slides/content.json').read_text(encoding='utf-8'))[9];assert current['title']=='Which formation best fits this shape?'
options=[]
descriptions=[('A','Role board','A clean formation board emphasizes the assigned roles.','A_role_board'),('B','Compare templates','Four candidate shapes show why one template fits better.','B_template_comparison'),('C','Normalization + result','Distribution changes explain the assigned formation.','C_normalization_and_result'),('D','Fit diagnostics','The observed shape and residuals reveal where the template struggles.','D_fit_diagnostics')]
for letter,name,takeaway,file in descriptions:
    slide=dict(current);slide['section']=f'SLIDE 10 OPTION {letter} · {name.upper()}';slide['image']='formation-options/'+file+'.png';slide['result']=takeaway;slide['status']=f'Option {letter} · Same players and window';slide['notes']+=f' Alternative {letter}: {name}. Same team, qualifying window, four candidate templates and assignment algorithm as the main deck; only the visualization differs. Role-board coordinates are schematic where shown; residual plots use observed centered medians.';options.append(slide)
(ROOT/'slides/formation-options.json').write_text(json.dumps(options,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'provenance.json').write_text(json.dumps({'match':1925299,'window_index':int(window),'window_seconds':[window*30,(window+1)*30],'player_ids':ids,'best_template':label,'scores':[{k:v for k,v in f.items() if k in ['label','rms']} for f in fits],'main_slide_10':'Unchanged until user selects an option'},indent=2)+'\n')
print('Rendered four alternatives; main slide 10 remains unchanged.')
