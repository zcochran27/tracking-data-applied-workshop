"""Attributed role-identification and GraphEPV additions."""
import nbformat as nbf

def enrich_slides(slides):
    additions=[]
    def add(title,body,image,sources,notes,cue=''):
        additions.append(dict(title=title,body=body,image='methods/'+image+'.png',sources=sources,notes=notes,cue=cue))
    add('Guess the current player roles',['Inspect two real team snapshots','Distinguish assigned position from occupied role','Use relative geometry to explain your answer'],'role_quiz',['pleuler'],'Audience prompt inspired by the supplied reference. These are actual SkillCorner frames, with identities hidden. A single snapshot is ambiguous; metadata positions are not frame-level role truth.')
    add('Position distributions and centering',['Plot a mean and covariance for each player','Subtract the team centroid in every frame','Compare dispersion before assigning a formation'],'role_distributions',['pleuler','formation'],'Independently generated from SkillCorner. Two-standard-deviation covariance ellipses, not confidence regions. Labels are metadata roles. Pros: removes team translation. Cons: averaging still mixes phases and rotations; covariance can hide multimodal behavior. Use identical qualifying samples in both panels.')
    add('Pleuler: rotating player viewpoints',['Place the origin at the player','Rotate a geometric viewing sector','Count teammates at each heading'],'angular_view',['pleuler'],'Pleuler (June 2024), independently implemented. Our choices: 24 headings and overlapping 90-degree sectors. This is geometric context, not observed head orientation, actual sight or occlusion. Attack-normalize both axes. Opponent-count channel is our extension. Pros: translation-invariant and intuitive. Cons: angular resolution, orientation and missing players affect features.', 'NOTEBOOK · inspect angular count features')
    add('From angular features to role labels',['Create one feature row per player and frame','Fit a supervised role classifier on labeled matches','Retain role probabilities for uncertain states'],'role_features',['pleuler'],'Pleuler used XGBoost. This notebook manufactures features but does not train or claim accuracy from a single match. Assigned-position metadata gives weak labels during rotations. For credible evaluation use manually reviewed frame roles and held-out matches/players. Add opponent counts as a separate tested extension. Pros: flexible nonlinear classification. Cons: label noise and domain shift.')
    add('Formation prediction by assignment',['Compare centered shape with candidate templates','Match ten outfield players to ten slots','Select the lowest assignment cost'],'formation_assignment',['efpi','efpidocs'],'Teaching baseline: four fixed templates, Hungarian minimum squared-distance assignment, attack-right orientation. RMS residual is not a probability. Unlike EFPI, this implementation has no elastic template optimization. Pros: interpretable assignments and no player-order dependence. Cons: template inventory, scale and asymmetry determine results.', 'NOTEBOOK · inspect template scores and assignments')
    add('Bekkers: elastic formation identification',['Allow templates to adapt to team shape','Assign players to formation roles','Analyze comparable windows and possession states'],'formation_assignment',['efpi','efpidocs'],'EFPI is the published extension using elastic templates and linear assignment. The displayed visualization is our simpler fixed-template baseline, not an EFPI result. Follow the linked tutorial for package inference. Pros: formation and role assignment together. Cons: parameter choices, substitutions, partial tracking and tactical ambiguity. Compare output to video-reviewed labels.')
    add('Detecting formation-change candidates',['Score successive windows in the same phase','Require persistent evidence before switching','Review changes alongside substitutions and video'],'formation_changes',['pleuler','efpi'],'Plot uses real defensive-context windows with at least 50 qualifying frames. Three consecutive available 30-second bins confirm a label; missing bins reset the candidate count. Existing confirmed state is retained through missing bins, not evidence of ongoing stability. This is an educational rule, not EFPI change logic. Pleuler explicitly proposed change detection without testing it. No tactical ground truth is available here. Role swaps alone need not imply formation changes.', 'NOTEBOOK · candidate timeline and persistence')
    insertion=next(i for i,s in enumerate(slides) if s['title']=='Formation detection')
    slides[insertion:insertion]=additions
    graph=[]
    def graphadd(title,body,image,notes):
        graph.append(dict(title=title,body=body,image='methods/'+image+'.png',sources=['graphepv','unravel'],notes=notes,cue=''))
    graphadd('Bekkers: building a football graph',['Represent players and ball as nodes','Encode team, motion and relative geometry','Choose edges to suit the prediction task'],'bekkers_graph','Real SkillCorner frame with one documented UnravelSports configuration: split-by-team connections plus ball links. This is not asserted as the unique GraphEPV topology. Pros: permutation-invariant aggregation and relational features. Cons: edges determine which interactions can be learned. Current documentation recommends PyTorch Geometric; the 2025 talk used Keras/Spektral.')
    graphadd('Bekkers: GraphEPV scoring target',['One tracking frame becomes one graph','Label goals by the possession team within 10 seconds','Train a graph classifier to estimate that probability'],'bekkers_epv','PyData London, 7 June 2025. Talk uses World Cup 2022 PFF data across 64 matches, with labels respecting team and period. This is a ten-second scoring target, not automatically the complete action-decomposed Fernández EPV framework. Schematic only: no pretrained model inference here. Strength: includes off-ball context. Limitation: rare correlated labels, calibration and transfer to another competition.')
    graphadd('GraphEPV and temporal extensions',['A frame model can use velocity features','History adds runs, pressure and changing lanes','Add temporal encoders with causal inputs'],'temporal_edges','Our extension discussion, not a claim that the 2025 GraphEPV presentation trained a temporal GNN. Use the existing lagged features, GRU, TCN and attention slides as alternative temporal encoders. Keep whole matches/possessions together when splitting; account for the ten-second outcome window. Compare against location xT and non-graph models on the same target.')
    index=next(i for i,s in enumerate(slides) if s['title']=='Expected possession value')
    slides[index:index]=graph
    return slides

def enrich_notebook(cells):
    md=nbf.v4.new_markdown_cell;code=nbf.v4.new_code_cell
    extra=[md('''## Player viewpoints, roles and formation changes
[Devin Pleuler, Fixed to Fluid (2024)](https://github.com/devinpleuler/research/blob/master/frame-by-frame-position.md) motivates teammate counts around a rotating player. We independently implement 24 overlapping 90° sectors. These are geometric viewpoints, not measured gaze. Opponent counts are our extension. Rotate both axes into attack-right coordinates to preserve left/right roles. Pleuler used XGBoost; this small sample produces features, not a validated trained role model.

The fixed-template assignment below illustrates the mechanics behind formation prediction. It is **not** the elastic optimization in [Bekkers' EFPI](https://arxiv.org/abs/2506.23843). Fit costs are not probabilities. Metadata positions are weak labels during tactical rotations.'''),code('''from role_methods import center_positions, viewpoint_counts, fit_formation, persistent_labels
from IPython.display import Image
display(Image(filename=str(ROOT/'assets/methods/role_distributions.png')))
role_frame=long[long.frame_id.eq(int(frames[50]))].dropna(subset=['x','y'])
focus=role_frame[role_frame.team_id.eq(1802)].player_id.iloc[0]
counts=viewpoint_counts(role_frame,focus,attack_sign=-1)
display(counts.head())
counts.assign(degrees=np.degrees(counts.angle)).plot(x='degrees',y=['teammates','opponents'],title='Geometric count features');plt.show()
keepers={str(p['id']) for p in meta['players'] if 'goalkeeper' in p['player_role']['name'].lower()}
shape=role_frame[role_frame.team_id.eq(1802)&~role_frame.player_id.isin(keepers)]
fits=fit_formation(-shape[['x','y']].to_numpy())
display(pd.DataFrame([{'candidate':r['formation'],'RMS metres':r['rms_m']} for r in fits]))
display(Image(filename=str(ROOT/'assets/methods/formation_assignment.png')))
display(pd.read_csv(ROOT/'outputs/formation_candidates.csv').head(12))
display(Image(filename=str(ROOT/'assets/methods/formation_changes.png')))
'''),md('''### Training and validating role classification
Each row should identify match, period, frame, player, phase, angular counts and a reviewed role label. Train XGBoost or another classifier on many labeled matches and inspect per-role probabilities and confusion matrices on **held-out matches and players**. Do not use player IDs as predictors. Keep left/right orientation consistent; compare teammates-only features against the added opponent channel. Metadata role labels cannot establish whether the model correctly recognizes a real rotation.

Formation-change candidates require comparable phases, stable player coverage, sustained score improvement and video review. The plotted three-window persistence rule is ours. Pleuler proposed change detection but did not test it in the article. Missing windows reset confirmation evidence. Four fixed templates cannot represent every tactical system.

## Joris Bekkers: GraphEPV
The [PyData London 2025 talk](https://rawcdn.githack.com/UnravelSports/keynotes/main/html/20250607-PyData-London.html) uses a graph per frame and a target of a goal by the possession team within the next **10 seconds**, in the same period. Its PFF World Cup data differ from this SkillCorner sample. The talk uses Keras/Spektral; the [current UnravelSports tutorial](https://unravelsports.readthedocs.io/en/latest/tutorials/soccer_gnn.html) recommends PyTorch Geometric. We show graph construction and target design, not trained GraphEPV predictions. Temporal extensions below are additional modeling choices, not an attribution to his frame model.'''),code('''display(Image(filename=str(ROOT/'assets/methods/bekkers_graph.png')))
display(Image(filename=str(ROOT/'assets/methods/bekkers_epv.png')))
# Labels require synchronized goal events and team identities; do not substitute dummy labels.
# A credible model needs held-out matches, a baseline and probability calibration.
''')]
    index=next((i for i,c in enumerate(cells) if c.cell_type=='markdown' and 'Temporal graph features' in c.source),len(cells))
    cells[index:index]=extra
    return cells
