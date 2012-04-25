'''
Created on Mar 20, 2012

@author: cbearden
'''

import unittest
import sys
sys.path.append('..')
import re
import copy
import match
from medication import ParsedMedication
from medication import make_medication
from constants import (MATCH_BRAND_NAME, MATCH_INGREDIENTS, 
                       MATCH_STRING, MATCH_TREATMENT_INTENT,
                       MEDICATION_FIELDS, KNOWN_MATCHING_FIELDS,)
import constants
import cPickle as pickle
import bz2
from mapping_context import MappingContext
import logging

logging.basicConfig(filename='test_match.log', level=logging.INFO)

rx = pickle.load(bz2.BZ2File('rxnorm.pickle.bz2', 'r'))
ts = pickle.load(bz2.BZ2File('treats.pickle.bz2', 'r'))
mappings = MappingContext(rx, ts)
test_match_objects = pickle.load(bz2.BZ2File('test_match.pickle.bz2', 'r'))

def rmIdsFromMatchDict(matchDict):
    newDict = copy.copy(matchDict)
    del(newDict['med1']['id'])
    del(newDict['med2']['id'])
    return newDict

class TestMatch(unittest.TestCase):
    """A set of unit tests to exercise the match.Match class.
    """
    medString1 = 'Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx'
    medString1b = 'Mirapex 0.5 MG Tablet;TAKE 2 TABLETS 3 TIMES DAILY.; Rx'
    medString2 = 'Pramipexole 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx'
    medString2a = 'PRAMIPEXOLE 0.5 MG TABLET;take 1 tablet 3 times daily.; rx'
    medString2b = 'PRAMIPEXOLE 0.5 MG TABLET;take 2 tablets 3 times daily.; rx'
    med1 = ParsedMedication(medString1, mappings)
    med1b = ParsedMedication(medString1b, mappings)
    med2 = ParsedMedication(medString2, mappings)
    med2a = ParsedMedication(medString2a, mappings)
    med2b = ParsedMedication(medString2b, mappings)
    test_objects = test_match_objects['TestMatch']
    # Match objects used in testing below
    matched_by_string = match.Match(med1, med2, 0.5, "MATCH_STRING")
    matched_by_brand_name = match.Match(med1, med2, 0.8, "MATCH_BRAND_NAME")
    matched_by_ingredients = match.Match(med1, med2, 0.9, "MATCH_INGREDIENTS")
    matched_by_treatment = match.Match(med1, med2, 0.5, "MATCH_TREATMENT_INTENT")
    matched_unspecified = match.Match(med1, med2, 0.1)
    matched_potential1 = match.Match(med1, med2, 0.5)
    matched_identical1 = match.Match(med2a, med2, 0.5)
    matched_potential2 = match.Match(med2, med1, 0.5)
    matched_identical2 = match.Match(med2, med2a, 0.5)
    matched_potential3 = match.Match(med1, med2, 0.4)
    matched_identical3 = match.Match(med2a, med2, 0.4)
    matched_potential4 = match.Match(med1b, med2, 0.5)
    matched_potential4_rev = match.Match(med2, med1b, 0.5)
    matched_identical4 = match.Match(med2a, med2, 0.5)
       
    def test_potential_match_eq1(self):
        "Test that a newly-instantiated potential match is equivalent to our baseline."
        self.assertEqual(self.matched_potential1, self.test_objects['matched_potential'])
    
    def test_potential_match_eq2(self):
        "Test that a newly-instantiated potential match with meds in reverse order is equivalent to our baseline."
        self.assertEqual(self.matched_potential2, self.test_objects['matched_potential'])
    
    def test_potential_match_ne1(self):
        "Test that a newly-instantiated potential match is not equivalent to our baseline (certainty differs)."
        self.assertNotEqual(self.matched_potential3, self.test_objects['matched_potential'])

    def test_potential_match_ne2(self):
        "Test that a newly-instantiated potential match is not equivalent to our baseline (dosage differs)."
        self.assertNotEqual(self.matched_potential4, self.test_objects['matched_potential'])
    
    def test_potential_match_ne3(self):
        "Test that a newly-instantiated potential match with meds in reverse order is not equivalent to our baseline."
        self.assertNotEqual(self.matched_potential4_rev, self.test_objects['matched_potential'])
    
    def test_identical_match_eq1(self):
        "Test that a newly-instantiated identical match is equivalent to our baseline."
        self.assertEqual(self.matched_identical1, self.test_objects['matched_identical'])

    def test_identical_match_eq2(self):
        "Test that a newly-instantiated identical match with meds in reverse order is equivalent to our baseline."
        self.assertEqual(self.matched_identical2, self.test_objects['matched_identical'])

    def test_by_string_dictionary(self):
        "Test that the dictionary from a by-string match is as we expect."
        self.assertEqual(rmIdsFromMatchDict(self.matched_by_string.as_dictionary()),
                         rmIdsFromMatchDict(self.test_objects['matched_by_string'].as_dictionary()))
    
    def test_by_brand_name_dictionary(self):
        "Test that the dictionary from a by-brand-name match is as we expect."
        self.assertEqual(rmIdsFromMatchDict(self.matched_by_brand_name.as_dictionary()),
                         rmIdsFromMatchDict(self.test_objects['matched_by_brand_name'].as_dictionary()))
    
    def test_by_ingredients_dictionary(self):
        "Test that the dictionary from a by-ingredients match is as we expect."
        self.assertEqual(rmIdsFromMatchDict(self.matched_by_ingredients.as_dictionary()),
                         rmIdsFromMatchDict(self.test_objects['matched_by_ingredients'].as_dictionary()))
    
    def test_by_treatment_dictionary(self):
        "Test that the dictionary from a by-treatment match is as we expect."
        self.assertEqual(rmIdsFromMatchDict(self.matched_by_treatment.as_dictionary()),
                         rmIdsFromMatchDict(self.test_objects['matched_by_treatment'].as_dictionary()))
    
    def test_unspecified_dictionary(self):
        "Test that a dictionary from a match by unspecified mechanism is as we expect."
        self.assertEqual(rmIdsFromMatchDict(self.matched_unspecified.as_dictionary()),
                         rmIdsFromMatchDict(self.test_objects['matched_unspecified'].as_dictionary()))

    
class TestFunctions(unittest.TestCase):
    """A set of unit tests to exercise the functions in the 'match' module. 
    """
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
    pMed3CUIs = set(['C0981139', 'C0981138', 'C0779882', 'C1276897', 'C0376218'])
    pMed3Tradenames = ['C0710779']
    medString4 = 'Protonix 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx'
    pMed4 = ParsedMedication(medString4, mappings)
    medString5 = 'Pantoprazole Sodium 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx'
    pMed5 = ParsedMedication(medString5, mappings)
    medString6 = 'Paroxetine 20 MG Tablet; TAKE 1 TABLET DAILY.; Rx'
    pMed6 = ParsedMedication(medString6, mappings)
    medString7 = 'Sertraline 50 MG Tablet;TAKE 1 TABLET BY MOUTH EVERY DAY; Rx'
    pMed7 = ParsedMedication(medString7, mappings)
    medString8 = 'Razadyne 16 MG Capsule Extended Release 24 Hour;TAKE 1 CAPSULE DAILY IN THE MORNING take with meal daily; Rx.'
    pMed8 = ParsedMedication(medString8, mappings)
    medString9 = 'Cyclandelate 16 MG Capsule Extended Release 24 Hour;TAKE 1 CAPSULE DAILY IN THE MORNING take with meal daily; Rx.'
    pMed9 = ParsedMedication(medString9, mappings)
    medString10 = 'docosahexaenoic acid 200 mg capsules; one cap BID'
    pMed10 = ParsedMedication(medString10, mappings)
    medString11 = 'Exelon 4.6 MG/24HR Transdermal Patch 24 Hour;APPLY 1 PATCH DAILY AS DIRECTED.; Rx'
    pMed11 = ParsedMedication(medString11, mappings)
    list1 = [pMed1, pMed2]
    list1rev = [pMed2, pMed1]
    list2 = [pMed2a, pMed3]
    list2rev = [pMed3, pMed2a]
    list3 = [pMed2b, pMed3]
    list3rev = [pMed3, pMed2b]
    medication_list_test_CUIs = [pMed1CUIs, pMed2CUIs, pMed2aCUIs, pMed3CUIs, pMed2bCUIs, pMed3CUIs]
    medication_list_test_tradenames = [pMed1Tradenames, pMed2Tradenames, pMed2aTradenames, pMed3Tradenames, pMed2bTradenames, pMed3Tradenames]
    test_objects = test_match_objects['TestFunctions']
    matched_by_strings = match.match_by_strings(list1, list2)
    matched_by_strings_rev = match.match_by_strings(list1rev, list2rev)
    matched_by_brand_name1 = match.match_by_brand_name(list1, list3)
    matched_by_brand_name1_rev = match.match_by_brand_name(list1rev, list3rev)
    matched_by_brand_name2 = match.match_by_brand_name(list3, list1)
    matched_by_ingredients_above = match.match_by_ingredients([pMed4], [pMed5], min_match_threshold=0.6)
    matched_by_ingredients_below = match.match_by_ingredients([pMed4], [pMed5], min_match_threshold=0.7)
    matched_by_ingredients_rev_above = match.match_by_ingredients([pMed5], [pMed4], min_match_threshold=0.6)
    matched_by_ingredients_rev_below = match.match_by_ingredients([pMed5], [pMed4], min_match_threshold=0.7)
    matched_by_treatment_above = match.match_by_treatment([pMed6], [pMed7], mappings, match_acceptance_threshold=0.3)
    matched_by_treatment_below = match.match_by_treatment([pMed6], [pMed7], mappings)
    matched_by_treatment_05_yes = match.match_by_treatment([pMed8], [pMed9], mappings, match_acceptance_threshold=0.5)
    matched_by_treatment_05_no = match.match_by_treatment([pMed8], [pMed9], mappings, match_acceptance_threshold=0.51)
    matched_by_treatment_04_yes = match.match_by_treatment([pMed10], [pMed11], mappings, match_acceptance_threshold=0.4)
    matched_by_treatment_04_no = match.match_by_treatment([pMed10], [pMed11], mappings, match_acceptance_threshold=0.43)
    # Use the demo lists for testing; this code was previously  in TestMatchResult
    demo_list_1 = [pm for pm in
      [make_medication(x, mappings, "List 1") for x in constants.demo_list_1]
        if isinstance(pm, ParsedMedication)]
    demo_list_2 = [pm for pm in
      [make_medication(x, mappings, "List 2") for x in constants.demo_list_2]
        if isinstance(pm, ParsedMedication)]
    demo_matched_by_strings = match.match_by_strings(demo_list_1, demo_list_2)
    demo_matched_by_strings_rev = match.match_by_strings(demo_list_2, demo_list_1)
    demo_matched_by_brand_name = match.match_by_brand_name(demo_list_1, demo_list_2)
    demo_matched_by_brand_name_rev = match.match_by_brand_name(demo_list_2, demo_list_1)
    demo_matched_by_ingredients = match.match_by_ingredients(demo_list_1, demo_list_2)
    demo_matched_by_ingredients_rev = match.match_by_ingredients(demo_list_2, demo_list_1)

    def test_match_by_strings(self):
        "Test that the MatchResult from a by-string match contains the lists we expect."
        self.assertEqual(self.matched_by_strings, self.test_objects['matched_by_strings'])

    def test_match_by_strings_rev(self):
        """Test that the MatchResult from a by-string match is order-independent
        with respect to the order the medication lists are passed in."""
        self.assertEqual(self.matched_by_strings_rev, self.test_objects['matched_by_strings_rev'])

    def test_medication_list_CUIs(self):
        "Test the operation of match.medication_list_CUIs()"
        cuis = match.medication_list_CUIs(self.list1 + self.list2 + self.list3)
        self.assertEqual(cuis, self.medication_list_test_CUIs)

    def test_medication_list_tradenames(self):
        "Test the operation of match.medication_list_tradenames()"
        tradenames = match.medication_list_tradenames(self.list1 + self.list2 + self.list3)
        self.assertEqual(tradenames, self.medication_list_test_tradenames)

    def test_match_by_brand_name1(self):
        """Test that the MatchResult from a by-brand-name match contains the 
        lists we expect."""
        self.assertEqual(self.matched_by_brand_name1, self.test_objects['matched_by_brand_name1'])

    def test_match_by_brand_name1_rev(self):
        """Test that the MatchResult from a by-brand-name match is order-independent
        with respect to the order the medication lists are passed in."""
        self.assertEqual(self.matched_by_brand_name1_rev, self.test_objects['matched_by_brand_name1_rev'])

    def test_match_by_brand_name2(self):
        """Test that the MatchResult from a by-brand-name match contains the
        lists we expect."""
        self.assertEqual(self.matched_by_brand_name2, self.test_objects['matched_by_brand_name2'])

    def test_match_by_ingredients_above(self):
        """Test reconcilation of medications by treatment intent that should
        match at a threshold of 0.6."""
        self.assertEqual(self.matched_by_ingredients_above, self.test_objects['matched_by_ingredients_above'])

    def test_match_by_ingredients_below(self):
        """Test reconcilation of medications by treatment intent that should
        not match at a threshold of 0.7."""
        self.assertEqual(self.matched_by_ingredients_below, self.test_objects['matched_by_ingredients_below'])

    def test_match_by_ingredients_rev_above(self):
        """Test order independence of the reconcilation of medications by 
        treatment intent that should match at a threshold of 0.6."""
        self.assertEqual(self.matched_by_ingredients_rev_above, self.test_objects['matched_by_ingredients_rev_above'])

    def test_match_by_ingredients_rev_below(self):
        """Test order independence of the reconcilation of medications by 
        treatment intent that should not match at a threshold of 0.7."""
        self.assertEqual(self.matched_by_ingredients_rev_below, self.test_objects['matched_by_ingredients_rev_below'])

    def test_demo_match_by_strings(self):
        """Use demo lists to test matching by strings."""
        self.assertEqual(self.demo_matched_by_strings, self.test_objects['demo_matched_by_strings'])

    def test_demo_match_by_strings_rev(self):
        """Use demo lists to test order independence of matching by strings."""
        self.assertEqual(self.demo_matched_by_strings_rev, self.test_objects['demo_matched_by_strings_rev'])
        
    def test_demo_match_by_brand_name(self):
        """Use demo lists to test matching by brand names."""
        self.assertEqual(self.demo_matched_by_brand_name, self.test_objects['demo_matched_by_brand_name'])

    def test_demo_match_by_brand_name_rev(self):
        """Use demo lists to test order independence of matching by brand names."""
        self.assertEqual(self.demo_matched_by_brand_name_rev, self.test_objects['demo_matched_by_brand_name_rev'])

    def test_demo_match_by_ingredients_list(self):
        """Use demo lists to test matching by ingredients."""
        self.assertEqual(self.demo_matched_by_ingredients, self.test_objects['demo_matched_by_ingredients'])

    def test_demo_match_by_ingredients_list_rev(self):
        """Use demo lists to test order independence of matching by ingredients."""
        self.assertEqual(self.demo_matched_by_ingredients_rev, self.test_objects['demo_matched_by_ingredients_rev'])

    def test_match_by_treatment_above(self):
        """These two medications should match by treatment if the 
        match_acceptance_threshold is set to 0.3; note that this
        behavior may change as the underlying 'treats' data change."""
        self.assertEqual(len(self.matched_by_treatment_above.reconciled), 1)

    def test_match_by_treatment_below(self):
        """These two medications should not match by treatment if the
        match_acceptance_threshold is set to default (0.5); note that this
        behavior may change as the underlying 'treats' data change."""
        self.assertEqual(len(self.matched_by_treatment_below.reconciled), 0)
    
    def test_match_by_treatment_varies(self):
        """Test matching by treatment intent, varying thresholds to induce
        matches and non-matches on the same two sets of medication lists.
        """
        self.assertEqual(len(self.matched_by_treatment_05_yes.reconciled), 1)
        self.assertEqual(len(self.matched_by_treatment_05_no.reconciled), 0)
        self.assertEqual(len(self.matched_by_treatment_04_yes.reconciled), 1)
        self.assertEqual(len(self.matched_by_treatment_04_no.reconciled), 0)


class TestMatchResult(unittest.TestCase):
    """A set of unit tests to exercise the match.Match class. The MatchResult 
    class gets exercised a lot above, so we'll implement only a basic test
    of the members of the class.
    """
    med1 = ParsedMedication(TestFunctions.medString1, mappings)
    med2a = ParsedMedication(TestFunctions.medString2, mappings)
    med2b = ParsedMedication(TestFunctions.medString2, mappings)
    med3 = ParsedMedication(TestFunctions.medString3, mappings)
    rec_med = match.Match(med2a, med2b)
    basic_match_result = match.MatchResult([med1], [med3], [rec_med])
    test_objects = test_match_objects['TestMatchResult']

    def test_basic(self):
        "Basic test of MatchResult functionality."
        self.assertEqual(self.basic_match_result, self.test_objects['basic_match_result'])



if __name__ == "__main__":
    unittest.main()
