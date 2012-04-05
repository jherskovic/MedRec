'''
Created on Mar 20, 2012

@author: cbearden
'''

import unittest
import sys
sys.path.append('..')
import re
import match
from medication import ParsedMedication
from constants import (MATCH_BRAND_NAME, MATCH_INGREDIENTS, 
                       MATCH_STRING, MATCH_TREATMENT_INTENT,
                       MEDICATION_FIELDS, KNOWN_MATCHING_FIELDS,
                       demo_list_1, demo_list_2)
import cPickle as pickle
import bz2
from mapping_context import MappingContext

import pdb

rx = pickle.load(bz2.BZ2File('rxnorm.pickle.bz2', 'r'))
ts = pickle.load(bz2.BZ2File('treats.pickle.bz2', 'r'))
mappings = MappingContext(rx, ts)
id_regex = re.compile(r'(?:0x[0-9a-f]{7,})')

def rmObjIds(repr_string):
    return id_regex.sub('', repr_string)

medId_regex = re.compile(r'(<Medication\s+)\d+')

def rmMedIds(repr_string):
    return medId_regex.sub(r'\1', repr_string)

def rmAllIds(repr_string):
    return(rmMedIds(rmObjIds(repr_string)))

class TestMatch(unittest.TestCase):

    medString1 = 'Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx'
    medString2 = 'Pramipexole 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx'
    medString2a = 'PRAMIPEXOLE 0.5 MG TABLET;take 1 tablet 3 times daily.; rx'
    med1 = ParsedMedication(medString1, mappings)
    med2 = ParsedMedication(medString2, mappings)
    med2a = ParsedMedication(medString2a, mappings)
    matched_by_string_dictionary = {
      'identical': ['UNITS', 'NORMALIZED_DOSE', 'DOSE', 'SIG', 'FORMULATION'],
      'med2': {
        'medication_name': 'PRAMIPEXOLE',
        'provenance': '',
        'formulation': 'TABLET',
        'units': 'MG',
        'id': 1,
        'instructions': 'TAKE 1 TABLET 3 TIMES DAILY.; RX',
        'original_string': 'Pramipexole 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx',
        'normalized_dose': '0.5 MG*3*1',
        'parsed': True,
        'dose': '0.5'
      },
      'med1': {
        'medication_name': 'MIRAPEX',
        'provenance': '',
        'formulation': 'TABLET',
        'units': 'MG',
        'id': 0,
        'instructions': 'TAKE 1 TABLET 3 TIMES DAILY.; RX',
        'original_string': 'Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx',
        'normalized_dose': '0.5 MG*3*1',
        'parsed': True,
        'dose': '0.5'
      },
      'score': 0.5, 'mechanism': 'MATCH_STRING'
    }
    matched_by_brand_name_dictionary = {
      'identical': ['UNITS', 'NORMALIZED_DOSE', 'DOSE', 'SIG', 'FORMULATION'],
      'med2': {
        'medication_name': 'PRAMIPEXOLE',
        'provenance': '',
        'formulation': 'TABLET',
        'units': 'MG',
        'id': 1,
        'instructions': 'TAKE 1 TABLET 3 TIMES DAILY.; RX',
        'original_string': 'Pramipexole 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx',
        'normalized_dose': '0.5 MG*3*1',
        'parsed': True,
        'dose': '0.5'
      },
      'med1': {
        'medication_name': 'MIRAPEX',
        'provenance': '',
        'formulation': 'TABLET',
        'units': 'MG',
        'id': 0,
        'instructions': 'TAKE 1 TABLET 3 TIMES DAILY.; RX',
        'original_string': 'Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx',
        'normalized_dose': '0.5 MG*3*1',
        'parsed': True,
        'dose': '0.5'
      },
      'score': 0.8, 'mechanism': 'MATCH_BRAND_NAME'
    }
    matched_by_ingredients_dictionary = {
      'identical': ['UNITS', 'NORMALIZED_DOSE', 'DOSE', 'SIG', 'FORMULATION'],
      'med2': {
        'medication_name': 'PRAMIPEXOLE',
        'provenance': '',
        'formulation': 'TABLET',
        'units': 'MG',
        'id': 1,
        'instructions': 'TAKE 1 TABLET 3 TIMES DAILY.; RX',
        'original_string': 'Pramipexole 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx',
        'normalized_dose': '0.5 MG*3*1',
        'parsed': True,
        'dose': '0.5'
      },
      'med1': {
        'medication_name': 'MIRAPEX',
        'provenance': '',
        'formulation': 'TABLET',
        'units': 'MG',
        'id': 0,
        'instructions': 'TAKE 1 TABLET 3 TIMES DAILY.; RX',
        'original_string': 'Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx',
        'normalized_dose': '0.5 MG*3*1',
        'parsed': True,
        'dose': '0.5'
      },
      'score': 0.9, 'mechanism': 'MATCH_INGREDIENTS'
    }
    matched_by_treatment_dictionary = {
      'identical': ['UNITS', 'NORMALIZED_DOSE', 'DOSE', 'SIG', 'FORMULATION'],
      'med2': {
        'medication_name': 'PRAMIPEXOLE',
        'provenance': '',
        'formulation': 'TABLET',
        'units': 'MG',
        'id': 1,
        'instructions': 'TAKE 1 TABLET 3 TIMES DAILY.; RX',
        'original_string': 'Pramipexole 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx',
        'normalized_dose': '0.5 MG*3*1',
        'parsed': True,
        'dose': '0.5'
      },
      'med1': {
        'medication_name': 'MIRAPEX',
        'provenance': '',
        'formulation': 'TABLET',
        'units': 'MG',
        'id': 0,
        'instructions': 'TAKE 1 TABLET 3 TIMES DAILY.; RX',
        'original_string': 'Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx',
        'normalized_dose': '0.5 MG*3*1',
        'parsed': True,
        'dose': '0.5'
      },
      'score': 0.5,
      'mechanism': 'MATCH_TREATMENT_INTENT'
    }
    matched_unspecified_dictionary = {
      'identical': ['UNITS', 'NORMALIZED_DOSE', 'DOSE', 'SIG', 'FORMULATION'],
      'med2': {
        'medication_name': 'PRAMIPEXOLE',
        'provenance': '',
        'formulation': 'TABLET',
        'units': 'MG',
        'id': 1,
        'instructions': 'TAKE 1 TABLET 3 TIMES DAILY.; RX',
        'original_string': 'Pramipexole 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx',
        'normalized_dose': '0.5 MG*3*1',
        'parsed': True,
        'dose': '0.5'
      },
      'med1': {
        'medication_name': 'MIRAPEX',
        'provenance': '',
        'formulation': 'TABLET',
        'units': 'MG',
        'id': 0,
        'instructions': 'TAKE 1 TABLET 3 TIMES DAILY.; RX',
        'original_string': 'Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx',
        'normalized_dose': '0.5 MG*3*1',
        'parsed': True,
        'dose': '0.5'
      },
      'score': 0.1, 'mechanism': 'unspecified'
    }
    matched_by_string = match.Match(med1, med2, 0.5, "MATCH_STRING")
    matched_by_brand_name = match.Match(med1, med2, 0.8, "MATCH_BRAND_NAME")
    matched_by_ingredients = match.Match(med1, med2, 0.9, "MATCH_INGREDIENTS")
    matched_by_treatment = match.Match(med1, med2, 0.5, "MATCH_TREATMENT_INTENT")
    matched_unspecified = match.Match(med1, med2, 0.1)
    matched_potential = match.Match(med1, med2, 0.5)
    matched_identical = match.Match(med2a, med2, 0.5)
    potential_match_repr = "<Potential reconciliation (50.00% certainty; unspecified) <Medication 12 @ 0x499b190: 'MIRAPEX' 0.5 'MG' 'TABLET' ('TAKE 1 TABLET 3 TIMES DAILY.; RX')> <-> <Medication 13 @ 0x499b1d0: 'PRAMIPEXOLE' 0.5 'MG' 'TABLET' ('TAKE 1 TABLET 3 TIMES DAILY.; RX')> @ 0x499b250>"
    identical_match_repr = "<Identical reconciliation (unspecified): <Medication 14 @ 0x499b210: 'PRAMIPEXOLE' 0.5 'MG' 'TABLET' ('TAKE 1 TABLET 3 TIMES DAILY.; RX')> @ 0x499b290>"
       
    def test_by_string_dictionary(self):
        self.assertEqual(self.matched_by_string.as_dictionary(), self.matched_by_string_dictionary)
    
    def test_by_brand_name_dictionary(self):
        self.assertEqual(self.matched_by_brand_name.as_dictionary(), self.matched_by_brand_name_dictionary)
    
    def test_by_ingredients_dictionary(self):
        self.assertEqual(self.matched_by_ingredients.as_dictionary(), self.matched_by_ingredients_dictionary)
    
    def test_by_treatment_dictionary(self):
        self.assertEqual(self.matched_by_treatment.as_dictionary(), self.matched_by_treatment_dictionary)
    
    def test_unspecified_dictionary(self):
        self.assertEqual(self.matched_unspecified.as_dictionary(), self.matched_unspecified_dictionary)

    def test_potential_match_repr(self):
        self.assertEqual(rmAllIds(repr(self.matched_potential)), rmAllIds(self.potential_match_repr))
    
    def test_identical_match_repr(self):
        self.assertEqual(rmAllIds(repr(self.matched_identical)), rmAllIds(self.identical_match_repr))

    
class TestMatchResult(unittest.TestCase):
    
    meds_list_1 = [pm for pm in
      [ParsedMedication(x, mappings, "List 1") for x in demo_list_1]
        if pm.parsed]
    meds_list_2 = [pm for pm in
      [ParsedMedication(x, mappings, "List 2") for x in demo_list_2]
        if pm.parsed]

    id_regex = re.compile(r'(?:0x[0-9a-f]{7,})')

    matched_by_strings_list1_repr = "[<Medication 2 @ 0xb86130c: 'ZOLOFT' 50 'MG' 'TABLET' ('TAKE 1 TABLET DAILY.; RPT')>, <Medication 5 @ 0xb85fa6c: 'PROTONIX' 40 'MG' 'TABLET DELAYED RELEASE' ('TAKE 1 TABLET DAILY.; RX')>, <Medication 8 @ 0xb85e70c: 'LISINOPRIL' 5 'MG' 'TABLET' ('TAKE TABLET TWICE DAILY; RX')>, <Medication 9 @ 0xb85e58c: 'COREG' 25 'MG' 'TABLET' ('TAKE 1 TABLET TWICE DAILY, WITH MORNING AND EVENING MEAL; RPT')>]"
    matched_by_strings_list2_repr = "[<Medication 13 @ 0xb85c46c: 'CARVEDILOL' 25 'MG' 'TABLET' ('TAKE 1 TABLET TWICE DAILY, WITH MORNING AND EVENING MEAL; RX')>, <Medication 15 @ 0xb85b1ac: 'LISINOPRIL' 5 'MG' 'TABLET' ('TAKE 1 TABLET TWICE DAILY; RX')>, <Medication 16 @ 0xb85ac8c: 'SYNTHROID' 100 'MCG' 'TABLET' ('TAKE 1 TABLET DAILY.; RX')>, <Medication 17 @ 0xb8588ac: 'PANTOPRAZOLE SODIUM' 40 'MG' 'TABLET DELAYED RELEASE' ('TAKE 1 TABLET DAILY.; RX')>, <Medication 18 @ 0xb85840c: 'SERTRALINE HCL' 50 'MG' 'TABLET' ('TAKE 1 TABLET DAILY.; RX')>]" 
    matched_by_strings_reconciled_repr = "[<Identical reconciliation (Identical strings): <Medication 3 @ 0xb8610ac: 'WARFARIN SODIUM' 2.5 'MG' 'TABLET' ('TAKE AS DIRECTED.; RX')> @ 0xb7faa2c>, <Identical reconciliation (Identical strings): <Medication 4 @ 0xb85ffec: 'LIPITOR' 10 'MG' 'TABLET' ('TAKE 1 TABLET DAILY.; RX')> @ 0xb7fa06c>, <Identical reconciliation (Identical strings): <Medication 6 @ 0xb85f68c: 'WARFARIN SODIUM' 5 'MG' 'TABLET' ('TAKE 1 TABLET DAILY AS DIRECTED.; RX')> @ 0xb7f9b6c>, <Identical reconciliation (Identical strings): <Medication 7 @ 0xb85e8cc: 'MIRAPEX' 0.5 'MG' 'TABLET' ('TAKE 1 TABLET 3 TIMES DAILY.; RX')> @ 0xb7f9aec>]" 
    matched_by_brand_name_list1_repr = "[<Medication 2 @ 0xcbdb2ac: 'ZOLOFT' 50 'MG' 'TABLET' ('TAKE 1 TABLET DAILY.; RPT')>, <Medication 3 @ 0xcbdb04c: 'WARFARIN SODIUM' 2.5 'MG' 'TABLET' ('TAKE AS DIRECTED.; RX')>, <Medication 4 @ 0xcbdaf8c: 'LIPITOR' 10 'MG' 'TABLET' ('TAKE 1 TABLET DAILY.; RX')>, <Medication 5 @ 0xcbdaa0c: 'PROTONIX' 40 'MG' 'TABLET DELAYED RELEASE' ('TAKE 1 TABLET DAILY.; RX')>, <Medication 6 @ 0xcbda62c: 'WARFARIN SODIUM' 5 'MG' 'TABLET' ('TAKE 1 TABLET DAILY AS DIRECTED.; RX')>, <Medication 7 @ 0xcbd886c: 'MIRAPEX' 0.5 'MG' 'TABLET' ('TAKE 1 TABLET 3 TIMES DAILY.; RX')>, <Medication 8 @ 0xcbd86ac: 'LISINOPRIL' 5 'MG' 'TABLET' ('TAKE TABLET TWICE DAILY; RX')>]"
    matched_by_brand_name_list2_repr = "[<Medication 11 @ 0xcbd6e4c: 'WARFARIN SODIUM' 2.5 'MG' 'TABLET' ('TAKE AS DIRECTED.; RX')>, <Medication 12 @ 0xcbd6aec: 'WARFARIN SODIUM' 5 'MG' 'TABLET' ('TAKE 1 TABLET DAILY AS DIRECTED.; RX')>, <Medication 14 @ 0xcbd524c: 'LIPITOR' 10 'MG' 'TABLET' ('TAKE 1 TABLET DAILY.; RX')>, <Medication 15 @ 0xcbd514c: 'LISINOPRIL' 5 'MG' 'TABLET' ('TAKE 1 TABLET TWICE DAILY; RX')>, <Medication 16 @ 0xcbd4c2c: 'SYNTHROID' 100 'MCG' 'TABLET' ('TAKE 1 TABLET DAILY.; RX')>, <Medication 17 @ 0xcbd284c: 'PANTOPRAZOLE SODIUM' 40 'MG' 'TABLET DELAYED RELEASE' ('TAKE 1 TABLET DAILY.; RX')>, <Medication 18 @ 0xcbd23ac: 'SERTRALINE HCL' 50 'MG' 'TABLET' ('TAKE 1 TABLET DAILY.; RX')>, <Medication 19 @ 0xcbd232c: 'MIRAPEX' 0.5 'MG' 'TABLET' ('TAKE 1 TABLET 3 TIMES DAILY.; RX')>]"
    matched_by_brand_name_reconciled_repr = "[<Potential reconciliation (100.00% certainty; Brand name and generic) <Medication 9 @ 0xcbd852c: 'COREG' 25 'MG' 'TABLET' ('TAKE 1 TABLET TWICE DAILY, WITH MORNING AND EVENING MEAL; RPT')> <-> <Medication 13 @ 0xcbd640c: 'CARVEDILOL' 25 'MG' 'TABLET' ('TAKE 1 TABLET TWICE DAILY, WITH MORNING AND EVENING MEAL; RX')> @ 0xcb73a8c>]"
    matched_by_ingredients_list1_repr = "[<Medication 9 @ 0xca9fb2c: 'COREG' 25 'MG' 'TABLET' ('TAKE 1 TABLET TWICE DAILY, WITH MORNING AND EVENING MEAL; RPT')>]"
    matched_by_ingredients_list2_repr = "[<Medication 13 @ 0xca9de6c: 'CARVEDILOL' 25 'MG' 'TABLET' ('TAKE 1 TABLET TWICE DAILY, WITH MORNING AND EVENING MEAL; RX')>, <Medication 16 @ 0xca9c3ac: 'SYNTHROID' 100 'MCG' 'TABLET' ('TAKE 1 TABLET DAILY.; RX')>]"
    matched_by_ingredients_reconciled_repr = "[<Potential reconciliation (100.00% certainty; Ingredient lists match) <Medication 2 @ 0xcaa262c: 'ZOLOFT' 50 'MG' 'TABLET' ('TAKE 1 TABLET DAILY.; RPT')> <-> <Medication 18 @ 0xca9992c: 'SERTRALINE HCL' 50 'MG' 'TABLET' ('TAKE 1 TABLET DAILY.; RX')> @ 0xca4314c>, <Identical reconciliation (Ingredient lists match): <Medication 3 @ 0xcaa258c: 'WARFARIN SODIUM' 2.5 'MG' 'TABLET' ('TAKE AS DIRECTED.; RX')> @ 0xca42b6c>, <Identical reconciliation (Ingredient lists match): <Medication 4 @ 0xcaa252c: 'LIPITOR' 10 'MG' 'TABLET' ('TAKE 1 TABLET DAILY.; RX')> @ 0xca4296c>, <Potential reconciliation (66.67% certainty; Ingredient lists match) <Medication 5 @ 0xcaa0eec: 'PROTONIX' 40 'MG' 'TABLET DELAYED RELEASE' ('TAKE 1 TABLET DAILY.; RX')> <-> <Medication 17 @ 0xca9b26c: 'PANTOPRAZOLE SODIUM' 40 'MG' 'TABLET DELAYED RELEASE' ('TAKE 1 TABLET DAILY.; RX')> @ 0xca4290c>, <Identical reconciliation (Ingredient lists match): <Medication 6 @ 0xcaa0e4c: 'WARFARIN SODIUM' 5 'MG' 'TABLET' ('TAKE 1 TABLET DAILY AS DIRECTED.; RX')> @ 0xca4262c>, <Identical reconciliation (Ingredient lists match): <Medication 7 @ 0xcaa042c: 'MIRAPEX' 0.5 'MG' 'TABLET' ('TAKE 1 TABLET 3 TIMES DAILY.; RX')> @ 0xca426ac>, <Potential reconciliation (100.00% certainty; Ingredient lists match) <Medication 8 @ 0xca9fbec: 'LISINOPRIL' 5 'MG' 'TABLET' ('TAKE TABLET TWICE DAILY; RX')> <-> <Medication 15 @ 0xca9d3ac: 'LISINOPRIL' 5 'MG' 'TABLET' ('TAKE 1 TABLET TWICE DAILY; RX')> @ 0xca4234c>]"
    matched_by_strings = match.match_by_strings(meds_list_1, meds_list_2)
    matched_by_brand_name = match.match_by_brand_name(meds_list_1, meds_list_2)
    matched_by_ingredients = match.match_by_ingredients(meds_list_1, meds_list_2)

    def rmObjIds(self, repr_string):
        #return repr_string
        return self.id_regex.sub('', repr_string)
    
    def setUp(self):
        mbs = self.matched_by_strings
        mbbn = self.matched_by_brand_name
        mbi = self.matched_by_ingredients
        #matched_by_treatment = match.match_by_treatment(self.meds_list_1, self.meds_list_2)
        #pdb.set_trace()
        
    def test_match_by_strings_list1(self):
        self.assertEqual(rmAllIds(repr(self.matched_by_strings.list1)),
                         rmAllIds(self.matched_by_strings_list1_repr))

    def test_match_by_strings_list2(self):
        self.assertEqual(rmAllIds(repr(self.matched_by_strings.list2)),
                         rmAllIds(self.matched_by_strings_list2_repr))

    def test_match_by_strings_reconciled(self):
        self.assertEqual(rmAllIds(repr(self.matched_by_strings.reconciled)),
                         rmAllIds(self.matched_by_strings_reconciled_repr))

    def test_match_by_brand_name_list1(self):
        self.assertEqual(rmAllIds(repr(self.matched_by_brand_name.list1)),
                         rmAllIds(self.matched_by_brand_name_list1_repr))

    def test_match_by_brand_name_list2(self):
        self.assertEqual(rmAllIds(repr(self.matched_by_brand_name.list2)),
                         rmAllIds(self.matched_by_brand_name_list2_repr))

    def test_match_by_brand_name_reconciled(self):
        self.assertEqual(rmAllIds(repr(self.matched_by_brand_name.reconciled)),
                         rmAllIds(self.matched_by_brand_name_reconciled_repr))

    def test_match_by_ingredients_list1(self):
        self.assertEqual(rmAllIds(repr(self.matched_by_ingredients.list1)),
                         rmAllIds(self.matched_by_ingredients_list1_repr))

    def test_match_by_ingredients_list2(self):
        self.assertEqual(rmAllIds(repr(self.matched_by_ingredients.list2)),
                         rmAllIds(self.matched_by_ingredients_list2_repr))

    def test_match_by_ingredients_reconciled(self):
        self.assertEqual(rmAllIds(repr(self.matched_by_ingredients.reconciled)),
                         rmAllIds(self.matched_by_ingredients_reconciled_repr))

class TestFunctions(unittest.TestCase):

    medString1 = 'Lisinopril 5 MG Tablet;TAKE  TABLET TWICE DAILY; Rx'
    pMed1 = ParsedMedication(medString1, mappings)
    pMed1CUIs = set(['C0065374'])
    pMed1Tradenames = ['C0591228', 'C0591229', 'C0678140', 'C0701176', 'C0722805', 'C1602677', 'C2368718', 'C2368722', 'C2368725']
    medString2 = 'Pramipexole 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx'
    pMed2 = ParsedMedication(medString2, mappings)
    pMed2CUIs = set(['C0074710'])
    pMed2Tradenames = ['C0721754']
    medString2a = 'PRAMIPEXOLE 0.5 MG TABLET;take 1 tablet 3 times daily.; rx'
    pMed2a = ParsedMedication(medString2a, mappings)
    pMed2aCUIs = set(['C0074710'])
    pMed2aTradenames = ['C0721754']
    medString2b = 'Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx'
    pMed2b = ParsedMedication(medString2b, mappings)
    pMed2bCUIs = set(['C0721754'])
    pMed2bTradenames = []
    medString3 = 'Warfarin Sodium 2.5 MG Tablet;TAKE AS DIRECTED.; Rx'
    pMed3 = ParsedMedication(medString3, mappings)
    pMed3CUIs = set(['C0376218'])
    pMed3Tradenames = []
    list1 = [pMed1, pMed2]
    list1rev = [pMed2, pMed1]
    list2 = [pMed2a, pMed3]
    list2rev = [pMed3, pMed2a]
    list3 = [pMed2b, pMed3]
    list3rev = [pMed3, pMed2b]
    matched_by_string_list1_repr = "[<Medication 18 @ 0x36ac090: 'LISINOPRIL' 5 'MG' 'TABLET' ('TAKE TABLET TWICE DAILY; RX')>]"
    matched_by_string_list2_repr = "[<Medication 24 @ 0x6c30850: 'WARFARIN SODIUM' 2.5 'MG' 'TABLET' ('TAKE AS DIRECTED.; RX')>]"
    matched_by_string_reconciled_repr = "[<Identical reconciliation (Identical strings): <Medication 22 @ 0x6c307d0: 'PRAMIPEXOLE' 0.5 'MG' 'TABLET' ('TAKE 1 TABLET 3 TIMES DAILY.; RX')> @ 0x45748d0>]"
    matched_by_tradenames_list1_repr = "[<Medication 18 @ 0x3ffa090: 'LISINOPRIL' 5 'MG' 'TABLET' ('TAKE TABLET TWICE DAILY; RX')>]"
    matched_by_tradenames_list2_repr = "[<Medication 22 @ 0x3ffa210: 'WARFARIN SODIUM' 2.5 'MG' 'TABLET' ('TAKE AS DIRECTED.; RX')>]"
    matched_by_tradenames_reconciled1_repr = "[<Potential reconciliation (100.00% certainty; Brand name and generic) <Medication 19 @ 0x42e2110: 'PRAMIPEXOLE' 0.5 'MG' 'TABLET' ('TAKE 1 TABLET 3 TIMES DAILY.; RX')> <-> <Medication 21 @ 0x42e21d0: 'MIRAPEX' 0.5 'MG' 'TABLET' ('TAKE 1 TABLET 3 TIMES DAILY.; RX')> @ 0x3aad150>]"
    matched_by_tradenames_reconciled2_repr = "[<Potential reconciliation (100.00% certainty; Brand name and generic) <Medication 21 @ 0x3347250: 'MIRAPEX' 0.5 'MG' 'TABLET' ('TAKE 1 TABLET 3 TIMES DAILY.; RX')> <-> <Medication 19 @ 0x3347190: 'PRAMIPEXOLE' 0.5 'MG' 'TABLET' ('TAKE 1 TABLET 3 TIMES DAILY.; RX')> @ 0x2ca2190>]"

    def test_match_by_strings(self):
        myMatchResult = match.match_by_strings(self.list1, self.list2)
        self.assertEqual(rmAllIds(repr(myMatchResult.list1)), rmAllIds(self.matched_by_string_list1_repr))
        self.assertEqual(rmAllIds(repr(myMatchResult.list2)), rmAllIds(self.matched_by_string_list2_repr))
        self.assertEqual(rmAllIds(repr(myMatchResult.reconciled)), rmAllIds(self.matched_by_string_reconciled_repr))

    def test_match_by_strings_rev(self):
        myMatchResult = match.match_by_strings(self.list1rev, self.list2rev)
        self.assertEqual(rmAllIds(repr(myMatchResult.list1)), rmAllIds(self.matched_by_string_list1_repr))
        self.assertEqual(rmAllIds(repr(myMatchResult.list2)), rmAllIds(self.matched_by_string_list2_repr))
        self.assertEqual(rmAllIds(repr(myMatchResult.reconciled)), rmAllIds(self.matched_by_string_reconciled_repr))

    def test_medication_list_CUIs(self):
        cuis = match.medication_list_CUIs(self.list1 + self.list2 + self.list3)
        self.assertEqual(cuis, [self.pMed1CUIs, self.pMed2CUIs, self.pMed2aCUIs, self.pMed3CUIs, self.pMed2bCUIs, self.pMed3CUIs])

    def test_medication_list_tradenames(self):
        tradenames = match.medication_list_tradenames(self.list1 + self.list2 + self.list3)
        self.assertEqual(tradenames, [self.pMed1Tradenames, self.pMed2Tradenames, self.pMed2aTradenames, self.pMed3Tradenames, self.pMed2bTradenames, self.pMed3Tradenames])

    def test_match_by_brand_name1(self):
        myMatchResult = match.match_by_brand_name(self.list1, self.list3)
        self.assertEqual(rmAllIds(repr(myMatchResult.list1)), rmAllIds(self.matched_by_tradenames_list1_repr))
        self.assertEqual(rmAllIds(repr(myMatchResult.list2)), rmAllIds(self.matched_by_tradenames_list2_repr))
        self.assertEqual(rmAllIds(repr(myMatchResult.reconciled)), rmAllIds(self.matched_by_tradenames_reconciled1_repr))

    def test_match_by_brand_name1_rev(self):
        myMatchResult = match.match_by_brand_name(self.list1rev, self.list3rev)
        self.assertEqual(rmAllIds(repr(myMatchResult.list1)), rmAllIds(self.matched_by_tradenames_list1_repr))
        self.assertEqual(rmAllIds(repr(myMatchResult.list2)), rmAllIds(self.matched_by_tradenames_list2_repr))
        self.assertEqual(rmAllIds(repr(myMatchResult.reconciled)), rmAllIds(self.matched_by_tradenames_reconciled1_repr))

    def test_match_by_brand_name2(self):
        myMatchResult = match.match_by_brand_name(self.list3, self.list1)
        self.assertEqual(rmAllIds(repr(myMatchResult.list1)), rmAllIds(self.matched_by_tradenames_list2_repr))
        self.assertEqual(rmAllIds(repr(myMatchResult.list2)), rmAllIds(self.matched_by_tradenames_list1_repr))
        self.assertEqual(rmAllIds(repr(myMatchResult.reconciled)), rmAllIds(self.matched_by_tradenames_reconciled2_repr))

#    def test_match_by_ingredients(self):
#        myMatchResult = match.match_by_brand_name(self.list1, self.list2)
#        pdb.set_trace()

    #def test_match_by_treatment(self):
    #    pass


if __name__ == "__main__":
    unittest.main()
