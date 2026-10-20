"""Generate method-specific figures from the cached SkillCorner match.

No learned outputs are invented: research-model diagrams are labeled schematics.
"""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse,FancyArrowPatch
from scipy.special import expit
from workshop import *
from analysis_tools import *

plt.rcParams.update({'font.size':13,'axes.titlesize':16,'axes.spines.top':False,'axes.spines.right':False})
_,wide,long,meta,events,phases,raw=load_data();motion=movement(long)
frames=choose_sequence(motion,wide);frame=int(frames[50]);nodes=motion[motion.frame_id.eq(frame)].dropna(subset=['x','y','vx','vy'])
out=ROOT/'assets/methods';out.mkdir(exist_ok=True);manifest={}
def save(name,description):
    plt.tight_layout();plt.savefig(out/(name+'.png'),dpi=150,bbox_inches='tight',facecolor='white');plt.close()
    manifest[name]={'description':description,'match_id':1925299,'kind':'derived from tracking / supplied events unless labeled schematic'}
    print(name,flush=True)
def caption(ax,s):ax.text(.01,-.14,s,transform=ax.transAxes,fontsize=10,color='#56665e')
def chart(title):
    fig,ax=plt.subplots(figsize=(10,6));ax.set_title(title);return fig,ax
def context(title):
    fig,ax=plt.subplots(figsize=(10,6.5));frame_plot(motion,wide,frame,ax);ax.set_title(title);return fig,ax
def flow(name,title,labels,detail,context_frame=None,context_label='Real tracking input'):
    # Tracking-derived context on the left; model structure on the right.
    fig=plt.figure(figsize=(11,6));ax=fig.add_axes([.04,.2,.44,.68]);frame_plot(motion,wide,frame if context_frame is None else context_frame,ax);ax.set_title(context_label,fontsize=13)
    ax=fig.add_axes([.53,.12,.44,.78]);ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
    ys=np.linspace(.85,.18,len(labels))
    for i,(y,label) in enumerate(zip(ys,labels)):
        ax.text(.5,y,label,ha='center',va='center',fontsize=15,bbox=dict(boxstyle='round,pad=.65',facecolor='#dfede6',edgecolor='#147d68'))
        if i:ax.annotate('',xy=(.5,y+.065),xytext=(.5,ys[i-1]-.065),arrowprops=dict(arrowstyle='->',lw=2,color='#147d68'))
    fig.suptitle(title,fontsize=18);fig.text(.52,.04,'Architecture schematic • no trained predictions',fontsize=11,color='#56665e')
    save(name,detail)

# Data foundations: each visual exposes a concrete representation.
fig,ax=context('Positions, identities and the ball');save('coordinates','One real tracking frame in native metric coordinates')
fig,ax=chart('A tracking frame becomes a table');ax.axis('off')
table=nodes[['player_id','team_id','x','y','vx','vy']].head(7).round(2)
t=ax.table(cellText=table.values,colLabels=table.columns,loc='center',cellLoc='center');t.auto_set_font_size(False);t.set_fontsize(13);t.scale(1,2.1)
save('loading','Kloppy-derived rows and movement features')
fig,ax=context('Observed and extrapolated player locations')
for detected,sub in nodes.groupby('is_detected'):
    ax.scatter(sub.x,sub.y,s=180,facecolors='none',edgecolors='black' if detected else '#db403b',lw=2,label='Detected' if detected else 'Extrapolated')
ax.legend(fontsize=10);save('quality','Raw is_detected flags for selected frame')
fig,axs=plt.subplots(1,3,figsize=(13,4.8))
for ax,f in zip(axs,[int(frames[0]),frame,int(frames[-1])]):frame_plot(motion,wide,f,ax);ax.set_title(f'Frame {f}')
save('animation','Three real snapshots from the embedded animation')

# Event detection uses observable cues, with provider possession available for comparison.
nearest=nearest_possession(motion,wide);win=nearest[nearest.frame_id.between(150,280)]
fig,(ax,bx)=plt.subplots(2,1,figsize=(10,6),sharex=True)
ax.plot(win.frame_id,win.ball_distance,color='#147d68');ax.axhline(2,ls='--',color='#e87524',label='2 m candidate zone');ax.set(ylabel='Nearest distance (m)',title='Possession candidates from player–ball proximity');ax.legend()
labels=sorted(set(win.candidate));mapping={p:i for i,p in enumerate(labels)}
bx.step(win.frame_id,win.candidate.map(mapping),where='post');bx.set(yticks=list(mapping.values()),yticklabels=list(mapping),xlabel='Frame',ylabel='Candidate ID')
save('possession','Nearest-player possession heuristic: candidate zones and unassigned frames')
fig,ax=chart('Candidate pass: player → ball travel → another player')
ball=wide[wide.frame_id.between(170,230)].dropna(subset=['ball_x','ball_y'])
pitch(ax);ax.plot(ball.ball_x,ball.ball_y,'k.-',lw=2,ms=3,label='Ball trajectory')
for f in [186,202,211,226]:
    r=wide.iloc[(wide.frame_id-f).abs().argmin()];ax.annotate(str(int(r.frame_id)),(r.ball_x,r.ball_y),xytext=(5,8),textcoords='offset points')
ax.legend();caption(ax,'Supplied possession endpoints shown; proximity switches alone are not validated passes.')
save('pass_detection','Real ball trajectory around supplied possession changes; event detection cues')

# Formation and phases remain separate methods.
keepers={str(p['id']) for p in meta['players'] if 'goalkeeper' in p['player_role']['name'].lower()}
outfield=motion[~motion.player_id.isin(keepers)]
shape=centered_shape(outfield)
fig,axs=plt.subplots(1,2,figsize=(11,6))
for ax,ip,label in zip(axs,[True,False],['In possession','Out of possession']):
    sh=centered_shape(outfield,in_possession=ip)
    ax.scatter(sh.x,sh.y,s=180,c='#e87524');
    for r in sh.itertuples():ax.annotate(r.player_id,(r.x,r.y),xytext=(4,4),textcoords='offset points',fontsize=9)
    ax.axhline(0,color='gray',lw=.5);ax.axvline(0,color='gray',lw=.5);ax.set(xlim=(-30,30),ylim=(-35,35),title=label,xlabel='Relative longitudinal position (m)',ylabel='Relative lateral position (m)')
fig.suptitle('Team-centred outfield role locations',fontsize=18);save('formation','Median team-centred positions split by possession, not a named formation prediction')
sh=line_clusters(shape);fig,ax=chart('Exploratory line detection from longitudinal positions')
ax.scatter(sh.x,sh.y,c=sh.line,cmap='Set2',s=230)
for k,s in sh.groupby('line'):
    ax.axvline(s.x.mean(),ls='--',alpha=.6);ax.text(s.x.mean(),32,f'{len(s)} players',ha='center',fontsize=11)
ax.set(xlabel='Relative x (m)',ylabel='Relative y (m)',ylim=(-35,35));caption(ax,'Ward clustering into 3 lines: illustrative choice, not an automatic 4–3–3 label.')
save('role_lines','Hierarchical clustering of real outfield positions into illustrative longitudinal lines')
fig,ax=chart('Supplied phases segment the tracking timeline')
ps=phases[(phases.period.eq(1)) & phases.frame_start.lt(9000)]
names=list(ps.team_in_possession_phase_type.dropna().unique());palette=plt.cm.Set2(np.linspace(0,1,len(names)))
for k,name in enumerate(names):
    for p in ps[ps.team_in_possession_phase_type.eq(name)].itertuples():ax.broken_barh([(p.frame_start/10,(min(p.frame_end,9000)-p.frame_start)/10)],(k-.35,.7),facecolors=palette[k])
ax.set(yticks=range(len(names)),yticklabels=names,xlabel='Source frame / 10 (s)',title='Provider labels • not a phase classifier trained here')
save('phases','SkillCorner supplied phase intervals within the cached source range')

# Physical calculations are individually illustrated.
summary=physical_summary(motion);pid=summary.iloc[0].player_id;g=motion[motion.player_id.eq(pid)].sort_values('frame_id')
fig,ax=chart('Speed from successive tracking positions')
ax.plot(g.seconds,g.raw_speed_kmh,alpha=.3,label='Raw derivative');ax.plot(g.seconds,g.speed_kmh,label='Smoothed estimate');ax.set(xlabel='Time (s)',ylabel='Speed (km/h)');ax.legend();save('speed','Real player raw and smoothed speed')
fig,ax=chart('Distance accumulates over valid tracking intervals')
ax.plot(g.seconds,(g.speed_kmh/3.6*.1).cumsum(),color='#147d68');ax.set(xlabel='Time (s)',ylabel='Cumulative estimated distance (m)');caption(ax,'Missing intervals excluded; line joins do not imply measured movement through gaps.');save('distance','Integral of real estimated speed over valid 0.1 second intervals')
fig,ax=chart('High-speed and sprint distance by player')
top=summary.head(8).sort_values('hsr_m');ax.barh(top.name,top.hsr_m,color='#e87524',label='20–25 km/h');ax.barh(top.name,top.sprint_m,left=top.hsr_m,color='#7761be',label='25+ km/h');ax.set(xlabel='Estimated distance (m)');ax.legend();save('zones','Real sample distances split using documented men’s speed bands')
best=None
for p,s in motion.groupby('player_id'):
    s=s.sort_values('frame_id');detected=efforts(s)
    if not detected.empty:
        chosen=detected.sort_values('peak_kmh',ascending=False).iloc[0]
        midpoint=(chosen.start+chosen.end)/2
        f=int(s.loc[(s.seconds-midpoint).abs().idxmin(),'frame_id']);best=(p,f);break
p,f=best;eff=motion[motion.player_id.eq(p)].sort_values('frame_id');local=eff[eff.frame_id.between(f-80,f+60)]
fig,ax=chart('Sprint efforts require an explicit duration rule');ax.plot(local.seconds,local.speed_kmh,color='#147d68');ax.axhline(25,ls='--',color='#7761be')
for r in efforts(eff).itertuples():
    if local.seconds.min()<=r.start<=local.seconds.max():ax.axvspan(r.start,r.end,alpha=.25,color='#7761be')
ax.set(xlabel='Time (s)',ylabel='Speed (km/h)');caption(ax,'Shading: >=25 km/h for >=1 s, no merging; our teaching rule.');save('efforts','Real threshold crossing and illustrative duration-based sprint segmentation')
valid=eff[['frame_id','seconds','speed_kmh']].dropna();groups=valid.frame_id.diff().ne(1).cumsum();valid['a']=np.nan
for _,s in valid.groupby(groups):
    if len(s)>3:valid.loc[s.index,'a']=np.gradient(s.speed_kmh.to_numpy()/3.6,s.seconds)
z=valid[valid.frame_id.between(f-80,f+60)]
fig,ax=chart('Acceleration and deceleration from scalar speed');ax.plot(z.seconds,z.a,color='#147d68');ax.axhline(0,color='gray');ax.axhline(3,ls='--',color='#e87524');ax.axhline(-3,ls='--',color='#7761be');ax.set(xlabel='Time (s)',ylabel='Signed acceleration (m/s²)');save('acceleration','Signed speed derivative, distinct from acceleration-vector magnitude')
for threshold,name in [(20,'time_hsr'),(25,'time_sprint')]:
    candidate=None
    for p,s in motion.groupby('player_id'):
        s=s.sort_values('frame_id').reset_index(drop=True)
        crosses=s.speed_kmh.ge(threshold) & s.speed_kmh.shift().lt(threshold)
        for end in np.flatnonzero(crosses.to_numpy()):
            start=max(0,end-100);w=s.iloc[start:end+1];below=w[w.speed_kmh.lt(9)]
            if below.empty:continue
            j=below.index[-1];w=s.loc[j:end]
            if len(w)>2 and w.speed_kmh.notna().all() and w.frame_id.diff().dropna().eq(1).all():
                if candidate is None or len(w)<len(candidate):candidate=w
    assert candidate is not None,f'No real threshold crossing for {threshold}'
    fig,ax=chart('Time to HSR' if threshold==20 else 'Time to sprint')
    t=candidate.seconds-candidate.seconds.iloc[0];ax.plot(t,candidate.speed_kmh,'o-',ms=3,color='#147d68');ax.axhline(9,ls='--',color='gray');ax.axhline(threshold,ls='--',color='#e87524')
    ax.annotate(f'{t.iloc[-1]:.1f} s threshold interval',xy=(t.iloc[-1]/2,threshold-2),ha='center');ax.set(xlabel='Seconds since selected <9 km/h start',ylabel='Speed (km/h)')
    caption(ax,'Real crossing; not a qualified production explosive-acceleration result.');save(name,'Real speed threshold interval; qualification and filtering explicitly not reproduced')
fig,ax=chart('Frame-speed samples differ from activity-speed samples')
s=g.speed_kmh.dropna();ax.hist(s,bins=35,color='#147d68',alpha=.75)
ax.set(xlabel='Speed (km/h)',ylabel='Valid tracking frames');ax.text(.02,.85,'PSV-99 uses an activity population >15 km/h.\nThis frame histogram does not reproduce it.',transform=ax.transAxes,fontsize=13,bbox=dict(facecolor='white',alpha=.9))
save('peak','Real frame-speed distribution; no false reconstruction of official activity-level PSV-99')
fig,ax=chart('Peak-speed estimation depends on valid tracking')
ax.plot(g.seconds,g.speed_kmh,color='#147d68',alpha=.5,label='Estimated frame speed')
ax.plot(g.seconds,g.speed_kmh.cummax(),color='#e87524',lw=2,label='Running sample maximum')
ax.set(xlabel='Time (s)',ylabel='Speed (km/h)');ax.legend();caption(ax,'Our sample maximum is not SkillCorner’s validated production Peak Velocity.')
save('peak_velocity','Real sample-speed maximum over time, explicitly not official production Peak Velocity')

# Easier value models precede graphs.
fig,ax=context('Shot-quality features at a hypothetical ball location');b=wide[wide.frame_id.eq(frame)].iloc[0];goal=-52.5
for gy in [-3.66,3.66]:ax.plot([b.ball_x,goal],[b.ball_y,gy],'k--',lw=2)
ax.plot([b.ball_x,goal],[b.ball_y,0],color='#e87524',lw=2);caption(ax,'Distance, goal angle and player context; no trained xG probability shown.');save('xg','Hypothetical shot geometry using real ball and player positions')
grid=xt_grid();fig,ax=chart('Expected Threat: location value from a fitted model');pitch(ax);im=ax.imshow(grid.T,origin='lower',extent=(-52.5,52.5,-34,34),cmap='YlOrRd',alpha=.8,aspect='auto');fig.colorbar(im,ax=ax,label='DataBallPy open-play xT');ax.set_title('DataBallPy fitted grid • attacking right');save('xt','Actual fitted DataBallPy open-play xT grid, rescaled from 106 to 105 m for display')
fig,ax=chart('xT endpoint difference on a tracked ball segment');pitch(ax);ax.imshow(grid.T,origin='lower',extent=(-52.5,52.5,-34,34),cmap='YlOrRd',alpha=.55,aspect='auto')
# Apply grid to observed ball endpoints, rotate home attack left to right.
start=wide[wide.frame_id.eq(int(frames[20]))].iloc[0];end=wide[wide.frame_id.eq(int(frames[80]))].iloc[0]
xy1=np.array([-start.ball_x,-start.ball_y]);xy2=np.array([-end.ball_x,-end.ball_y]);v1=float(xt_value(xy1[0]*106/105,xy1[1]));v2=float(xt_value(xy2[0]*106/105,xy2[1]));ax.annotate('',xy=xy2,xytext=xy1,arrowprops=dict(arrowstyle='->',lw=3,color='black'))
ax.text(.02,.96,f'V(end) − V(start) = {v2:.4f} − {v1:.4f} = {v2-v1:+.4f}',transform=ax.transAxes,va='top',bbox=dict(facecolor='white',alpha=.9));caption(ax,'Observed ball displacement, not an asserted completed pass or causal player credit.');save('xt_gain','Fitted xT lookup on real normalized ball endpoints')
for model,name in [('Voronoi','voronoi'),('Gaussian influence','gaussian'),('Arrival-time baseline','arrival')]:
    fig,ax=plt.subplots(figsize=(10,6.5));control_plot(motion,wide,frame,model,ax);save(name,model+' on a real common frame; see methodology assumptions')
fig,ax=context('A Gaussian influence model follows movement')
r=nodes.sort_values('speed_kmh',ascending=False).iloc[0];angle=np.degrees(np.arctan2(r.vy,r.vx));ax.add_patch(Ellipse((r.x+.5*r.vx,r.y+.5*r.vy),width=18,height=8,angle=angle,facecolor='#e87524',alpha=.3,edgecolor='black'))
ax.quiver(r.x,r.y,r.vx,r.vy,angles='xy',scale_units='xy',scale=1,color='black');save('individual_gaussian','Directional influence ellipse anchored to a real moving player')
flow('physics','Ball-aware interception models',['Choose a pass destination','Ball travel + player arrival','Integrate competing control rates'],'Schematic of Spearman-style model stages with real tracking context')

# Public pass simulator and supplied threat values.
import accessible_space
selected=[int(frames[20]),frame,int(frames[80])];td=das_input(motion,wide,selected)
das=accessible_space.get_dangerous_accessible_space(td,period_col='period_id',attacking_direction_col='attacking_direction',player_in_possession_col='player_in_possession',infer_attacking_direction=False,n_angles=30,n_v0=8,radial_gridsize=3,use_progress_bar=False,additional_fields_to_return=['attack_poss_density'])
for result,name,title in [(das.simulation_result,'accessible','Accessible space'),(das.dangerous_result,'dangerous','Dangerous accessible space')]:
    fig,ax=context(title+' from simulated passes');plt.sca(ax);accessible_space.plot_expected_completion_surface(result,frame_index=1,plot_gridpoints=False);save(name,'Actual public accessible-space model output on the selected real frame')
fig,ax=chart('Accessible space and dangerous space change over time');ax.plot(selected,[das.acc_space[td.frame_id.eq(f)].iloc[0] if isinstance(das.acc_space,pd.Series) else np.asarray(das.acc_space)[td.frame_id.eq(f)][0] for f in selected],'o-',label='AS (m²)')
ax.set(xlabel='Frame',ylabel='AS (m²)');bx=ax.twinx();bx.plot(selected,[np.asarray(das.das)[td.frame_id.eq(f)][0] for f in selected],'s-',color='#e87524',label='DAS');bx.set_ylabel('DAS (danger-weighted m²)');save('das_change','Actual AS and DAS values on three frames with separate unit axes')
poss=int(start.ball_owning_team_id);receivers=nodes[nodes.team_id.eq(poss)].copy();passer=receivers.player_in_possession.iloc[0];targets=receivers[receivers.player_id.ne(passer)].head(5)
options=pd.DataFrame({'frame_id':frame,'player_id':passer,'team_id':poss,'x':b.ball_x,'y':b.ball_y,'x_target':targets.x.to_numpy(),'y_target':targets.y.to_numpy()})
xc=accessible_space.get_expected_pass_completion(options,td,event_frame_col='frame_id',event_player_col='player_id',event_team_col='team_id',event_start_x_col='x',event_start_y_col='y',event_end_x_col='x_target',event_end_y_col='y_target',tracking_period_col='period_id',use_progress_bar=False)
fig,ax=context('Expected completion for hypothetical pass targets')
for r,v in zip(options.itertuples(),xc.xc):
    ax.annotate('',xy=(r.x_target,r.y_target),xytext=(r.x,r.y),arrowprops=dict(arrowstyle='->',color=plt.cm.viridis(v),lw=2));ax.text(r.x_target,r.y_target+2,f'{v:.2f}',fontsize=11)
save('completion','Actual public model xC inference on hypothetical passes to real teammates')
re=events[events.event_type.eq('off_ball_run') & events.frame_start.lt(9000)].dropna(subset=['xthreat']).sort_values('xthreat',ascending=False).head(7)
fig,ax=chart('Supplied SkillCorner run threat');ax.barh(re.player_name+' • f'+re.frame_start.astype(str),re.xthreat,color='#147d68');ax.invert_yaxis();ax.set(xlabel='Provider xthreat',title='Supplied off-ball run threat • individual events');save('run_threat','Supplied SkillCorner xthreat values for real off-ball runs, not reconstructed predictions')

# Graphs and time: every method has an explicit diagram or measured feature plot.
fig,ax=context('A spatial interaction graph');edges=graph_edges(nodes)
for e in edges.itertuples():
    if e.source>e.target:continue
    a=nodes[nodes.player_id.eq(e.source)].iloc[0];z=nodes[nodes.player_id.eq(e.target)].iloc[0];ax.plot([a.x,z.x],[a.y,z.y],color='gray',alpha=.4)
save('graph','15 m radius graph from actual player coordinates')
fig,ax=chart('Node and edge features are measurable inputs');ax.axis('off');table=edges[['source','target','distance','dx','dy','same_team']].head(6).round(2);t=ax.table(cellText=table.values,colLabels=table.columns,loc='center',cellLoc='center');t.auto_set_font_size(False);t.set_fontsize(12);t.scale(1,2.2);save('edge_features','Real graph edge attributes')
flow('message','Message passing learns relational context',['Player + neighbour + edge','Shared message function','Aggregate → update player'],'GNN message-passing architecture schematic with actual tracking context')
tf=temporal_features(motion,frames);selected_pid=nodes.sort_values('speed_kmh',ascending=False).iloc[0].player_id;z=tf[tf.player_id.eq(selected_pid)]
fig,(ax,bx)=plt.subplots(2,1,figsize=(10,6),sharex=True);ax.plot(z.seconds,z.speed_kmh,label='Current speed');ax.plot(z.seconds,z.speed_kmh_lag10,label='Speed 1 s earlier');ax.legend();ax.set(ylabel='km/h',title='Historical node features track change');bx.plot(z.seconds,z.speed_change_1s,color='#e87524');bx.axhline(0,color='gray');bx.set(xlabel='Time (s)',ylabel='Δ speed over 1 s');save('temporal_features','Causal lagged features from real contiguous player trajectories')
fig,axs=plt.subplots(1,3,figsize=(13,5))
for ax,f in zip(axs,[int(frames[0]),frame,int(frames[-1])]):
    frame_plot(motion,wide,f,ax);ax.set_title(f't = {(f-frames[0])/10:.1f} s')
    snapshot=motion[motion.frame_id.eq(f)].dropna(subset=['x','y'])
    for edge in graph_edges(snapshot).itertuples():
        if edge.source>edge.target:continue
        source=snapshot[snapshot.player_id.eq(edge.source)].iloc[0];target=snapshot[snapshot.player_id.eq(edge.target)].iloc[0]
        ax.plot([source.x,target.x],[source.y,target.y],color='gray',alpha=.35,lw=.8)
    z=motion[motion.player_id.eq(selected_pid)&motion.frame_id.between(frames[0],f)];ax.plot(z.x,z.y,'k-',lw=2)
fig.suptitle('Same identities, changing positions and spatial edges',fontsize=17);save('dynamic_graph','Actual tracking snapshots and a player trail illustrate time-varying graphs')
fig,ax=chart('Temporal identity edges connect graph snapshots');ax.axis('off');ax.set(xlim=(-.4,2.6),ylim=(-.8,3.1))
ids=list(nodes.player_id.iloc[:3])
for ti in range(3):
    for j,p in enumerate(ids):
        ax.scatter(ti,j,s=1800,color=COLORS[int(nodes[nodes.player_id.eq(p)].team_id.iloc[0])]);ax.text(ti,j,p,ha='center',va='center',fontsize=9,color='white')
        if ti<2:ax.annotate('',xy=(ti+.8,j),xytext=(ti+.2,j),arrowprops=dict(arrowstyle='->',lw=2,color='#147d68'))
    ax.plot([ti,ti],[0,2],color='gray',alpha=.4,zorder=0);ax.text(ti,-.5,['t−2','t−1','t'][ti],ha='center',fontsize=16)
caption(ax,'Schematic layout with real player IDs • temporal arrows point forward only.');save('temporal_edges','Spatial links within time and identity links across time; schematic topology')
flow('temporal_model','A temporal graph model combines space and history',['Frame GNN embeddings','GRU / causal temporal attention','Future outcome or trajectory'],'Temporal GNN architecture alternatives; no trained output or future leakage')
flow('gru','Recurrent temporal graph modeling',['Frame GNN embeddings','GRU hidden-state update','Predict from the latest hidden state'],'Recurrent GNN architecture schematic; no trained predictions')
flow('tcn','Temporal convolution over graph embeddings',['Historical frame embeddings','Causal temporal convolution','Window-level prediction'],'Temporal convolution architecture schematic; no trained predictions')
flow('attention','Causal attention over graph history',['Historical graph embeddings + time','Masked attention to earlier states','Context-dependent prediction'],'Temporal attention architecture schematic; no trained predictions')
flow('spatiotemporal','Joint spatial and temporal message passing',['Player nodes at multiple times','Spatial + forward identity edges','Spatiotemporal node updates'],'Spatiotemporal message-passing schematic, distinct from frame encoders followed by sequence models')
flow('soccermap','SoccerMap learns spatial probability surfaces',['Tracking → spatial channels','Convolutional network','Pass selection / success surface'],'SoccerMap architecture schematic, not an implemented pretrained prediction')
flow('epv','EPV combines selection, outcomes and value',['P(action | state)','Success + failure branches','Expected value after action'],'EPV decomposition with turnover branches; architecture schematic')
ep=events[events.frame_start.lt(9000)&events.event_type.eq('player_possession')].dropna(subset=['pass_epv_delta_for']).head(30)
fig,ax=chart('Supplied pass value changes through a sequence');ax.bar(ep.frame_start,ep.pass_epv_delta_for,width=10,color=np.where(ep.pass_epv_delta_for.ge(0),'#147d68','#e87524'));ax.axhline(0,color='gray');ax.set(xlabel='Source frame',ylabel='Provider pass_epv_delta_for');caption(ax,'Supplied SkillCorner field; not predictions from our own EPV model.');save('provider_epv','Actual supplied pass EPV change values')
flow('defcon','DEFCON evaluates defensive contribution',['Graph-based action components','Opponent EPV before / after','Defensive contribution accounting'],'DEFCON conceptual pipeline; not a reproduced defensive-credit model')
flow('counterattack','U.S. Soccer models counterattack success',['SkillCorner + event context','Graph classification','Predict defined success outcome'],'Counterattack project architecture; not model inference from published weights')
corner=events[events.frame_start.lt(9000)&events.start_type.eq('corner_reception')].iloc[0]
corner_frame=int(wide.iloc[(wide.frame_id-corner.frame_start).abs().argmin()].frame_id)
flow('tacticai','TacticAI models corner-kick interactions',['Corner-specific graph','Receiver / shot predictions','Generate positional alternatives'],'TacticAI architecture schematic with real corner-reception context, not trained predictions',context_frame=corner_frame,context_label='Real corner-reception context')
flow('forecast','Trajectory forecasting models future movement',['Historical tracking graphs','Conditional sequence model','Multiple possible future trajectories'],'Generative forecasting schematic; no invented future tracks presented as predictions')
fig,ax=chart('Neighboring frames are not independent test examples');ax.axis('off')
for i,(label,color) in enumerate([('Match A: training','#147d68'),('Match B: validation','#e87524'),('Match C: test','#7761be')]):
    ax.broken_barh([(0,10)],(i,.6),facecolors=color);ax.text(.2,i+.3,label,color='white',va='center',fontsize=17)
ax.set(xlim=(0,10),ylim=(-.2,3));save('validation','Schematic match-level data split, not measured validation performance')
(ROOT/'resources/visual_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Generated',len(manifest),'method figures')
