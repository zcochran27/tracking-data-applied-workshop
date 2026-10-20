import unittest
import numpy as np
import pandas as pd
from analysis_tools import temporal_features,temporal_edges,xt_value,xt_grid

class TemporalTests(unittest.TestCase):
    def sample(self):
        n=24
        return pd.DataFrame({'player_id':['a']*n,'team_id':1802,'period_id':1,'frame_id':np.arange(n),'x':np.arange(n)*.1,'y':0.,'vx':1.,'vy':0.,'speed_kmh':np.arange(n,dtype=float)})
    def test_lags_mask_gap(self):
        m=self.sample();f=temporal_features(m,m.frame_id)
        self.assertEqual(f.loc[10,'speed_change_1s'],10)
        m=m[m.frame_id.ne(7)];f=temporal_features(m,m.frame_id)
        self.assertTrue(f.loc[f.frame_id.eq(12),'speed_kmh_lag10'].isna().all())
    def test_identity_edges_forward_and_contiguous(self):
        m=self.sample();m=m[m.frame_id.ne(7)]
        e=temporal_edges(m,m.frame_id)
        t=e[e.edge_type.eq('temporal')]
        self.assertTrue((t.target_frame-t.source_frame).eq(1).all())
        self.assertTrue(t.source.eq(t.target).all())
    def test_xt_lookup_orientation(self):
        g=xt_grid()
        self.assertEqual(float(xt_value(-53,-34)),float(g[0,0]))
        self.assertEqual(float(xt_value(53,34)),float(g[-1,-1]))

if __name__=='__main__':unittest.main()
