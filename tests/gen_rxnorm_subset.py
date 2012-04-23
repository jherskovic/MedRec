#!/usr/bin/python

import sys
import os

fileNames = ('MRCONSO.RRF', 'MRSTY.RRF', 'MRREL.RRF',)
coreCuiSet = set([
  'C0002800',
  'C0010525',
  'C0027396',
  'C0043031',
  'C0054836',
  'C0065374',
  'C0070122',
  'C0074393',
  'C0284660',
  'C0376218',
  'C0546873',
  'C0556150',
  'C0701345',
  'C0710779',
  'C0719509',
  'C0721754',
  'C0730987',
  'C0779882',
  'C0876139',
  'C0878174',
  'C0939465',
  'C0981138',
  'C0981139',
  'C0987219',
  'C1170283',
  'C1254306',
  'C1276897',
  'C1606652',
  'C1606780',
  'C1631235',
  'C1815010',
  'C2709901',
  'C2718935',
  'C2929464',
  'C3195286',
])
pathToSubSet = sys.argv[1]
savePath = sys.argv[2]

def matchLineStartRxnorm(line):
    lineElems = line.split('|')
    cui1 = lineElems[0]
    everythingElse = set(lineElems[1:])
    if cui1 in cuiSet and 'RXNORM' in everythingElse:
        return True
    return False

def matchLineStart(line):
    lineElems = line.split('|')
    cui1 = lineElems[0]
    if cui1 in cuiSet:
        return True
    return False

def matchLineAnywhere(line):
    for cui in cuiSet:
        if line.find(cui) >= 0:
            return True
    return False

def getLineMatcher(fileName):
    if fileName == 'MRSTY.RRF':
        return matchLineStart
    else:
        return matchLineStartRxnorm

def progressMeter(count, dotCount, barCount, numCount):
    if count % numCount == 0:
        sys.stdout.write("| %d\n" % count)
        sys.stdout.flush()
    elif count % barCount == 0:
        sys.stdout.write('|')
        sys.stdout.flush()
    elif count % dotCount == 0:
        sys.stdout.write('.')
        sys.stdout.flush()

# Get all RXNORM concepts related to our core concepts
print "Gathering related CUIs"
relatedCuis = set()
i = 0
inFile = open(os.path.join(pathToSubSet, 'MRREL.RRF'))
for line in inFile:
    i += 1
    lineElems = line.split('|')
    cui1, cui2, rel, vocab = lineElems[0], lineElems[4], lineElems[7], lineElems[10]
    if vocab == 'RXNORM' and cui2 in coreCuiSet:
        relatedCuis.add(cui1)
    progressMeter(i, 25000, 250000, 1000000)
inFile.close()
print "\nFound related %d cuis" % len(relatedCuis)

cuiSet = coreCuiSet | relatedCuis

# Make subset
for fileName in fileNames:
    matchLine = getLineMatcher(fileName)
    print "Making %s" % fileName
    inFile = open(os.path.join(pathToSubSet, fileName))
    outFile = open(os.path.join(savePath, fileName), 'w')
    i = 0
    mi = 0
    for line in inFile:
        i += 1
        if matchLine(line):
            mi += 1
            outFile.write(line)
        progressMeter(i, 25000, 250000, 1000000)
    print "\nAcquired %d matching %s lines" % (mi, fileName)
    inFile.close()
    outFile.close()
    print

