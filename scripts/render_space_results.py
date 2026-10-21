"""Published accessible-space outputs for slides; notebook proxies remain separate."""
from pathlib import Path
import ast,io,contextlib,json,subprocess
import nbformat,numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import accessible_space
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/results';OUT.mkdir(exist_ok=True)
n=nbformat.read(ROOT/'notebooks/methods/06_physical_metrics.ipynb',as_version=4);ns={}
with contextlib.redirect_stdout(io.StringIO()):
    for c in [c for c in n.cells if c.cell_type=='code'][:3]:exec(c.source,ns)
for c in n.cells:
    if c.cell_type!='code':continue
    for node in ast.parse(c.source).body:
        if isinstance(node,ast.FunctionDef) and node.name in ['smooth_coordinates','differentiate_coordinates','derive_motion']:
            exec(ast.get_source_segment(c.source,node),ns)
ns['gaussian_filter1d']=gaussian_filter1d
motion=ns['derive_motion'](ns['tracking']);wide=ns['wide'];meta=ns['metadata']
motion.to_pickle(ROOT/'.build/slide_motion.pkl');wide.to_pickle(ROOT/'.build/slide_wide.pkl')
valid=motion.dropna(subset=['vx','vy']).groupby('frame_id').size();complete=set(valid[valid.eq(22)].index)
eligible=wide[wide.frame_id.isin(complete)&wide.ball_owning_team_id.notna()&wide.frame_id.gt(1000)]
owner_by_frame=motion.groupby('frame_id').player_in_possession.first()
eligible=eligible[eligible.frame_id.map(owner_by_frame).isin(set(motion.player_id))]
eligible=eligible[(eligible.ball_x*np.where(eligible.ball_owning_team_id.eq(1802),-1,1)).between(10,35)&eligible.ball_y.abs().lt(15)]
first=next(int(f) for f in eligible.frame_id if all(f+2*j in complete for j in range(24)))
selected=[first+2*j for j in range(24)];td=motion[motion.frame_id.isin(selected)].copy()
direction={1802:-1,871:1};td['attacking_direction']=td.team_in_possession.map(direction)
ball=wide[wide.frame_id.isin(selected)][['frame_id','period_id','ball_x','ball_y','ball_owning_team_id']].copy();ball.columns=['frame_id','period_id','x','y','team_in_possession'];ball['player_id']='ball';ball['team_id']=None;ball['vx']=0.;ball['vy']=0.;ball['attacking_direction']=ball.team_in_possession.map(direction);ball['player_in_possession']=ball.frame_id.map(td.groupby('frame_id').player_in_possession.first());td=pd.concat([td,ball],ignore_index=True)
das=accessible_space.get_dangerous_accessible_space(td,period_col='period_id',attacking_direction_col='attacking_direction',player_in_possession_col='player_in_possession',infer_attacking_direction=False,n_angles=30,n_v0=8,radial_gridsize=3,use_progress_bar=False,additional_fields_to_return=['attack_poss_density'])
def picture(result,index,title):
    fig,ax=plt.subplots(figsize=(13,7));ns['pitch'](ax);plt.sca(ax);accessible_space.plot_expected_completion_surface(result,frame_index=index,plot_gridpoints=False);f=selected[index];nodes=td[td.frame_id.eq(f)&td.player_id.ne('ball')]
    for team,col in [(1802,'#e87524'),(871,'#7959b5')]:
        q=nodes[nodes.team_id.eq(team)];ax.scatter(q.x,q.y,c=col,s=45,edgecolors='white',zorder=5)
    ax.set_title(title,fontsize=19);return fig,ax
for result,key,title in [(das.simulation_result,'accessible','Published-model accessible-space surface'),(das.dangerous_result,'dangerous','Published-model dangerous accessible-space surface')]:
    fig,ax=picture(result,0,title);fig.text(.5,.02,'Actual accessible-space 2.0.13 inference on SkillCorner · not the notebook area-integral proxy',ha='center',fontsize=11);fig.tight_layout(rect=(0,.045,1,1));fig.savefig(OUT/(key+'.png'),dpi=140);plt.close(fig)
f=first;frame=wide[wide.frame_id.eq(f)].iloc[0];team=int(frame.ball_owning_team_id);passer=td[td.frame_id.eq(f)&td.team_id.eq(team)].player_in_possession.iloc[0]
gx,gy=np.meshgrid(np.linspace(-50,50,26),np.linspace(-32,32,18));options=pd.DataFrame({'frame_id':f,'player_id':passer,'team_id':team,'x':frame.ball_x,'y':frame.ball_y,'x_target':gx.ravel(),'y_target':gy.ravel()})
xc=accessible_space.get_expected_pass_completion(options,td,tracking_period_col='period_id',tracking_attacking_direction_col='attacking_direction',infer_attacking_direction=False,respect_offside=True,use_progress_bar=False)
fig=plt.figure(figsize=(14,7));gs=fig.add_gridspec(1,3,width_ratios=[1,1,.85]);ax=fig.add_subplot(gs[:,:2]);ns['pitch'](ax);im=ax.imshow(np.asarray(xc.xc).reshape(gx.shape),origin='lower',extent=[-50,50,-32,32],cmap='viridis',vmin=0,vmax=1,alpha=.8);fig.colorbar(im,ax=ax,shrink=.65,label='Published-model expected completion')
nodes=td[td.frame_id.eq(f)&td.player_id.ne('ball')];ax.scatter(nodes.x,nodes.y,c=np.where(nodes.team_id.eq(team),'#e87524','#7959b5'),edgecolors='white',s=55);ax.scatter(frame.ball_x,frame.ball_y,c='black',marker='*',s=120);ax.set_title('Hypothetical target completion map')
# Small independently parameterized survival example: explicitly a different teaching model.
target=nodes[nodes.team_id.eq(team)&nodes.player_id.ne(passer)].iloc[-1];u=np.linspace(0,1,30);path=np.array([frame.ball_x,frame.ball_y])[None,:]+u[:,None]*(np.array([target.x,target.y])-np.array([frame.ball_x,frame.ball_y]))
ball_t=np.linalg.norm(path-path[0],axis=1)/12;opponents=nodes[nodes.team_id.ne(team)];arrival=np.linalg.norm(path[:,None,:]-opponents[['x','y']].to_numpy()[None,:,:],axis=-1)/5+.7;hazard=(1/(1+np.exp(np.clip((arrival-ball_t[:,None])/.3,-50,50)))).sum(1);survival=np.exp(-np.cumsum(hazard)*max(ball_t[-1],.1)/len(u));small=fig.add_subplot(gs[:,2]);small.plot(u,survival,c='#e87524',lw=2);small.set(xlabel='Fraction along one pass',ylabel='No-interception score',ylim=(0,1),title='Teaching survival proxy');fig.text(.5,.02,'Main map: published implementation · inset: independent uncalibrated teaching example · offside respected in main map',ha='center',fontsize=10);fig.tight_layout(rect=(0,.05,1,1));fig.savefig(OUT/'completion.png',dpi=140);plt.close(fig)
# Actual model surfaces over the same moving frames.
dest=ROOT/'assets/videos/dangerous_space_result.mp4';proc=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','5','-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)],stdin=subprocess.PIPE)
as_values=[];das_values=[]
for i,f in enumerate(selected):
    mask=td.frame_id.eq(f);as_values.append(float(np.asarray(das.acc_space)[mask][0]));das_values.append(float(np.asarray(das.das)[mask][0]))
for i,f in enumerate(selected):
    fig=plt.figure(figsize=(12.8,7.2),dpi=100,facecolor='#fbfcf8');gs=fig.add_gridspec(2,2,height_ratios=[3,1])
    for j,(result,title) in enumerate([(das.simulation_result,'Accessible space'),(das.dangerous_result,'Danger-weighted accessible space')]):
        ax=fig.add_subplot(gs[0,j]);ns['pitch'](ax);plt.sca(ax);accessible_space.plot_expected_completion_surface(result,frame_index=i,plot_gridpoints=False);nodes=td[td.frame_id.eq(f)&td.player_id.ne('ball')];ax.scatter(nodes.x,nodes.y,s=20,c=np.where(nodes.team_id.eq(1802),'#e87524','#7959b5'),edgecolors='white');ax.set_title(title,fontsize=15)
    for j,(values,title) in enumerate([(as_values,'AS (m²)'),(das_values,'DAS (danger-weighted m²)')]):
        ax=fig.add_subplot(gs[1,j]);t=np.arange(len(selected))*.2;ax.plot(t,values,c='#147d68' if j==0 else '#e87524');ax.axvline(t[i],c='black');ax.set(xlabel='Clip time (s)',ylabel=title)
    fig.suptitle('How does useful space change as players move?',fontsize=20);fig.text(.5,.015,'Actual published-model output on real tracking · separate units/scales · changes do not establish causal player credit',ha='center',fontsize=10);fig.tight_layout(rect=(0,.035,1,.94));fig.canvas.draw();rgb=np.asarray(fig.canvas.buffer_rgba())[:,:,:3].copy()
    if i==0:plt.imsave(ROOT/'assets/methods/video_dangerous_space_result.png',rgb)
    proc.stdin.write(rgb.tobytes());plt.close(fig)
proc.stdin.close();assert proc.wait()==0
(OUT/'space_result_provenance.json').write_text(json.dumps({'package':'accessible-space','version':'2.0.13','match':1925299,'frames':selected,'completion_frame':first,'passer':str(passer),'as_m2':as_values,'das_danger_weighted_m2':das_values,'note':'Published-model outputs; independent notebook proxies are not the same calculation'},indent=2)+'\n')
print('Rendered published completion, AS/DAS surfaces and moving-space video',flush=True)
