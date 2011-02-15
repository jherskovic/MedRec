#!/usr/bin/env python

class Drug(object):
    __slots__=["_cui", "_name", "_st"]
    # Extract from MRCONSO by CUI - grep RXNORM MRCONSO.RRF | head
    def __init__(self, MRCONSO_LINE):
        items=MRCONSO_LINE.split('|')
        self._cui=items[0]
        self._name=items[14]
        self._st=None
    @property
    def CUI(self):
        return self._cui
    def get_semtypes(self):
        return set([type_kinds[x] for x in self._st])
    def set_semtypes(self, st):
        self._st=set([reverse_type_kinds[x] for x in st])
    semtypes=property(get_semtypes, set_semtypes)
    def __hash__(self):
        return hash(self._cui)
    def __repr__(self):
        return "<Drug %s (%s) [%s] @0x%x>" % (self._name, self._cui, 
                                              self.semtypes,
                                              id(self)) 
    @property
    def name(self):
        return self._name
        
# List obtained via:
# grep RXNORM MRREL.RRF | awk -F\| '{ print $8 }' | sort | uniq

relation_kinds="""consists_of
constitutes
contained_in
contains
dose_form_of
form_of
has_dose_form
has_form
has_ingredient
has_precise_ingredient
has_quantified_form
has_tradename
ingredient_of
inverse_isa
isa
precise_ingredient_of
quantified_form_of
reformulated_to
reformulation_of
tradename_of""".split('\n')

class Relation(object):
    __slots__=["_concept1", "_concept2", "_relation"]
    def __init__(self, MRREL_LINE, concepts):
        items=MRREL_LINE.split('|')
        if items[7]=="" or items[10]!='RXNORM': 
            self._relation=None
        else:
            self._relation=relation_kinds.index(items[7])
        self._concept1=concepts[items[0]]
        self._concept2=concepts[items[4]]
    def get_relation(self):
        return relation_kinds[self._relation] if self._relation is not None else None
    relation=property(get_relation)

type_kinds={}
reverse_type_kinds={}

class SemanticTypeLine(object):
    __slots__=['_cui', '_type']
    def __init__(self, MRSTY_LINE):
        global type_kinds
        items=MRSTY_LINE.split('|')
        tk=items[1]
        self._cui=items[0]
        if tk in type_kinds:
            self._type=tk
        else:
            type_kinds[tk]=items[3]
            reverse_type_kinds[items[3]]=tk
            self._type=tk
    @property
    def semtype(self):
        return type_kinds[self._type]
    @property
    def CUI(self):
        return self._cui
        
class RXNORM(object):
    def __init__(self, concepts, relations, ingredients):
        self.concepts=concepts
        self.relations=relations
        self.formulas=ingredients
    def __getstate__(self):
        return {"c": self.concepts, 
                "r": self.relations,
                "f": self.formulas,
                "t": type_kinds,
                "rt": reverse_type_kinds}
    def __setstate__(self, state):
        global type_kinds
        global reverse_type_kinds
        self.concepts=state['c']
        self.relations=state['r']
        self.formulas=state['f']
        type_kinds=state['t']
        reverse_type_kinds=state['rt']
