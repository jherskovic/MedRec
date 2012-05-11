'''
Created on Feb 28, 2012

@author: cbearden
'''
import sys
sys.path.append('..')
import os
import cPickle as pickle
import bz2
import unittest
from constants import demo_list_1, demo_list_2
import medication
from mapping_context import MappingContext
from drug_problem_kb import ProblemRelation, problem_relation_factory

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

    medList = demo_list_1 + demo_list_2
    parsedMedList = [medication.medication_parser.match(med) for med in medList]
   
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


class TestMedication(unittest.TestCase):
    
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
        """Test that Medication class raises a TypeError if it isn't 
        initialized with a string."""
        self.assertRaises(TypeError, medication.Medication)

    def test_normalize_string(self):
        """Test that .normalize_string() normalizes both test strings to the same test output."""
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
        """Test that the optional provenance parameter becomes an attribute of the object."""
        medInstance = medication.Medication(self.original_strings[0], provenance=self.provenance)
        self.assertEqual(medInstance.provenance, self.provenance)
    
    def test_no_provenance(self):
        """Test that a Medication initialized without the provenance 
        parameter has an empty provenance attribute."""
        medInstance = medication.Medication(self.original_strings[0])
        self.assertEqual(medInstance.provenance, "")

    def test_provenance_readonly(self):
        """Test that the provenance attribute is immutable."""
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
if os.path.isfile('drug_problem_relations.pickle.bz2'):
    drug_problem_relations = pickle.load(bz2.BZ2File('drug_problem_relations.pickle.bz2', 'r'))
else:
    drug_problem_relations = None
if rxnorm is not None:
    mappings = MappingContext(rxnorm, treats, drug_problem_relations)
else:
    mappings = None


class TestParsedMedication(unittest.TestCase):
    
    original     = 'Protonix 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx'
    normalized   = 'PROTONIX 40 MG TABLET DELAYED RELEASE;TAKE 1 TABLET DAILY.; RX'
    multi_tradenames = 'Naproxen 500 MG Tablet;TAKE 1 TABLET EVERY 12 HOURS AS NEEDED.; Rx'
    original_generic = 'Sertraline 50 MG Tablet;TAKE 1 TABLET DAILY.; RPT'
    name         = 'Protonix'
    normalized_name = 'PROTONIX'
    dose         = '40'
    normalized_dose = '40'
    units        = 'MG'
    normalized_units = 'MG'
    formulation  = 'Tablet Delayed Release'
    normalized_formulation  = 'TABLET DELAYED RELEASE'
    instructions = 'TAKE 1 TABLET DAILY.; Rx'
    normalized_instructions = 'TAKE 1 TABLET DAILY.; RX'
    normalized_dose = '40 MG*1*1'
    provenance   = 'List 42'
    generic_formula = ['PANTOPRAZOLE (AS PANTOPRAZOLE SODIUM SESQUIHYDRATE)', 'PANTOPRAZOLE SODIUM']
    generic_formula.sort()
    CUIs         = ['C0876139']
    tradenames = ['C0002800', 'C0591117', 'C0591706', 'C0591843', 
        'C0591844', 'C0591891', 'C0592014', 'C0592068', 'C0592182',
        'C0593835', 'C0594335', 'C0699095', 'C0700017', 'C0718343',
        'C0721957', 'C0731332', 'C0731333', 'C0875956', 'C1170025',
        'C1186767', 'C1186768', 'C1186779', 'C1631235', 'C1724066',
        'C2343621', 'C2684675', 'C2725144', 'C2911866', 'C2911868', 'C3194766']
    original_dict = {
      'medication_name' : normalized_name,
      'dose'            : dose,
      'units'           : units,
      'formulation'     : normalized_formulation,
      'instructions'    : normalized_instructions,
      'original_string' : original,
      'provenance'      : provenance,
      'normalized_dose' : normalized_dose,
    }
    drug_names_tobe_normalized = ['MetFORMIN HCl', 'Dextromethorphan Hydrobromide']
    drug_names_normalized = ['METFORMIN HYDROCHLORIDE', 'DEXTROMETHORPHAN HYDROBROMIDE']
    ne_name = 'Protronix 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx'
    ne_dose = 'Protonix 20 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx'
    ne_units = 'Protonix 20 ml Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx'
    ne_formulation = 'Protonix 20 ml Capsule;TAKE 1 TABLET DAILY.; Rx'
    ne_instructions = 'Protonix 20 ml Capsule;TAKE 2 TABLETS DAILY.; Rx'
    constructed  = medication.ParsedMedication(original, provenance=provenance)
    constructed_mappings  = medication.ParsedMedication(original, mappings, provenance)
    constructed_multitradenames = medication.ParsedMedication(multi_tradenames, mappings)
    problemList = [problem_relation_factory(*t) for t in (
        ('Chronic Reflux Esophagitis', 3, 0.750000),
        ('Esophageal Reflux', 9, 0.236842),)]

    def test_construct_no_text(self):
        """Test that constructor requires at least one argument."""
        self.assertRaises(TypeError, medication.ParsedMedication)
    
    def test_c_original_string_equals(self):
        """Test that the original string arg to the constructor becomes the 
        .original_string attribute of the object."""
        self.assertEqual(self.constructed.original_string, self.original,
          "ParsedMedication class wasn't properly initialized from constructor.")

    def test_cm_original_string_equals(self):
        """Test that the original string arg to the constructor becomes the 
        .original_string attribute of the object when the object is initialized
        with a mappings arg."""
        self.assertEqual(self.constructed_mappings.original_string, self.original,
          "ParsedMedication class wasn't properly initialized from constructor.")

    def test_c_original_string_readonly(self):
        """Test that the .original_string property is immutable."""
        self.assertRaises(AttributeError, self.constructed.__setattr__, 'original_string', 'foo') 

    def test_c_normalized_string_equals(self):
        """Test that the original string is normalized as expected."""
        self.assertEqual(self.constructed.normalized_string, self.normalized,
          "ParsedMedication class wasn't properly initialized from constructor.")

    def test_cm_normalized_string_equals(self):
        """Test that the original string is normalized as expected when the 
        object is initialized with a mappings arg."""
        self.assertEqual(self.constructed_mappings.normalized_string, self.normalized,
          "ParsedMedication class wasn't properly initialized from constructor.")

    def test_c_normalized_string_readonly(self):
        """Test that the .normalized_string property is immutable."""
        self.assertRaises(AttributeError, self.constructed.__setattr__, 'normalized_string', 'foo')

    def test_name_ne(self):
        """Test that a difference in name makes ParsedMedication objects unequal."""
        name_ne = medication.ParsedMedication(self.ne_name, mappings)
        self.assertNotEqual(self.constructed, name_ne)

    def test_dose_ne(self):
        """Test that a difference in dose makes ParsedMedication objects unequal."""
        dose_ne = medication.ParsedMedication(self.ne_dose, mappings)
        self.assertNotEqual(self.constructed, dose_ne)

    def test_units_ne(self):
        """Test that a difference in units makes ParsedMedication objects unequal."""
        units_ne = medication.ParsedMedication(self.ne_units, mappings)
        self.assertNotEqual(self.constructed, units_ne)

    def test_formulation_ne(self):
        """Test that a difference in formulation makes ParsedMedication objects unequal."""
        formulation_ne = medication.ParsedMedication(self.ne_formulation, mappings)
        self.assertNotEqual(self.constructed, formulation_ne)

    def test_instructions_ne(self):
        """Test that a difference in instructions makes ParsedMedication objects unequal."""
        instructions_ne = medication.ParsedMedication(self.ne_instructions, mappings)
        self.assertNotEqual(self.constructed, instructions_ne)
    
    def test_name_sort(self):
        """Test that ParsedMedications that differ in name sort in the correct order."""
        orig = medication.ParsedMedication(self.original, mappings)
        orig_generic = medication.ParsedMedication(self.original_generic, mappings) 
        self.assertLess(orig, orig_generic)
        self.assertGreater(orig_generic, orig)

    def test_formulation_sort(self):
        """Test that ParsedMedications that differ in formulation sort in the correct order."""
        ne_units = medication.ParsedMedication(self.ne_units, mappings)
        ne_formulation = medication.ParsedMedication(self.ne_formulation, mappings)
        self.assertLess(ne_formulation, ne_units)
        self.assertGreater(ne_units, ne_formulation)

    def test_normalized_dose_sort(self):
        """Test that ParsedMedications that differ in normalized dose sort in the correct order."""
        ne_dose = medication.ParsedMedication(self.ne_dose, mappings)
        original = medication.ParsedMedication(self.original, mappings) 
        self.assertLess(ne_dose, original)
        self.assertGreater(original, ne_dose)

    def test_name_get(self):
        """Test that the .name property has the expected value."""
        self.assertEqual(self.constructed.name, self.normalized_name)

    def test_name_readonly(self):
        """Test that the .name property is immutable."""
        self.assertRaises(AttributeError, self.constructed.__setattr__,
          'name', "Dr. Jimson's Pantonic Remedy")
    
    def test_dose_get(self):
        """Test that the .dose property has the expected value."""
        self.assertEqual(self.constructed.dose, self.dose)

    def test_dose_readonly(self):
        """Test that the .dose property is immutable."""
        self.assertRaises(AttributeError, self.constructed.__setattr__,
          'dose', '1')

    def test_units_get(self):
        """Test that the .units property has the expected value."""
        self.assertEqual(self.constructed.units, self.normalized_units)

    def test_units_readonly(self):
        """Test that the .units property is immutable."""
        self.assertRaises(AttributeError, self.constructed.__setattr__,
          'units', 'bottle')

    def test_formulation_get(self):
        """Test that the .formulation property has the expected value."""
        self.assertEqual(self.constructed.formulation, self.normalized_formulation)

    def test_formulation_readonly(self):
        """Test that the .formulation property is immutable."""
        self.assertRaises(AttributeError, self.constructed.__setattr__,
          'formulation', 'elixir')

    def test_instructions_get(self):
        """Test that the .instructions property has the expected value."""
        self.assertEqual(self.constructed.instructions, self.normalized_instructions)

    def test_instructions_readonly(self):
        """Test that the .instructions property is immutable."""
        self.assertRaises(AttributeError, self.constructed.__setattr__,
          'instructions', 'Drink 1 tblsp every 4 hours')

    def test_normalized_dose_get(self):
        """Test that the .normalized_dose property has the expected value."""
        self.assertEqual(self.constructed.normalized_dose, self.normalized_dose)

    def test_normalized_dose_readonly(self):
        """Test that the .normalized_dose property is immutable."""
        self.assertRaises(AttributeError, self.constructed_mappings.__setattr__,
          'normalized_dose', '1 Tblsp*6*1')

    def test_provenance_get(self):
        """Test that the .provenance property has the expected value."""
        self.assertEqual(self.constructed_mappings.provenance, self.provenance)

    def test_provenance_readonly(self):
        """Test that the .provenance property is immutable."""
        self.assertRaises(AttributeError, self.constructed_mappings.__setattr__,
          'provenance', 'Lot 49')

    def test_as_dictionary(self):
        """Test that the dictionary representation of the ParsedMedication 
        object contains the expected items."""
        test_dict_set = set(self.original_dict.items())
        obj_dict_set  = set(self.constructed.as_dictionary().items())
        test_dict_set.add(('id', self.constructed.as_dictionary()['id']))
        self.assertTrue(test_dict_set <= obj_dict_set)

    @unittest.skipUnless(os.path.isfile('rxnorm.pickle.bz2'), 'missing needed test data from rxnorm.pickle.bz2')
    def test_generic_formula_get(self):
        """Test that the .generic_formula property has the expected value."""
        generic_formula = self.constructed_mappings.generic_formula
        self.assertEqual(set(generic_formula), set(self.generic_formula))

    def test_generic_formula_readonly(self):
        """Test that the .generic_formula property is immutable."""
        self.assertRaises(AttributeError, self.constructed_mappings.__setattr__,
          'generic_formula', 'Generic Elixir')

    def test_generic_formula_nomappings(self):
        """Test that a MappingContextError is raised when the 
        .generic_formula property of an object initialized without a 
        MappingContext is accessed."""
        self.assertRaises(medication.MappingContextError, self.constructed.__getattribute__, 'generic_formula')

    @unittest.skipUnless(os.path.isfile('rxnorm.pickle.bz2'), 'missing needed test data from rxnorm.pickle.bz2')
    def test_CUIs_get(self):
        """Test that we get the expected CUIs from our test object."""
        CUIs = list(self.constructed_mappings.CUIs)
        self.assertEqual(set(CUIs), set(self.CUIs))

    def test_CUIs_readonly(self):
        """Test that the CUIs property is immutable."""
        self.assertRaises(AttributeError, self.constructed_mappings.__setattr__,
          'CUIs', set(['C02','C01']))

    def test_CUIs_nomappings(self):
        """A ParsedMedication object initialized without CUIs should raise an
        error when the CUIs are accessed."""
        self.assertRaises(medication.MappingContextError,
          self.constructed.__getattribute__, 'CUIs')

    @unittest.skipUnless(os.path.isfile('rxnorm.pickle.bz2'), 'missing needed test data from rxnorm.pickle.bz2')
    def test_tradenames_get(self):
        """Test that we get the expected tradenames from our test object."""
        tradenames = list(self.constructed_multitradenames.tradenames)
        tradenames.sort()
        self.assertEqual(tradenames, self.tradenames)

    def test_tradenames_readonly(self):
        """Test that the tradenames property is immutable."""
        self.assertRaises(AttributeError, self.constructed_mappings.__setattr__,
          'tradenames', set(['C02','C01']))

    def test_tradenames_nomappings(self):
        """A ParsedMedication object initialized without a MappingContext 
        should raise a MappingContextError when .CUIs is accessed."""
        self.assertRaises(medication.MappingContextError,
          self.constructed.__getattribute__, 'tradenames')

    @unittest.skipUnless(os.path.isfile('drug_problem_relations.pickle.bz2'), 'missing needed test data from drug_problem_relations.pickle.bz2')
    def test_problems(self):
        """Test that the ParsedMedication initialized with the mappings has
        the expected problem list.""" 
        self.assertEqual(self.constructed_mappings.problems, self.problemList)

    def test__normalize_drug_name(self):
        """Test that the ._normalize_drug_name() class method normalizes 
        drug names as expected."""
        normalized_drug_names = []
        for drug_name in self.drug_names_tobe_normalized:
            normalized_drug_name = self.constructed._normalize_drug_name(drug_name)
            normalized_drug_names.append(normalized_drug_name)
        self.assertEqual(set(normalized_drug_names), set(self.drug_names_normalized))

    def test_fieldwise_comparison(self):
        """Test that fieldwise comparison of two ParsedMedication objects 
        yields the expected results."""
        desired_results = ['UNITS', 'NORMALIZED_DOSE', 'DOSE', 'SIG', 'FORMULATION']
        pm1 = medication.ParsedMedication('Sertraline 50 MG Tablet;TAKE 1 TABLET DAILY.; RPT', mappings)
        pm2 = medication.ParsedMedication('Zoloft 50 MG Tablet;TAKE 1 TABLET DAILY.; RPT', mappings)
        self.assertEqual(set(pm1.fieldwise_comparison(pm2)), set(desired_results))

    def test_factory_m1(self):
        """Test that a Medication initialized with an unparseable string and 
        a provenance yields the expected results."""
        med_line = "Take 2 aspirin and call me in the morning"
        provenance="List 2"
        m = medication.make_medication(med_line, provenance=provenance)
        self.assertTrue(isinstance(m, medication.Medication))
        self.assertEqual(m.original_string, med_line)
        self.assertEqual(m.provenance, provenance)
        
    def test_factory_m2(self):
        """Test that a Medication initialized with an unparseable string and 
        without a provenance yields the expected results."""
        med_line = "James Beam (for medicinal purposes only)"
        provenance = ""
        m = medication.make_medication(med_line)
        self.assertTrue(isinstance(m, medication.Medication))
        self.assertEqual(m.original_string, med_line)
        self.assertEqual(m.provenance, provenance)

    def test_factory_pm1(self):
        """Test that a ParsedMedication initialized with a parseable string 
        and a provenance yields the expected results."""
        provenance = "List 1"
        pm = medication.make_medication(self.original, provenance=provenance, mappings=mappings)
        self.assertTrue(isinstance(pm, medication.ParsedMedication))
        self.assertEqual(pm.original_string, self.original)
        self.assertEqual(pm.provenance, provenance)

    def test_factory_pm2(self):
        """Test that a ParsedMedication initialized with a dictionary 
        and a provenance yields the expected results."""
        original = 'Protonix 40 MG Tablet Delayed Release; TAKE 1 TABLET DAILY.; Rx'
        dikt = dict(
            name=self.name,
            units=self.units,
            dose=self.dose,
            formulation=self.formulation,
            instructions=self.instructions,
            original_line = original,
        )
        provenance = "List 3"
        pm = medication.make_medication(dikt, provenance=provenance, mappings=mappings)
        self.assertTrue(isinstance(pm, medication.ParsedMedication))
        self.assertEqual(pm.original_string, original)
        self.assertEqual(pm.provenance, provenance)

    def test_factory_pm3(self):
        """Test that a ParsedMedication initialized with a dictionary 
        containing a provenance and with a provenance yields 
        the expected results."""
        original = 'Protonix 40 MG Tablet Delayed Release; TAKE 1 TABLET DAILY.; Rx'
        dikt = dict(
            name=self.name,
            units=self.units,
            dose=self.dose,
            formulation=self.formulation,
            instructions=self.instructions,
            original_line=self.original
        )
        provenance = "List 3"
        pm = medication.make_medication(dikt, provenance=provenance, mappings=mappings)
        self.assertTrue(isinstance(pm, medication.ParsedMedication))
        self.assertEqual(pm.original_string, self.original)
        self.assertEqual(pm.provenance, provenance)


loader = unittest.TestLoader()
allTestsSuite = unittest.TestSuite()
allTestsSuite.addTests(loader.loadTestsFromTestCase(TestMedParsing))
allTestsSuite.addTests(loader.loadTestsFromTestCase(TestMedication))
allTestsSuite.addTests(loader.loadTestsFromTestCase(TestParsedMedication))
allTestsSuite.addTests(loader.loadTestsFromTestCase(TestParsedMedication))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
