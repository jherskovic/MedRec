#!/usr/bin/python
"""
generate_drug_problem_file.py

Reads data on relations between drugs and problems, and creates structured
data to represent these problems.

The expected input is a bz2-compressed CSV file with at least the following fields:
mcui          (string, the CUI of the medication)
medication    (string, the name of the medication)
problem       (string, the name of the problem)
patientcount  (int, the count of patients)
ratio         (float, the ratio of patients)

For each row in this file, a DrugProblem object will be instantiated and 
appended to a list in a dictionary with the CUI 'mcui' as the key. This 
dictionary serves as the input data for the DrugProblemKB object, which 
will be pickled and bz2'd.

Created by Charles Bearden 
--Copyright (c) 2011 UTHealth School of Biomedical Informatics. All rights reserved.
"""
import drug_problem_kb
import sys
import os.path
import random
import cPickle as pickle
import bz2
import csv
from collections import defaultdict

def display_count(count, dot_threshold=1000, pipe_threshold=10000, 
                  newline_threshold=50000, output_stream=sys.stderr):
    if count % dot_threshold == 0:
        output_stream.write(".")
        output_stream.flush()
    if count % pipe_threshold == 0:
        output_stream.write("|")
        output_stream.flush()
    if count % newline_threshold == 0:
        print >>output_stream, " %d" % count
        output_stream.flush()

src_file = sys.argv[1]
save_file = sys.argv[2]
drug_problem_mapping = defaultdict(set)
print >>sys.stderr, "Reading Drug/Problem data"
infile = csv.DictReader(bz2.BZ2File(src_file, 'r'))
for row in infile:
    cui, name, patientcount, ratio = row['mcui'], row['problem'], int(row['patientcount']), float(row['ratio'])
    pr = drug_problem_kb.problem_relation_factory(name, patientcount, ratio)
    drug_problem_mapping[cui].add(pr)
    
print >>sys.stderr

print >>sys.stderr, "Saving drug/problem knowledgebase to", save_file
dpkb = drug_problem_kb.DrugProblemKB(drug_problem_mapping)
pickle.dump(dpkb, bz2.BZ2File(save_file, 'wb'), pickle.HIGHEST_PROTOCOL)
