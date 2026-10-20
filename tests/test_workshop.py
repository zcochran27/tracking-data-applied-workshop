import unittest
import numpy as np
import pandas as pd
from workshop import movement,physical_summary,efforts,surfaces,graph_edges

class PhysicalTests(unittest.TestCase):
    def fixture(self):
        n=100
        return pd.DataFrame({'player_id':'p','team_id':1802,'name':'Test','period_id':1,'frame_id':np.arange(n),'seconds':np.arange(n)/10,'x':np.arange(n)*.5,'y':0.})
    def test_constant_velocity_and_gap(self):
        g=self.fixture();g.loc[45:55,['x','y']]=np.nan
        m=movement(g)
        self.assertTrue(np.allclose(m.speed_kmh.dropna(),18,atol=.2))
        self.assertTrue(m.loc[45:55,'speed_kmh'].isna().all())
        s=physical_summary(m).iloc[0]
        self.assertAlmostEqual(s.distance_m,s.valid_seconds*5,delta=1)
    def test_effort_duration_and_gap(self):
        g=self.fixture();g['speed_kmh']=30
        self.assertEqual(len(efforts(g)),1)
        g.loc[50,'speed_kmh']=np.nan
        self.assertEqual(len(efforts(g)),2)
    def test_control_bounds_and_symmetry(self):
        g=pd.DataFrame({'x':[-10,10],'y':[0,0],'vx':[0,0],'vy':[0,0],'team_id':[1802,871],'player_id':['a','b']})
        _,_,maps=surfaces(g,(0,0))
        for a in maps.values():self.assertTrue(np.all((a>=0)&(a<=1)))
        self.assertAlmostEqual(maps['Gaussian influence'].mean(),.5,places=8)
        self.assertEqual(len(graph_edges(g,25)),2)
        self.assertEqual(len(graph_edges(g,15)),0)

if __name__=='__main__':unittest.main()
