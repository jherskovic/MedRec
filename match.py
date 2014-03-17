'''
Created on Oct 28, 2011

@author: jherskovic
'''

import copy
import logging
from collections import namedtuple
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


class ComparableMedicationList(object):
    """Bookkeeping class to handle the maintenance tasks of comparing different medication attributes
     and manage the addition and removal of items simultaneously to several lists."""
    ComparableMedicationItem = namedtuple("ComparableMedicationItem", ["attr", "original"])

    def __init__(self, original_list, comparable):
        """'Comparable' should be a function or lambda that, given an item of a medication list,
        returns the value of interest."""
        self._interesting_attribute=[comparable(x) for x in original_list]
        self._original = original_list[:]

    def index(self, interesting):
        """Returns the position of an item of interest in the list."""
        return self._interesting_attribute.index(interesting)

    def pop(self, position):
        """Removes an item at a certain position from the list and returns it."""
        del self._interesting_attribute[position]
        item = self._original[position]
        del self._original[position]
        return item

    def popitem(self, item):
        return self.pop(self.index(item))

    def original_index(self, item):
        return self._original.index(item)

    def __delitem__(self, key):
        del self._interesting_attribute[key]
        del self._original[key]

    def __contains__(self, item):
        return item in self._interesting_attribute

    def __len__(self):
        return len(self._original)

    @property
    def objects(self):
        return self._original

    def iterattributes(self):
        for a in self._interesting_attribute:
            yield a
        return

    def iteritems(self):
        for i in xrange(len(self._interesting_attribute)):
            yield self.ComparableMedicationItem(self._interesting_attribute[i], self._original[i])
        return

    def __getitem__(self, item):
        return self._original[item]


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
    original_1 = ComparableMedicationList(list1, lambda x: x.normalized_string)
    new_list_1 = []
    new_list_2 = ComparableMedicationList(list2, lambda x: x.normalized_string)
    # We keep a list of objects separate from a list of strings, so
    # we don't need to recompute the normalized strings over and over.
    common = []
    for normstring, med1 in original_1.iteritems():
        if normstring in new_list_2:
            common.append(Match(med1, new_list_2.popitem(normstring), 1.0, MATCH_STRING))
        else:
            new_list_1.append(med1)

    return MatchResult(new_list_1, new_list_2.objects, common)


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
    original_1 = ComparableMedicationList(list1, lambda x: x.RxCUIs)
    new_list_1 = []
    new_list_2 = ComparableMedicationList(list2, lambda x: x.RxCUIs)
    # We keep a list of objects separate from a list of strings, so
    # we don't need to recompute the normalized strings over and over.
    common = []
    for concept, med1 in original_1.iteritems():
        if concept == ['NOCODE']:
            new_list_1.append(med1)
        elif concept in new_list_2:
            med2=new_list_2.popitem(concept)
            common.append(Match(med1, med2,
                                1.0 if med2.normalized_dose == med1.normalized_dose else 0.5,
                                MATCH_COMPOUND))
        else:
            new_list_1.append(med1)
    return MatchResult(new_list_1, new_list_2.objects, common)


def medication_list_tradenames(medication_list):
    """Given a medication list, returns a list of the tradenames for each
    element (respecting the original order, so both the original and the
    new lists have the same indices)."""
    return [x.tradenames for x in medication_list]


def medication_list_CUIs(medication_list):
    """Given a medication list, returns a list of the matching CUIs for each
    medication."""
    return [x.CUIs for x in medication_list]


def find_brand_name_matches(c1, concepts_of_c2):
    logging.debug("Testing %r against %r", c1, concepts_of_c2)
    potential_matches = [c1 in t for t in concepts_of_c2 if t is not None]
    logging.debug("Result: %r", potential_matches)
    matches = potential_matches.index(True) \
        if True in potential_matches \
        else None
    return matches


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
    cuis_tradenames = namedtuple("cuis_tradenames", ['cuis', 'tradenames'])
    concepts_and_tradenames = lambda x: cuis_tradenames(x.CUIs, x.tradenames)

    original_1 = ComparableMedicationList(list1, concepts_and_tradenames)
    new_list_1 = []
    new_list_2 = ComparableMedicationList(list2, concepts_and_tradenames)

    # Handlers to unpack the attributes for performing checks
    just_concepts = lambda x: [y.cuis for y in x.iterattributes()]
    just_tradenames = lambda x: [y.tradenames for y in x.iterattributes()]

    # If one of the lists is empty, or there are no known tradenames for
    # any medications, the entire analysis is useless, so we stop analyzing
    # and just return the input.
    if (just_concepts(original_1) == [] or just_tradenames(new_list_2) == []) \
            and (just_concepts(new_list_2) == [] or just_tradenames(original_1) == []):
        return MatchResult(list1, list2, [])

    # We keep a list of objects separate from a list of strings, so
    # we don't need to recompute the normalized strings over and over.
    common = []
    logging.debug("Length of concepts_1: %d", len(original_1))

    for attr, med1 in original_1.iteritems():
        matches = None
        dose_1 = med1.normalized_dose
        concepts_1 = attr.cuis
        if concepts_1 is not None:
            # Test to see if any concept in concepts_1 is one of the tradenames of c2
            for c1 in concepts_1:
                # Find the index of the first medication in list 2 one of whose tradenames c1 matches
                matches = find_brand_name_matches(c1, just_tradenames(new_list_2))
                if matches is not None:
                    med2 = new_list_2.pop(matches)
                    dose_2 = med2.normalized_dose
                    # If the dosages are equal, we have a match
                    match_score = 1.0 if dose_1 == dose_2 else 0.5
                    common.append(Match(med1, med2, match_score, MATCH_BRAND_NAME))
                    break
        if matches is None:
            if med1.tradenames is not None:
                # Test to see if any concept in tradenames_of_c1 is one of the concepts of c2
                for t1 in med1.tradenames:
                    # Find the index of the first medication in list 2 whose concept matches a tradename of a med in list 1
                    matches = find_brand_name_matches(t1, just_concepts(new_list_2))
                    if matches is not None:
                        med2 = new_list_2.pop(matches)
                        dose_2 = med2.normalized_dose
                        # If the dosages are equal, we have a match
                        match_score = 1.0 if dose_1 == dose_2 else 0.5
                        common.append(Match(med1, med2, match_score, MATCH_BRAND_NAME))
                        break

        if matches is None:
            new_list_1.append(med1)
    return MatchResult(new_list_1, new_list_2.objects, common)


def match_by_ingredients(list1, list2, min_match_threshold=0.3):
    """Computes equivalence between two lists of medications by comparing their
    lists of ingredients."""
    formula_dose = namedtuple("formula_dose", ["formula", "normalized_dose"])
    formulas_and_doses = lambda x: formula_dose(x.generic_formula, x.normalized_dose)

    original_1 = ComparableMedicationList(list1, formulas_and_doses)
    new_list_1 = []
    new_list_2 = ComparableMedicationList(list2, formulas_and_doses)
    common = []

    for ph1, item in original_1.iteritems():
        match = [0.0] * len(new_list_2)
        match_index = 0
        for ph2, item2 in new_list_2.iteritems():
            logging.debug("Comparing %r against %r", ph1, ph2)
            for p in ph1.formula:
                if p in ph2.formula:
                    if ph1.normalized_dose != ph2.normalized_dose:
                        # If the daily total dose doesn't match, penalize it
                        match[match_index] = 0.5
                        break
                    else:
                        match[match_index] += 1.0
            # The match score is the average of dose matches
            match[match_index] = match[match_index] / float((len(ph2.formula) + len(ph1.formula)) / 2.0)
            match_index += 1

        # After reverse-sorting the list by score, item [0] is the highest-scoring match.
        top_match_score = -1 if len(match) == 0 else max(match)
        if top_match_score > min_match_threshold:
            top_match_position = match.index(top_match_score)
            med2 = new_list_2.pop(top_match_position)

            logging.debug("Matched %r to %r by generics with score %r",
                          item, med2,
                          top_match_score)
            common.append(Match(item, med2, top_match_score,
                                MATCH_INGREDIENTS))
        else:
            new_list_1.append(item)

    return MatchResult(new_list_1, new_list_2.objects, common)


def build_treatment_lists(concepts, mappings):
    this_treats = set([])
    if concepts is not None:
        for each_concept in concepts:
            for each_treated_thing in mappings.treatment.get(each_concept, []):
                this_treats.add(each_treated_thing)
    return this_treats


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
    # Build a data structure to store the treatments for each medication
    treat = namedtuple("treat", ["cuis", "treatments"])
    concepts_and_treatments = lambda x: treat(x.CUIs, build_treatment_lists(x.CUIs, mappings))
    original_1 = ComparableMedicationList(list1, concepts_and_treatments)
    new_list_1 = []
    new_list_2 = ComparableMedicationList(list2, concepts_and_treatments)

    # Handlers to unpack the attributes for performing checks
    just_concepts = lambda x: [y.cuis for y in x.iterattributes()]
    just_treatments = lambda x: [y.treatments for y in x.iterattributes()]

    logging.debug("Concepts for %r: %r", list1, just_concepts(original_1))
    logging.debug("Concepts for %r: %r", list2, just_concepts(new_list_2))

    if (just_concepts(original_1) == [] or just_concepts(new_list_2) == []):
        # Without CUIs there's nothing to do here.
        return MatchResult(list1, list2, [])

    # We keep a list of objects separate from a list of strings, so
    # we don't need to recompute the normalized strings over and over.
    #my_list_1 = []
    #my_list_2_of_objects = list2[:]
    common = []

    # Build lists of potential treatments
    logging.debug("Treatment list for medication list 1: %r", just_treatments(original_1))
    logging.debug("Treatment list for medication list 2: %r", just_treatments(new_list_2))

    scored_comparison = namedtuple("scored_comparison", ["match", "medication"])

    for treat1, med1 in original_1.iteritems():
        # Compare the "treatment sphere" of each medication in list 1 to the
        # "treatment sphere" of each medication in list 2
        comparison = [scored_comparison(
            match_percentage(treat1, x.attr.treatments),
            x.original)
                      for x in new_list_2.iteritems()]
        comparison.sort(reverse=True)
        # The first item of comparison is now the highest-ranked match
        if len(comparison) > 0 and comparison[0].match >= match_acceptance_threshold:
            # Renormalize match score
            logging.debug("Highest comparison tuple (accepted) for %d: %r", y,
                          comparison[0])
            score = comparison[0].match * highest_possible_match
            matched_item = comparison[0].medication
            position = new_list_2.original_index(matched_item)

            common.append(Match(med1,
                                new_list_2.pop(position),
                                score,
                                MATCH_TREATMENT_INTENT))
        else:
            new_list_1.append(med1)

    return MatchResult(new_list_1, new_list_2.objects, common)
