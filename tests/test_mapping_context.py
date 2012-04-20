'''
Created on Apr 12, 2012

@author: cbearden
'''
import sys
sys.path.append('..')
import unittest
import cPickle as pickle
import bz2
from mapping_context import MappingContext
#import logging

#logging.basicConfig(filename='test_match.log', level=logging.DEBUG)

rx = pickle.load(bz2.BZ2File('rxnorm.pickle.bz2', 'r'))
ts = pickle.load(bz2.BZ2File('treats.pickle.bz2', 'r'))
mappings = MappingContext(rx, ts)


class TestMappingContext(unittest.TestCase):
    """A set of tests to ensure that the basic functionality of 
    mapping.MappingContext works as expected.
    """
    
    paxilTreats = set(['C0038454', 'C0020114', 'C0011581', 'C0678222', 'C0030705', 'C0008059', 'C0525045', 'C0030319'])

    def test_concept_names(self):
        """Ensure that we get the expected CUI for the given name."""
        self.assertEqual(mappings.concept_names['naproxen injectable solution'], set(['C1250438']))

    def test_rxnorm(self):
        """Ensure that we get the expected name for the given concept."""
        self.assertEqual(mappings.rxnorm.concepts['C1250438'].name.lower(), 'Naproxen Injectable Solution'.lower())

    def test_treatment(self):
        """Ensure that the set of entities treated by Paxil is as expected."""
        self.assertEqual(mappings.treatment.get('C0376414'), self.paxilTreats)

if __name__ == "__main__":
    unittest.main()