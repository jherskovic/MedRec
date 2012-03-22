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
import pdb

#type_kinds = rxnorm.type_kinds
#reverse_type_kinds = rxnorm.reverse_type_kinds

semtypesData = """C0000001|T109|A1.4.1.2.1|Organic Chemical|AT123456789|256|
C0000001|T121|A1.4.1.1.1|Pharmacologic Substance|AT123456789|256|
C0000002|T109|A1.4.1.2.1|Organic Chemical|AT123456789|256|
C0000002|T121|A1.4.1.1.1|Pharmacologic Substance|AT123456789|256|
C0000003|T109|A1.4.1.2.1|Organic Chemical|AT123456789|256|
C0000003|T121|A1.4.1.1.1|Pharmacologic Substance|AT123456789|256|
C0000003|T131|A1.4.1.1.5|Hazardous or Poisonous Substance|AT123456789|256|
C0000004|T109|A1.4.1.2.1|Organic Chemical|AT123456789|256|
C0000004|T121|A1.4.1.1.1|Pharmacologic Substance|AT123456789|256|
"""
semtypesFile = StringIO(semtypesData)

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


drugsFile = StringIO("""C0000002|ENG|P|L0000002|PF|S0000002|N|A00000002|234567|7528||RXNORM|IN|7258|Naproxen|0|N|256|
C0000001|ENG|P|L0000001|PF|S0000001|N|A00000001|123345|7685||RXNORM|BN|768|Synflex|0|N|256|
C0000003|ENG|P|L0000003|PF|S0000003|N|A00000003|360443|1298||RXNORM|IN|11289|Warfarin|0|N|256|
C0000004|ENG|P|L0000004|PF|S0000004|N|A00000004|395370|2302||RXNORM|IN|20352|carvedilol|0|N|256|
""")

class TestDrug(unittest.TestCase):
    

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
        self.drugObjects = self.make_drugObjects(drugsFile)

    def test_constructor(self):
        """Test that all drug objects got built."""
        for drugObject in self.drugObjects:
            self.assertTrue(drugObject)

    def test_cui_get(self):
        """Test that CUIs are correctly read from their Drug objects."""
        i = 0
        while i < len(self.drugObjects):
            self.assertEqual(self.drugObjects[i].CUI, self.cuisByLine[i])
            i += 1

    def test_cui_readonly(self):
        """Test that we cannot modify the CUI property."""
        d = random.sample(self.drugObjects, 1)[0]
        self.assertRaises(AttributeError, d.__setattr__, 'CUI', 'Foo')

    @classmethod
    def make_drugObjects(self, drugsFile):
        drugObjects = []
        drugsFile.seek(0)
        for drugLine in drugsFile:
            if drugLine.strip() == '':
                continue
            d = rxnorm.Drug(drugLine)
            drugObjects.append(d)
        return drugObjects

    @classmethod
    def make_semtypesDict(self, semtypesFile):
        """Helper method to make a dictionary of semantic types:
            CUI -> [<semantic type name>, ...]"""
        semtypesDict = {}
        semtypesFile.seek(0)
        for semtypeLine in semtypesFile:
            stl = rxnorm.SemanticTypeLine(semtypeLine)
            cui = stl.CUI
            semtype = stl.semtype
            if semtypesDict.get(cui):
                semtypesDict[cui].append(semtype)
            else:
                semtypesDict[cui] = [semtype]
        return semtypesDict

    @classmethod
    def semtypes_set(self, drugObjects, semtypesFile):
        """Helper method to set semantic types on Drug objects."""
        i = 0
        semtypesDict = self.make_semtypesDict(semtypesFile)
        while i < len(drugObjects):
            myDrug = drugObjects[i]
            myDrug.semtypes = semtypesDict[myDrug.CUI]
            i += 1

    def test_semtypes_get(self):
        """Test that semantic types are correctly read from their Drug objects."""
        self.semtypes_set(self.drugObjects, semtypesFile)
        i = 0
        while i < len(self.drugObjects):
            myDrug = self.drugObjects[i]
            cui = myDrug.CUI
            semtypes = myDrug.semtypes
            self.assertEqual(set(semtypes), set(self.typesByCui[cui]))
            i += 1
            
    def test_name_get(self):
        """Test that drug names are correctly read from their Drug objects."""
        i = 0
        while i < len(self.drugObjects):
            self.assertEqual(self.drugObjects[i].name, self.namesByLine[i])
            i += 1

    def test_name_readonly(self):
        """Test that we cannot modify the name property."""
        d = random.sample(self.drugObjects, 1)[0]
        self.assertRaises(AttributeError, d.__setattr__, 'name', 'Foo')

    def test_is_brandname(self):
        """Test that is_brandname property is correctly read from Drug objects."""
        i = 0
        while i < len(self.drugObjects):
            self.assertEqual(self.drugObjects[i].is_brandname, self.brandNamesByLine[i])
            i += 1

relsFile = StringIO("""C0000002|A0000002|SCUI|RN|C0000006|A0000006|SCUI|tradename_of|R49812212||RXNORM|RXNORM|||N||
C0000002|A0000002|SCUI|RO|C0000009|A0000009|SCUI|has_part|R119278182||RXNORM|RXNORM|||N||
C0000002|A0000002|SCUI|RN|C0000005|A0000005|SCUI|form_of|R45060517||RXNORM|RXNORM|||N||
C0000001|A0000001|SCUI|RB|C0000005|A0000005|SCUI|precise_ingredient_of|R54937606||RXNORM|RXNORM|||N||
C0000001|A0000001|SCUI|RB|C0000002|A0000002|SCUI|has_tradename|R49106210||RXNORM|RXNORM|||N||
C0000001|A0000001|SCUI|RO|C0000010|A0000010|SCUI|has_ingredient|R45440713||RXNORM|RXNORM|||N||
C0000008|A0000008|SCUI|RO|C0000003|A0000003|SCUI|ingredient_of|R111424489||RXNORM|RXNORM|||N||
C0000007|A0000007|SCUI|RB|C0000004|A0000004|SCUI|has_form|R57803279||RXNORM|RXNORM|||N||
""")

class TestRelation(unittest.TestCase):

    drugsPenumbraFile = StringIO("""
C0000005|ENG|P|L0597793|PF|S0694278|N|A16794380|947619|142442||RXNORM|PIN|142442|Naproxen sodium|0|N|256|
C0000006|ENG|P|L5864455|PF|S6708923|Y|A10739551|2381552|603347||RXNORM|BN|603347|Midol Extended Relief|0|N||
C0000007|ENG|P|L6336465|PF|S7264080|Y|A16797269|2605488|668310||RXNORM|PIN|668310|carvedilol phosphate|0|N|256|
C0000008|ENG|P|L1895717|PF|S2895019|Y|A16944408|2978151|855295||RXNORM|SCDC|855295|Warfarin Sodium 10 MG|0|N|256|
C0000009|ENG|P|L9472585|PF|S11770019|Y|A18445510|3297943|1008561||RXNORM|MIN|1008561|Acetaminophen / Naproxen|0|N||
C0000010|ENG|P|L5577617|PF|S6390231|Y|A10664536|2055106|379829||RXNORM|SBDF|379829|Naproxen Oral Tablet [Synflex]|0|O||
""")

    semtypesPenumbra = """C0000005|T109|A1.4.1.2.1|Organic Chemical|AT08642239|256|
C0000005|T121|A1.4.1.1.1|Pharmacologic Substance|AT07968750|256|
C0000006|T109|A1.4.1.2.1|Organic Chemical|AT60330339||
C0000006|T121|A1.4.1.1.1|Pharmacologic Substance|AT60334103||
C0000007|T109|A1.4.1.2.1|Organic Chemical|AT67452078|256|
C0000007|T121|A1.4.1.1.1|Pharmacologic Substance|AT67544285|256|
C0000008|T200|A1.3.3|Clinical Drug|AT116288740|256|
C0000009|T121|A1.4.1.1.1|Pharmacologic Substance|AT128872031||
C0000010|T200|A1.3.3|Clinical Drug|AT37405600||
"""
    semtypesFile = StringIO(semtypesData + semtypesPenumbra)

    def setUp(self):
        drugObjects = TestDrug.make_drugObjects(drugsFile) + TestDrug.make_drugObjects(self.drugsPenumbraFile)
        TestDrug.semtypes_set(drugObjects, self.semtypesFile)
        concepts = {}
        for drugObject in drugObjects:
            concepts[drugObject.CUI] = drugObject
        self.relObjects = self.make_relObjects(relsFile, concepts)

    @classmethod
    def make_relObjects(self, relsFile, concepts):
        relObjects = []
        relsFile.seek(0)
        for relLine in relsFile:
            r = rxnorm.Relation(relLine, concepts)
            relObjects.append(r)
        return relObjects
    
    def test_true(self):
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
