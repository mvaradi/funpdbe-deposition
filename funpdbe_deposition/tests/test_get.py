from __future__ import unicode_literals
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from funpdbe_deposition.models import Entry


class ApiGetTests(TestCase):
    """
    Testing GET methods of the deposition API
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("test", "test@test.test", "test")
        self.entry = Entry.objects.create(owner_id=1, pdb_id="0x00", data_resource="cath-funsites")

    def tearDown(self):
        User.objects.all().delete()
        Entry.objects.all().delete()

    def generic_get_test(self, url):
        Entry.objects.all().delete()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    """
    Test simple GET for all entries
    This should return 200
    """
    def test_getting_all_entries(self):
        response = self.client.get("/funpdbe_deposition/entries/")
        self.assertEqual(response.status_code, 200)

    """
    Test GET all entries when none exists
    This should return 404
    """
    def test_getting_all_entries_when_none(self):
        self.generic_get_test("/funpdbe_deposition/entries/")

    """
    Test GET with PDB id which does not exist
    This should return 404
    """
    def test_getting_one_by_pdb_id_non(self):
        self.generic_get_test("/funpdbe_deposition/entries/pdb/0x00/")

    """
    Test GET with PDB id
    This should return 200
    """
    def test_getting_one_by_pdb_id(self):
        response = self.client.get("/funpdbe_deposition/entries/pdb/0x00/")
        self.assertEqual(response.status_code, 200)

    """
    Test GET with invalid PDB id
    This should return 400 (bad request)
    """
    def test_getting_one_by_invalid_pdb_id(self):
        response = self.client.get("/funpdbe_deposition/entries/pdb/invalid/")
        self.assertEqual(response.status_code, 400)

    """
    Test GET all by resource
    This should return 200
    """
    def test_getting_all_by_resource(self):
        response = self.client.get("/funpdbe_deposition/entries/resource/cath-funsites/")
        self.assertEqual(response.status_code, 200)

    """
    Test GET all by resource when non entry exists
    This should return 404
    """
    def test_getting_all_by_resource_none(self):
        self.generic_get_test("/funpdbe_deposition/entries/resource/cath-funsites/")

    """
    Test GET with PDB id and resource
    This should return 200
    """
    def test_getting_one_by_pdb_id_and_resource(self):
        response = self.client.get("/funpdbe_deposition/entries/resource/cath-funsites/0x00/")
        self.assertEqual(response.status_code, 200)

    """
    Test GET with PDB id and resource when entry is not there
    This should return 404
    """
    def test_getting_one_by_pdb_id_and_resource_none(self):
        self.generic_get_test("/funpdbe_deposition/entries/resource/cath-funsites/0x00/")

    """
    Test GET all by invalid resource
    This should return 400 (bad request)
    """
    def test_getting_all_by_invalid_resource(self):
        response = self.client.get("/funpdbe_deposition/entries/resource/whatever/")
        self.assertEqual(response.status_code, 400)

    """
    Test GET with PDB id and invalid resource
    This should return 400 (bad request)
    """
    def test_getting_one_by_pdb_id_and_bad_resource(self):
        response = self.client.get("/funpdbe_deposition/entries/resource/whatever/0x00/")
        self.assertEqual(response.status_code, 400)

    """
    Test GET with invalid PDB id and resource
    This should return 400 (bad request)
    """
    def test_getting_one_by_bad_pdb_id_and_resource(self):
        response = self.client.get("/funpdbe_deposition/entries/resource/cath-funsites/whatever/")
        self.assertEqual(response.status_code, 400)