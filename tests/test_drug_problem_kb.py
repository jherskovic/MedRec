'''
Created on May 9, 2012

@author: cbearden
'''
import sys
sys.path.append('..')
from collections import defaultdict
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
    dpkbData = (
      dict(
        cuis = ('C0983887', 'C0004147'),
        drugName = 'Atenolol 100 MG Oral Tablet',
        probName = 'Coronary Artery Disease',
        patientCount = 8,
        ratio = 0.170213,
      ),
      dict(
        cuis = ('C0983889',),
        drugName = 'Atenolol 50 MG Oral Tablet',
        probName = 'Coronary Artery Disease',
        patientCount = 22,
        ratio = 0.128655,
      ),
      dict(
        cuis = ('C0983889', 'C0004147'),
        drugName = 'Atenolol 50 MG Oral Tablet',
        probName = 'Essential Hypertension',
        patientCount = 90,
        ratio = 0.545455,
      ),
      dict(
        cuis = ('C0027396', 'C1346834',),
        drugName = 'Naproxen 500 MG Oral Tablet',
        probName = 'Joint Pain, Localized In The Wrist',
        patientCount = 4,
        ratio = 0.266667,
      ),
      dict(
        cuis = ('C0065374',),
        drugName = 'Lisinopril 40 MG Oral Tablet',
        probName = '2-vessel Coronary Artery Stenosis',
        patientCount = 2,
        ratio = 0.2,
      ),
      dict(
        cuis = ('C0724633',),
        drugName = 'Metoprolol Succinate 50 MG Oral Tablet Extended Release 24 Hour',
        probName = '2-vessel Coronary Artery Stenosis',
        patientCount = 2,
        ratio = 0.2,
      ),
    )


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

    def testConstruction(self):
        """Test that each of our bits of test data can be initialized as a
        ProblemRelation instance."""
        for tpl in self.atenolol + self.naproxen + self.stenosis:
            pr = drug_problem_kb.problem_relation_factory(*tpl)
            self.assertTrue(isinstance(pr, drug_problem_kb.ProblemRelation))

    def testIdentity(self):
        """Test that the factory constructs only one ProblemRelation instance 
        for each particular tuple of of data."""
        pr1 = drug_problem_kb.problem_relation_factory(*self.stenosis[0])
        pr2 = drug_problem_kb.problem_relation_factory(*self.stenosis[0])
        self.assertTrue(pr1 is pr2)


class TestDrugProblemKB(TestProblemRelationData):

    def testLookup(self):
        """Test that a DrugProblemKB instance returns the expected problem 
        lists in the expected order, given a CUI."""
        fields = ('probName', 'patientCount', 'ratio')
        # Manually created & sorted lists of expected problems for the 
        # given CUIs from our test data
        C0983887 = [drug_problem_kb.problem_relation_factory(*map(self.dpkbData[0].get, fields))]
        C0004147 = [drug_problem_kb.problem_relation_factory(*map(self.dpkbData[2].get, fields)),
                    drug_problem_kb.problem_relation_factory(*map(self.dpkbData[0].get, fields)),]
        C0065374 = [drug_problem_kb.problem_relation_factory(*map(self.dpkbData[4].get, fields))]
        dpdict = defaultdict(set)
        fields = ('probName', 'patientCount', 'ratio')
        for dp in self.dpkbData:
            pr = drug_problem_kb.problem_relation_factory(*map(dp.get, fields))
            for cui in dp['cuis']:
                dpdict[cui].add(pr)
        dpkb = drug_problem_kb.DrugProblemKB(dpdict)
        self.assertEqual(dpkb.problem_by_drug_cui('C0983887'), C0983887)
        self.assertEqual(dpkb.problem_by_drug_cui('C0004147'), C0004147)
        self.assertEqual(dpkb.problem_by_drug_cui('C0065374'), C0065374)


loader = unittest.TestLoader()
allTestsSuite = unittest.TestSuite()
allTestsSuite.addTests(loader.loadTestsFromTestCase(TestProblemRelation))
allTestsSuite.addTests(loader.loadTestsFromTestCase(TestFactory))
allTestsSuite.addTests(loader.loadTestsFromTestCase(TestDrugProblemKB))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
