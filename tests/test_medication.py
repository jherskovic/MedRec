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
  ), #testMedParse1
  dict(
    original     = 'Warfarin Sodium 2.5 MG Tablet;TAKE AS DIRECTED.; Rx',
    name         = 'Warfarin Sodium',
    dosage       = '2.5',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE AS DIRECTED.; Rx',
  ), #testMedParse2
  dict(
    original     = 'Lipitor 10 MG Tablet;TAKE 1 TABLET DAILY.; Rx',
    name         = 'Lipitor',
    dosage       = '10',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE 1 TABLET DAILY.; Rx',
  ), #testMedParse3
  dict(
    original     = 'Protonix 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx',
    name         = 'Protonix',
    dosage       = '40',
    units        = 'MG',
    formulation  = 'Tablet Delayed Release',
    instructions = 'TAKE 1 TABLET DAILY.; Rx',
  ), #testMedParse4
  dict(
    original     = 'Warfarin Sodium 5 MG Tablet;TAKE 1 TABLET DAILY AS DIRECTED.; Rx',
    name         = 'Warfarin Sodium',
    dosage       = '5',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE 1 TABLET DAILY AS DIRECTED.; Rx',
  ), #testMedParse5
  dict(
    original     = 'Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx',
    name         = 'Mirapex',
    dosage       = '0.5',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE 1 TABLET 3 TIMES DAILY.; Rx',
  ), #testMedParse6
  dict(
    original     = 'Lisinopril 5 MG Tablet;TAKE  TABLET TWICE DAILY; Rx',
    name         = 'Lisinopril',
    dosage       = '5',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE  TABLET TWICE DAILY; Rx',
  ), #testMedParse7
  dict(
    original     = 'Coreg 25 MG Tablet;TAKE 1 TABLET TWICE DAILY,  WITH MORNING AND EVENING MEAL; RPT',
    name         = 'Coreg',
    dosage       = '25',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE 1 TABLET TWICE DAILY,  WITH MORNING AND EVENING MEAL; RPT',
  ), #testMedParse8
  dict(
    original     = 'Pantoprazole Sodium 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx',
    name         = 'Pantoprazole Sodium',
    dosage       = '40',
    units        = 'MG',
    formulation  = 'Tablet Delayed Release',
    instructions = 'TAKE 1 TABLET DAILY.; Rx',
  ), #testMedParse9
)
parsedFields = ('name', 'dosage', 'units', 'formulation', 'instructions',)


class TestMedParsing(unittest.TestCase):
    
    def setUp(self):
        self.medList = demo_list_1 + demo_list_2
        self.parsedMedList = [medication_parser.match(med) for med in self.medList]

    def testMedParse1(self):
        m = medication_parser.match(self.medList[0])
        d = parsedDemoMeds[0]
        for field in parsedFields:
            parsedVal = m.group(field)
            givenVal = d[field]
            self.assertEqual(parsedVal, givenVal, 'Incorrect parsing of %s in example %d: "%s" vs "%s"' % (field, 1, parsedVal, givenVal))

        
    def testMedParse2(self):
        m = medication_parser.match(self.medList[1])
        d = parsedDemoMeds[1]
        for field in parsedFields:
            parsedVal = m.group(field)
            givenVal = d[field]
            self.assertEqual(parsedVal, givenVal, 'Incorrect parsing of %s in example %d: "%s" vs "%s"' % (field, 1, parsedVal, givenVal))

    def testMedParse3(self):
        m = medication_parser.match(self.medList[2])
        d = parsedDemoMeds[2]
        for field in parsedFields:
            parsedVal = m.group(field)
            givenVal = d[field]
            self.assertEqual(parsedVal, givenVal, 'Incorrect parsing of %s in example %d: "%s" vs "%s"' % (field, 1, parsedVal, givenVal))

    def testMedParse4(self):
        m = medication_parser.match(self.medList[3])
        d = parsedDemoMeds[3]
        for field in parsedFields:
            parsedVal = m.group(field)
            givenVal = d[field]
            self.assertEqual(parsedVal, givenVal, 'Incorrect parsing of %s in example %d: "%s" vs "%s"' % (field, 1, parsedVal, givenVal))

    def testMedParse5(self):
        m = medication_parser.match(self.medList[4])
        d = parsedDemoMeds[4]
        for field in parsedFields:
            parsedVal = m.group(field)
            givenVal = d[field]
            self.assertEqual(parsedVal, givenVal, 'Incorrect parsing of %s in example %d: "%s" vs "%s"' % (field, 1, parsedVal, givenVal))

    def testMedParse6(self):
        m = medication_parser.match(self.medList[5])
        d = parsedDemoMeds[5]
        for field in parsedFields:
            parsedVal = m.group(field)
            givenVal = d[field]
            self.assertEqual(parsedVal, givenVal, 'Incorrect parsing of %s in example %d: "%s" vs "%s"' % (field, 1, parsedVal, givenVal))

    def testMedParse7(self):
        m = medication_parser.match(self.medList[6])
        d = parsedDemoMeds[6]
        for field in parsedFields:
            parsedVal = m.group(field)
            givenVal = d[field]
            self.assertEqual(parsedVal, givenVal, 'Incorrect parsing of %s in example %d: "%s" vs "%s"' % (field, 1, parsedVal, givenVal))

    def testMedParse8(self):
        m = medication_parser.match(self.medList[7])
        d = parsedDemoMeds[7]
        for field in parsedFields:
            parsedVal = m.group(field)
            givenVal = d[field]
            self.assertEqual(parsedVal, givenVal, 'Incorrect parsing of %s in example %d: "%s" vs "%s"' % (field, 1, parsedVal, givenVal))

    def testMedParse9(self):
        m = medication_parser.match(self.medList[7])
        d = parsedDemoMeds[7]
        for field in parsedFields:
            parsedVal = m.group(field)
            givenVal = d[field]
            self.assertEqual(parsedVal, givenVal, 'Incorrect parsing of %s in example %d: "%s" vs "%s"' % (field, 1, parsedVal, givenVal))
        
    def _parseHorse(self, m, d, i):
        for field in parsedFields:
            print 'woof'
            self.assertEqual(m.group('name'), d['name'], 'Incorrect parsing of %s in example %d' % (field, i))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
