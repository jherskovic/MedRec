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

parsedDemoMeds = (
  dict(
    original     = 'Zoloft 50 MG Tablet;TAKE 1 TABLET DAILY.; RPT',
    name         = 'Zoloft',
    dosage       = '50',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE 1 TABLET DAILY.; RPT',
  ),
  dict(
    original     = 'Warfarin Sodium 2.5 MG Tablet;TAKE AS DIRECTED.; Rx',
    name         = 'Warfarin Sodium',
    dosage       = '2.5',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE AS DIRECTED.; Rx',
  ),
  dict(
    original     = 'Lipitor 10 MG Tablet;TAKE 1 TABLET DAILY.; Rx',
    name         = 'Lipitor',
    dosage       = '10',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE 1 TABLET DAILY.; Rx',
  ),
  dict(
    original     = 'Protonix 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx',
    name         = 'Protonix',
    dosage       = '40',
    units        = 'MG',
    formulation  = 'Tablet Delayed Release',
    instructions = 'TAKE 1 TABLET DAILY.; Rx',
  ),
  dict(
    original     = 'Warfarin Sodium 5 MG Tablet;TAKE 1 TABLET DAILY AS DIRECTED.; Rx',
    name         = 'Warfarin Sodium',
    dosage       = '5',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE 1 TABLET DAILY AS DIRECTED.; Rx',
  ),
  dict(
    original     = 'Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx',
    name         = 'Mirapex',
    dosage       = '0.5',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE 1 TABLET 3 TIMES DAILY.; Rx',
  ),
  dict(
    original     = 'Lisinopril 5 MG Tablet;TAKE  TABLET TWICE DAILY; Rx',
    name         = 'Lisinopril',
    dosage       = '5',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE  TABLET TWICE DAILY; Rx',
  ),
  dict(
    original     = 'Coreg 25 MG Tablet;TAKE 1 TABLET TWICE DAILY,  WITH MORNING AND EVENING MEAL; RPT',
    name         = 'Coreg',
    dosage       = '25',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE 1 TABLET TWICE DAILY,  WITH MORNING AND EVENING MEAL; RPT',
  ),
  dict(
    original     = 'Pantoprazole Sodium 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx',
    name         = 'Pantoprazole Sodium',
    dosage       = '40',
    units        = 'MG',
    formulation  = 'Tablet Delayed Release',
    instructions = 'TAKE 1 TABLET DAILY.; Rx',
  ),
  dict(
    original     = 'Amiodarone 200 mg 1 tablet every other day',
    name         = 'Amiodarone',
    dosage       = '200',
    units        = 'mg',
    formulation  = '',
    instructions = '1 tablet every other day',
  ),
  dict(
    original     = 'amlodipine 2.5 mg 1 tablet p.o. twice daily',
    name         = 'amlodipine',
    dosage       = '2.5',
    units        = 'mg',
    formulation  = '',
    instructions = '1 tablet p.o. twice daily',
  ),
#  dict(
#    original     = 'aspirin 325 mg 1 tablet p.o. daily',
#    name         = '',
#    dosage       = '',
#    units        = '',
#    formulation  = '',
#    instructions = '',
#  ),
#  dict(
#    original     = 'Hyzaar 100/25 mg 1 tablet p.o. daily',
#    name         = '',
#    dosage       = '',
#    units        = '',
#    formulation  = '',
#    instructions = '',
#  ),
#  dict(
#    original     = 'Toprol-XL 25 mg 1 tablet p.o. daily',
#    name         = '',
#    dosage       = '',
#    units        = '',
#    formulation  = '',
#    instructions = '',
#  ),
#  dict(
#    original     = 'nitroglycerin 0.4 sublingual p.r.n. for chest pain',
#    name         = '',
#    dosage       = '',
#    units        = '',
#    formulation  = '',
#    instructions = '',
#  ),
#  dict(
#    original     = 'Vytorin 10/20 1 tablet p.o. daily.',
#    name         = '',
#    dosage       = '',
#    units        = '',
#    formulation  = '',
#    instructions = '',
#  ),
#  dict(
#    original     = 'isosorbide dinitrate 30 mg 1 tablet p.o. 3 times daily',
#    name         = '',
#    dosage       = '',
#    units        = '',
#    formulation  = '',
#    instructions = '',
#  ),
)
parsedFields = ('name', 'dosage', 'units', 'formulation', 'instructions',)


class TestMedParsing(unittest.TestCase):
    
    def setUp(self):
        self.medList = demo_list_1 + demo_list_2
        self.parsedMedList = [medication_parser.match(med) for med in self.medList]
   
    def testDemoMedParsing(self):
        i = 0
        while i < len(parsedDemoMeds):
            d = parsedDemoMeds[i]
            m = medication_parser.match(d.get('original'))
            self._parseHorse(m,d,i)
            i += 1
        return
    
    def _parseHorse(self, m, d, i):
        for field in parsedFields:
            parsedVal = m.group(field)
            givenVal = d[field]
            self.assertEqual(parsedVal, givenVal, 'Incorrect parsing of %s in example %d: "%s" vs "%s"' % (field, i+1, parsedVal, givenVal))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
