"""Independent teaching implementations, inspired by Pleuler and template matching.

These fixed templates are not EFPI's elastic optimization or a trained role model.
"""
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment


def center_positions(rows):
    result = rows.copy()
    result[['cx', 'cy']] = rows[['x', 'y']].to_numpy() - rows.groupby(
        ['period_id', 'frame_id', 'team_id'])[['x', 'y']].transform('mean').to_numpy()
    return result


def viewpoint_counts(nodes, player_id, bins=24, fov_degrees=90, attack_sign=1):
    """Geometric counts in overlapping angular windows, not measured vision.

    Rotate both coordinates by 180 degrees for attack-left teams. Angle zero is
    upfield, positive pi/2 is left. No distance cutoff or occlusion is modeled.
    Opponent counts extend Pleuler's teammate-count idea.
    """
    p = nodes.loc[nodes.player_id.eq(str(player_id))].iloc[0]
    other = nodes.loc[~nodes.player_id.eq(str(player_id))].dropna(subset=['x', 'y'])
    delta = attack_sign * (other[['x', 'y']].to_numpy() - p[['x', 'y']].to_numpy(dtype=float))
    angles = np.arctan2(delta[:, 1], delta[:, 0])
    headings = np.linspace(-np.pi, np.pi, bins, endpoint=False)
    separation = np.angle(np.exp(1j * (angles[:, None] - headings)))
    visible = np.abs(separation) <= np.deg2rad(fov_degrees / 2) + 1e-12
    same = other.team_id.eq(p.team_id).to_numpy()
    return pd.DataFrame({'angle': headings, 'teammates': visible[same].sum(axis=0),
                         'opponents': visible[~same].sum(axis=0)})


def formation_templates():
    # Outfield only, attack right. Width and depth are teaching parameters.
    result = {}
    for label, lines in {'4-4-2': [4, 4, 2], '4-3-3': [4, 3, 3],
                         '4-2-3-1': [4, 2, 3, 1], '3-5-2': [3, 5, 2]}.items():
        points = [(x, y) for x, n in zip(np.linspace(-18, 18, len(lines)), lines)
                  for y in (np.linspace(-23, 23, n) if n > 1 else [0])]
        a = np.asarray(points); result[label] = a - a.mean(axis=0)
    return result


def fit_formation(points):
    """Minimum one-to-one squared-distance assignment; costs are not probabilities."""
    points = np.asarray(points, dtype=float)
    if points.shape != (10, 2) or not np.isfinite(points).all():
        raise ValueError('Requires ten finite outfield positions')
    centered = points - points.mean(axis=0)
    fits = []
    for label, template in formation_templates().items():
        cost = ((centered[:, None] - template[None]) ** 2).sum(axis=2)
        rows, cols = linear_sum_assignment(cost)
        fits.append(dict(formation=label, rms_m=float(np.sqrt(cost[rows, cols].mean())),
                         assignment=cols, template=template))
    return sorted(fits, key=lambda f: f['rms_m'])


def persistent_labels(labels, confirmations=3):
    """Confirm a candidate after N consecutive windows, with no future backfill."""
    current = None; candidate = None; count = 0; result = []
    for label in labels:
        if label is None:
            candidate = None; count = 0
        else:
            count = count + 1 if label == candidate else 1
            candidate = label
            if count >= confirmations: current = candidate
        result.append(current)
    return result
