"""Draw the actual broadcast footprint and player detection flags for slide 4."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from matplotlib.lines import Line2D
from matplotlib.path import Path as PlotPath

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/1925299'
meta=json.loads((DATA/'1925299_match.json').read_text(encoding='utf-8'))
frame=next(json.loads(s) for s in (DATA/'1925299_tracking_extrapolated.jsonl').open() if json.loads(s)['frame']==163)
corners=frame['image_corners_projection']
polygon=np.array([(corners['x_'+k],corners['y_'+k]) for k in ['top_left','bottom_left','bottom_right','top_right']])
players=frame['player_data'];xy=np.array([[p['x'],p['y']] for p in players])
inside=PlotPath(polygon).contains_points(xy)
detected=np.array([p['is_detected'] is True for p in players])
assert inside.sum()==11 and detected.sum()==11 and np.array_equal(inside,detected)
lookup={p['id']:p for p in meta['players']};colors={meta['home_team']['id']:'#e87524',meta['away_team']['id']:'#7959b5'}
fig,ax=plt.subplots(figsize=(12.8,7.2),dpi=150,facecolor='#fbfcf8')
ax.set_facecolor('#fbfcf8')
field=Rectangle((-52.5,-34),105,68,facecolor='#e2e6e3',edgecolor='#536a5e',lw=1.3,zorder=0);ax.add_patch(field)
coverage=Polygon(polygon,closed=True,facecolor='#b6dfd1',edgecolor='none',alpha=.8,zorder=1);coverage.set_clip_path(field);ax.add_patch(coverage)
ax.add_patch(Polygon(polygon,closed=True,fill=False,edgecolor='#147d68',lw=2.5,zorder=3))
ax.scatter(*polygon.T,marker='s',c='#147d68',s=40,zorder=5)
ax.plot([0,0],[-34,34],color='#536a5e',lw=1);ax.add_patch(Circle((0,0),9.15,fill=False,edgecolor='#536a5e',lw=1))
for x in [-52.5,36]:ax.add_patch(Rectangle((x,-20.16),16.5,40.32,fill=False,edgecolor='#536a5e',lw=1))
for p,q,det in zip(players,xy,detected):
    color=colors[lookup[p['player_id']]['team_id']]
    ax.scatter(*q,s=115,facecolors=color if det else '#fbfcf8',edgecolors='white' if det else color,linewidths=1.8,zorder=6)
ball=frame['ball_data'];ax.scatter(ball['x'],ball['y'],c='black',marker='*',s=110,zorder=7)
ax.text(-17,28,'In camera\nfootprint',ha='center',fontsize=12,color='#147d68',weight='bold')
ax.text(34,24,'Outside camera\ncoverage',ha='center',fontsize=12,color='#607066')
ax.set(xlim=(-65,65),ylim=(-43,45),aspect='equal',xlabel='x (m)',ylabel='y (m)')
ax.spines[['top','right']].set_visible(False)
ax.set_title('Broadcast camera footprint · real SkillCorner frame 163',fontsize=17,pad=12)
legend=[Polygon([[0,0],[1,0],[1,1]],facecolor='#b6dfd1',edgecolor='#147d68',label='Projected camera coverage'),
        Line2D([],[],marker='o',ls='',markerfacecolor='#52665e',markeredgecolor='white',markersize=9,label='Filled: detected (11)'),
        Line2D([],[],marker='o',ls='',markerfacecolor='white',markeredgecolor='#52665e',markersize=9,label='Hollow: extrapolated (11)')]
fig.legend(handles=legend,loc='lower center',bbox_to_anchor=(.5,.045),ncol=3,frameon=False,fontsize=11)
fig.text(.5,.025,'Green boundary: image_corners_projection  |  Player marker style: is_detected',ha='center',fontsize=10,color='#43594f')
fig.text(.5,.005,'Orange: Brisbane · Purple: Perth · Camera footprint and detection status are separate fields.',ha='center',fontsize=9,color='#43594f')
fig.subplots_adjust(left=.07,right=.98,top=.9,bottom=.2)
fig.savefig(ROOT/'assets/methods/quality.png',facecolor=fig.get_facecolor());plt.close(fig)
print('Frame 163: 11 players inside/detected; 11 outside/extrapolated. Marker states read directly from is_detected.')
