'''
Created on Apr 12, 2012

@author: cbearden
'''
import sys
sys.path.append('..')
import os
import unittest
import cPickle as pickle
import bz2
from mapping_context import MappingContext
#import logging

#logging.basicConfig(filename='test_match.log', level=logging.DEBUG)

#if os.path.isfile('rxnorm.pickle.bz2'):
#    rxnorm = pickle.load(bz2.BZ2File('rxnorm.pickle.bz2', 'r'))
#else:
#    rxnorm = None
#if os.path.isfile('treats.pickle.bz2'):
#    treats = pickle.load(bz2.BZ2File('treats.pickle.bz2', 'r'))
#else:
#    treats = None
#if os.path.isfile('drug_problem_relations.pickle.bz2'):
#    drug_problem_relations = pickle.load(bz2.BZ2File('drug_problem_relations.pickle.bz2', 'r'))
#else:
#    drug_problem_relations = None
#if rxnorm is not None:
#    mappings = MappingContext(rxnorm, treats, drug_problem_relations)
#else:
#    mappings = None

from mappings_for_testing import mappings


class TestMappingContext(unittest.TestCase):
    """A set of tests to ensure that the basic functionality of 
    mapping.MappingContext works as expected.
    """
    
    paxilTreats = set(['C0038454', 'C0020114', 'C0011581', 'C0678222', 'C0030705', 'C0008059', 'C0525045', 'C0030319'])

    @unittest.skipUnless(mappings, 'MappingContext with RXNORM data')
    def test_concept_names(self):
        """Ensure that we get the expected CUI for the given name."""
        self.assertEqual(mappings.concept_names['naproxen injectable solution'], set(['C1250438']))

    @unittest.skipUnless(mappings, 'MappingContext with RXNORM data')
    def test_rxnorm(self):
        """Ensure that we get the expected name for the given concept."""
        self.assertEqual(mappings.rxnorm.concepts['C1250438'].name.lower(), 'Naproxen Injectable Solution'.lower())

    @unittest.skipUnless(mappings, 'MappingContext with RXNORM data')
    @unittest.skipUnless(mappings and mappings.treatment, 'missing treatment data in MappingContext')
    def test_treatment(self):
        """Ensure that the set of entities treated by Paxil is as expected."""
        self.assertEqual(mappings.treatment.get('C0376414'), self.paxilTreats)


loader = unittest.TestLoader()
allTestsSuite = unittest.TestSuite()
allTestsSuite.addTests(loader.loadTestsFromTestCase(TestMappingContext))


if __name__ == "__main__":
    unittest.main()