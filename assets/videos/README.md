# Slide videos

These H.264 MP4 files are embedded directly in the PowerPoint deck. In PowerPoint slideshow view, click the movie to play. Each movie retains a still poster image when stopped. The standalone files below provide an alternative way to view the clips.

These are visualizations computed from actual SkillCorner tracking data and model outputs, not broadcast footage. Raw tracking downloads are excluded from Git. SkillCorner/PySport source attribution and license are retained in the repository.

| Video | Interpretation |
|---|---|
| [Tracking playback](tracking_playback.mp4) | Real player and ball motion at native 10 Hz; 15 seconds. |
| [Event detection](event_detection.mp4) | Heuristic pass candidate, proximity gate and release/transit/reception; half-speed playback. Not a verified pass label. |
| [Formation centering](formation_centering.mp4) | Same players before and after subtracting their current team centroid; native-rate playback. |
| [Formation candidates](formation_candidates.mp4) | Fixed-template matching on 30-second defensive windows, three-bin confirmation and missing-data gaps; 60× playback. Not validated tactical changes or elastic EFPI. |
| [Control comparison](control_comparison.mp4) | Same moving frame under Voronoi, directional Gaussian and simplified arrival-time scores; 5 Hz, real-time playback. Scores are not calibrated probabilities. |
| [Dynamic graph](dynamic_graph.mp4) | Player-only 20 m radius graph recomputed from real tracking; native 10 Hz. Not learned attention. |
| [Graph EPV possession](graph_epv_possession.mp4) | Actual notebook-16 frozen-model predictions on an unseen match, synchronized with tracking. Independent workshop GNN, not provider EPV or Bekkers' weights. |

`manifest.json` records clip provenance and poster paths. Rebuild with `python scripts/render_slide_videos.py` after caching the SkillCorner sample and generating notebook 16's GIF. Requires ffmpeg on PATH. Method notebooks remain self-contained.
