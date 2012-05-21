import cPickle as pickle
import bz2
import os
from mapping_context import MappingContext

rxnormFname = '../rxnorm.pickle.bz2.big.new'
treatsFname = 'treats.pickle.bz2'
drugProbFname = 'drug_problem_relations.pickle.bz2'

if os.path.isfile(rxnormFname):
    rxnorm = pickle.load(bz2.BZ2File(rxnormFname, 'r'))
else:
    rxnorm = None
if os.path.isfile(treatsFname):
    treats = pickle.load(bz2.BZ2File(treatsFname, 'r'))
else:
    treats = None
if os.path.isfile(drugProbFname):
    drug_problem_relations = pickle.load(bz2.BZ2File(drugProbFname, 'r'))
else:
    drug_problem_relations = None
if rxnorm is not None:
    mappings = MappingContext(rxnorm, treats, drug_problem_relations)
else:
    mappings = None
