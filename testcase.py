import match
from medication import ParsedMedication
from mapping_context import MappingContext
from constants import demo_list_1
from constants import demo_list_2
import cPickle as pickle
import bz2
import re
import logging

logging.basicConfig(filename='example.log', level=logging.DEBUG)

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

#med_1 = 'Coreg 25 MG Tablet;TAKE 1 TABLET TWICE DAILY,  WITH MORNING AND EVENING MEAL; RPT'
#med_2 = 'Carvedilol 25 MG Tablet;TAKE 1 TABLET TWICE DAILY,  WITH MORNING AND EVENING MEAL; Rx'
#meds_list_1 = [ParsedMedication(med_1, mappings, "List 1")]
#meds_list_2 = [ParsedMedication(med_2, mappings, "List 2")]

# <Potential reconciliation (66.67% certainty; Ingredient lists match) 
# <Medication 3 @ 0x3626d10: 'PROTONIX' 40 'MG' 'TABLET DELAYED RELEASE' ('TAKE 1 TABLET DAILY.; RX')> <-> 
# <Medication 15 @ 0x37f4210: 'PANTOPRAZOLE SODIUM' 40 'MG' 'TABLET DELAYED RELEASE' ('TAKE 1 TABLET DAILY.; RX')> @ 0x37f4510>
med1 = ParsedMedication('Protonix 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx', mappings, 'List 1')
med2 = ParsedMedication('Pantoprazole Sodium 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx', mappings, 'List 2')
mbi = match.match_by_ingredients([med1], [med2], min_match_threshold=0.7)
