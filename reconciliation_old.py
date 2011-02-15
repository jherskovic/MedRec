import re
import rxnorm
import cPickle as pickle
import sys
import copy
import logging
from medication import Medication 
import os.path

known_times_per_day=[
               ('%FORM% DAILY', 1),
               ('%FORM%S DAILY', 1),
               ('%FORM%S A DAY', 1),
               ('%FORM% TWICE A DAY', 2),
               ('%FORM% TWICE DAILY', 2),
               ('%FORM% THREE TIMES DAILY', 3),
               ('%FORM% THREE TIMES A DAY', 3),
               (r'(\d+) TIME[S]? PER DAY', -1),
               (r'(\d+) TIME[S]? DAILY', -1),
               (r'(\d+) TIME[S]? A DAY', -1),
               ('QD', 1),
               ('Q.D.', 1),
               ('Q.D', 1),
               ('BID', 2),
               ('TID', 3),
               ('QID', 4),
               ('T.I.D.', 3),
               ('T.I.D', 3),               
               ('B.I.D.', 2),
               ('B.I.D', 2),
               ('Q.I.D.', 4),
               ('Q.I.D', 4),
               ('A DAY', 1),
               ('AT NIGHT', 1),
              ]
               
known_number_of_doses=[
               (r'TAKE (\d+) %FORM%[S]?', -1),
               ('TAKE %FORM%', 1),
               (r'(\d+) %FORM%[S]?', -1),
              ]

MEDLIST_SEPARATOR="******"
UNDESIRABLE_PUNCTUATION=".,;:!?@#$%^&*()"

HTML_TEMPLATE="""<html><head><title>MedRec %(filename)s</title></head>
<body>
<p>Original lists</p>
<table border=1>
<tr><td style="background-color:#B892CA">%(original_list_1)s</td>
<td style="background-color:#95A7CA">%(original_list_2)s</td></tr>
</table>
<p>Reconciliation</p>
<table border=1>
%(reconciled)s
%(unreconciled)s
</table>
<p>Hooper's Indexing Consistency: %(hoopers)1.7f</p>
</body>
</html>
"""

RECONCILED_TEMPLATE="""<tr><td style="background-color:green;color:white">%(reconciled)s</td></tr>"""
UNRECONCILED_TEMPLATE="""<tr><td><table border=1><tr><td style="background-color:#B892CA">%(unreconciled_list_1)s</td>
<td style="background-color:#95A7CA">%(unreconciled_list_2)s</td></tr></table></td></tr>"""

# Physical forms extracted from SNOMED 2010
# We got all things that are described as "IS_A unit dose"
# print '\n'.join([s._concepts[s._relationships[x].CONCEPTID1].FullySpecifiedName for x in s._rel_c2_dict[408102007L]])
# Where 's' was an instance of my own PySNOMED Snomed class
physical_forms="""Drop - unit of product usage (qualifier value)
Suppository - unit of product usage (qualifier value)
Puff - unit of product usage (qualifier value)
Base - unit of product usage (qualifier value)
Bottle - unit of product usage (qualifier value)
Box - unit of product usage (qualifier value)
Packet - unit of product usage (qualifier value)
Tube - unit of product usage (qualifier value)
Glassful - unit of product usage (qualifier value)
Inhalation - unit of product usage (qualifier value)
Dropperful - unit of product usage (qualifier value)
Swab - unit of product usage (qualifier value)
Pad - unit of product usage (qualifier value)
Implant - unit of product usage (qualifier value)
Sponge - unit of product usage (qualifier value)
Lozenge - unit of product usage (qualifier value)
Patch - unit of product usage (qualifier value)
Bar - unit of product usage (qualifier value)
Kit - unit of product usage (qualifier value)
Bag - unit of product usage (qualifier value)
Case - unit of product usage (qualifier value)
Spray - unit of product usage (qualifier value)
Blister - unit of product usage (qualifier value)
Sachet - unit of product usage (qualifier value)
Can - unit of product usage (qualifier value)
Pellet - unit of product usage (qualifier value)
Disc - unit of product usage (qualifier value)
Insert - unit of product usage (qualifier value)
Scoop - unit of product usage (qualifier value)
Tablet - unit of product usage (qualifier value)
Cup - unit of product usage (qualifier value)
Application - unit of product usage (qualifier value)
Vial - unit of product usage (qualifier value)
Gum - unit of product usage (qualifier value)
Teaspoonful - unit of product usage (qualifier value)
Tablespoonful - unit of product usage (qualifier value)
Capsule - unit of product usage (qualifier value)
Ampule - unit of product usage (qualifier value)""".split('\n')
# Extract everything before the hyphen, uppercase it, and strip whitespace
physical_forms=[x.split('-')[0].upper().strip() for x in physical_forms]

abbreviations={'HCL': 'HYDROCHLORIDE'}

    
def normalize_list(a_list):
    my_list=[x.upper().strip() for x in a_list[:]]
    for punct in UNDESIRABLE_PUNCTUATION:
        my_list=[x.strip(punct) for x in my_list]
    my_list=[' '.join(x.split()) for x in my_list]
    return [x for x in my_list if len(x) > 0]
    
def string_matching(list1, list2):
    """Takes two lists and returns the elements that are common to both"""
    my_list_1=[]
    my_list_2=list2[:]
    common=[]
    for item in list1:
        if item in my_list_2:
            where_in_2=my_list_2.index(item)
            common.append(item)
            del my_list_2[where_in_2]
        else:
            my_list_1.append(item)
    return (my_list_1, my_list_2, common)
    
def normalize_drug_name(drug_name):
    truncated=drug_name.split('@')[0].strip().upper()
    components=truncated.split()
    final_version=[]
    # Replace abbreviations
    for x in components:
        if x in abbreviations:
            final_version.append(abbreviations[x])
        else:
            final_version.append(x)
    return ' '.join(final_version)
    
def build_regular_expressions(list_of_tuples, formulation):
    my_regexps=[]
    for k, v in list_of_tuples:
        new_k=k[:].replace('%FORM%', formulation)
        my_regexps.append((new_k, v))
    return my_regexps
    
def normalize_dose(med):
    """Takes a drug tuple (i.e. the output of the regular expression listed 
    above) and returns the total number of units a day the patient is 
    receiving"""
    number_of_units=None # Assume that (if not mentioned) there is 
                      #one tablet/capsule/whatever per unit of time
    formulation=med.formulation
    # Make sure that we have a formulation we know about! Replace formulations 
    # with standard names.
    for known_formulation in physical_forms:
        if known_formulation in formulation:
            formulation=known_formulation
            continue
                
    regexps=build_regular_expressions(known_number_of_doses, formulation)
    for regexp, num in regexps:
        if num==-1:
            result=re.findall(regexp, med.instructions)
            if len(result)>0:
                number_of_units=int(result[0])
                continue
        else:
            if regexp in med.instructions:
                number_of_units=num
                continue
    if number_of_units is None:
        logging.info("Failed matching number of units on %r; assuming 1", med)
        number_of_units=1
    regexps=build_regular_expressions(known_times_per_day, formulation)
    times_per_day=None
    for regexp, times in regexps:
        if times==-1:
            # Regular expression to be parsed
            result=re.findall(regexp, med.instructions)
            if len(result)>0:
                times_per_day=int(result[0])
                continue
        else:
            if regexp in med.instructions:
                times_per_day=times
                continue
    if times_per_day is None:
        logging.info("Failed matching times per day on %r. Assuming 1.", med)
        times_per_day=1
    # else:
        #print drug_tuple, "is taken %d times a day" % times_per_day
    logging.debug("The total quantity of %r is %1.2f %s a day", 
        med.name, med.dose*times_per_day*number_of_units, med.units)
    try:
        return '%s %s*%d*%d' % (str(med.dose), med.units, times_per_day, number_of_units)
    except ValueError:
        return None
    
def pharma_matching(list1, list2, match_threshold=0.5):
    print "Matching",list1,"against",list2
    my_list_1=[]
    my_list_2=list2[:]
    common=[]
    for item in list1:
        ph1=([normalize_drug_name(x) for x in item.name], normalize_dose(item))
        match=[0.0] * len(my_list_2)
        for item2 in xrange(len(my_list_2)):
            ph2=([normalize_drug_name(x) for x in my_list_2[item2].name], 
                 normalize_dose(my_list_2[item2]))
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
        matched_items.sort(reverse=True)
        if len(matched_items)>0 and matched_items[0][0]>=match_threshold:
            where_in_2=my_list_2.index(matched_items[0][1])
            common.append(matched_items[0][1])
            del my_list_2[where_in_2]
        else:
            my_list_1.append(item)
        if len(matched_items)>0:
            print "The best match for", ph1, "is", matched_items[0]
    return (my_list_1, my_list_2, common)
    
def reconcile_medications(list1, list2):
    my_list_1=normalize_list(list1)
    my_list_2=normalize_list(list2)
    # Step 1: Common strings
    my_list_1, my_list_2, reconciled=string_matching(my_list_1, my_list_2)
    # Eliminate reconciled medications from the original lists
    return (my_list_1, my_list_2, reconciled)
    
def turn_medication_into_generics(med, rxnorm, concept_names):
    generic=copy.copy(med)
    if med.name is not None:
        name_of_medication=med.name.lower()
        if name_of_medication in concept_names:
            concepts=copy.copy(concept_names[name_of_medication])
            logging.debug("Concepts for %s=%r", name_of_medication, concepts)
            try:
                concept=concepts.pop()
                ingredients=rxnorm.formulas[concept]
                generic.name=[x.name for x in ingredients]
                return generic
            except KeyError:
                logging.warn("Couldn't find ingredients for %s", concept)
        else:
            logging.debug("Couldn't find %s in RXNorm" % name_of_medication)
    generic.name=[generic.name]
    return generic
    
def output_html(current_l1, current_l2, l1, l2, rec, output_filename):
    f=open(output_filename, "w")
    reconciled_list="<br>\n".join(rec)
    original_1="<br>\n".join(current_l1)
    original_2="<br>\n".join(current_l2)
    unrec_1="<br>\n".join(l1)
    unrec_2="<br>\n".join(l2)
    unreconciled=UNRECONCILED_TEMPLATE % {"unreconciled_list_1": unrec_1,
                                          "unreconciled_list_2": unrec_2}
    hoopers=float(len(rec))/float(len(rec)+len(l1)+len(l2))
    reconciled=RECONCILED_TEMPLATE % {"reconciled": reconciled_list}
    f.write(HTML_TEMPLATE % {"original_list_1": original_1,
                             "original_list_2": original_2,
                             "reconciled": reconciled,
                             "unreconciled": unreconciled,
                             "filename": os.path.split(output_filename)[1],
                             "hoopers": hoopers,
                             })
    f.close()

def reconcile_lists(list1, list2, rx, concept_names):
    print "********** RECONCILIATION STEP 1 **********"
    print
    print "Original list 1=\n", '\n'.join(list1)
    print
    print "Original list 2=\n", '\n'.join(list2)
    print
    rec=reconcile_medications(list1, list2)
    rec_list_1=rec[0]
    rec_list_2=rec[1]
    print "After reconciling list 1=\n", '\n'.join(rec_list_1)
    print
    print "After reconciling list 2=\n", '\n'.join(rec_list_2)
    print
    print "Reconciled meds=\n", '\n'.join(rec[2])
    print
    print "**********     END OF STEP 1     **********"
    print
    print "********** RECONCILIATION STEP 2 **********"
    print
    print "Extracting drug names."
    meds_list_1=[Medication(x) for x in rec_list_1]
    meds_list_2=[Medication(x) for x in rec_list_2]
    print
    # Separate parsed and unparsed medications
    parsed_meds_1=[x for x in meds_list_1 if x.parsed]
    parsed_meds_2=[x for x in meds_list_2 if x.parsed]
    unparsed_meds_1=[rec_list_1[x] for x in xrange(len(meds_list_1)) if not meds_list_1[x].parsed]
    unparsed_meds_2=[rec_list_2[x] for x in xrange(len(meds_list_2)) if not meds_list_2[x].parsed]
    # Unpack the lists produced by the regular expression.findall,
    # and restore missing meds if they couldn't be parsed    
    generics_list_1=[]
    generics_list_2=[]
    for m in parsed_meds_1:
        generics_list_1.append(turn_medication_into_generics(m, rx, concept_names))
    for m in parsed_meds_2:
        generics_list_2.append(turn_medication_into_generics(m, rx, concept_names))
    print "List 1 with generic substitutions=", generics_list_1
    print
    print "List 2 with generic substitutions=", generics_list_2
    print
    pm1, pm2, pmrec=pharma_matching(generics_list_1, generics_list_2)
    left1=[x.original_line for x in pm1] + unparsed_meds_1
    left2=[x.original_line for x in pm2] + unparsed_meds_2
    print "List 1 after pharma matching=\n", '\n'.join(left1)
    print
    print "List 2 after pharma matching=\n", '\n'.join(left2)
    print
    print "Reconciled after pharma matching=\n", '\n'.join([x.original_line for x in pmrec])
    print 
    already_reconciled=[x.original_line for x in pmrec]+rec[2]
    print "All reconciled=\n", '\n'.join(already_reconciled)
    print
    print "**********     END OF STEP 2     **********"
    print
    return (left1, left2, already_reconciled)
    
def main(args):
    print "Loading RXNorm"
    logging.getLogger().setLevel(logging.DEBUG)
    rx=pickle.load(open('rxnorm.pickle', 'rb'))
    print "Indexing concepts"
    concept_names={}
    for c in rx.concepts:
        cn=rx.concepts[c]._name.lower()
        cn=cn.split('@')[0].strip() # Just use stuff to the left of a @ for a concept name
        if cn in concept_names:
            concept_names[cn].add(c)
        else:
            concept_names[cn]=set([c])
    if len(args)==1:
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
        reconcile_lists(test_list_1, test_list_2, rx, concept_names)
        return
    # Use the file provided
    current_list=[]
    current_l1=None
    current_l2=None
    f=open(args[1], "rU")
    try:
        output_path=args[2]
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
                output_filename=os.path.join(output_path, "rec_%05d.html" % count)
                l1, l2, rec=reconcile_lists(current_l1, current_l2, rx, concept_names)
                output_html(current_l1, current_l2, l1, l2, rec, output_filename)
        else:
            current_list.append(l)
    
    
if __name__ == '__main__':
    main(sys.argv)
