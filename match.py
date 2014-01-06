'''
Created on Oct 28, 2011

@author: jherskovic
'''

import copy
import logging
from constants import (MATCH_BRAND_NAME, MATCH_INGREDIENTS,
                       MATCH_STRING, MATCH_TREATMENT_INTENT,
                       MATCH_COMPOUND,
                       MEDICATION_FIELDS, KNOWN_MATCHING_FIELDS)


class Match(object):
    """Represents a pair of reconciled meds (or potentially-reconciled
    meds); 'med1' and 'med2' are medication.ParsedMedication objects."""

    def __init__(self, med1, med2, strength=1.0, reconciliation_mechanism="unspecified"):
        super(Match, self).__init__()
        if med1 < med2:
            self.med1 = med1
            self.med2 = med2
        else:
            self.med1 = med2
            self.med2 = med1
        self.strength = strength
        self.mechanism = reconciliation_mechanism

    def as_dictionary(self):
        """Return a dictionary representing attributes of this match that
        are used by interfaces."""
        my_dict = {'med1': self.med1.as_dictionary(),
                   'score': self.strength,
                   'mechanism': str(self.mechanism)
        }
        if KNOWN_MATCHING_FIELDS.get(self.mechanism, None) is None:
            try:
                similarity = self.med1.fieldwise_comparison(self.med2)
            except:
                # catchall for not both being ParsedMedications, or one being None
                similarity = set()
        else:
            similarity = KNOWN_MATCHING_FIELDS[self.mechanism]
        my_dict['identical'] = similarity

        if self.med2 is not None:
            my_dict['med2'] = self.med2.as_dictionary()
        return my_dict

    def __repr__(self):
        if self.med1.normalized_string == self.med2.normalized_string:
            return "<Identical reconciliation (%s): %r @ 0x%x>" % (self.mechanism,
                                                                   self.med1,
                                                                   id(self))
        return "<Potential reconciliation (%1.2f%% certainty; %s) %r <-> %r @ 0x%x>" % \
               (self.strength * 100.0, self.mechanism,
                self.med1, self.med2, id(self))

    def _is_eq(self, other):
        return ((self.med1 == other.med1 and self.med2 == other.med2) or \
                (self.med1 == other.med2 and self.med2 == other.med1)) and \
               self.strength == other.strength and \
               self.mechanism == other.mechanism

    def __eq__(self, other):
        return self._is_eq(other)

    def __ne__(self, other):
        return not self._is_eq(other)

    def _is_lt(self, other):
        if self.med1 < other.med1:
            return True
        elif self.med1 > other.med1:
            return False
        elif self.med2 < other.med2:
            return True
        elif self.med2 > other.med2:
            return False
        elif self.mechanism < other.mechanism:
            return True
        elif self.mechanism > other.mechanism:
            return False
        elif self.strength >= other.strength:
            return True
        elif self.strength < other.strength:
            return False

    def __lt__(self, other):
        return self._is_lt(other)

    def __gt__(self, other):
        return not self._is_lt(other)


class MatchResult(object):
    """Represents the results of medication reconciliation: the two
    lists of medications to be reconciled minus the medications they
    have in common removed, along with a list of medications common
    to both lists.
    """

    def __init__(self, new_list_1, new_list_2, reconciled_list):
        self._list1 = new_list_1
        self._list1_sorted = None
        self._list2 = new_list_2
        self._list2_sorted = None
        self._reconciled = reconciled_list
        self._reconciled_sorted = None
        self._sort_lists()

    @property
    def list1(self):
        "First input list minus the medications that were reconciled."
        return copy.copy(self._list1)

    @property
    def list2(self):
        "Second input list minus the medications that were reconciled."
        return copy.copy(self._list2)

    @property
    def reconciled(self):
        "List of medications that were reconciled."
        return copy.copy(self._reconciled)

    def _sort_list(self, liszt):
        sorted_list = copy.copy(liszt)
        sorted_list.sort()
        return sorted_list

    def _sort_lists(self):
        self._list1_sorted = self.list1[:]
        self._list1_sorted.sort()
        self._list2_sorted = self.list2[:]
        self._list2_sorted.sort()
        self._reconciled_sorted = self.reconciled[:]
        self._reconciled_sorted.sort()

    def _lists_comparison(self, other):
        if self._list1_sorted == other._list1_sorted and \
                        self._list2_sorted == other._list2_sorted and \
                        self._reconciled_sorted == other._reconciled_sorted:
            return True
        return False

    def __eq__(self, other):
        areSame = self._lists_comparison(other)
        if areSame:
            return True
        return False

    def __ne__(self, other):
        areSame = self._lists_comparison(other)
        if areSame:
            return False
        return True

    def __repr__(self):
        return "<MatchResult list 1: %d; list 2: %d; reconciled: %d; 0x%x>" % \
               (len(self._list1), len(self._list2), len(self._reconciled), id(self),)


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
            common.append(Match(item, my_list_2_of_objects[where_in_2], 1.0, MATCH_STRING))
            del my_list_2[where_in_2]
            del my_list_2_of_objects[where_in_2]
        else:
            my_list_1.append(item)
    return MatchResult(my_list_1, my_list_2_of_objects, common)


def medication_list_CUIs(medication_list):
    """Given a medication list, returns a list of the matching CUIs for each
    medication."""
    return [x.CUIs for x in medication_list]


def match_by_rxcuis(list1, list2):
    """Match medication list 1 (list1) to medication list 2 by comparing the
    CUIs of each. This is an O(n^2) comparison, but given the average
    size of a medication list it's pretty fast.

    The function takes two lists and builds a third one from the common
    elements from both lists. If an element matches to exactly the same
    CUIs as another element, they are pharmacologically identical
    courtesy of RXNorm.

    The function returns a MatchResult containing three lists:
    * the first list, minus the common elements
    * the second list, minus the common elements
    * the list of common elements
    """
    concepts_1 = [x.RxCUIs for x in list1]
    concepts_2 = [x.RxCUIs for x in list2]
    # We keep a list of objects separate from a list of strings, so
    # we don't need to recompute the normalized strings over and over.
    my_list_1 = []
    my_list_2_of_objects = list2[:]
    common = []
    for i in xrange(len(concepts_1)):
        if concepts_1[i] == ['NOCODE']:
            my_list_1.append(list1[i])
        elif concepts_1[i] in concepts_2:
            where_in_2 = concepts_2.index(concepts_1[i])
            med2 = my_list_2_of_objects[where_in_2]
            common.append(Match(list1[i], my_list_2_of_objects[where_in_2],
                                1.0 if med2.normalized_dose == list1[i].normalized_dose else 0.5,
                                MATCH_COMPOUND))
            del my_list_2_of_objects[where_in_2]
            del concepts_2[where_in_2]
        else:
            my_list_1.append(list1[i])
    return MatchResult(my_list_1, my_list_2_of_objects, common)


def medication_list_tradenames(medication_list):
    """Given a medication list, returns a list of the tradenames for each
    element (respecting the original order, so both the original and the
    new lists have the same indices)."""
    return [x.tradenames for x in medication_list]


def find_brand_name_matches(c1, concepts_of_c2):
    logging.debug("Testing %r against %r", c1, concepts_of_c2)
    potential_matches = [c1 in t for t in concepts_of_c2 if t is not None]
    logging.debug("Result: %r", potential_matches)
    matches = potential_matches.index(True) \
        if True in potential_matches \
        else None
    return matches


def brand_name_match_bookkeeping(list_2, tradenames_c2, concepts_2, matches):
    del list_2[matches]
    del tradenames_c2[matches]
    del concepts_2[matches]


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
        matches = None
        dose_1 = list1[y].normalized_dose
        logging.debug("Testing %r", concepts_1[y])
        if concepts_1[y] is not None:
            # Test to see if any concept in concepts_1 is one of the tradenames of c2
            for c1 in concepts_1[y]:
                # Find the index of the first medication in list 2 one of whose tradenames c1 matches
                matches = find_brand_name_matches(c1, tradenames_of_c2)
                if matches is not None:
                    dose_2 = my_list_2_of_objects[matches].normalized_dose
                    # If the dosages are equal, we have a match
                    match_score = 1.0 if dose_1 == dose_2 else 0.5
                    common.append(Match(list1[y], my_list_2_of_objects[matches], match_score, MATCH_BRAND_NAME))
                    brand_name_match_bookkeeping(my_list_2_of_objects, tradenames_of_c2, concepts_2, matches)
                    break
        if matches is None:
            if tradenames_of_c1[y] is not None:
                # Test to see if any concept in tradenames_of_c1 is one of the concepts of c2
                for t1 in tradenames_of_c1[y]:
                    # Find the index of the first medication in list 2 whose concept matches a tradename of a med in list 1
                    matches = find_brand_name_matches(t1, concepts_2)
                    if matches is not None:
                        dose_2 = my_list_2_of_objects[matches].normalized_dose
                        # If the dosages are equal, we have a match
                        match_score = 1.0 if dose_1 == dose_2 else 0.5
                        common.append(Match(list1[y], my_list_2_of_objects[matches], match_score, MATCH_BRAND_NAME))
                        brand_name_match_bookkeeping(my_list_2_of_objects, tradenames_of_c2, concepts_2, matches)
                        break

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
                        # If the daily total dose doesn't match, penalize it
                        match[item2] = 0.5
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


def build_treatment_lists(concepts, mappings):
    treats = []
    for c in concepts:
        this_treats = set([])
        if c is not None:
            for each_concept in c:
                for each_treated_thing in mappings.treatment.get(each_concept, []):
                    this_treats.add(each_treated_thing)
        treats.append(this_treats)
    return treats


def match_by_treatment(list1, list2, mappings,
                       highest_possible_match=0.5,
                       match_acceptance_threshold=0.5):
    def match_percentage(set1, set2):
        """Computes Hooper's consistency to use as a match percentage"""
        len_1 = len(set1)
        len_2 = len(set2)
        if len_1 + len_2 == 0:
            return 0.0
        len_common = len(set1 & set2)
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
    treats_1 = build_treatment_lists(concepts_1, mappings)
    logging.debug("Treatment list for medication list 1: %r", treats_1)

    treats_2 = build_treatment_lists(concepts_2, mappings)
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
