#!/usr/bin/env python
# encoding: utf-8
"""
reconcile.py

The main medication reconciliation routines.

Created by Jorge Herskovic on 2011-01-11.
Copyright (c) 2011 UTHSC School of Health Information Sciences. All rights reserved.
"""

import sys
import logging
import operator
import cPickle as pickle
import bz2
import copy
import os.path
from constants import *
from medication import Medication, ParsedMedication

class Reconciliation(object):
    """Represents a pair of reconciled meds (or potentially-reconciled meds)"""
    def __init__(self, med1, med2, strength=1.0, reconciliation_mechanism="unspecified"):
        super(Reconciliation, self).__init__()
        self.med1=med1
        self.med2=med2
        self.strength=strength
        self.mechanism=reconciliation_mechanism
    def __repr__(self):
        if self.med1.normalized_string==self.med2.normalized_string:
            return "<Identical reconciliation (%s): %r @ %x>" % (self.mechanism,
                                                                     self.med1,
                                                                     id(self))
        return "<Potential reconciliation (%1.2f%% certainty; %s) %r <-> %r @ %x>" % \
               (self.strength * 100.0, self.mechanism,
                self.med1, self.med2, id(self))
    
def reconcile_by_strings(list1, list2):
    my_list_1=[]
    my_list_2=[x.normalized_string for x in list2]
    my_list_2_of_objects=list2[:]
    common=[]
    for item in list1:
        if item.normalized_string in my_list_2:
            where_in_2=my_list_2.index(item.normalized_string)
            common.append(Reconciliation(item, item, 1.0, "string matching"))
            del my_list_2[where_in_2]
            del my_list_2_of_objects[where_in_2]
        else:
            my_list_1.append(item)
    return (my_list_1, my_list_2_of_objects, common)

def reconcile_by_brand_name(list1, list2, rx, concept_names):
    logging.debug("Determining CUIs for %r", list1)
    concepts_1=[x.CUIs(rx, concept_names) for x in list1]
    logging.debug("Concepts for %r: %r", list1, concepts_1)
    logging.debug("Computing tradenames for %r", list1)
    tradenames_of_c1=[x.tradenames(rx, concept_names) for x in list1]
    logging.debug("Tradenames for %r: %r", list1, tradenames_of_c1)

    logging.debug("Determining CUIs for %r", list2)
    concepts_2=[x.CUIs(rx, concept_names) for x in list2]
    logging.debug("Concepts for %r: %r", list2, concepts_2)
    logging.debug("Computing tradenames for %r", list2)
    tradenames_of_c2=[x.tradenames(rx, concept_names) for x in list2]
    logging.debug("Tradenames for %r: %r", list2, tradenames_of_c2)

    if (concepts_1==[] or tradenames_of_c2==[]) \
        and (concepts_2==[] or tradenames_of_c1==[]):
        return list1, list2, []
    my_list_1=[]
    my_list_2_of_objects=list2[:]
    common=[]
    logging.debug("Length of concepts_1: %d", len(concepts_1))
    for y in range(len(list1)):
        logging.debug("y=%d", y)
        # Test to see if the concept in c1 is one of the tradenames of c2
        matches=None
        dose_1=list1[y].normalized_dose
        logging.debug("Testing %r", concepts_1[y])
        if concepts_1[y] is not None:
            for c1 in concepts_1[y]:
                print "Testing", c1, "against", tradenames_of_c2
                potential_matches=[c1 in t for t in tradenames_of_c2
                                  if t is not None]
                print "Result:", potential_matches
                matches=potential_matches.index(True) \
                        if True in potential_matches \
                        else None
                if matches is not None:
                    dose_2=my_list_2_of_objects[matches].normalized_dose
                    if dose_1==dose_2:
                        common.append(Reconciliation(list1[y], my_list_2_of_objects[matches],
                                                     1.0, "brand name"))
                        del my_list_2_of_objects[matches]
                        del tradenames_of_c2[matches]
                        del concepts_2[matches]
                        break
                    else:
                        matches=None
        if matches is None:
            if tradenames_of_c1[y] is not None:
                for t1 in tradenames_of_c1[y]:
                    # Test to see if the concepts in c2 match any tradenames of c1
                    print "Testing", t1, "against", concepts_2
                    potential_matches=[t1 in c for c in concepts_2 if c is not None]
                    print "Result:", potential_matches
                    matches=potential_matches.index(True) \
                            if True in potential_matches \
                            else None
                    if matches:
                        dose_2=my_list_2_of_objects[matches].normalized_dose
                        if dose_1==dose_2:
                            common.append(Reconciliation(list1[y], my_list_2_of_objects[matches],
                                                         1.0, "brand name"))
                            del my_list_2_of_objects[matches]
                            del tradenames_of_c2[matches]
                            del concepts_2[matches]
                            break
                        else:
                            matches=None
        if matches is None:
            my_list_1.append(list1[y])
    return (my_list_1, my_list_2_of_objects, common)
            
def reconcile_by_generics(list1, list2, min_match_threshold=0.3):
    my_list_1=[]
    my_list_2=[x.generic_formula for x in list2]
    my_list_2_of_objects=list2[:]
    common=[]
    for item in list1:
        ph1=(item.generic_formula, item.normalized_dose)
        match=[0.0] * len(my_list_2)
        for item2 in xrange(len(my_list_2)):
            ph2=(my_list_2[item2], 
                 my_list_2_of_objects[item2].normalized_dose)
            print "Comparing", ph1, "against", ph2
            for p in ph1[0]:
                if p in ph2[0]:
                    if ph1[1]!=ph2[1]:
                        # If the daily total dose doesn't match, it doesn't match.
                        match[item2]=-1.0
                        break
                    else:
                        match[item2]=match[item2]+1.0
            match[item2]=match[item2]/float((len(ph2[0])+len(ph1[0]))/2.0)
        matched_items=[(match[x], my_list_2[x]) for x in xrange(len(my_list_2))]
        # We choose the highest-ranking match 
        matched_items.sort(reverse=True)
        if len(matched_items)>0 and matched_items[0][0]>min_match_threshold:
            where_in_2=my_list_2.index(matched_items[0][1])
            logging.debug("Matched %r to %r by generics with score %r", 
                          item, my_list_2_of_objects[where_in_2],
                          matched_items[0][0])
            common.append(Reconciliation(item, my_list_2_of_objects[where_in_2],
                                               matched_items[0][0], "ingredients list"))
            del my_list_2[where_in_2]
            del my_list_2_of_objects[where_in_2]
        else:
            my_list_1.append(item)
        if len(matched_items)>0:
            print "The best match for", ph1, "is", matched_items[0]
    return (my_list_1, my_list_2_of_objects, common)

def reconcile_by_treatment(list1, 
                           list2, 
                           rx, 
                           concept_names, 
                           ts, 
                           highest_possible_match=0.5,
                           match_acceptance_threshold=0.5):
    def match_percentage(set1, set2):
        """Computes Hooper's consistency to use as a match percentage"""
        len_1=len(set1)
        len_2=len(set2)
        if len_1+len_2==0:
            return 0.0
        len_common=len([x for x in set1 if x in set2])
        return float(len_common)/float(len_1+len_2-len_common) 
    logging.debug("Determining CUIs for %r", list1)
    concepts_1=[x.CUIs(rx, concept_names) for x in list1]
    logging.debug("Concepts for %r: %r", list1, concepts_1)

    logging.debug("Determining CUIs for %r", list2)
    concepts_2=[x.CUIs(rx, concept_names) for x in list2]
    logging.debug("Concepts for %r: %r", list2, concepts_2)

    if (concepts_1==[] or concepts_2==[]):
        # Without CUIs there's nothing to do here.
        return list1, list2, []
    my_list_1=[]
    my_list_2_of_objects=list2[:]
    common=[]
    
    # Build lists of potential treatments
    treats_1=[]
    for c in concepts_1:
        this_treats=set([])
        if c is not None:
            for each_concept in c:
                for each_treated_thing in ts.get(each_concept, []):
                    this_treats.add(each_treated_thing)
        treats_1.append(this_treats)
    logging.debug("Treatment list for medication list 1: %r", treats_1)
    treats_2=[]
    for c in concepts_2:
        this_treats=set([])
        if c is not None:
            for each_concept in c:
                for each_treated_thing in ts.get(each_concept, []):
                    this_treats.add(each_treated_thing)
        treats_2.append(this_treats)
    logging.debug("Treatment list for medication list 2: %r", treats_2)
    
    for y in range(len(concepts_1)):
        # Compare the "treatment sphere" of each medication in list 1 to the
        # "treatment sphere" of each medication in list 2
        comparison=[(match_percentage(treats_1[y], treats_2[x]), x) for x in range(len(treats_2))]
        comparison.sort(reverse=True)
        # The first item of comparison is now the highest-ranked match
        if len(comparison)>0 and comparison[0][0]>=match_acceptance_threshold:
            # Renormalize match score
            logging.debug("Highest comparison tuple (accepted) for %d: %r", y,
                          comparison[0])
            score=comparison[0][0]*highest_possible_match
            matched_item=comparison[0][1]
            common.append(Reconciliation(list1[y], 
                                         my_list_2_of_objects[matched_item], 
                                         score, 
                                         "therapeutic intent"))
            del my_list_2_of_objects[matched_item]
            del treats_2[matched_item]
        else:
            my_list_1.append(list1[y])

    return (my_list_1, my_list_2_of_objects, common)
    
def separate_parsed_from_unparsed(medication_list):
    """Returns a tuple of two lists. The first one contains the medications with
    the 'parsed' flag set, the second one contains the rest."""
    return ([x for x in medication_list if x.parsed], 
            [x for x in medication_list if not x.parsed])
    
def reconcile_lists(list1, list2, rx, concept_names, treat_sets):
    print "********** BEFORE RECONCILIATION **********"
    print
    print "Original list 1=\n", '\n'.join(list1)
    print
    print "Original list 2=\n", '\n'.join(list2)
    print
    meds_list_1=[ParsedMedication(x) for x in list1]
    meds_list_2=[ParsedMedication(x) for x in list2]
    # Remove empty meds (parsed blank lines)
    meds_list_1=[x for x in meds_list_1 if not x.is_empty()]
    meds_list_2=[x for x in meds_list_2 if not x.is_empty()]
    print
    print "Parsed list 1=\n", '\n'.join(str(x) for x in meds_list_1)
    print
    print "Parsed list 2=\n", '\n'.join(str(x) for x in meds_list_2)
    print
    print "********** RECONCILIATION STEP 1 **********"
    print
    rec=reconcile_by_strings(meds_list_1, meds_list_2)
    rec_list_1=rec[0]
    rec_list_2=rec[1]
    print "After reconciling list 1=\n", '\n'.join(str(x) for x in rec_list_1)
    print
    print "After reconciling list 2=\n", '\n'.join(str(x) for x in rec_list_2)
    print
    print "Reconciled meds=\n", '\n'.join(str(x) for x in rec[2])
    print "**********     END OF STEP 1     **********"
    print
    print "********** RECONCILIATION STEP 2 **********"
    print
    # Separate parsed and unparsed medications
    parsed_meds_1, unparsed_meds_1=separate_parsed_from_unparsed(rec_list_1)
    parsed_meds_2, unparsed_meds_2=separate_parsed_from_unparsed(rec_list_2)
    # Unpack the lists produced by the regular expression.findall,
    # and restore missing meds if they couldn't be parsed    
    for m in parsed_meds_1:
        m.compute_generics(rx, concept_names)
        m.normalize_dose()
    for m in parsed_meds_2:
        m.compute_generics(rx, concept_names)
        m.normalize_dose()
    #print parsed_meds_2
    #return
    print
    pb1, pb2, bnrec=reconcile_by_brand_name(parsed_meds_1, parsed_meds_2, rx, concept_names)
    left1=[x for x in pb1] + unparsed_meds_1
    left2=[x for x in pb2] + unparsed_meds_2
    print "List 1 after brand name matching=\n", '\n'.join([str(x) for x in left1])
    print
    print "List 2 after brand name matching=\n", '\n'.join([str(x) for x in left2])
    print
    print "Reconciled after brand name matching=\n", '\n'.join([str(x) for x in bnrec])
    print 
    already_reconciled=[x for x in bnrec] + rec[2]
    print "All reconciled=\n", '\n'.join([str(x) for x in already_reconciled])
    print "**********     END OF STEP 2     **********"
    print
    print "********** RECONCILIATION STEP 3 **********"
    pm1, pm2, pmrec=reconcile_by_generics(pb1, pb2)
    left1=[x for x in pm1] + unparsed_meds_1
    left2=[x for x in pm2] + unparsed_meds_2
    print "List 1 after pharma matching=\n", '\n'.join([str(x) for x in left1])
    print
    print "List 2 after pharma matching=\n", '\n'.join([str(x) for x in left2])
    print
    print "Reconciled after pharma matching=\n", '\n'.join([str(x) for x in pmrec])
    print 
    already_reconciled=[x for x in already_reconciled]+pmrec
    print "All reconciled=\n", '\n'.join([str(x) for x in already_reconciled])
    print "**********     END OF STEP 3     **********"
    print
    print "********** RECONCILIATION STEP 4 **********"
    print
    pt1, pt2, ptrec=reconcile_by_treatment(pm1, pm2, rx, concept_names, treat_sets, 
                                           match_acceptance_threshold=0.3)
    left1=[x for x in pt1] + unparsed_meds_1
    left2=[x for x in pt2] + unparsed_meds_2    
    print "List 1 after therapeutic intent matching=\n", '\n'.join([str(x) for x in left1])
    print
    print "List 2 after therapeutic intent matching=\n", '\n'.join([str(x) for x in left2])
    print
    print "Reconciled after therapeutic intent matching=\n", '\n'.join([str(x) for x in ptrec])
    print 
    already_reconciled=[x for x in already_reconciled] + ptrec
    print "All reconciled=\n", '\n'.join([str(x) for x in already_reconciled])
    print "**********     END OF STEP 4     **********"
    return (left1, left2, already_reconciled)

ITERATION_TEMPLATE="""
########################################################

          MEDICATION RECONCILIATION ITERATION %d

########################################################

"""

from html_output import output_html
from optparse import OptionParser

def main():
    usage="""Usage: %prog [options] [file_to_process] [output_directory]""" + \
    """
    Reconciles two or more successive medication lists (i.e. assumes that all 
    lists belong to the same patient, and if given many lists L1, L2, L3,..., Ln
    it will reconcile L1 with L2, then L2 with L3, then L3 with L4, etc.). 
    
    Each list of medications contained in the same text file should have one
    medication per line and should end with a line consisting solely of 
    %(separator)s, i.e.
    
    Penicillin 100 ucg 
    %(separator)s
    Penicillin 200 ucg 
    Aspirin 81 mg po
    %(separator)s
    Penicillin 100 ucg 
    %(separator)s
    
    defines three lists: 
        1. Penicillin 100 ucg, 
        2. Penicillin 200 ucg and Aspirin 81 mg po,
        3. Penicillin 100 ucg
    
    if no [file_to_process] is given, the program will perform a demo by 
    reconciling two demonstration lists and quit. 
    
    If [file_to_process] is specified, the program will output an HTML table for
    each reconciliation it performs. If you don't specify [output_directory], 
    the current directory is assumed.
    """ % {'separator': MEDLIST_SEPARATOR}
    
    options_parser=OptionParser(usage=usage)
    options_parser.add_option("-v", "--verbose", dest="verbose", default=False,
                      help="Show debugging information as script runs.",
                      action="store_true")
    options_parser.add_option("-r", "--rxnorm", dest="rxnorm", metavar="FILE",
                      default="rxnorm.pickle.bz2",
                      help="Read a pickled instance of RXNorm from FILE")
    options_parser.add_option("-t", "--treatment", dest="treatment", 
                      metavar="FILE", default='treats.pickle.bz2',
                      help="Read a pickled instance of treatment sets from FILE")
    (options, args)=options_parser.parse_args()
    print "Loading RXNorm"
    logging.basicConfig(level=logging.DEBUG if options.verbose else logging.INFO, 
                        format='%(asctime)s %(levelname)s ' \
                        '%(module)s. %(funcName)s: %(message)s')
    rx=pickle.load(bz2.BZ2File(options.rxnorm, 'r'))
    print "Loading treatment sets"
    try:
        ts=pickle.load(bz2.BZ2File(options.treatment, 'r'))
    except:
        print "No treatment sets available. Fourth reconciliation step will be a null op."
        ts={}
    print "Indexing concepts"
    concept_names={}
    for c in rx.concepts:
        cn=rx.concepts[c]._name.lower()
        cn=cn.split('@')[0].strip() # Just use stuff to the left of a @ for a concept name
        if cn in concept_names:
            concept_names[cn].add(c)
        else:
            concept_names[cn]=set([c])
    if len(args)==0:
        # Test run with no parameters
        test_list_1="""Zoloft 50 MG Tablet;TAKE 1 TABLET DAILY.; RPT
                Warfarin Sodium 2.5 MG Tablet;TAKE AS DIRECTED.; Rx
                Lipitor 10 MG Tablet;TAKE 1 TABLET DAILY.; Rx
                Protonix 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx
                Warfarin Sodium 5 MG Tablet;TAKE 1 TABLET DAILY AS DIRECTED.; Rx
                Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx
                Lisinopril 5 MG Tablet;TAKE  TABLET TWICE DAILY; Rx
                Coreg 25 MG Tablet;TAKE 1 TABLET TWICE DAILY,  WITH MORNING AND EVENING MEAL; RPT
        """.split('\n')
        test_list_2="""Warfarin Sodium 2.5 MG Tablet;TAKE AS DIRECTED.; Rx
        Warfarin Sodium 5 MG Tablet;TAKE 1 TABLET DAILY AS DIRECTED.; Rx
        Carvedilol 25 MG Tablet;TAKE 1 TABLET TWICE DAILY,  WITH MORNING AND EVENING MEAL; Rx
        Lipitor 10 MG Tablet;TAKE 1 TABLET DAILY.; Rx
        Lisinopril 5 MG Tablet;TAKE 1 TABLET TWICE DAILY; Rx
        Synthroid 100 MCG Tablet;TAKE 1 TABLET DAILY.; Rx
        Pantoprazole Sodium 40 MG Tablet Delayed Release;TAKE 1 TABLET DAILY.; Rx
        Sertraline HCl 50 MG Tablet;TAKE 1 TABLET DAILY.; Rx
        Mirapex 0.5 MG Tablet;TAKE 1 TABLET 3 TIMES DAILY.; Rx.""".split('\n')
        reconcile_lists(test_list_1, test_list_2, rx, concept_names, ts)
        return
    # Use the file provided
    current_list=[]
    current_l1=None
    current_l2=None
    f=open(args[0], "rU")
    try:
        output_path=args[1]
    except IndexError:
        output_path="."
    count=0
    for l in f:
        l=l.strip()
        if l==MEDLIST_SEPARATOR:
            current_l1=copy.copy(current_l2)
            current_l2=copy.copy(current_list)
            current_list=[]
            if current_l1 is not None:
                count+=1
                print ITERATION_TEMPLATE % count
                output_filename=os.path.join(output_path, "rec_%05d.html" % count)
                l1, l2, rec=reconcile_lists(current_l1, current_l2, rx, concept_names, ts)
                output_html(current_l1, current_l2, l1, l2, rec, output_filename)
        else:
            current_list.append(l)

if __name__ == '__main__':
    main()
