'''
Created on Feb 28, 2012

@author: cbearden
'''
import sys
sys.path.append('..')
#print sys.path
import unittest
from constants import demo_list_1, demo_list_2
from medication import medication_parser


class TestMedParsing(unittest.TestCase):
    
    def setUp(self):
        self.medList = demo_list_1 + demo_list_2
        self.parsedMedList = [medication_parser.match(med) for med in self.medList]
        #self.medParser = medication_parser(self.medList[0])

    def testMedParse1(self):
        self.assertEqual(self.parsedMedList[0].group('name'), 'Zoloft', 'Name not parsed in 1st example')
        self.assertEqual(self.parsedMedList[0].group('dosage'), '50', 'Dosage not parsed in 1st example')
        self.assertEqual(self.parsedMedList[0].group('units'), 'MG', 'Units not parsed in 1st example')
        self.assertEqual(self.parsedMedList[0].group('formulation'), 'TABLET', 'Formulation not parsed in 1st example')
        self.assertEqual(self.parsedMedList[0].group('instructions'), 'TAKE 1 TABLET DAILY.; RPT', 'Instructions not parsed in 1st example')
        
    def testMedParse2(self):
        self.assertEqual(self.parsedMedList[1].group('name'), 'Warfarin Sodium', 'Name not parsed in 2nd example')
        self.assertEqual(self.parsedMedList[1].group('dosage'), '2.5', 'Dosage not parsed in 2nd example')
        self.assertEqual(self.parsedMedList[1].group('units'), 'MG', 'Units not parsed in 2nd example')
        self.assertEqual(self.parsedMedList[1].group('formulation'), 'Tablet', 'Formulation not parsed in 2nd example')
        self.assertEqual(self.parsedMedList[1].group('instructions'), 'TAKE AS DIRECTED.; Rx', 'Instructions not parsed in 2nd example')
        
    def _parseHorse(self, m):
        return


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
