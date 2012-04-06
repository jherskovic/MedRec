import match
from medication import ParsedMedication
from mapping_context import MappingContext
import cPickle as pickle
import bz2

rx = pickle.load(bz2.BZ2File('../MedRec/tests/rxnorm.pickle.bz2', 'r'))
#rx = pickle.load(bz2.BZ2File('../MedRec/rxnorm.pickle.bz2', 'r'))
ts = pickle.load(bz2.BZ2File('../MedRec/treats.pickle.bz2', 'r'))
mappings = MappingContext(rx, ts)

pm1 = ParsedMedication('Pramipexole 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx', mappings)
l1 = [pm1]
pm2 = ParsedMedication('Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx', mappings)
l2 = [pm2]

mr = match.match_by_brand_name([pm1], [pm2])
print mr.list1
print mr.list2
print mr.reconciled

