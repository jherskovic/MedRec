#!/usr/bin/python
"""
medication.py

Defines the Medication and ParsedMedication classes. Medication represents a 
single line from the medication lists to reconcile; ParsedMedication is a 
subclass of Medication that decomposes a line according to regexps (see
constants.py)

Created by Jorge Herskovic 
Copyright (c) 2011 UTHealth School of Biomedical Informatics. All rights reserved.
"""

import re
from decimal import *
import copy
import logging
import operator
from constants import *
from mapping_context import MappingContextError

medication_parser = re.compile(r"""^\s*(?P<name>.*?)
                                  \s+(?P<dose>[0-9\.\/]+)
                                  \s*(?P<units>([mck]|mc)g|[md]l)
                                  \s*(?P<formulation>.*?)
                                  ;
                                  \s*?(?P<instructions>.*)""",
                                  re.IGNORECASE | re.VERBOSE)

def _sequential_id_gen(starting=0):
    while True:
        yield starting
        starting += 1

_sequential_id=_sequential_id_gen()

def normalize_field(field):
    """Remove leading & trailing whitespace and undesirable punctuation;
    normalize internal spacing."""
    my_field = field.upper().strip()
    # Remove undesirable trailing and leading punctuation
    for punct in UNDESIRABLE_PUNCTUATION:
        my_field = my_field.strip(punct)
    # Normalize spacing to only one space between components
    my_field = ' '.join(my_field.split())
    return my_field

class MedicationInitializationError(Exception): pass

class Medication(object):
    """Represents a single medication from a list to be reconciled."""
    def __init__(self, original_string, provenance=""):
        self._original_string = original_string
        self._normalized_string = normalize_field(original_string)
        self._provenance = provenance
        self._seq_id=_sequential_id.next()
    def _normalize_field(self, field):
        return normalize_field(field)
    @property
    def original_string(self):
        "The original unparsed string for the medication"
        return self._original_string
    @property
    def normalized_string(self):
        "The original string, normalized using _normalize_string()"
        return self._normalized_string
    def is_empty(self):
        return self.normalized_string.strip() == ""
    @property
    def provenance(self):
        "The medication's provenance"
        return self._provenance
    def __eq__(self, other):
        return self._normalized_string == other._normalized_string
    def __ne__(self, other):
        return self._normalized_string != other._normalized_string
    def __gt__(self, other):
        return self._normalized_string >= other._normalized_string
    def __lt__(self, other):
        return self._normalized_string < other._normalized_string
        
def build_regular_expressions(list_of_tuples, formulation):
    my_regexps = []
    for k, v in list_of_tuples:
        new_k = k[:].replace('%FORM%', formulation)
        my_regexps.append((new_k, v))
    return my_regexps

class ParsedMedication(Medication):
    formulation_regexp_cache = {}
    times_regexp_cache = {}
    def __init__(self, med_info, context=None, provenance=""):
        """ParsedMedication constructor. It attempts to parse the med_line 
        arg into its components using the from_text() method. Pass
        a MappingContext as part of the context parameter to provide 
        a version of rxnorm to perform computations. Pass a provenance
        to assist in reconciling several lists of medications."""
        if isinstance(med_info, dict):
            # FIXME: for now we fabricate a synthetic med_line
            if med_info.get('original_line'):
                med_line = med_info.get('original_line')
            else:
                med_line = self._dict_to_string(med_info)
        else:
            med_line = med_info
        super(ParsedMedication, self).__init__(med_line, provenance)
        self._name = None
        self._dose = None
        self._units = None
        self._formulation = None
        self._instructions = None
        self._generic_formula = None
        self._norm_dose = None
        self._cuis = None
        self._tradenames = None
        self._problems = None
        self._mappings = context
        if isinstance(med_info, str):
            self._from_text(med_info)
        else:
            self._from_dict(med_info)
    def _dict_to_string(self, med_dict):
        return "%(name)s %(dose)s %(units)s %(formulation)s; %(instructions)s" % med_dict
    def _from_text(self, med_line):
        """Separates a medication string into its components according to the
        medication_parser regular expression."""
        #super(ParsedMedication, self).from_text(med_line)
        med = medication_parser.findall(self.normalized_string)
        if len(med) > 0:
            med = med[0]
            self._name = self._normalize_field(med[0])
            self._dose = self._normalize_field(med[1])
            self._units = self._normalize_field(med[2])
            self._formulation = self._normalize_field(med[3])
            self._instructions = self._normalize_field(med[4])
            self._norm_dose = self._normalize_dose()
        else:
            logging.debug("Could not parse %s.", med_line)
    def _from_dict(self, med_dict):
        self._name = self._normalize_field(med_dict['name'])
        self._dose = self._normalize_field(med_dict['dose'])
        self._units = self._normalize_field(med_dict['units'])
        self._formulation = self._normalize_field(med_dict['formulation'])
        self._instructions = self._normalize_field(med_dict['instructions'])
        self._norm_dose = self._normalize_dose()
    def __repr__(self):
        return "<Medication %d @ 0x%x: %r %s %r %r (%r)>" % (
            self._seq_id,
            id(self),
            self.name,
            self.dose,
            self.units,
            self.formulation,
            self.instructions)
    def __str__(self):
        return "%s %s %s %s: %s" % (
            self.name,
            self.dose,
            self.units,
            self.formulation,
            self.instructions)
    @property
    def name(self):
        return self._name
    @property
    def dose(self):
        return self._dose
    @property
    def units(self):
        return self._units
    @property
    def formulation(self):
        return copy.copy(self._formulation)
    @property
    def instructions(self):
        return copy.copy(self._instructions)
    @property
    def original_string(self):
        return self._original_string
    @property 
    def generic_formula(self):
        if self._generic_formula is None:
            if self._mappings is None:
                raise MappingContextError, "Requires an instance initialized with a MappingContext object."
            self._compute_generics()
        return copy.copy(self._generic_formula)
    def as_dictionary(self):
        return {'medication_name': str(self.name),
                'dose': str(self.dose),
                'units': str(self.units),
                'formulation': str(self.formulation),
                'instructions': str(self.instructions),
                'original_string': self.original_string,
                'provenance': self.provenance,
                'normalized_dose': self._norm_dose,
                'id': self._seq_id,
               }
    def _normalize_drug_name(self, drug_name):
        truncated = drug_name.split('@')[0].strip().upper()
        components = truncated.split()
        final_version = []
        # Replace abbreviations
        for x in components:
            if x in abbreviations:
                final_version.append(abbreviations[x])
            else:
                final_version.append(x)
        return ' '.join(final_version)
    @property
    def mappings(self):
        return self._mappings
    def _compute_generics(self):
        """Computes the generic equivalent of a drug according to RXNorm."""
        mappings=self._mappings
        if mappings is None:
            raise MappingContextError, "Requires an instance initialized with a MappingContext object."
        concepts = self.CUIs
        if concepts is not None and len(concepts) > 0:
            logging.debug("Concepts for %s=%r", self.name, concepts)
            try:
                concept = concepts.pop()
                ingredients = mappings.rxnorm.formulas[concept]
                self._generic_formula = [self._normalize_drug_name(x.name)
                                       for x in ingredients]
                return 
            except KeyError:
                logging.debug("Couldn't find ingredients for %s", concept)
        else:
            logging.debug("Couldn't find %s in RXNorm" % self.name)
        self._generic_formula = [self._normalize_drug_name(self.name)]
        return 
    @property
    def CUIs(self):
        mappings = self._mappings
        if mappings is None:
            raise MappingContextError, "Requires an instance initialized with a MappingContext object."
        if self._cuis is None:
            name_of_medication = self.name.lower()
            if name_of_medication in mappings.concept_names:
                concepts = copy.copy(mappings.concept_names[name_of_medication])
                self._cuis = concepts
            else:
                self._cuis = set()
        return copy.copy(self._cuis)
    @property
    def tradenames(self):
        mappings=self._mappings
        if mappings is None:
            raise MappingContextError, "Requires an instance initialized with a MappingContext object."
        if self._tradenames is None:
            self._tradenames = []
            my_cuis = self.CUIs
            if self.CUIs is not None and len(self.CUIs) > 0:
                self._tradenames = reduce(operator.add, [[x._concept2.CUI 
                                          for x in mappings.rxnorm.relations 
                                          if x.relation == 'tradename_of'
                                              and x._concept1.CUI == y] 
                                          for y in my_cuis])
        return copy.copy(self._tradenames)
    @property
    def problems(self):
        if self._problems is not None:
            return copy.copy(self._problems)
        if self._cuis is None:
            return []
        mappings = self._mappings
        if mappings is None:
            raise MappingContextError, "Requires an instance initialized with a MappingContext object."
        elif mappings.drug_problem is None:
            raise MappingContextError, "Requires that the MappingContext object be initialized with a drug/problem dataset."
        problems_set = set()
        cuis = self._cuis
        for cui in cuis:
            for problem in mappings.drug_problem.problem_by_drug_cui(cui):
                problems_set.add(problem)
        problems_list = list(problems_set)
        problems_list.sort()
        self._problems = problems_list
        return copy.copy(self._problems)
        
    def _normalize_dose(self):
        """Takes a drug tuple (i.e. the output of the regular expression listed 
        above) and returns the total number of units a day the patient is 
        receiving"""
        # Assume that (if not mentioned) there is 
        # one tablet/capsule/whatever per unit of time
        number_of_units = None
        form = self.formulation
        # Make sure that we have a formulation we know about! Replace formulations 
        # with standard names.
        for known_formulation in physical_forms:
            if known_formulation in form:
                form = known_formulation
                continue
        logging.debug("The form of %r is %s.", self, form)
        if form in ParsedMedication.formulation_regexp_cache:
            regexps = ParsedMedication.formulation_regexp_cache[form]
        else:
            # Keep a cache of the regular expressions we build; doing so is
            # much faster than building them for each and every medication 
            regexps = build_regular_expressions(known_number_of_doses, form)
            logging.debug("Regexps for form %s=%r", form, regexps)
            ParsedMedication.formulation_regexp_cache[form] = regexps
        for regexp, num in regexps:
            if num == -1:
                result = re.findall(regexp, self.instructions)
                if len(result) > 0:
                    number_of_units = int(result[0])
                    continue
            else:
                if regexp in self.instructions:
                    number_of_units = num
                    continue
        if number_of_units is None:
            logging.debug("Failed matching number of units on %r; assuming 1", self)
            number_of_units = 1
        if form in ParsedMedication.times_regexp_cache:
            regexps = ParsedMedication.times_regexp_cache[form]
        else:
            regexps = build_regular_expressions(known_times_per_day, form)
            ParsedMedication.times_regexp_cache[form] = regexps
        times_per_day = None
        for regexp, times in regexps:
            if times == -1:
                # Regular expression to be parsed
                result = re.findall(regexp, self.instructions)
                if len(result) > 0:
                    times_per_day = int(result[0])
                    continue
            else:
                if regexp in self.instructions:
                    times_per_day = times
                    continue
        if times_per_day is None:
            logging.debug("Failed matching times per day on %r. Assuming 1.", self)
            times_per_day = 1
        # else:
            #print drug_tuple, "is taken %d times a day" % times_per_day
        #logging.debug("The total quantity of %r is %1.2f %s a day", 
        #    self.name, self.dose*times_per_day*number_of_units, self.units)
        try:
            return '%s %s*%d*%d' % (
                str(self.dose), self.units, times_per_day, number_of_units)
        except ValueError:
            return
        logging.debug("The normalized dose for %s is %s", self,
                      self._norm_dose)
    @property
    def normalized_dose(self):
        if self._norm_dose is None:
            self._normalize_dose()
        return copy.copy(self._norm_dose)
    def fieldwise_comparison(self, other):
        """Compares two medication objects field by field, based on the 
        contents of the MEDICATION_FIELDS constant. Returns a set containing
        the identical fields."""
        result=set()
        for field in MEDICATION_FIELDS.keys():
            if self.__getattribute__(field)==other.__getattribute__(field):
                result.add(MEDICATION_FIELDS[field])
        return list(result)
    def _is_eq(self, other):
        """We test equality on name, dose, units, formulation, and
        instructions; be ridiculously conservative in matching."""
        if self._name == other._name and self._dose == other._dose and \
               self._units == other._units and \
               self._formulation == other._formulation and \
               self._instructions == other._instructions:
            return True
        return False
    def __eq__(self, other):
        return self._is_eq(other)
    def __ne__(self, other):
        return not self._is_eq(other)
    def _is_lt(self, other):
        """We test magnitude on the medication name, formulation, and normalized dose."""
        if self._name < other._name:
            return True
        elif self._name > other._name:
            return False
        elif self._formulation < other._formulation:
            return True
        elif self._formulation > other._formulation:
            return False
        elif self._norm_dose <= other._norm_dose:
            return True
        elif self._norm_dose > other._norm_dose:
            return False
    def __lt__(self, other):
        return self._is_lt(other)
    def __gt__(self, other):
        return not self._is_lt(other)

def find_missing_keys(dikt, reqd_fields):
    missing_fields = []
    for field in reqd_fields:
        if not dikt.get(field):
            missing_fields.append(field)
    return missing_fields

def make_medication(med_info, mappings=None, provenance=None):
    """Factory function to return a ParsedMedication object if 'med_info' is
    suitably parseable, a Medication object otherwise."""
    reqd_fields = ('name', 'units', 'dose', 'formulation', 'instructions','original_line')
    argz = {}
    if mappings:
        argz['context'] = mappings
    if provenance:
        argz['provenance'] = provenance
    if isinstance(med_info, dict):
        missing_fields = find_missing_keys(med_info, reqd_fields)
        if len(missing_fields) > 0:
            raise MedicationInitializationError, "Can't construct a ParsedMedication without fields %r" % missing_fields
        return ParsedMedication(med_info, **argz)
    elif isinstance(med_info, str):
        med_match = medication_parser.match(normalize_field(med_info))
        if med_match:
            med_dict = med_match.groupdict()
            med_dict['original_line'] = med_info
            missing_fields = find_missing_keys(med_dict, reqd_fields)
            if len(missing_fields) > 0:
                return Medication(med_info, provenance=argz.get('provenance', ''))
            return ParsedMedication(med_dict, **argz)
        return Medication(med_info, provenance=argz.get('provenance', ''))
    else:
        raise MedicationInitializationError, "Don't know how to construct a Medication object from a %s" % type(med_info)
