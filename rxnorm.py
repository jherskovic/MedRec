#!/usr/bin/env python

class Drug(object):
    """Class to represent a drug from an MRCONSO line. Assumes that
    appropriate selection of MRCONSO lines is done prior to instantiation."""
    __slots__ = ["_cui", "_name", "_st", "_is_brandname"]
    # Extract from MRCONSO by CUI - grep RXNORM MRCONSO.RRF | head
    def __init__(self, MRCONSO_LINE):
        items = MRCONSO_LINE.split('|')
        self._cui = items[0]
        self._name = items[14]
        self._st = None
        self._is_brandname = items[12] == "BN"
    @property
    def CUI(self):
        """Property: the CUI of the drug represented by an instance of this class."""
        return self._cui
    @property
    def semtypes(self):
        """Property: a set of semantic type abbreviations for the drug 
            represented by an instance of this class."""
        return set([type_kinds[x] for x in self._st])
    @semtypes.setter
    def semtypes(self, st):
        """Setter: given a sequence of semantic type names, set their 
            abbreviations on this Drug object."""
        self._st = set([reverse_type_kinds[x] for x in st])
    def __hash__(self):
        return hash(self._cui)
    def __repr__(self):
        return "<Drug %s (%s) [%s] %s @0x%x>" % (self._name, self._cui,
                                              self.semtypes,
                                              "(BN)" if self._is_brandname else "",
                                              id(self)) 
    @property
    def name(self):
        """Property: the RXNORM name of this drug."""
        return self._name
    @property
    def is_brandname(self):
        """Property: True if the name property of this Drug object is a brand name, False otherwise."""
        return self._is_brandname

class Relation(object):
    """Class to represent a line from MRREL as to its CUIs and the relation
    (rela) between the CUIs."""
    __slots__ = ["_concept1", "_concept2", "_relation"]
    def __init__(self, MRREL_LINE, concepts):
        """'MRREL_LINE' is as the name suggests a line from MRREL;
        'concepts' is a sequence of rxnorm.Drug objects (or objects
        with a like interface)."""
        items = MRREL_LINE.split('|')
        if items[7] == "" or items[10] != 'RXNORM': 
            self._relation = None
        else:
            self._relation = items[7]
        self._concept1 = concepts[items[0]]
        self._concept2 = concepts[items[4]]
    @property
    def relation(self):
        return self._relation
    @property
    def concept1(self):
        return self._concept1
    @property
    def concept2(self):
        return self._concept2
    def __repr__(self):
        return "<Relation %r %r %r>" % (self._concept1, self.relation,
                                        self._concept2)

type_kinds = {}
reverse_type_kinds = {}

class SemanticTypeLine(object):
    """Class to represent an MRSTY line as to its CUI and semantic type."""
    __slots__ = ['_cui', '_type']
    def __init__(self, MRSTY_LINE):
        # These two dictionaries exist at the module level, to be available
        # to Drug and RXNORM objects, but must be modified within instances
        # of this class
        global type_kinds
        global reverse_type_kinds
        items = MRSTY_LINE.split('|')
        tk = items[1]
        self._cui = items[0]
        if tk in type_kinds:
            self._type = tk
        else:
            type_kinds[tk] = items[3]
            reverse_type_kinds[items[3]] = tk
            self._type = tk
    @property
    def semtype(self):
        """Property: the name of the sementic type for this MRSTY line;
            depends on the global type_kinds dictionary."""
        return type_kinds[self._type]
    @property
    def CUI(self):
        """Property: the CUI of the drug associated with this MRSTY line."""
        return self._cui
    def __repr__(self):
        return "<SemanticType %s: '%s' 0x%x>" % (self._cui, type_kinds[self._type], id(self))
        
class RXNORM(object):
    def __init__(self, concepts, relations, ingredients):
        # 'concepts' is a dictionary of Drug objects indexed by CUI
        self.concepts = concepts
        # 'relations' is a list of Relation objects
        self.relations = relations
        # 'formulas' is a dictionary of sets of Drug objects indexed
        # by the CUI of the drug of which they are a formulation
        self.formulas = ingredients
    def __getstate__(self):
        return {"c": self.concepts,
                "r": self.relations,
                "f": self.formulas,
                "t": type_kinds,
                "rt": reverse_type_kinds}
    def __setstate__(self, state):
        global type_kinds
        global reverse_type_kinds
        self.concepts = state['c']
        self.relations = state['r']
        self.formulas = state['f']
        type_kinds = state['t']
        reverse_type_kinds = state['rt']
