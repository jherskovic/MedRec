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


class TestSemanticTypeLine(unittest.TestCase):

    semtypeLines = """C0000001|T109|A1.4.1.2.1|Organic Chemical|AT123456789|256|
C0000001|T121|A1.4.1.1.1|Pharmacologic Substance|AT123456789|256|
C0000002|T109|A1.4.1.2.1|Organic Chemical|AT123456789|256|
C0000002|T121|A1.4.1.1.1|Pharmacologic Substance|AT123456789|256|
C0000003|T109|A1.4.1.2.1|Organic Chemical|AT123456789|256|
C0000003|T121|A1.4.1.1.1|Pharmacologic Substance|AT123456789|256|
C0000003|T131|A1.4.1.1.5|Hazardous or Poisonous Substance|AT123456789|256|
C0000004|T109|A1.4.1.2.1|Organic Chemical|AT123456789|256|
C0000004|T121|A1.4.1.1.1|Pharmacologic Substance|AT123456789|256|
"""
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
    semtypesFile = StringIO(semtypeLines)
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
        self.assertRaises(AttributeError, stl.semtype.__setattr__, 'semtype', 'Foo')

    def test_CUI_get(self):
        i = 0
        while i < len(self.semtypeObjects):
            self.assertEqual(self.semtypeObjects[i].CUI,
                             self.cuisByLine[i])
            i += 1

    def test_CUI_readonly(self):
        stl = random.sample(self.semtypeObjects, 1)[0]
        self.assertRaises(AttributeError, stl.semtype.__setattr__, 'CUI', 'Foo')


class TestDrug(unittest.TestCase):
    
    drugLines = """C0002800|ENG|P|L0039089|PF|S0090601|N|A10336519|23345|768||RXNORM|BN|768|Synflex|0|N|256|
C0027396|ENG|P|L0027396|PF|S0065163|N|A10335927|235877|7258||RXNORM|IN|7258|Naproxen|0|N|256|
C0043031|ENG|P|L0043031|PF|S0005681|N|A10334524|360443|11289||RXNORM|IN|11289|Warfarin|0|N|256|
C0054836|ENG|P|L0054836|PF|S0141520|N|A10337004|395370|20352||RXNORM|IN|20352|carvedilol|0|N|256|
"""

if __name__ == "__main__":
    unittest.main()
