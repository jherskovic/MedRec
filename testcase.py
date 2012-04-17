import match
from medication import ParsedMedication
from mapping_context import MappingContext
#from constants import demo_list_1
#from constants import demo_list_2
import cPickle as pickle
import bz2
import re
import logging
import sys

rx = pickle.load(bz2.BZ2File('../MedRec/tests/rxnorm.pickle.bz2', 'r'))
#rx = pickle.load(bz2.BZ2File('../MedRec/rxnorm.pickle.bz2', 'r'))
ts = pickle.load(bz2.BZ2File('../MedRec/treats.pickle.bz2', 'r'))
mappings = MappingContext(rx, ts)

#Paxil = ts['C0376414']
#Paroxetine = ts['C0070122']
#Zoloft = ts['C0284660']
#Sertraline = ts['C0074393']
#duloxetine = ts['C0245561']
#Cymbalta = ts['C1505021']
#
#medsTuple = (('Paxil', Paxil), ('Paroxetine', Paroxetine), ('Zoloft', Zoloft), ('Sertraline', Sertraline), ('duloxetine', duloxetine), ('Cymbalta', Cymbalta),)
#
#def match_percentage(set1, set2):
#    """Computes Hooper's consistency to use as a match percentage"""
#    len_1 = len(set1)
#    len_2 = len(set2)
#    if len_1 + len_2 == 0:
#        return 0.0
#    len_common = len(set1 & set2)
#    return float(len_common) / float(len_1 + len_2 - len_common)
#
#def byTreatment(meds, acc):
#    first = meds[0]
#    rest = meds[1:]
#    if len(rest) == 0:
#        return acc
#    firstOfRest = rest[0]
#    acc = byTreatmentHelper(first, rest, acc)
#    return byTreatment(rest, acc)
#
#def byTreatmentHelper(med1, meds, acc):
#    if len(meds) == 0:
#        return acc
#    med2 = meds[0]
#    acc.append(((match_percentage(med1[1], med2[1]), med1[0], med2[0])))
#    return byTreatmentHelper(med1, meds[1:], acc)
#
#byTreatmentList = byTreatment(medsTuple, [])
#byTreatmentList.sort(reverse=True)

medString = 'Paroxetine 20 MG Tablet; TAKE 1 TABLET DAILY.; Rx'
medDict = {
  'name'         : 'PAROXETINE',
  'dose'         : '20',
  'units'        : 'MG',
  'formulation'  : 'TABLET',
  'instructions' : 'TAKE 1 TABLET DAILY.; RX',
}

ml1 = [ParsedMedication(medString, mappings)]
ml2 = [ParsedMedication(medDict, mappings)]
