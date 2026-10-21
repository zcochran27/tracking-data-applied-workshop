"""Display the licensed fitted xT grid on actual supplied completed-pass endpoints."""
from pathlib import Path
import json,numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];grid=np.load(ROOT/'resources/models/open_play_xT.npy');events=pd.read_csv(ROOT/'data/1925299/1925299_dynamic_events.csv')
passes=events[events.event_type.eq('player_possession')&events.end_type.eq('pass')&events.pass_outcome.eq('successful')&events.frame_start.lt(9000)].dropna(subset=['x_end','y_end','player_targeted_x_reception','player_targeted_y_reception']).copy()
def value(x,y):
    xi=np.clip(((np.asarray(x)*106/105+53)/106*grid.shape[0]).astype(int),0,grid.shape[0]-1);yi=np.clip(((np.asarray(y)+34)/68*grid.shape[1]).astype(int),0,grid.shape[1]-1);return grid[xi,yi]
passes['start_v']=value(passes.x_end,passes.y_end);passes['end_v']=value(passes.player_targeted_x_reception,passes.player_targeted_y_reception);passes['gain']=passes.end_v-passes.start_v
selected=pd.concat([passes.nlargest(2,'gain'),passes.nsmallest(1,'gain')]).drop_duplicates('event_id')
plt.rcParams.update({'font.size':13,'axes.spines.top':False,'axes.spines.right':False})
fig,(ax,small)=plt.subplots(1,2,figsize=(14,7),gridspec_kw={'width_ratios':[3,1]},facecolor='#fbfcf8')
im=ax.imshow(grid.T,origin='lower',extent=[-52.5,52.5,-34,34],cmap='YlOrRd',aspect='equal');ax.plot([-52.5,52.5,52.5,-52.5,-52.5],[-34,-34,34,34,-34],c='#65756d');ax.plot([0,0],[-34,34],c='#65756d');ax.set(xlabel='Attack-normalized x (m)',ylabel='y (m)',title='Fitted location value and completed-pass xT gain');fig.colorbar(im,ax=ax,shrink=.6,label='External fitted xT')
rows=[]
for i,r in enumerate(selected.itertuples()):
    start=[r.x_end,r.y_end];end=[r.player_targeted_x_reception,r.player_targeted_y_reception];color='#147d68' if r.gain>=0 else '#7959b5';ax.annotate('',xy=end,xytext=start,arrowprops=dict(arrowstyle='->',lw=2.5,color=color));ax.text(end[0],end[1]+3,f'{r.gain:+.3f}',color=color,weight='bold',fontsize=13,bbox={'facecolor':'white','alpha':.8,'edgecolor':'none'});rows.append({'event_id':int(r.event_id),'gain':float(r.gain),'start':start,'end':end})
history=[np.zeros(2)];reward=np.array([0.,.5]);transition=np.array([[0.,.5],[0.,0.]])
for _ in range(4):history.append(reward+transition@history[-1])
small.plot(np.array(history),'o-',lw=2);small.set(xlabel='Update iteration',ylabel='Toy state value',title='Fitting illustration');small.legend(['State 0','State 1'],fontsize=10);small.text(.05,.1,'Reward +\nfuture movement value',transform=small.transAxes,fontsize=12)
fig.text(.5,.02,'Main: externally fitted DataBallPy grid + supplied successful-pass endpoints · inset: synthetic two-state notebook example',ha='center',fontsize=10);fig.tight_layout(rect=(0,.05,1,1));fig.savefig(ROOT/'assets/results/xt_result.png',dpi=140);plt.close(fig)
(ROOT/'assets/results/xt_result_provenance.json').write_text(json.dumps({'model':'resources/models/open_play_xT.npy','coordinates':'Attack-normalized SkillCorner event endpoints, pitch x scaled 105 to 106 m for lookup','actions':rows,'selection':'Two largest positive and one largest negative gain in bounded sample; illustrative, not a passing-skill ranking'},indent=2)+'\n')
print('Rendered xT result with',len(rows),'supplied completed passes')
