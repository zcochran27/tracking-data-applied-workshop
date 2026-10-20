from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import matplotlib
matplotlib.use('Agg')
from workshop import *

dataset,wide,long,meta,events,phases,raw=load_data()
motion=movement(long);frames=choose_sequence(motion,wide);frame=int(frames[50])
out=ROOT/'assets'
def save(name):
    plt.tight_layout();plt.savefig(out/name,dpi=150,bbox_inches='tight',facecolor='white');plt.close()
frame_plot(motion,wide,frame);save('frame.png')
fig,axs=plt.subplots(1,3,figsize=(16,5))
for ax,model in zip(axs,['Voronoi','Gaussian influence','Arrival-time baseline']):control_plot(motion,wide,frame,model,ax)
save('control.png')
s=physical_summary(motion);g=motion[motion.player_id.eq(s.iloc[0].player_id)]
fig,ax=plt.subplots(figsize=(10,4))
ax.plot(g.seconds,g.raw_speed_kmh,alpha=.25,label='Raw derivative');ax.plot(g.seconds,g.speed_kmh,label='Smoothed estimate')
ax.axhline(20,ls='--',color='orange',label='HSR 20');ax.axhline(25,ls='--',color='purple',label='Sprint 25')
ax.set(xlabel='Time (s)',ylabel='Speed (km/h)',title=g.name.iloc[0]);ax.legend(ncol=2);save('speed.png')
nodes=motion[motion.frame_id.eq(frame)].dropna(subset=['x','y','vx','vy'])
edges=graph_edges(nodes);ax=frame_plot(motion,wide,frame)
for e in edges.itertuples():
    if e.source>e.target:continue
    a=nodes[nodes.player_id.eq(e.source)].iloc[0];b=nodes[nodes.player_id.eq(e.target)].iloc[0]
    ax.plot([a.x,b.x],[a.y,b.y],color='gray',alpha=.4)
ax.set_title('Tracking frame as a radius graph (15 m)');save('graph.png')
(ROOT/'outputs/physical_sample.csv').write_text(s.to_csv(index=False,lineterminator='\n'),encoding='utf-8')
(ROOT/'resources/clip.json').write_text(json.dumps({'match_id':1925299,'first_frame':int(frames[0]),'last_frame':int(frames[-1]),'selection':'10 s live-ball sequence with high coordinate/velocity coverage; selected for territory, not a labeled goal event'},indent=2))
print('Figures rendered; frame',frame)
