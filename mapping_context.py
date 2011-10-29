'''
Created on Oct 29, 2011

@author: jherskovic
'''
class MappingContext(object):
    """Packages the information needed to map medications to each other and the
    UMLS."""
    def __init__(self, rxnorm, treatment):
        self._rxnorm=rxnorm
        self._treatment=treatment
        concept_names = {}
        for c in rxnorm.concepts:
            cn = rxnorm.concepts[c]._name.lower()
            cn = cn.split('@')[0].strip() # Just use stuff to the left of a @ for a concept name
            if cn in concept_names:
                concept_names[cn].add(c)
            else:
                concept_names[cn] = set([c])
        self._concept_names=concept_names
    @property
    def rxnorm(self):
        return self._rxnorm
    @property
    def treatment(self):
        return self._treatment
    @property
    def concept_names(self):
        return self._concept_names