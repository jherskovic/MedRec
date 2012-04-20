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
    """Basic testing of medication parsing.
    """
    def setUp(self):
        self.medList = demo_list_1 + demo_list_2
        self.parsedMedList = [medication.medication_parser.match(med) for med in self.medList]
   
    def testDemoMedParsing(self):
        """Test to ensure that medication.medication_parser parses all the 
        medications in the demo lists as expected. 
        """
        i = 0
        while i < len(parsedDemoMeds):
            d = parsedDemoMeds[i]
            m = medication.medication_parser.match(d.get('original'))
            self._parseHorse(m,d,i)
            i += 1
        return
    
    def _parseHorse(self, m, d, i):
        """Helper function that iterates over each field in a ParsedMedication 
        object and compares its value to the baseline.
        """
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
        """Ensure that the normalized_string attribute is immutable."""
        self.assertRaises(AttributeError, self.instance.__setattr__,
          'normalized_string', self.original_strings[1])

    def test_original_string(self):
        """Ensure that .original_string contains the original, unnormalized 
        version of the medication string."""
        i = 0
        for original_string in self.original_strings:
            i += 1
            medInstance = medication.Medication(original_string)
            self.assertEqual(medInstance.original_string, original_string, "Failed original string equality in example %d" % i)
    
    def test_original_string_readonly(self):
        """Ensure that the original_string attribute is immutable."""
        self.assertRaises(AttributeError, self.instance.__setattr__,
          'original_string', self.original_strings[1])

    def test_is_empty(self):
        """Ensure that Medication.empty_string() method successfully detects
        when the Medication object was initialized with an empty string and 
        when not."""
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
        self.dose         = '40'
        self.normalized_dose = '40'
        self.units        = 'MG'
        self.normalized_units = 'MG'
        self.formulation  = 'Tablet Delayed Release'
        self.normalized_formulation  = 'TABLET DELAYED RELEASE'
        self.instructions = 'TAKE 1 TABLET DAILY.; Rx'
        self.normalized_instructions = 'TAKE 1 TABLET DAILY.; RX'
        self.normalized_dose = '40 MG*1*1'
        self.provenance   = 'List 42'
        self.generic_formula = ['PANTOPRAZOLE (AS PANTOPRAZOLE SODIUM SESQUIHYDRATE)', 'PANTOPRAZOLE SODIUM']
        self.generic_formula.sort()
        self.CUIs         = ['C0876139']
        self.tradenames = ['C0002800', 'C0591117', 'C0591706', 'C0591843', 
            'C0591844', 'C0591891', 'C0592014', 'C0592068', 'C0592182',
            'C0593835', 'C0594335', 'C0699095', 'C0700017', 'C0718343',
            'C0721957', 'C0731332', 'C0731333', 'C0875956', 'C1170025',
            'C1186767', 'C1186768', 'C1186779', 'C1631235', 'C1724066',
            'C2343621', 'C2684675', 'C2725144', 'C2911866', 'C2911868', 'C3194766']
        self.original_dict = {
          'medication_name' : self.normalized_name,
          'dose'            : self.dose,
          'units'           : self.units,
          'formulation'     : self.normalized_formulation,
          'instructions'    : self.normalized_instructions,
          'original_string' : self.original,
          'provenance'      : self.provenance,
          'normalized_dose' : self.normalized_dose,
          'parsed'          : True,
        }
        self.drug_names_tobe_normalized = ['MetFORMIN HCl', 'Dextromethorphan Hydrobromide']
        self.drug_names_normalized = ['METFORMIN HYDROCHLORIDE', 'DEXTROMETHORPHAN HYDROBROMIDE']
        self.constructed  = medication.ParsedMedication(self.original, provenance=self.provenance)
        self.constructed_mappings  = medication.ParsedMedication(self.original, mappings, self.provenance)
        self.constructed_multitradenames = medication.ParsedMedication(self.multi_tradenames, mappings)

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
        self.assertRaises(AttributeError, self.constructed.__setattr__, 'original_string', 'foo') 

    def test_c_normalized_string_equals(self):
        self.assertEqual(self.constructed.normalized_string, self.normalized,
          "ParsedMedication class wasn't properly initialized from constructor.")

    def test_cm_normalized_string_equals(self):
        self.assertEqual(self.constructed_mappings.normalized_string, self.normalized,
          "ParsedMedication class wasn't properly initialized from constructor.")

    def test_c_normalized_string_readonly(self):
        self.assertRaises(AttributeError, self.constructed.__setattr__, 'normalized_string', 'foo')

    def test_name_get(self):
        self.assertEqual(self.constructed.name, self.normalized_name)

    def test_name_readonly(self):
        self.assertRaises(AttributeError, self.constructed.__setattr__,
          'name', "Dr. Jimson's Pantonic Remedy")
    
    def test_dose_get(self):
        self.assertEqual(self.constructed.dose, self.dose)

    def test_dose_readonly(self):
        self.assertRaises(AttributeError, self.constructed.__setattr__,
          'dose', '1')

    def test_units_get(self):
        self.assertEqual(self.constructed.units, self.normalized_units)

    def test_units_readonly(self):
        self.assertRaises(AttributeError, self.constructed.__setattr__,
          'units', 'bottle')

    def test_formulation_get(self):
        self.assertEqual(self.constructed.formulation, self.normalized_formulation)

    def test_formulation_readonly(self):
        self.assertRaises(AttributeError, self.constructed.__setattr__,
          'formulation', 'elixir')

    def test_instructions_get(self):
        self.assertEqual(self.constructed.instructions, self.normalized_instructions)

    def test_instructions_readonly(self):
        self.assertRaises(AttributeError, self.constructed.__setattr__,
          'instructions', 'Drink 1 tblsp every 4 hours')

    def test_normalized_dose_get(self):
        self.assertEqual(self.constructed.normalized_dose, self.normalized_dose)

    def test_normalized_dose_readonly(self):
        self.assertRaises(AttributeError, self.constructed_mappings.__setattr__,
          'normalized_dose', '1 Tblsp*6*1')

    def test_provenance_get(self):
        self.assertEqual(self.constructed_mappings.provenance, self.provenance)

    def test_provenance_readonly(self):
        self.assertRaises(AttributeError, self.constructed_mappings.__setattr__,
          'provenance', 'Lot 49')

    def test_as_dictionary(self):
        test_dict_set = set(self.original_dict.items())
        obj_dict_set  = set(self.constructed.as_dictionary().items())
        test_dict_set.add(('id', self.constructed.as_dictionary()['id']))
        self.assertTrue(test_dict_set <= obj_dict_set)

    def test_generic_formula_get(self):
        generic_formula = self.constructed_mappings.generic_formula
        self.assertEqual(set(generic_formula), set(self.generic_formula))

    def test_generic_formula_readonly(self):
        self.assertRaises(AttributeError, self.constructed_mappings.__setattr__,
          'generic_formula', 'Generic Elixir')

    def test_generic_formula_nomappings(self):
        self.assertRaises(medication.MappingContextError, self.constructed.__getattribute__, 'generic_formula')

    def test_CUIs_get(self):
        CUIs = list(self.constructed_mappings.CUIs)
        self.assertEqual(set(CUIs), set(self.CUIs))

    def test_CUIs_readonly(self):
        self.assertRaises(AttributeError, self.constructed_mappings.__setattr__,
          'CUIs', set(['C02','C01']))

    def test_CUIs_nomappings(self):
        self.assertRaises(medication.MappingContextError,
          self.constructed.__getattribute__, 'CUIs')

    def test_tradenames_get(self):
        tradenames = list(self.constructed_multitradenames.tradenames)
        tradenames.sort()
        self.assertEqual(tradenames, self.tradenames)

    def test_tradenames_readonly(self):
        self.assertRaises(AttributeError, self.constructed_mappings.__setattr__,
          'tradenames', set(['C02','C01']))

    def test_tradenames_nomappings(self):
        self.assertRaises(medication.MappingContextError,
          self.constructed.__getattribute__, 'tradenames')

    def test__normalize_drug_name(self):
        normalized_drug_names = []
        for drug_name in self.drug_names_tobe_normalized:
            normalized_drug_name = self.constructed._normalize_drug_name(drug_name)
            normalized_drug_names.append(normalized_drug_name)
        self.assertEqual(set(normalized_drug_names), set(self.drug_names_normalized))

    def test_fieldwise_comparison(self):
        desired_results = ['UNITS', 'NORMALIZED_DOSE', 'DOSE', 'SIG', 'FORMULATION']
        pm1 = medication.ParsedMedication('Sertraline 50 MG Tablet;TAKE 1 TABLET DAILY.; RPT', mappings)
        pm2 = medication.ParsedMedication('Zoloft 50 MG Tablet;TAKE 1 TABLET DAILY.; RPT', mappings)
        self.assertEqual(set(pm1.fieldwise_comparison(pm2)), set(desired_results))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
