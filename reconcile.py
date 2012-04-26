#!/usr/bin/env python
# encoding: utf-8
"""
reconcile.py

The main medication reconciliation routines.

Created by Jorge Herskovic on 2011-01-11.
Copyright (c) 2011 UTHSC School of Health Information Sciences. All rights reserved.
"""

import logging
import cPickle as pickle
import bz2
import copy
import os.path
from constants import *
from medication import make_medication
from medication import ParsedMedication
from json_output import *
from match import Match, match_by_strings, match_by_brand_name, match_by_ingredients, match_by_treatment
from mapping_context import MappingContext
         
def separate_parsed_from_unparsed(medication_list):
    """Returns a tuple of two lists. The first one contains the medications with
    the 'parsed' flag set, the second one contains the rest."""
    return ([x for x in medication_list if isinstance(x, ParsedMedication)],
            [x for x in medication_list if not isinstance(x, ParsedMedication)])

def reconciliation_setup(list1, list2, mappings, stats):
    print "********** BEFORE RECONCILIATION **********"
    print
    print "Original list 1=\n", '\n'.join(list1)
    print
    print "Original list 2=\n", '\n'.join(list2)
    print
    meds_list_1 = [make_medication(x, mappings, "List 1") for x in list1]
    meds_list_2 = [make_medication(x, mappings, "List 2") for x in list2]
    if stats is not None:
        stats['size_original_list_1'] = len(meds_list_1)
        stats['size_original_list_2'] = len(meds_list_2)
    # Remove empty meds (parsed blank lines)
    meds_list_1 = [x for x in meds_list_1 if not x.is_empty()]
    meds_list_2 = [x for x in meds_list_2 if not x.is_empty()]
    if stats is not None:
        stats['size_parsed_list_1'] = len(meds_list_1)
        stats['size_parsed_list_2'] = len(meds_list_2)        
    print
    print "Parsed list 1=\n", '\n'.join(str(x) for x in meds_list_1)
    print
    print "Parsed list 2=\n", '\n'.join(str(x) for x in meds_list_2)
    return meds_list_1, meds_list_2, stats

def reconciliation_step_1(list1, list2, mappings, stats):
    """Helper function to handle matching by strings."""
    print "********** RECONCILIATION STEP 1 **********"
    print
    rec = match_by_strings(list1, list2)
    rec_list_1 = rec.list1
    rec_list_2 = rec.list2
    print "After reconciling list 1=\n", '\n'.join(str(x) for x in rec_list_1)
    print
    print "After reconciling list 2=\n", '\n'.join(str(x) for x in rec_list_2)
    print
    print "Reconciled meds=\n", '\n'.join(str(x) for x in rec.reconciled)
    if stats is not None:
        stats['reconciled_strings'] = len(rec.reconciled)
    print "**********     END OF STEP 1     **********"
    return dict(rec_list_1=rec_list_1, rec_list_2=rec_list_2, rec=rec, stats=stats)

def reconciliation_step_2(rec_list_1=[], rec_list_2=[], rec=[], stats={}):
    """Helper function to handle matching by brand names."""
    print "********** RECONCILIATION STEP 2 **********"
    print
    # Separate parsed and unparsed medications
    parsed_meds_1, unparsed_meds_1 = separate_parsed_from_unparsed(rec_list_1)
    parsed_meds_2, unparsed_meds_2 = separate_parsed_from_unparsed(rec_list_2)
    # Unpack the lists produced by the regular expression.findall,
    # and restore missing meds if they couldn't be parsed    
    print
    rec_bn = match_by_brand_name(parsed_meds_1, parsed_meds_2)
    pb1, pb2, bnrec = rec_bn.list1, rec_bn.list2, rec_bn.reconciled
    left1 = pb1 + unparsed_meds_1
    left2 = pb2 + unparsed_meds_2
    print "List 1 after brand name matching=\n", '\n'.join([str(x) for x in left1])
    print
    print "List 2 after brand name matching=\n", '\n'.join([str(x) for x in left2])
    print
    print "Reconciled after brand name matching=\n", '\n'.join([str(x) for x in bnrec])
    print 
    if stats is not None:
        stats['reconciled_brand_name'] = len(bnrec)
    already_reconciled = [x for x in bnrec] + rec.reconciled
    print "All reconciled=\n", '\n'.join([str(x) for x in already_reconciled])
    print "**********     END OF STEP 2     **********"
    return dict(
      pb1=pb1,
      pb2=pb2,
      unparsed_meds_1=unparsed_meds_1,
      unparsed_meds_2=unparsed_meds_2,
      already_reconciled=already_reconciled,
      stats=stats
    )

def reconciliation_step_3(pb1=[], pb2=[], unparsed_meds_1=[], unparsed_meds_2=[], already_reconciled=[], stats={}):
    """Helper function to handle matching by ingredients."""
    print "********** RECONCILIATION STEP 3 **********"
    rec_ing = match_by_ingredients(pb1, pb2)
    pm1, pm2, pmrec = rec_ing.list1, rec_ing.list2, rec_ing.reconciled
    left1 = pm1 + unparsed_meds_1
    left2 = pm2 + unparsed_meds_2
    print "List 1 after pharma matching=\n", '\n'.join([str(x) for x in left1])
    print
    print "List 2 after pharma matching=\n", '\n'.join([str(x) for x in left2])
    print
    print "Reconciled after pharma matching=\n", '\n'.join([str(x) for x in pmrec])
    print 
    if stats is not None:
        stats['reconciled_generics'] = len(pmrec)
    already_reconciled = [x for x in already_reconciled] + pmrec
    print "All reconciled=\n", '\n'.join([str(x) for x in already_reconciled])
    print "**********     END OF STEP 3     **********"
    return dict(pm1=pm1, pm2=pm2, already_reconciled=already_reconciled, stats=stats)

def reconciliation_step_4(pm1=[], pm2=[], unparsed_meds_1=[], unparsed_meds_2=[], already_reconciled=[], mappings=None, stats={}):
    """Helper function to handle matching by treatment intent."""
    print "********** RECONCILIATION STEP 4 **********"
    print
    rec_treat = match_by_treatment(pm1, pm2, mappings,
                                           match_acceptance_threshold=0.3)
    pt1, pt2, ptrec = rec_treat.list1, rec_treat.list2, rec_treat.reconciled
    left1 = pt1 + unparsed_meds_1
    left2 = pt2 + unparsed_meds_2    
    print "List 1 after therapeutic intent matching=\n", '\n'.join([str(x) for x in left1])
    print
    print "List 2 after therapeutic intent matching=\n", '\n'.join([str(x) for x in left2])
    print
    print "Reconciled after therapeutic intent matching=\n", '\n'.join([str(x) for x in ptrec])
    print 
    already_reconciled = [x for x in already_reconciled] + ptrec
    if stats is not None:
        stats['reconciled_therapeutic_intent'] = len(ptrec)
    print "All reconciled=\n", '\n'.join([str(x) for x in already_reconciled])
    print "**********     END OF STEP 4     **********"    
    return left1, left2, already_reconciled, stats

# If you pass a dictionary as the "stats" parameter to this function, you'll
# get statistics in it after it's done
def reconcile_lists(list1, list2, mappings, stats=None):
    meds_list_1, meds_list_2, stats = reconciliation_setup(list1, list2, mappings, stats)
    print
    # By strings
    step1 = reconciliation_step_1(meds_list_1, meds_list_2, mappings, stats)
    print
    # By brand names
    step2 = reconciliation_step_2(**step1)
    print
    # By ingredients
    step3 = reconciliation_step_3(**step2)
    step3['unparsed_meds_1'] = step2['unparsed_meds_1']
    step3['unparsed_meds_2'] = step2['unparsed_meds_2']
    step3['mappings'] = mappings
    print
    # By treatment intent
    left1, left2, already_reconciled, stats = reconciliation_step_4(**step3)
    return (left1, left2, already_reconciled)

ITERATION_TEMPLATE = """
########################################################

          MEDICATION RECONCILIATION ITERATION %d

########################################################

"""

from html_output import output_html
from optparse import OptionParser

def main():
    usage = """Usage: %prog [options] [file_to_process] [output_directory]""" + \
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
    
    options_parser = OptionParser(usage=usage)
    options_parser.add_option("-v", "--verbose", dest="verbose", default=False,
                      help="Show debugging information as the script runs.",
                      action="store_true")
    options_parser.add_option("-r", "--rxnorm", dest="rxnorm", metavar="FILE",
                      default="rxnorm.pickle.bz2",
                      help="Read a pickled instance of RXNorm from FILE")
    options_parser.add_option("-t", "--treatment", dest="treatment",
                      metavar="FILE", default='treats.pickle.bz2',
                      help="Read a pickled instance of treatment sets from FILE")
    options_parser.add_option("-j", "--json", dest="json",
                              default=False, action="store_true",
                              help="Output JSON instead of HTML.")
    (options, args) = options_parser.parse_args()
    print "Loading RXNorm"
    logging.basicConfig(level=logging.DEBUG if options.verbose else logging.INFO,
                        format='%(asctime)s %(levelname)s ' \
                        '%(module)s. %(funcName)s: %(message)s')
    rx = pickle.load(bz2.BZ2File(options.rxnorm, 'r'))
    print "Loading treatment sets"
    try:
        ts = pickle.load(bz2.BZ2File(options.treatment, 'r'))
    except:
        print "No treatment sets available. Fourth reconciliation step will be a null op."
        ts = {}
    print "Indexing concepts"
    mc = MappingContext(rx, ts)
    
    if len(args) == 0:
        # Demo run with no parameters
        l1, l2, rec = reconcile_lists(demo_list_1, demo_list_2, mc)
        print output_json(demo_list_1, demo_list_2, l1, l2, rec)
        return
    # Use the file provided
    current_list = []
    current_l1 = None
    current_l2 = None
    f = open(args[0], "rU")
    try:
        output_path = args[1]
    except IndexError:
        output_path = "."
    count = 0
    for l in f:
        l = l.strip()
        if l == MEDLIST_SEPARATOR:
            current_l1 = copy.copy(current_l2)
            current_l2 = copy.copy(current_list)
            current_list = []
            if current_l1 is not None:
                count += 1
                print ITERATION_TEMPLATE % count
                output_extension=".json" if options.json else ".html"
                output_filename = os.path.join(output_path, ("rec_%05d" + output_extension) % count)
                l1, l2, rec = reconcile_lists(current_l1, current_l2, mc)
                if options.json:
                    output_json(current_l1, current_l2, l1, l2, rec, output_filename)
                else:
                    output_html(current_l1, current_l2, l1, l2, rec, output_filename)
        else:
            current_list.append(l)

if __name__ == '__main__':
    main()
