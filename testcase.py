import match
from medication import ParsedMedication
from mapping_context import MappingContext
#from constants import demo_list_1
#from constants import demo_list_2
import cPickle as pickle
import bz2
import re
import logging

logging.basicConfig(filename='example.log', level=logging.DEBUG)

demo_list_1 = """Zoloft 50 MG Tablet;TAKE 1 TABLET DAILY.; RPT
Warfarin Sodium 2.5 MG Tablet;TAKE AS DIRECTED.; Rx
Lipitor 10 MG Tablet;TAKE 1 TABLET DAILY.; Rx
Protonix 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx
Warfarin Sodium 5 MG Tablet;TAKE 1 TABLET DAILY AS DIRECTED.; Rx
Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx
Lisinopril 5 MG Tablet;TAKE  TABLET TWICE DAILY; Rx
Coreg 25 MG Tablet;TAKE 1 TABLET TWICE DAILY,  WITH MORNING AND EVENING MEAL; RPT
Enalapril 20mg;TAKE 1 TABLET TWICE DAILY,  WITH MORNING AND EVENING MEAL; RPT
""".split('\n')
demo_list_2 = """Warfarin Sodium 2.5 MG Tablet;TAKE AS DIRECTED.; Rx
Aspirin 325 mg;TAKE 1 TABLET DAILY AS DIRECTED.; Rx
metformin 1 g;TAKE 1 TABLET TWICE DAILY,  WITH MORNING AND EVENING MEAL; Rx
Nexium 40 mg;TAKE 1 TABLET DAILY.; Rx
Norvasc 5 mg;TAKE 1 TABLET TWICE DAILY; Rx
Kayexalate 15 g;TAKE 1 TABLET DAILY.; Rx
Toprol-XL 50;TAKE 1 TABLET DAILY.; Rx
enalapril 20 mg;TAKE 1 TABLET DAILY.; Rx
Vytorin 10/40;TAKE 1 TABLET 3 TIMES DAILY.; Rx.""".split('\n')

new_list_1, new_list_2, toss = open('docpairs/pair0000005.txt').read().split('******')
demo_list_1 = new_list_1.split('\n')
demo_list_2 = new_list_2.split('\n')

rx = pickle.load(bz2.BZ2File('../MedRec/tests/rxnorm.pickle.bz2', 'r'))
#rx = pickle.load(bz2.BZ2File('../MedRec/rxnorm.pickle.bz2', 'r'))
ts = pickle.load(bz2.BZ2File('../MedRec/treats.pickle.bz2', 'r'))
mappings = MappingContext(rx, ts)

#meds_list_1 = [pm for pm in
#  [ParsedMedication(x, mappings, "List 1") for x in demo_list_1]
#    if pm.parsed]
#meds_list_2 = [pm for pm in
#  [ParsedMedication(x, mappings, "List 2") for x in demo_list_2]
#    if pm.parsed]

meds_list_1 = [ParsedMedication(x, mappings, "List 1") for x in demo_list_1]
meds_list_2 = [ParsedMedication(x, mappings, "List 2") for x in demo_list_2]

#matchResult = match.match_by_treatment(meds_list_1, meds_list_2, mappings)
mbs = match.match_by_strings(meds_list_1, meds_list_2)
mbbn = match.match_by_brand_name(meds_list_1, meds_list_2)
mbi = match.match_by_ingredients(meds_list_1, meds_list_2)
mbt = match.match_by_treatment(meds_list_1, meds_list_2, mappings)