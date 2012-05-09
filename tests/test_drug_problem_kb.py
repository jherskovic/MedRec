'''
Created on May 9, 2012

@author: cbearden
'''
import sys
sys.path.append('..')
import drug_problem_kb
import unittest

class TestProblemRelationData(unittest.TestCase):
    atenolol = (
        ('Essential Hypertension', 4, 0.5,),
        ('Coronary Artery Disease', 8, 0.170213,),
        ('Coronary Artery Disease', 22, 0.128655,),
        ('Coronary Artery Disease', 8, 0.128655,),
        ('Essential Hypertension', 8, 0.128655,),
    )
    naproxen = (
      ('Joint Pain, Localized In The Wrist', 4, 0.266667,),
      ('Joint Pain, Localized In The Wrist', 4, 0.200000,),
      ('Joint Pain, Localized In The Wrist', 5, 0.266667,),
      ('Joint Pain, Localized In The Ankle', 4, 0.266667,),
    )
    stenosis = (('2-vessel Coronary Artery Stenosis', 2, 0.2,),)

class TestProblemRelation(TestProblemRelationData):

    def testConstruction(self):
        """Test that DrugProblem objects constructed with certain params 
        have the expected values."""
        problem, count, ratio = self.atenolol[0]
        dp = drug_problem_kb.ProblemRelation(problem, count, ratio)
        self.assertTrue(isinstance(dp, drug_problem_kb.ProblemRelation))
        self.assertEqual(dp.name, problem)
        self.assertEqual(dp.patient_count, count)
        self.assertEqual(dp.ratio, ratio)
    
    def testEqualityTrue(self):
        """Drug/problem objects with the same problem name, patient counts,
        & ratios should be equal."""
        dp1 = drug_problem_kb.ProblemRelation(*self.stenosis[0])
        dp2 = drug_problem_kb.ProblemRelation(*self.stenosis[0])
        self.assertEqual(dp1, dp2)

    def testEqualityFalse1(self):
        """Drug/problem objects with the same problem name but different 
        patient counts & ratios should not be equal."""
        dp1 = drug_problem_kb.ProblemRelation(*self.atenolol[0])
        dp2 = drug_problem_kb.ProblemRelation(*self.atenolol[1])
        self.assertNotEqual(dp1, dp2)

    def testEqualityFalse2(self):
        """Drug/problem objects with the same problem name and patient counts 
        but different ratios should not be equal."""
        dp1 = drug_problem_kb.ProblemRelation(*self.naproxen[0])
        dp2 = drug_problem_kb.ProblemRelation(*self.naproxen[1])
        self.assertNotEqual(dp1, dp2)

    def testEqualityFalse3(self):
        """Drug/problem objects with the same problem name and ratio
        but different patient counts should not be equal."""
        dp1 = drug_problem_kb.ProblemRelation(*self.naproxen[0])
        dp2 = drug_problem_kb.ProblemRelation(*self.naproxen[2])
        self.assertNotEqual(dp1, dp2)

    def testEqualityFalse4(self):
        """Drug/problem objects with the same patient counts and ratio
        but different problem name should not be equal."""
        dp1 = drug_problem_kb.ProblemRelation(*self.naproxen[0])
        dp2 = drug_problem_kb.ProblemRelation(*self.naproxen[3])
        self.assertNotEqual(dp1, dp2)

    def testSorting(self):
        """Test ProblemRelation sorting: by ratio desc, patient_count desc, name asc"""
        atenolol1 = self.atenolol[1]
        atenolol2 = self.atenolol[2]
        atenolol3 = self.atenolol[3]
        atenolol4 = self.atenolol[4]
        # Manually sorted correctly to function as the baseline
        baseline = [
            drug_problem_kb.ProblemRelation(*atenolol1),
            drug_problem_kb.ProblemRelation(*atenolol2),
            drug_problem_kb.ProblemRelation(*atenolol3),
            drug_problem_kb.ProblemRelation(*atenolol4),
        ]
        testdata = [
            drug_problem_kb.ProblemRelation(*atenolol3),
            drug_problem_kb.ProblemRelation(*atenolol1),
            drug_problem_kb.ProblemRelation(*atenolol4),
            drug_problem_kb.ProblemRelation(*atenolol2),
        ]
        testdata.sort()
        self.assertEqual(baseline, testdata)


class TestFactory(TestProblemRelationData):
    pass

class TestDrugProblemKB(TestProblemRelationData):

    def testName(self):
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
