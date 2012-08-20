'''
Created on Oct 29, 2011

@author: jherskovic
'''
import shelve


class MappingContextError(Exception): pass


class MappingContext(object):
    """Packages the information needed to map medications to each other and the
    UMLS."""

    def __init__(self, rxnorm, treatment, drug_problem=None, concept_name_index=None):
        self._rxnorm = rxnorm
        self._treatment = treatment
        self._drug_problem = drug_problem
        concept_names = {}
        if concept_name_index is not None:
            self._concept_names = shelve.open(concept_name_index, flag='r')
            return
        for c in rxnorm.concepts:
            cn = rxnorm.concepts[c]._name.lower()
            cn = cn.split('@')[0].strip() # Just use stuff to the left of a @ for a concept name
            if cn in concept_names:
                concept_names[cn].add(c)
            else:
                concept_names[cn] = set([c])
            # Use a shelf for
        self._concept_names = concept_names

    @property
    def rxnorm(self):
        return self._rxnorm

    @property
    def treatment(self):
        return self._treatment

    @property
    def concept_names(self):
        return self._concept_names

    @property
    def drug_problem(self):
        return self._drug_problem

    def __repr__(self):
        rxcount = len(self._rxnorm.concepts)
        tscount = len(self._treatment)
        dpcount = len(self._drug_problem._drug_problem_dict) if self._drug_problem is not None else 0
        return "<MappingContext RXNORM: %d; treats: %d; drug/problem: %d; 0x%x>" % (
        rxcount, tscount, dpcount, id(self),)