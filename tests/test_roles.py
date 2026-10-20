import unittest
import numpy as np
import pandas as pd
from role_methods import fit_formation, formation_templates, viewpoint_counts, persistent_labels

class RoleMethodsTests(unittest.TestCase):
    def test_assignment_translation_and_permutation(self):
        shape=formation_templates()['4-3-3']
        result=fit_formation(shape[::-1]+[50,-20])[0]
        self.assertEqual(result['formation'],'4-3-3')
        self.assertAlmostEqual(result['rms_m'],0)

    def test_viewpoint_translation_and_attack_rotation(self):
        nodes=pd.DataFrame({'player_id':['a','b','c'],'team_id':[1,1,2],'x':[0,10,-10],'y':[0,0,0]})
        first=viewpoint_counts(nodes,'a')
        changed=nodes.copy();changed[['x','y']]=-nodes[['x','y']]+[20,30]
        pd.testing.assert_frame_equal(first,viewpoint_counts(changed,'a',attack_sign=-1))
        self.assertEqual(first.loc[first.angle.eq(0),'teammates'].iloc[0],1)

    def test_persistence_no_backfill_and_gap_reset(self):
        self.assertEqual(persistent_labels(['a','a',None,'a','a','a','b','b','b']),[None,None,None,None,None,'a','a','a','b'])

if __name__=='__main__':unittest.main()
