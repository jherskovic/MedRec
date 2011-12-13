'''
Created on Oct 28, 2011

@author: jherskovic
'''

import copy
import logging
from constants import (MATCH_BRAND_NAME, MATCH_INGREDIENTS, 
                       MATCH_STRING, MATCH_TREATMENT_INTENT,
                       MEDICATION_FIELDS, KNOWN_MATCHING_FIELDS)

class Match(object):
    """Represents a pair of reconciled meds (or potentially-reconciled meds)"""
    def __init__(self, med1, med2, strength=1.0, reconciliation_mechanism="unspecified"):
        super(Match, self).__init__()
        self.med1 = med1
        self.med2 = med2
        self.strength = strength
        self.mechanism = reconciliation_mechanism
    def as_dictionary(self):
        my_dict = {'med1': self.med1.as_dictionary(),
                   'score': self.strength,
                   'mechanism': str(self.mechanism)
                }
        if KNOWN_MATCHING_FIELDS.get(self.mechanism, None) is None:
            try:
                similarity=self.med1.fieldwise_comparison(self.med2)
            except:
                # catchall for not both being ParsedMedications, or one being None
                similarity=set()
        else:
            similarity=KNOWN_MATCHING_FIELDS[self.mechanism]
        my_dict['similarity']=similarity
        
        if self.med2 is not None:
            my_dict['med2'] = self.med2.as_dictionary()
        return my_dict 
    def __repr__(self):
        if self.med1.normalized_string == self.med2.normalized_string:
            return "<Identical reconciliation (%s): %r @ %x>" % (self.mechanism,
                                                                     self.med1,
                                                                     id(self))
        return "<Potential reconciliation (%1.2f%% certainty; %s) %r <-> %r @ %x>" % \
               (self.strength * 100.0, self.mechanism,
                self.med1, self.med2, id(self))
    
class MatchResult(object):
    def __init__(self, new_list_1, new_list_2, reconciled_list):
        self._list1 = new_list_1
        self._list2 = new_list_2
        self._reconciled = reconciled_list
    @property
    def list1(self):
        return copy.copy(self._list1)
    @property
    def list2(self):
        return copy.copy(self._list2)
    @property
    def reconciled(self):
        return copy.copy(self._reconciled)
    
def match_by_strings(list1, list2):
    """Match medication list 1 (list1) to medication list 2 by comparing the
    strings one by one. This is an O(n^2) comparison, but given the average 
    size of a medication list it's pretty fast.
    
    The function takes two lists and builds a third one from the common
    elements from both lists. If two elements in a list (say list1) are
    identical to one element in the other list (list2), only the first
    identical element in list1 will be removed.  
    
    The function returns a MatchResult containing three lists: 
    * the first list, minus the common elements
    * the second list, minus the common elements
    * the list of common elements
    """  
    my_list_1 = []
    my_list_2 = [x.normalized_string for x in list2]
    # We keep a list of objects separate from a list of strings, so
    # we don't need to recompute the normalized strings over and over.
    my_list_2_of_objects = list2[:]
    common = []
    for item in list1:
        if item.normalized_string in my_list_2:
            where_in_2 = my_list_2.index(item.normalized_string)
            common.append(Match(item, item, 1.0, MATCH_STRING))
            del my_list_2[where_in_2]
            del my_list_2_of_objects[where_in_2]
        else:
            my_list_1.append(item)
    return MatchResult(my_list_1, my_list_2_of_objects, common)

def medication_list_CUIs(medication_list):
    """Given a medication list, returns a list of the matching CUIs for each
    medication."""
    return [x.CUIs() for x in medication_list]

def medication_list_tradenames(medication_list):
    """Given a medication list, returns a list of the tradenames for each
    element (respecting the original order, so both the original and the
    new lists have the same indices)."""
    return [x.tradenames() for x in medication_list]

def match_by_brand_name(list1, list2):
    """Match medication list 1 (list1) to medication list 2 by checking whether
    elements in list1 are brand names of elements in list2, and viceversa.
    
    The function takes two lists and builds a third one from the common
    elements from both lists. If two elements of list1 are brand names for
    elements in list2, only the first matching element in list1 will be 
    removed.  
    
    The function returns a MatchResult containing three lists: 
    * the first list, minus the common elements
    * the second list, minus the common elements
    * the list of common elements
    """  
    logging.debug("Determining CUIs for %r", list1)
    concepts_1 = medication_list_CUIs(list1)
    logging.debug("Concepts for %r: %r", list1, concepts_1)
    
    logging.debug("Computing tradenames for %r", list1)
    tradenames_of_c1 = medication_list_tradenames(list1)
    logging.debug("Tradenames for %r: %r", list1, tradenames_of_c1)

    logging.debug("Determining CUIs for %r", list2)
    concepts_2 = medication_list_CUIs(list2)
    logging.debug("Concepts for %r: %r", list2, concepts_2)
    
    logging.debug("Computing tradenames for %r", list2)
    tradenames_of_c2 = medication_list_tradenames(list2)
    logging.debug("Tradenames for %r: %r", list2, tradenames_of_c2)

    # If one of the lists is empty, or there are no known tradenames for
    # any medications, the entire analysis is useless, so we stop analyzing
    # and just return the input.
    if (concepts_1 == [] or tradenames_of_c2 == []) \
        and (concepts_2 == [] or tradenames_of_c1 == []):
        return MatchResult(list1, list2, [])
    
    # We keep a list of objects separate from a list of strings, so
    # we don't need to recompute the normalized strings over and over.
    my_list_1 = []
    my_list_2_of_objects = list2[:]
    common = []
    logging.debug("Length of concepts_1: %d", len(concepts_1))
    
    for y in xrange(len(list1)):
        logging.debug("y=%d", y)
        # Test to see if the concept in c1 is one of the tradenames of c2
        matches = None
        dose_1 = list1[y].normalized_dose
        logging.debug("Testing %r", concepts_1[y])
        if concepts_1[y] is not None:
            for c1 in concepts_1[y]:
                logging.debug("Testing %r against %r", c1, tradenames_of_c2)
                potential_matches = [c1 in t for t in tradenames_of_c2
                                  if t is not None]
                logging.debug("Result: %r", potential_matches)
                matches = potential_matches.index(True) \
                        if True in potential_matches \
                        else None
                if matches is not None:
                    dose_2 = my_list_2_of_objects[matches].normalized_dose
                    if dose_1 == dose_2:
                        common.append(Match(list1[y], my_list_2_of_objects[matches],
                                                     1.0, MATCH_BRAND_NAME))
                        del my_list_2_of_objects[matches]
                        del tradenames_of_c2[matches]
                        del concepts_2[matches]
                        break
                    else:
                        matches = None
        if matches is None:
            if tradenames_of_c1[y] is not None:
                for t1 in tradenames_of_c1[y]:
                    # Test to see if the concepts in c2 match any tradenames of c1
                    logging.debug("Testing %r" % t1 + " against %r" % concepts_2)
                    potential_matches = [t1 in c for c in concepts_2 if c is not None]
                    logging.debug("Result: %r", potential_matches)
                    matches = potential_matches.index(True) \
                            if True in potential_matches \
                            else None
                    if matches:
                        dose_2 = my_list_2_of_objects[matches].normalized_dose
                        if dose_1 == dose_2:
                            common.append(Match(list1[y], my_list_2_of_objects[matches],
                                                         1.0, MATCH_BRAND_NAME))
                            del my_list_2_of_objects[matches]
                            del tradenames_of_c2[matches]
                            del concepts_2[matches]
                            break
                        else:
                            matches = None
        if matches is None:
            my_list_1.append(list1[y])
    return MatchResult(my_list_1, my_list_2_of_objects, common)

def match_by_ingredients(list1, list2, min_match_threshold=0.3):
    """Computes equivalence between two lists of medications by comparing their
    lists of ingredients."""
    # We keep a list of objects separate from a list of strings, so
    # we don't need to recompute the normalized strings over and over.
    my_list_1 = []
    my_list_2 = [x.generic_formula for x in list2]
    my_list_2_of_objects = list2[:]
    common = []
    
    for item in list1:
        ph1 = (item.generic_formula, item.normalized_dose)
        match = [0.0] * len(my_list_2)
        for item2 in xrange(len(my_list_2)):
            ph2 = (my_list_2[item2],
                 my_list_2_of_objects[item2].normalized_dose)
            logging.debug("Comparing %r against %r", ph1, ph2)
            for p in ph1[0]:
                if p in ph2[0]:
                    if ph1[1] != ph2[1]:
                        # If the daily total dose doesn't match, it doesn't match.
                        match[item2] = -1.0
                        break
                    else:
                        match[item2] = match[item2] + 1.0
            match[item2] = match[item2] / float((len(ph2[0]) + len(ph1[0])) / 2.0)
        matched_items = [(match[x], my_list_2[x]) for x in xrange(len(my_list_2))]
        # We choose the highest-ranking match 
        matched_items.sort(reverse=True)
        if len(matched_items) > 0 and matched_items[0][0] > min_match_threshold:
            where_in_2 = my_list_2.index(matched_items[0][1])
            logging.debug("Matched %r to %r by generics with score %r",
                          item, my_list_2_of_objects[where_in_2],
                          matched_items[0][0])
            common.append(Match(item, my_list_2_of_objects[where_in_2],
                                               matched_items[0][0], MATCH_INGREDIENTS))
            del my_list_2[where_in_2]
            del my_list_2_of_objects[where_in_2]
        else:
            my_list_1.append(item)
        if len(matched_items) > 0:
            logging.debug("The best match for %r is %r", ph1, matched_items[0])
    return MatchResult(my_list_1, my_list_2_of_objects, common)

def match_by_treatment(list1, list2, mappings,
                       highest_possible_match=0.5,
                       match_acceptance_threshold=0.5):
    def match_percentage(set1, set2):
        """Computes Hooper's consistency to use as a match percentage"""
        len_1 = len(set1)
        len_2 = len(set2)
        if len_1 + len_2 == 0:
            return 0.0
        len_common = len([x for x in set1 if x in set2])
        return float(len_common) / float(len_1 + len_2 - len_common)
     
    logging.debug("Determining CUIs for %r", list1)
    concepts_1 = medication_list_CUIs(list1)
    logging.debug("Concepts for %r: %r", list1, concepts_1)

    logging.debug("Determining CUIs for %r", list2)
    concepts_2 = medication_list_CUIs(list2)
    logging.debug("Concepts for %r: %r", list2, concepts_2)

    if (concepts_1 == [] or concepts_2 == []):
        # Without CUIs there's nothing to do here.
        return MatchResult(list1, list2, [])
    
    # We keep a list of objects separate from a list of strings, so
    # we don't need to recompute the normalized strings over and over.
    my_list_1 = []
    my_list_2_of_objects = list2[:]
    common = []
    
    # Build lists of potential treatments
    treats_1 = []
    for c in concepts_1:
        this_treats = set([])
        if c is not None:
            for each_concept in c:
                for each_treated_thing in mappings.treatment.get(each_concept, []):
                    this_treats.add(each_treated_thing)
        treats_1.append(this_treats)
    logging.debug("Treatment list for medication list 1: %r", treats_1)
    
    treats_2 = []
    for c in concepts_2:
        this_treats = set([])
        if c is not None:
            for each_concept in c:
                for each_treated_thing in mappings.treatment.get(each_concept, []):
                    this_treats.add(each_treated_thing)
        treats_2.append(this_treats)
    logging.debug("Treatment list for medication list 2: %r", treats_2)
    
    for y in xrange(len(concepts_1)):
        # Compare the "treatment sphere" of each medication in list 1 to the
        # "treatment sphere" of each medication in list 2
        comparison = [(match_percentage(treats_1[y], treats_2[x]), x) for x in range(len(treats_2))]
        comparison.sort(reverse=True)
        # The first item of comparison is now the highest-ranked match
        if len(comparison) > 0 and comparison[0][0] >= match_acceptance_threshold:
            # Renormalize match score
            logging.debug("Highest comparison tuple (accepted) for %d: %r", y,
                          comparison[0])
            score = comparison[0][0] * highest_possible_match
            matched_item = comparison[0][1]
            common.append(Match(list1[y],
                                         my_list_2_of_objects[matched_item],
                                         score,
                                         MATCH_TREATMENT_INTENT))
            del my_list_2_of_objects[matched_item]
            del treats_2[matched_item]
        else:
            my_list_1.append(list1[y])

    return MatchResult(my_list_1, my_list_2_of_objects, common)
