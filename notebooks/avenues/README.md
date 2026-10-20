# Avenue notebooks
Each notebook starts from a fresh kernel and contains its method implementations. Only loading and pitch drawing are shared. The main walkthrough notebook is unchanged.

- [Data foundations: loading, quality and animation](00_data_foundations.ipynb)
- [Event detection from continuous tracking](01_event_detection.ipynb)
- [Formations, angular role features and change detection](02_formations_and_roles.ipynb)
- [Match segmentation and phases of play](03_match_segmentation.ipynb)
- [Physical metrics from coordinates](04_physical_metrics.ipynb)
- [Game modeling: xG, xT, control, passing and possession value](05_game_modeling.ipynb)
- [Graphs and temporal models from scratch](06_graphs_and_temporal_models.ipynb)

Training routines are implemented explicitly, with synthetic numerical checks where the partial match lacks credible outcome/role labels. These checks are marked and are not model-performance claims. Game-modeling proxies are distinct from published or provider production metrics.

Regenerate: `python scripts/build_avenue_notebooks.py`. Execute and export: `python scripts/execute_avenue_notebooks.py`.
