'''
Created on Feb 28, 2012

@author: cbearden
'''
import sys
sys.path.append('..')
import os
#print sys.path
import cPickle as pickle
import bz2
import unittest
from constants import demo_list_1, demo_list_2
import medication
from mapping_context import MappingContext

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
        self.instance = medication.Medication(self.original_strings[0])
    
    def test_construct_no_text(self):
        """Medication class is read-only & must be initialized with a string;
        if it isn't, a TypeError should be thrown with the message 
        '__init__() takes at least 2 arguments (1 given)'"""
        self.assertRaises(TypeError, medication.Medication)

    def test_normalize_string(self):
        """.normalize_string() should normalize both test strings to the same test output."""
        i = 0
        for original_string in self.original_strings:
            i += 1
            medInstance = medication.Medication(original_string)
            self.assertEqual(self.normalized_string, medInstance.normalized_string, "Failed to normalize example %d" % i)

    def test_normalized_string_readonly(self):
        self.assertRaises(AttributeError, self.instance.__setattr__,
          'normalized_string', self.original_strings[1])

    def test_original_string(self):
        i = 0
        for original_string in self.original_strings:
            i += 1
            medInstance = medication.Medication(original_string)
            self.assertEqual(medInstance.original_string, original_string, "Failed original string equality in example %d" % i)
    
    def test_original_string_readonly(self):
        self.assertRaises(AttributeError, self.instance.__setattr__,
          'original_string', self.original_strings[1])

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

    def test_provenance_readonly(self):
        self.assertRaises(AttributeError, self.instance.__setattr__,
          'provenance', self.original_strings[1])


if os.path.isfile('rxnorm.pickle.bz2'):
    rxnorm = pickle.load(bz2.BZ2File('rxnorm.pickle.bz2', 'r'))
else:
    rxnorm = None
if os.path.isfile('treats.pickle.bz2'):
    treats = pickle.load(bz2.BZ2File('treats.pickle.bz2', 'r'))
else:
    treats = None
if rxnorm is not None:
    mappings = MappingContext(rxnorm, treats)
else:
    mappings = None


class TestParsedMedicationClass(unittest.TestCase):
    
    def setUp(self):
        self.original     = 'Protonix 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx'
        self.normalized   = 'PROTONIX 40 MG TABLET DELAYED RELEASE;TAKE 1 TABLET DAILY.; RX'
        self.multi_tradenames = 'Naproxen 500 MG Tablet;TAKE 1 TABLET EVERY 12 HOURS AS NEEDED.; Rx'
        self.original_generic = 'Sertraline 50 MG Tablet;TAKE 1 TABLET DAILY.; RPT'
        self.name         = 'Protonix'
        self.normalized_name = 'PROTONIX'
        # self.name_new     = 'Mirapex;'
        # self.normalized_name_new = 'MIRAPEX'
        self.dose         = '40'
        self.normalized_dose = '40'
        # self.dose_new     = '30'
        self.units        = 'MG'
        self.normalized_units = 'MG'
        # self.units_new    = 'cl'
        # self.normalized_units_new    = 'CL'
        self.formulation  = 'Tablet Delayed Release'
        self.normalized_formulation  = 'TABLET DELAYED RELEASE'
        # self.formulation_new = 'Elixir'
        # self.normalized_formulation_new = 'ELIXIR'
        self.instructions = 'TAKE 1 TABLET DAILY.; Rx'
        self.normalized_instructions = 'TAKE 1 TABLET DAILY.; RX'
        self.normalized_dose = '40 MG*1*1'
        self.provenance   = 'List 42'
        # self.instructions_new = 'Take 1 Tablet 3 Times Daily.'
        # self.normalized_instructions_new = 'TAKE 1 TABLET 3 TIMES DAILY'
        self.generic_formula = ['PANTOPRAZOLE (AS PANTOPRAZOLE SODIUM SESQUIHYDRATE)', 'PANTOPRAZOLE SODIUM']
        self.generic_formula.sort()
        self.CUIs         = set(['C0876139'])
        self.tradenames = ['C0002800', 'C0591117', 'C0591706', 'C0591843', 
            'C0591844', 'C0591891', 'C0592014', 'C0592068', 'C0592182',
            'C0593835', 'C0594335', 'C0699095', 'C0700017', 'C0718343',
            'C0721957', 'C0731332', 'C0731333', 'C0875956', 'C1170025',
            'C1186767', 'C1186768', 'C1186779', 'C1631235', 'C1724066',
            'C2343621', 'C2684675', 'C2725144', 'C2911866', 'C2911868', 'C3194766']
        self.tradenames.sort()
        self.original_dict = {
          'medication_name' : self.normalized_name,
          'dose'            : self.dose,
          'units'           : self.units,
          'formulation'     : self.normalized_formulation,
          'instructions'    : self.normalized_instructions,
          'original_string' : self.original,
          'provenance'      : self.provenance,
          'normalized_dose' : self.normalized_dose,
        }
        self.constructed  = medication.ParsedMedication(self.original)
        self.constructed_mappings  = medication.ParsedMedication(self.original, mappings, self.provenance)
		self.constructed_multitradenames  = medication.ParsedMedication(self.multi_tradenames, mappings)
        #self.init_from_text    = medication.ParsedMedication()
        #self.init_from_text.from_text(self.original)
        #self.init_no_text = medication.ParsedMedication()

    def test_construct_no_text(self):
        """Must pass a string to the constructor."""
        self.assertRaises(TypeError, medication.ParsedMedication)
    
    def test_c_original_string_equals(self):
        self.assertEqual(self.constructed.original_string, self.original,
          "ParsedMedication class wasn't properly initialized from constructor.")

    def test_cm_original_string_equals(self):
        self.assertEqual(self.constructed_mappings.original_string, self.original,
          "ParsedMedication class wasn't properly initialized from constructor.")

    def test_c_original_string_readonly(self):
        self.assertRaises(TypeError, self.constructed.__setattr__, 'original_string', 'foo') 

    def test_c_normalized_string_equals(self):
        self.assertEqual(self.constructed.normalized_string, self.normalized,
          "ParsedMedication class wasn't properly initialized from constructor.")

    def test_cm_normalized_string_equals(self):
        self.assertEqual(self.constructed_mappings.normalized_string, self.normalized,
          "ParsedMedication class wasn't properly initialized from constructor.")

    def test_c_normalized_string_readonly(self):
        self.assertRaises(TypeError, self.constructed.__setattr__, 'normalized_string', 'foo')

#    def test_init_from_text(self):        
#        self.assertEqual(self.init_from_text.original_string, self.original, "ParsedMedication class wasn't properly initialized with .from_text().")
        
    def test_name_get(self):
        self.assertEqual(self.constructed.name, self.normalized_name)

    def test_name_readonly(self):
        self.assertRaises(AttributeError, self.instance.__setattr__,
          'name', "Dr. Jimson's Pantonic Remedy")
    
    def test_dose_get(self):
        self.assertEqual(self.constructed.dose, self.normalized_dose)

    def test_dose_readonly(self):
        self.assertRaises(AttributeError, self.instance.__setattr__,
          'dose', '1')

    def test_units_get(self):
        self.assertEqual(self.constructed.units, self.normalized_units)

    def test_units_readonly(self):
        self.assertRaises(AttributeError, self.instance.__setattr__,
          'units', 'bottle')

    def test_formulation_get(self):
        self.assertEqual(self.constructed.formulation, self.normalized_formulation)

    def test_formulation_readonly(self):
        self.assertRaises(AttributeError, self.instance.__setattr__,
          'formulation', 'elixir')

    def test_instructions_get(self):
        self.assertEqual(self.constructed.instructions, self.normalized_instructions)

    def test_instructions_readonly(self):
        self.assertRaises(AttributeError, self.instance.__setattr__,
          'instructions', 'Drink 1 tblsp every 4 hours')

    def test_normalized_dose_get(self):
        self.assertEqual(self.constructed.normalized_dose, self.normalized_dose)

    def test_normalized_dose_readonly(self):
        self.assertRaises(TypeError, self.constructed_mappings.__setattr__,
          'normalized_dose', '1 Tblsp*6*1')

    def test_provenance_get(self):
        self.assertEqual(self.constructed.provenance, self.provenance)

    def test_provenance_readonly(self):
        self.assertRaises(TypeError, self.constructed_mappings.__setattr__,
          'provenance', 'Lot 49')

    def test_dictionary_get(self):
        test_dict_set = set(self.original_dict.items())
        obj_dict_set  = set(self.constructed.dictionary.items())
        self.assertTrue(test_dict_set <= obj_dict_set)

    def test_dictionary_readonly(self):
        self.assertRaises(TypeError, self.constructed_mappings.__setattr__,
          'dictionary', {'foo':'bar'})

#    def test_original_line(self):
#        self.assertEqual(self.init_from_text.original_line, self.original)

#    def test_parsed_constructed(self):
#        self.assertTrue(self.constructed.parsed)
        
#    def test_parsed_from_text(self):
#        self.assertTrue(self.init_from_text.parsed)
        
#    def test_parsed_no_text(self):
#        self.assertTrue(not self.init_no_text.parsed)
        
    def test_generic_formula_get(self):
        generic_formula = self.constructed_mappings.generic_formula
        generic_formula.sort()
        self.assertEqual(generic_formula, self.generic_formula)

    def test_generic_formula_readonly(self):
        self.assertRaises(TypeError, self.constructed_mappings.__setattr__,
          'generic_formula', 'Generic Elixir')

    def test_generic_formula_nomappings(self):
        self.assertRaises(medication.MappingContextError, self.context.__getattr__, 'generic_formula')

#    def test_compute_generics_nomapping(self):
#        self.assertRaises(medication.MappingContextError, self.constructed.__getattribute__,
#          'generic_formula')
#
#    def test_compute_generics(self):
#        self.constructed.compute_generics(mappings)
#        generic_formula = self.constructed_mappings.generic_formula
#        generic_formula.sort()
#        self.assertEquals(self.generic_formula, generic_formula)
        
    def test_CUIs_get(self):
        CUIs = list(self.constructed_mappings.CUIs)
        CUIs.sort()
        self.assertEqual(CUIs, self.CUIs)

    def test_CUIs_readonly(self):
        self.assertRaises(TypeError, self.constructed_mappings.__setattr__,
          'CUIs', set(['C02','C01']))

    def test_CUIs_nomappings(self):
        self.assertRaises(medication.MappingContextError,
          self.context.__getattr__, 'CUIs')

    def test_tradenames_get(self):
        tradenames = list(self.constructed_mappings.tradenames)
        tradenames.sort()
        self.assertEqual(tradenames, self.tradenames)

    def test_tradenames_readonly(self):
        self.assertRaises(TypeError, self.constructed_mappings.__setattr__,
          'tradenames', set(['C02','C01']))

    def test_tradenames_nomappings(self):
        self.assertRaises(medication.MappingContextError,
          self.context.__getattr__, 'tradenames')

#    def test__normalize_drug_name(self): pass
#    def test__compute_generics(self): pass
#    def test__compute_cuis(self): pass
#    def test__compute_tradenames(self): pass
#    def test__normalize_dose(self): pass
#    def test_fieldwise_comparison(self): pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
