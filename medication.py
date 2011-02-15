import re
from decimal import *
import copy
import logging
import operator
from constants import *

medication_parser=re.compile(r"""^\s*(?P<name>.*?)
                                  \s+(?P<dosage>[0-9\.\/]+)
                                  \s+(?P<units>m?c?k?g|m?d?l)
                                  \s*(?P<formulation>.*?)\s*
                                  \;?
                                  \s*(?P<instructions>.*)""",
                                  re.IGNORECASE | re.VERBOSE)

class Medication(object):
    """Represents a single medication from a list to be reconciled."""
    def __init__(self, original_string):
        super(Medication, self).__init__()
        self._original_string=original_string
        self._normalized_string=self._normalize_string()
    def _normalize_string(self):
        # Uppercase and remove trailing and leading whitespace
        my_string=self.original_string.upper().strip()
        # Remove undesirable trailing punctuation
        for punct in UNDESIRABLE_PUNCTUATION:
            my_string=my_string.strip(punct)
        # Normalize spacing to only one space between components
        my_string=' '.join(my_string.split())
        return my_string
    def original_string():
        doc = "The original_string property."
        def fget(self):
            return self._original_string
        return locals()
    original_string = property(**original_string())
    def normalized_string():
        doc = "The normalized_string property."
        def fget(self):
            return self._normalized_string
        return locals()
    normalized_string = property(**normalized_string())
    def is_empty(self):
        return self.normalized_string.strip()==""
        
def build_regular_expressions(list_of_tuples, formulation):
    my_regexps=[]
    for k, v in list_of_tuples:
        new_k=k[:].replace('%FORM%', formulation)
        my_regexps.append((new_k, v))
    return my_regexps

class ParsedMedication(Medication):
    formulation_regexp_cache={}
    times_regexp_cache={}
    def __init__(self, med_line=None):
        super(ParsedMedication, self).__init__(med_line)
        self._name=None
        self._dose=None
        self._units=None
        self._formulation=None
        self._instructions=None
        self._parsed=False
        self._generic_formula=None
        self._norm_dose=None
        self._cuis=None
        if med_line is not None:
            self.from_text(med_line)
    def from_text(self, med_line):
        med=medication_parser.findall(self.normalized_string)
        if len(med)>0:
            med=med[0]
            self._name=med[0]
            self._dose=med[1]
            self._units=med[2]
            self._formulation=med[3]
            self._instructions=med[4]
            self._parsed=True
        else:
            logging.debug("Could not parse %s. _parsed is %r", med_line,
                          self._parsed)
    def __repr__(self):
        if self._parsed:
            return "<Medication 0x%x: %r %s %r %r (%r)>" % (
                id(self),
                self.name,
                self.dose,
                self.units,
                self.formulation,
                self.instructions)
        else:
            return "<Medication (not parsed) 0x%x: %s>" %(
                id(self),
                self.normalized_string)
    def __str__(self):
        if self._parsed:
            return "%s %s %s %s: %s" % (
                self.name,
                self.dose,
                self.units,
                self.formulation,
                self.instructions)
        else:
            return "%s" % self.normalized_string
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name=copy.copy(value)
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
    def original_line(self):
        return self._original_line
    @property
    def parsed(self):
        return self._parsed
    @property 
    def generic_formula(self):
        return copy.copy(self._generic_formula)
    def _normalize_drug_name(self, drug_name):
        truncated=drug_name.split('@')[0].strip().upper()
        components=truncated.split()
        final_version=[]
        # Replace abbreviations
        for x in components:
            if x in abbreviations:
                final_version.append(abbreviations[x])
            else:
                final_version.append(x)
        return ' '.join(final_version)
    def compute_generics(self, rx, concept_names):
        """Computes the generic equivalent of a drug according to RXNorm."""
        concepts=self.CUIs(rx, concept_names)
        if concepts is not None:
            logging.debug("Concepts for %s=%r", self.name, concepts)
            try:
                concept=concepts.pop()
                ingredients=rx.formulas[concept]
                self._generic_formula=[self._normalize_drug_name(x.name)
                                       for x in ingredients]
                return 
            except KeyError:
                logging.debug("Couldn't find ingredients for %s", concept)
        else:
            logging.debug("Couldn't find %s in RXNorm" % self.name)
        self._generic_formula=[self._normalize_drug_name(self.name)]
        return 
    def CUIs(self, rx, concept_names):
        if self._cuis is None:
            if self.name is not None:
                name_of_medication=self.name.lower()
                if name_of_medication in concept_names:
                    concepts=copy.copy(concept_names[name_of_medication])
                    self._cuis=concepts
        return copy.copy(self._cuis)
    def tradenames(self, rx, concept_names):
        my_cuis=self.CUIs(rx, concept_names)
        if my_cuis is None:
            return []
        return  reduce(operator.add, [[x._concept2.CUI 
                                       for x in rx.relations 
                                       if x.relation=='tradename_of'
                                          and x._concept1.CUI==y] 
                                      for y in my_cuis])
    def normalize_dose(self):
        """Takes a drug tuple (i.e. the output of the regular expression listed 
        above) and returns the total number of units a day the patient is 
        receiving"""
        number_of_units=None # Assume that (if not mentioned) there is 
                          #one tablet/capsule/whatever per unit of time
        form=self.formulation
        # Make sure that we have a formulation we know about! Replace formulations 
        # with standard names.
        for known_formulation in physical_forms:
            if known_formulation in form:
                form=known_formulation
                continue
        logging.debug("The form of %r is %s.", self, form)
        if form in ParsedMedication.formulation_regexp_cache:
            regexps=ParsedMedication.formulation_regexp_cache[form]
        else:
            regexps=build_regular_expressions(known_number_of_doses, form)
            logging.debug("Regexps for form %s=%r", form, regexps)
            ParsedMedication.formulation_regexp_cache[form]=regexps
        for regexp, num in regexps:
            if num==-1:
                result=re.findall(regexp, self.instructions)
                if len(result)>0:
                    number_of_units=int(result[0])
                    continue
            else:
                if regexp in self.instructions:
                    number_of_units=num
                    continue
        if number_of_units is None:
            logging.debug("Failed matching number of units on %r; assuming 1", self)
            number_of_units=1
        if form in ParsedMedication.times_regexp_cache:
            regexps=ParsedMedication.times_regexp_cache[form]
        else:
            regexps=build_regular_expressions(known_times_per_day, form)
            ParsedMedication.times_regexp_cache[form]=regexps
        times_per_day=None
        for regexp, times in regexps:
            if times==-1:
                # Regular expression to be parsed
                result=re.findall(regexp, self.instructions)
                if len(result)>0:
                    times_per_day=int(result[0])
                    continue
            else:
                if regexp in self.instructions:
                    times_per_day=times
                    continue
        if times_per_day is None:
            logging.debug("Failed matching times per day on %r. Assuming 1.", self)
            times_per_day=1
        # else:
            #print drug_tuple, "is taken %d times a day" % times_per_day
        #logging.debug("The total quantity of %r is %1.2f %s a day", 
        #    self.name, self.dose*times_per_day*number_of_units, self.units)
        try:
            self._norm_dose='%s %s*%d*%d' % (
                str(self.dose), self.units, times_per_day, number_of_units)
        except ValueError:
            return
        logging.debug("The normalized dose for %s is %s", self, 
                      self._norm_dose)
    @property
    def normalized_dose(self):
        if self._norm_dose is None:
            self.normalize_dose()
        return copy.copy(self._norm_dose)
        