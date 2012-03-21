'''
Created on Mar 20, 2012

@author: cbearden
'''

import unittest
import sys
sys.path.append('..')
import rxnorm
from cStringIO import StringIO
import random

#type_kinds = rxnorm.type_kinds
#reverse_type_kinds = rxnorm.reverse_type_kinds

semtypesFile = StringIO("""C0000001|T109|A1.4.1.2.1|Organic Chemical|AT123456789|256|
C0000001|T121|A1.4.1.1.1|Pharmacologic Substance|AT123456789|256|
C0000002|T109|A1.4.1.2.1|Organic Chemical|AT123456789|256|
C0000002|T121|A1.4.1.1.1|Pharmacologic Substance|AT123456789|256|
C0000003|T109|A1.4.1.2.1|Organic Chemical|AT123456789|256|
C0000003|T121|A1.4.1.1.1|Pharmacologic Substance|AT123456789|256|
C0000003|T131|A1.4.1.1.5|Hazardous or Poisonous Substance|AT123456789|256|
C0000004|T109|A1.4.1.2.1|Organic Chemical|AT123456789|256|
C0000004|T121|A1.4.1.1.1|Pharmacologic Substance|AT123456789|256|
""")

class TestSemanticTypeLine(unittest.TestCase):

    cuisByLine = ('C0000001', 'C0000001', 'C0000002', 'C0000002',
                  'C0000003', 'C0000003', 'C0000003', 'C0000004',
                  'C0000004',)
    semtypesByLine = ('Organic Chemical', 'Pharmacologic Substance',
      'Organic Chemical', 'Pharmacologic Substance', 'Organic Chemical',
      'Pharmacologic Substance', 'Hazardous or Poisonous Substance',
      'Organic Chemical', 'Pharmacologic Substance',)
    typesByCui = {
      'C0000001' : ['Pharmacologic Substance', 'Organic Chemical'],
      'C0000002' : ['Pharmacologic Substance', 'Organic Chemical'],
      'C0000003' : ['Pharmacologic Substance', 'Organic Chemical',
                    'Hazardous or Poisonous Substance'],
      'C0000004' : ['Pharmacologic Substance', 'Organic Chemical'],
    }
    cuisByType  = {
      'Pharmacologic Substance' : ['C0000001', 'C0000002', 'C0000003',
                                   'C0000004',],
      'Organic Chemical'        : ['C0000001', 'C0000002', 'C0000003',
                                   'C0000004',],
      'Hazardous or Poisonous Substance' : ['C0000003',],
    }
    semtypeObjects = []
    semtypesFile.seek(0)
    for semtypeLine in semtypesFile:
        stl = rxnorm.SemanticTypeLine(semtypeLine)
        semtypeObjects.append(stl)
    
    def setUp(self):
        pass
    
    def test_constructor(self):
        for semtypeObject in self.semtypeObjects:
            self.assertTrue(semtypeObject)

    def test_semtype_get(self):
        i = 0
        while i < len(self.semtypeObjects):
            self.assertEqual(self.semtypeObjects[i].semtype,
                             self.semtypesByLine[i])
            i += 1

    def test_semtype_readonly(self):
        stl = random.sample(self.semtypeObjects, 1)[0]
        self.assertRaises(AttributeError, stl.__setattr__, 'semtype', 'Foo')

    def test_CUI_get(self):
        i = 0
        while i < len(self.semtypeObjects):
            self.assertEqual(self.semtypeObjects[i].CUI,
                             self.cuisByLine[i])
            i += 1

    def test_CUI_readonly(self):
        stl = random.sample(self.semtypeObjects, 1)[0]
        self.assertRaises(AttributeError, stl.__setattr__, 'CUI', 'Foo')


class TestDrug(unittest.TestCase):
    
    drugsFile = StringIO("""C0000002|ENG|P|L0000002|PF|S0000002|N|A00000002|234567|7528||RXNORM|IN|7258|Naproxen|0|N|256|
C0000001|ENG|P|L0000001|PF|S0000001|N|A00000001|123345|7685||RXNORM|BN|768|Synflex|0|N|256|
C0000003|ENG|P|L0000003|PF|S0000003|N|A00000003|360443|1298||RXNORM|IN|11289|Warfarin|0|N|256|
C0000004|ENG|P|L0000004|PF|S0000004|N|A00000004|395370|2302||RXNORM|IN|20352|carvedilol|0|N|256|
""")
    typesByCui = {
      'C0000001' : ['Pharmacologic Substance', 'Organic Chemical'],
      'C0000002' : ['Pharmacologic Substance', 'Organic Chemical'],
      'C0000003' : ['Pharmacologic Substance', 'Organic Chemical',
                    'Hazardous or Poisonous Substance'],
      'C0000004' : ['Pharmacologic Substance', 'Organic Chemical'],
    }
    cuisByLine = ('C0000002', 'C0000001', 'C0000003', 'C0000004')
    namesByLine = ('Naproxen', 'Synflex', 'Warfarin', 'carvedilol')
    brandNamesByLine = (False, True, False, False)

    def setUp(self):
        self.drugObjects = []
        self.drugsFile.seek(0)
        for drugLine in self.drugsFile:
            d = rxnorm.Drug(drugLine)
            self.drugObjects.append(d)

    def test_constructor(self):
        for drugObject in self.drugObjects:
            self.assertTrue(drugObject)

    def test_cui_get(self):
        i = 0
        while i < len(self.drugObjects):
            self.assertEqual(self.drugObjects[i].CUI, self.cuisByLine[i])
            i += 1

    def test_cui_readonly(self):
        d = random.sample(self.drugObjects, 1)[0]
        self.assertRaises(AttributeError, d.__setattr__, 'CUI', 'Foo')

    def make_semtypesDict(self):
        semtypesDict = {}
        semtypesFile.seek(0)
        for line in semtypesFile:
            elems = line.split('|')
            cui = elems[0]
            semtype = elems[3]
            #name = elems[3]
            if semtypesDict.get(cui):
                semtypesDict[cui].append(semtype)
            else:
                semtypesDict[cui] = [semtype]
        return semtypesDict

    def semtypes_set(self):
        i = 0
        semtypesDict = self.make_semtypesDict()
        while i < len(self.drugObjects):
            myDrug = self.drugObjects[i]
            myDrug.set_semtypes(semtypesDict[myDrug.CUI])
            i += 1

    def test_semtypes_get(self):
        self.semtypes_set()
        i = 0
        while i < len(self.drugObjects):
            myDrug = self.drugObjects[i]
            cui = myDrug.CUI
            semtypes = myDrug.semtypes
            self.assertEqual(set(semtypes), set(self.typesByCui[cui]))
            i += 1
            
    def test_name_get(self):
        i = 0
        while i < len(self.drugObjects):
            self.assertEqual(self.drugObjects[i].name, self.namesByLine[i])
            i += 1

    def test_is_brandname(self):
        i = 0
        while i < len(self.drugObjects):
            self.assertEqual(self.drugObjects[i].is_brandname, self.brandNamesByLine[i])
            i += 1


if __name__ == "__main__":
    unittest.main()
