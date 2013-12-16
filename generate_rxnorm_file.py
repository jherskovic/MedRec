#!/usr/bin/python
"""
generate_rxnorm_file.py

Extracts RXNORM from the UMLS and converts it to a format that is usable by the
medication reconciliation algorithm. 

Pass your Metathesaurus directory (the one containing .RRF files) as the first 
argument and the output filename as the second parameter (recommended: 
rxnorm.pickle.bz2)

Created by Jorge Herskovic 
Copyright (c) 2011 UTHealth School of Biomedical Informatics. All rights reserved.
"""
try:
    import semidbm as dbmaccess
except ImportError:
    print "semidbm not available. I'll try to use anydbm instead, but depending on the size " \
          "of your UMLS installation, this script may crash."
    import anydbm as dbmaccess
    
import rxnorm
import sys
import os.path
import random
import cPickle as pickle
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
        print >> output_stream, " %d" % count
        output_stream.flush()

rrf_dir = sys.argv[1]
save_file = sys.argv[2]

print >> sys.stderr, "Reading Semantic Types"
sty_filename = os.path.join(rrf_dir, "MRSTY.RRF")
sty_file = open(sty_filename, 'rU')
types = {}
count = 0
for line in sty_file:
    st = rxnorm.SemanticTypeLine(line)
    if st.CUI in types:
        types[st.CUI].add(st.semtype)
    else:
        types[st.CUI] = set([st.semtype])
    count += 1
    display_count(count)

print >> sys.stderr

print  >> sys.stderr, "Reading concepts"
conso_filename = os.path.join(sys.argv[1], "MRCONSO.RRF")
conso_file = open(conso_filename, "rU")
concepts = {}
count = 0

ttys = ('PN', 'MIN', 'SCD', 'SBD', 'SY', 'SCDF', 'SBDF', 'SCDC', 'DF',
        'SBDC', 'BN', 'PIN', 'IN', 'BPCK', 'GPCK', 'TMSY', 'OCD',
        ('S', 'OCD'))
CUI = 0
TS = 2
SAB = 11
TTY = 12
STR = 14

candidateLines = defaultdict(dict)
actualLines = {}
cuis = set()
#desirable_vocabularies=set(['RXNORM', 'GS', 'MDDB', 'MSH', 'MMSL', 'MMX', 'SNOMEDCT', 'MTHFDA', 'MTHSPL', 'NDDF', 'M'])
# Select the candidate lines for creating the Drug concepts
for line in conso_file:
    if 'RXNORM' not in line and 'MTH' not in line:
        continue
    lineAry = line.strip().split('|')
    cui = lineAry[CUI]
    ts = lineAry[TS]
    tty = lineAry[TTY]
    sab = lineAry[SAB]
    if sab == 'RXNORM':
        cuis.add(cui)
    if sab == 'RXNORM' and ts == 'P':
        candidateLines[cui][tty] = line
    elif sab == 'MTH' and ts == 'P' and tty == 'PN':
        candidateLines[cui][tty] = line
    elif sab == 'RXNORM' and ts == 'S' and tty == 'OCD':
        candidateLines[cui][(ts, tty)] = line
# From the candidate lines select the ones we will actually use
for cui, ttyDict in candidateLines.items():
    for tty in ttys:
        if cui in cuis:
            s = ttyDict.get(tty, None)
            if s:
                actualLines[cui] = s
                break
# Produce the drug concepts
for line in actualLines.values():
    c = rxnorm.Drug(line)
    c.semtypes = types[c.CUI]
    concepts[c.CUI] = c
    cuis.remove(c.CUI)
    count += 1
    display_count(count)

print >> sys.stderr, "\nForgetting semantic type db"
del types

print >> sys.stderr, "Reading relations"
rel_filename = os.path.join(sys.argv[1], "MRREL.RRF")
rel_file = open(rel_filename, "rU")
count = 0
relations = []

for line in rel_file:
    if 'RXNORM' not in line:
        continue
    try:
        r = rxnorm.Relation(line, concepts)
    except:
        sys.stderr.write("!")
        continue
    if r.relation is not None:
        relations.append(r)
    count += 1
    display_count(count)
print >> sys.stderr

print >> sys.stderr, len(concepts), "concepts and", len(relations), "relations."
print >> sys.stderr, 'Building indices.'
ingredients = {}
ingredient_rel = set(["ingredient_of",
                      "precise_ingredient_of",
                      # rxnorm.relation_kinds.index("has_tradename"),
])

count = 0
for r in relations:
    if r.relation in ingredient_rel:
        if r._concept1.CUI in ingredients:
            ingredients[r._concept1.CUI].add(r._concept2)
        else:
            ingredients[r._concept1.CUI] = set([r._concept2])
    count += 1
    display_count(count)
print >> sys.stderr

concept_names = {}
for c in concepts:
    cn = concepts[c]._name.lower()
    if cn in concept_names:
        concept_names[cn].add(c)
    else:
        concept_names[cn] = set([c])

print >> sys.stderr, "Ingredients for 10 random drugs:"
for x in [random.choice(ingredients.keys()) for x in xrange(10)]:
    print >> sys.stderr, "Ingredients for", concepts[x]._name, ":", [y for y in ingredients[x]]
    print >> sys.stderr, "Ingredients that are Pharmacologic Substances for", concepts[x]._name, ":", ', '.join(
        y._name for y in ingredients[x] if 'Pharmacologic Substance' in y.semtypes)
    print

zoloft = concept_names['zoloft']
for z in zoloft:
    print >> sys.stderr, "Ingredients for", concepts[z]._name, ":", [y for y in ingredients[z]]

conc_file = "concepts." + save_file
print >> sys.stderr, "Shelving concepts to", conc_file
#conc_shelf = dbmaccess.open(conc_file, protocol=pickle.HIGHEST_PROTOCOL)
conc_shelf = dbmaccess.open(conc_file, 'c')
count = 0
for c in concepts:
    conc_shelf[c] = pickle.dumps(concepts[c], pickle.HIGHEST_PROTOCOL)
    count += 1
    display_count(count)

conc_shelf.close()
print >> sys.stderr

ing_file = "ingredients." + save_file
print >> sys.stderr, "Shelving ingredients to", ing_file
#ing_shelf = dbmaccess.open(ing_file, protocol=pickle.HIGHEST_PROTOCOL)
ing_shelf = dbmaccess.open(ing_file, 'c')
count = 0
for i in ingredients:
    ing_shelf[i] = pickle.dumps(ingredients[i], pickle.HIGHEST_PROTOCOL)
    count += 1
    display_count(count)

ing_shelf.close()
print >> sys.stderr

rels_file = "relationships." + save_file
print >> sys.stderr, "Shelving relationships to", rels_file
print >> sys.stderr, "First, building a relationship dictionary."
rel_dict = {}
count = 0
for r in relations:
    rel_id = r.concept1.CUI + "|" + r.concept2.CUI
    if rel_id not in rel_dict:
        rel_dict[rel_id] = []
    rel_dict[rel_id].append(r)
    count += 1
    display_count(count)
print >> sys.stderr

del relations
print >> sys.stderr, "Now actually shelving it."
#rel_shelf = dbmaccess.open(rels_file, protocol=pickle.HIGHEST_PROTOCOL)
rel_shelf = dbmaccess.open(rels_file, 'c')
count = 0
for r in rel_dict:
    rel_shelf[r] = pickle.dumps(rel_dict[r], pickle.HIGHEST_PROTOCOL)
    count += 1
    display_count(count)
rel_shelf.close()
print >> sys.stderr

print >> sys.stderr, "Saving to", save_file
r = rxnorm.RXNORM(conc_file, rels_file, ing_file)
pickle.dump(r, open(save_file, 'wb'), pickle.HIGHEST_PROTOCOL)

