import match
from medication import ParsedMedication
from mapping_context import MappingContext
from constants import demo_list_1
from constants import demo_list_2
import cPickle as pickle
import bz2
import re

id_regex = re.compile(r'(?:0x[0-9a-f]{7,})')

def rmObjIds(repr_string):
    return id_regex.sub('', repr_string)

medId_regex = re.compile(r'(<Medication\s+)\d+')

def rmMedIds(repr_string):
    return medId_regex.sub(r'\1', repr_string)

def rmAllIds(repr_string):
    return(rmMedIds(rmObjIds(repr_string)))

#rx = pickle.load(bz2.BZ2File('../MedRec/tests/rxnorm.pickle.bz2', 'r'))
rx = pickle.load(bz2.BZ2File('../MedRec/rxnorm.pickle.bz2', 'r'))
ts = pickle.load(bz2.BZ2File('../MedRec/treats.pickle.bz2', 'r'))
mappings = MappingContext(rx, ts)

meds_list_1 = [pm for pm in
  [ParsedMedication(x, mappings, "List 1") for x in demo_list_1]
    if pm.parsed]
meds_list_2 = [pm for pm in
  [ParsedMedication(x, mappings, "List 2") for x in demo_list_2]
    if pm.parsed]

matched_by_brand_name = match.match_by_brand_name(meds_list_1, meds_list_2)
matched_by_brand_name_rev = match.match_by_brand_name(meds_list_2, meds_list_1)

mfor = matched_by_brand_name
mrev = matched_by_brand_name_rev

print "List1 forward"
mfor_list1 = [repr(x) for x in mfor.list1]
mfor_list1.sort()
print '\n'.join(mfor_list1)

print "List1 reversed"
mrev_list1 = [repr(x) for x in mrev.list1]
mrev_list1.sort()
print '\n'.join(mrev_list1)

print "List2 forward"
mfor_list2 = [repr(x) for x in mfor.list2]
mfor_list2.sort()
print '\n'.join(mfor_list2)

print "List2 reversed"
mrev_list2 = [repr(x) for x in mrev.list2]
mrev_list2.sort()
print '\n'.join(mrev_list2)

print "Reonciled forward"
mfor_reconciled = [repr(x) for x in mfor.reconciled]
mfor_reconciled.sort()
print '\n'.join(mfor_reconciled)

print "Reonciled reversed"
mrev_reconciled = [repr(x) for x in mrev.reconciled]
mrev_reconciled.sort()
print '\n'.join(mrev_reconciled)

