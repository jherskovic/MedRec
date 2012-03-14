'''
Created on Feb 28, 2012

@author: cbearden
'''
import sys
sys.path.append('..')
#print sys.path
import unittest
from constants import demo_list_1, demo_list_2
import medication

parsedDemoMeds = (
  dict(
    original     = 'Zoloft 50 MG Tablet;TAKE 1 TABLET DAILY.; RPT',
    name         = 'Zoloft',
    dose         = '50',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE 1 TABLET DAILY.; RPT',
  ),
  dict(
    original     = 'Warfarin Sodium 2.5 MG Tablet;TAKE AS DIRECTED.; Rx',
    name         = 'Warfarin Sodium',
    dose         = '2.5',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE AS DIRECTED.; Rx',
  ),
  dict(
    original     = 'Lipitor 10 MG Tablet;TAKE 1 TABLET DAILY.; Rx',
    name         = 'Lipitor',
    dose         = '10',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE 1 TABLET DAILY.; Rx',
  ),
  dict(
    original     = 'Protonix 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx',
    name         = 'Protonix',
    dose         = '40',
    units        = 'MG',
    formulation  = 'Tablet Delayed Release',
    instructions = 'TAKE 1 TABLET DAILY.; Rx',
  ),
  dict(
    original     = 'Warfarin Sodium 5 MG Tablet;TAKE 1 TABLET DAILY AS DIRECTED.; Rx',
    name         = 'Warfarin Sodium',
    dose         = '5',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE 1 TABLET DAILY AS DIRECTED.; Rx',
  ),
  dict(
    original     = 'Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx',
    name         = 'Mirapex',
    dose         = '0.5',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE 1 TABLET 3 TIMES DAILY.; Rx',
  ),
  dict(
    original     = 'Lisinopril 5 MG Tablet;TAKE  TABLET TWICE DAILY; Rx',
    name         = 'Lisinopril',
    dose         = '5',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE  TABLET TWICE DAILY; Rx',
  ),
  dict(
    original     = 'Coreg 25 MG Tablet;TAKE 1 TABLET TWICE DAILY,  WITH MORNING AND EVENING MEAL; RPT',
    name         = 'Coreg',
    dose         = '25',
    units        = 'MG',
    formulation  = 'Tablet',
    instructions = 'TAKE 1 TABLET TWICE DAILY,  WITH MORNING AND EVENING MEAL; RPT',
  ),
  dict(
    original     = 'Pantoprazole Sodium 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx',
    name         = 'Pantoprazole Sodium',
    dose         = '40',
    units        = 'MG',
    formulation  = 'Tablet Delayed Release',
    instructions = 'TAKE 1 TABLET DAILY.; Rx',
  ),
#  dict(
#    original     = 'Amiodarone 200 mg 1 tablet every other day',
#    name         = 'Amiodarone',
#    dose         = '200',
#    units        = 'mg',
#    formulation  = '',
#    instructions = '1 tablet every other day',
#  ),
#  dict(
#    original     = 'amlodipine 2.5 mg 1 tablet p.o. twice daily',
#    name         = 'amlodipine',
#    dose         = '2.5',
#    units        = 'mg',
#    formulation  = '',
#    instructions = '1 tablet p.o. twice daily',
#  ),
)
parsedFields = ('name', 'dose', 'units', 'formulation', 'instructions',)


class TestMedParsing(unittest.TestCase):
    
    def setUp(self):
        self.medList = demo_list_1 + demo_list_2
        self.parsedMedList = [medication.medication_parser.match(med) for med in self.medList]
   
    def testDemoMedParsing(self):
        i = 0
        while i < len(parsedDemoMeds):
            d = parsedDemoMeds[i]
            m = medication.medication_parser.match(d.get('original'))
            self._parseHorse(m,d,i)
            i += 1
        return
    
    def _parseHorse(self, m, d, i):
        for field in parsedFields:
            self.assertTrue(m, "No match in example %d" % i)
            parsedVal = m.group(field)
            givenVal = d[field]
            self.assertEqual(parsedVal, givenVal, 'Incorrect parsing of %s in example %d: "%s" vs "%s"' % (field, i+1, parsedVal, givenVal))


class TestMedicationClass(unittest.TestCase):
    
    def setUp(self):
        self.original_strings = [
            'Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx.',
            '(Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx)',
            ]
        self.empty_strings = ['', ' ', "\t "]
        self.normalized_string = 'MIRAPEX 0.5 MG TABLET;TAKE 1 TABLET 3 TIMES DAILY.; RX'
        self.provenance = 'list1'
    
    def test_construct_no_text(self):
        self.assertTrue(medication.Medication(), "Unable to construct Medication without text.")

    def test_normalize_string(self):
        i = 0
        for original_string in self.original_strings:
            i += 1
            medInstance = medication.Medication(original_string)
            self.assertEqual(self.normalized_string, medInstance.normalized_string, "Failed to normalize example %d" % i)
    
    def test_original_string(self):
        i = 0
        for original_string in self.original_strings:
            i += 1
            medInstance = medication.Medication(original_string)
            self.assertEqual(medInstance.original_string, original_string, "Failed original string equality in example %d" % i)
    
    def test_is_empty(self):
        i = 0
        for empty_string in self.empty_strings:
            i += 1
            medInstance = medication.Medication(empty_string)
            self.assertTrue(medInstance.is_empty(), "Failed to detect empty string in example %d" % i)
        for nonempty_string in self.original_strings:
            i += 1
            medInstance = medication.Medication(nonempty_string)
            self.assertTrue(not medInstance.is_empty(), "Failed to detect non-empty string in example %d" % i)
    
    def test_provenance(self):
        medInstance = medication.Medication(self.original_strings[0], provenance=self.provenance)
        self.assertEqual(medInstance.provenance, self.provenance)


class TestParsedMedicationClass(unittest.TestCase):

    def setUp(self):
        self.original     = 'Protonix 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx'
        self.name         = 'Protonix'
        self.normalized_name = 'PROTONIX'
        self.name_new     = 'Mirapex;'
        self.normalized_name_new = 'MIRAPEX'
        self.dose         = '40'
        self.dose_new     = '30'
        self.units        = 'MG'
        self.units_new    = 'cl'
        self.normalized_units_new    = 'CL'
        self.formulation  = 'Tablet Delayed Release'
        self.normalized_formulation  = 'TABLET DELAYED RELEASE'
        self.formulation_new = 'Elixir'
        self.normalized_formulation_new = 'ELIXIR'
        self.instructions = 'TAKE 1 TABLET DAILY.; Rx'
        self.normalized_instructions = 'TAKE 1 TABLET DAILY.; RX'
        self.instructions_new = 'Take 1 Tablet 3 Times Daily.'
        self.normalized_instructions_new = 'TAKE 1 TABLET 3 TIMES DAILY'
        self.constructed  = medication.ParsedMedication(self.original)
        self.init_from_text    = medication.ParsedMedication()
        self.init_from_text.from_text(self.original)

    def test_construct_no_text(self):
        self.assertTrue(medication.ParsedMedication(), "Unable to construct ParsedMedication without text.")
    
    def test_constructed(self):
        self.assertEqual(self.constructed.original_string, self.original,"ParsedMedication class wasn't properly initialized from constructor.")

    def test_init_from_text(self):
        self.assertEqual(self.init_from_text.original_string, self.original, "ParsedMedication class wasn't properly initialized with .from_text().")
        
    def test_name_get(self):
        self.assertEqual(self.constructed.name, self.normalized_name)

    def test_name_set(self):
        self.constructed.name = self.name_new
        self.assertEqual(self.constructed.name, self.normalized_name_new)
    
    def test_dose_get(self):
        self.assertEqual(self.constructed.dose, self.dose)

    def test_dose_set(self):
        self.constructed.dose = self.dose_new
        self.assertEqual(self.constructed.dose, self.dose_new)

    def test_units_get(self):
        self.assertEqual(self.constructed.units, self.units)

    def test_units_set(self):
        self.constructed.units = self.units_new
        self.assertEqual(self.constructed.units, self.normalized_units_new)

    def test_formulation_get(self):
        self.assertEqual(self.constructed.formulation, self.normalized_formulation)

    def test_formulation_set(self):
        self.constructed.formulation = self.formulation_new
        self.assertEqual(self.constructed.formulation, self.normalized_formulation_new)

    def test_instructions_get(self):
        self.assertEqual(self.constructed.instructions, self.normalized_instructions)

    def test_instructions_set(self):
        self.constructed.instructions = self.instructions_new
        self.assertEqual(self.constructed.instructions, self.normalized_instructions_new)

    def test_original_line(self):
        self.assertEqual(self.init_from_text.original_line, self.original)

#    def test_parsed(self): pass
#    def test_generic_formula(self): pass
#    def test_as_dictionary(self): pass
#    def test_compute_generics(self): pass
#    def test_CUIs(self): pass
#    def test_tradenames(self): pass
#    def test_normalize_dose(self): pass
#    def test_normalized_dose(self): pass
#    def test_fieldwise_comparison(self): pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
