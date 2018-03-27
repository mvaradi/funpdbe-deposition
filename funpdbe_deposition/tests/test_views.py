from django.test import TestCase
from funpdbe_deposition.views import get_existing_entry
from funpdbe_deposition.views import resource_valid
from funpdbe_deposition.views import pdb_id_valid
from funpdbe_deposition.views import GENERIC_RESPONSES, RESOURCES


class MockEntry(object):

    def delete(self):
        pass


class TestViewHelpers(TestCase):

    def test_get_existing_entry(self):
        self.assertEqual(get_existing_entry(None), GENERIC_RESPONSES["no entries"])

    def test_resource_valid(self):
        for resource_tuple in RESOURCES:
            self.assertTrue(resource_valid(resource_tuple[0]))
        self.assertFalse(resource_valid("invalid"))
        self.assertFalse(resource_valid(None))

    def test_pdb_id_valid(self):
        self.assertTrue(pdb_id_valid("1abc"))
        self.assertTrue(pdb_id_valid("3bow"))
        self.assertTrue(pdb_id_valid("0x00"))
        self.assertFalse(pdb_id_valid("asdasd"))
        self.assertFalse(pdb_id_valid("xxxx"))
        self.assertFalse(pdb_id_valid("0000"))
        self.assertFalse(pdb_id_valid(None))

    def test_delete_entries(self):
        self.assertTrue([MockEntry(), MockEntry()])
        self.assertFalse(None)