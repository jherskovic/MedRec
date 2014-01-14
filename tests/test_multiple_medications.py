__author__ = 'Jorge Herskovic <jherskovic@gmail.com>'

import sys

sys.path.append('..')
import unittest
from constants import demo_list_1
import medication
from mappings_for_testing import mappings
from multiple_medications import MultipleMedications


class TestMultipleMedications(unittest.TestCase):
    def setUp(self):
        # Build parsed medications
        self.parsedMeds = [medication.make_medication(med, mappings) for med in demo_list_1]

    def test_known_medications(self):
        # Ensure that the demo medications are the ones we expect for the test!
        self.assertEqual(self.parsedMeds[0].original_string, "Zoloft 50 MG Tablet;TAKE 1 TABLET DAILY.; RPT")
        self.assertEqual(self.parsedMeds[1].original_string, "Warfarin Sodium 2.5 MG Tablet;TAKE AS DIRECTED.; Rx")
        self.assertEqual(self.parsedMeds[2].original_string, "Lipitor 10 MG Tablet;TAKE 1 TABLET DAILY.; Rx")

    def test_known_medications_actually_were_parsed(self):
        self.assertIsInstance(self.parsedMeds[0], medication.ParsedMedication)
        self.assertIsInstance(self.parsedMeds[1], medication.ParsedMedication)
        self.assertIsInstance(self.parsedMeds[2], medication.ParsedMedication)
        self.assertEqual(self.parsedMeds[0].name, 'ZOLOFT')

    def test_build_multiple_medication(self):
        mm = MultipleMedications(self.parsedMeds[0:3])
        self.assertIsInstance(mm, MultipleMedications)

    def test_access_contained_type(self):
        mm = MultipleMedications(self.parsedMeds[0:3])
        self.assertEqual(mm._contained_type, medication.ParsedMedication)

    def test_access_contained_list(self):
        mm = MultipleMedications(self.parsedMeds[0:3])
        self.assertEqual(mm._contained_meds, self.parsedMeds[0:3])

    def test_access_multiple_attributes(self):
        # Get the descriptions of all the drugs at the same time
        mm = MultipleMedications(self.parsedMeds[0:3])
        self.assertEqual(mm.name, ['ZOLOFT', 'WARFARIN SODIUM', 'LIPITOR'])

    def test_access_multiple_callables(self):
        mm = MultipleMedications(self.parsedMeds[0:3])
        mm_dicts = mm.as_dictionary()
        self.assertEqual(mm_dicts[0]['medication_name'], 'ZOLOFT')
        self.assertEqual(mm_dicts[1]['medication_name'], 'WARFARIN SODIUM')
        self.assertEqual(mm_dicts[2]['medication_name'], 'LIPITOR')


if __name__ == '__main__':
    unittest.main()
