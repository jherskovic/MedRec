#!/usr/bin/python

"""Comprehensive test suite for MedRec. 
"""
import unittest
import test_rxnorm
import test_medication
import test_mapping_context
import test_match
import test_drug_problem_kb

allTestsSuite = unittest.TestSuite()
allTestsSuite.addTests(test_rxnorm.allTestsSuite)
allTestsSuite.addTests(test_medication.allTestsSuite)
allTestsSuite.addTests(test_mapping_context.allTestsSuite)
allTestsSuite.addTests(test_match.allTestsSuite)
allTestsSuite.addTests(test_drug_problem_kb.allTestsSuite)

runner = unittest.TextTestRunner()
runner.run(allTestsSuite)