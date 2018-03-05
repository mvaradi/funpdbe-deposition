# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from funpdbe_deposition.models import Entry
from funpdbe_deposition.apps import FunpdbeDepositionConfig


class MockData(object):
    """
    This is a mock JSON data which complies with the JSON data schema
    defined at https://github.com/funpdbe-consortium/funpdbe_schema
    """

    def __init__(self):
        self.data = {
            "pdb_id": "2abc",
            "data_resource": "funsites",
            "resource_version": "1.0.0",
            "software_version": "1.0.0",
            "resource_entry_url": "https://example.com/foo/bar",
            "release_date": "01/01/2000",
            "chains": [
                {
                    "chain_label": "A",
                    "chain_annotation": "foo",
                    "residues": [
                        {
                            "pdb_res_label": "1",
                            "aa_type": "ALA",
                            "site_data": [
                                {
                                    "site_id_ref": 1,
                                    "raw_score": 0.7,
                                    "confidence_score": 0.9,
                                    "confidence_classification": "high"
                                }
                            ]
                        }
                    ]
                }
            ],
            "sites": [
                {
                    "site_id": 1,
                    "label": "ligand_binding_site",
                    "source_database": "pdb",
                    "source_accession": "2abc",
                    "source_release_date": "01/01/2000"
                }
            ],
            "evidence_code_ontology": [
                {
                    "eco_term": "computational combinatorial evidence used in automatic assertion",
                    "eco_code": "ECO:0000246"
                },
                {
                    "eco_term": "computational evidence used in automatic assertion",
                    "eco_code": "ECO:0000242"
                }
            ]
        }


class ApiGetTests(TestCase):
    """
    Testing GET methods of the deposition API
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("test", "test@test.test", "test")
        self.entry = Entry.objects.create(owner_id=1, pdb_id="0x00", data_resource="funsites")

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
        response = self.client.get("/funpdbe_deposition/entries/resource/funsites/")
        self.assertEqual(response.status_code, 200)

    """
    Test GET all by resource when non entry exists
    This should return 404
    """
    def test_getting_all_by_resource_none(self):
        self.generic_get_test("/funpdbe_deposition/entries/resource/funsites/")

    """
    Test GET with PDB id and resource
    This should return 200
    """
    def test_getting_one_by_pdb_id_and_resource(self):
        response = self.client.get("/funpdbe_deposition/entries/resource/funsites/0x00/")
        self.assertEqual(response.status_code, 200)

    """
    Test GET with PDB id and resource when entry is not there
    This should return 404
    """
    def test_getting_one_by_pdb_id_and_resource_none(self):
        self.generic_get_test("/funpdbe_deposition/entries/resource/funsites/0x00/")

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
        response = self.client.get("/funpdbe_deposition/entries/resource/funsites/whatever/")
        self.assertEqual(response.status_code, 400)


class ApiPostTests(TestCase):
    """
    Testing POST methods of the deposition API
    """

    def setUp(self):
        self.client = Client()
        self.data = MockData()

    def generic_user_setup(self, resource):
        group = Group.objects.create(name=resource)
        user = User.objects.create_user('test', 'test@test.test', 'test')
        group.user_set.add(user)
        self.client.login(username='test', password='test')

    def generic_post_test(self, resource, url, code):
        self.generic_user_setup(resource)
        response = self.client.post(url, json.dumps(self.data.data), content_type="application/json")
        self.assertEqual(response.status_code, code)

    """
    Test if POST is allowed without providing user login information
    This should fail with 403 (forbidden)
    """
    def test_posting_without_login(self):
        url = "/funpdbe_deposition/entries/resource/funsites/"
        response = self.client.post(url, json.dumps(self.data.data), content_type="application/json")
        self.assertEqual(response.status_code, 403)

    """
    Test if POST is allowed when user does provide login information,
    but does not belong to the group of the resource the user tries 
    to POST to
    For example user "foo" wants to POST to resource "bar", but does not
    have such permission
    This should fail with 403 (forbidden)
    """
    def test_posting_without_permission(self):
        user = User.objects.create_user('test', 'test@test.test', 'test')
        self.client.login(username='test', password='test')
        url = "/funpdbe_deposition/entries/resource/funsites/"
        response = self.client.post(url, json.dumps(self.data.data), content_type="application/json")
        self.assertEqual(response.status_code, 403)

    """
    Test if POST works for a user who has permission to POST to a
    specific resource
    This should succeed with 201 (created)
    """
    def test_posting_with_permission(self):
        self.generic_post_test("funsites", "/funpdbe_deposition/entries/resource/funsites/", 201)

    """
    Test if POST works for a user who has permission to POST to a
    specific resource but POSTs bad data
    This should fail sith 400 (bad request)
    """
    def test_posting_with_permission_but_bad_data(self):
        self.data.data = {}
        self.generic_post_test("funsites", "/funpdbe_deposition/entries/resource/funsites/", 400)

    """
    Test if POST works for a user who has permission to POST to a
    specific resource but POSTs partly bad data
    This should fail sith 400 (bad request)
    """
    def test_posting_with_permission_but_semi_bad_data(self):
        self.data.data = {"data_resource": "funsites"}
        self.generic_post_test("funsites", "/funpdbe_deposition/entries/resource/funsites/", 400)

    """
    Test if POST works for a permitted user who sends data where the resource
    name does not match the intended resource name 
    This should fail with 400 (bad request)
    """
    def test_posting_with_permission_but_resource_mismatch(self):
        self.generic_post_test("nod", "/funpdbe_deposition/entries/resource/nod/", 400)

    """
    Test if POST works for a permitted user who sends data that is
    already in the database
    This should fail with 400 (bad request)
    """
    def test_posting_with_permission_but_entry_is_there_already(self):
        self.generic_user_setup("funsites")
        url = "/funpdbe_deposition/entries/resource/funsites/"
        self.client.post(url, json.dumps(self.data.data), content_type="application/json")
        response_2 = self.client.post(url, json.dumps(self.data.data), content_type="application/json")
        self.assertEqual(response_2.status_code, 400)

    """
    Test if POST works for a user who provides invalid
    resource name
    This should fail with 400 (bad request)
    """
    def test_posting_with_invalid_resource_name(self):
        self.generic_post_test("foo", "/funpdbe_deposition/entries/resource/foo/", 400)


class ApiDeleteTests(TestCase):
    """
    Testing DELETE methods of the deposition API
    """

    def setUp(self):
        self.client = Client()
        self.group = Group.objects.create(name="funsites")
        self.user = User.objects.create_user("test", "test@test.test", "test")
        self.group.user_set.add(self.user)
        self.entry = Entry.objects.create(owner_id=1, pdb_id="0x00", data_resource="funsites")

    def generic_delete_test(self, url, code):
        self.client.login(username='test', password='test')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, code)

    """
    Test if DELETE works for anonymous user
    This should fail with 403 (forbidden)
    """
    def test_deleting_without_login(self):
        response = self.client.delete("/funpdbe_deposition/entries/resource/funsites/0x00/")
        self.assertEqual(response.status_code, 403)

    """
    Test if DELETE works for logged in, but not permitted user
    This should fail with 403 (forbidden)
    """
    def test_deleting_without_permission(self):
        User.objects.create_user('test2', 'test2@test.test', "test2")
        self.client.login(username='test2', password='test2')
        response = self.client.delete("/funpdbe_deposition/entries/resource/funsites/0x00/")
        self.assertEqual(response.status_code, 403)

    """
    Test if DELETE works for permitted user
    This should succeed with 301 (permanently moved)
    """
    def test_deleting_with_permission(self):
        self.generic_delete_test('/funpdbe_deposition/entries/resource/funsites/0x00/', 301)

    """
    Test if DELETE works for permitted user, who is different
    than the entry owner
    This should succeed with 301 (permanently moved)
    """
    def test_deleting_with_permission_but_not_owner(self):
        user2 = User.objects.create_user("test2", "test2@test.test", "test2")
        self.group.user_set.add(user2)
        self.client.login(username='test2', password='test2')
        response = self.client.delete("/funpdbe_deposition/entries/resource/funsites/0x00/")
        self.assertEqual(response.status_code, 301)

    """
    Test if DELETE works when entry does not exist
    this should fail with 404 (not found)
    """
    def test_deleting_when_entry_is_not_there(self):
        self.generic_delete_test('/funpdbe_deposition/entries/resource/funsites/0x42/', 404)

    """
    Test if DELETE works when resource name is invalid
    This should fail with 400 (bad request)
    """
    def test_deleting_when_resource_is_invalid(self):
        self.generic_delete_test('/funpdbe_deposition/entries/resource/invalid/0x00/', 400)

    """
    Test if DELETE works when PDB id in invalid
    This should fail with 400 (bad request)
    """
    def test_deleting_when_pdb_id_is_invalid(self):
        self.generic_delete_test('/funpdbe_deposition/entries/resource/funsites/9999/', 400)


class ApiPutTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.group = Group.objects.create(name="funsites")
        self.user = User.objects.create_user("test", "test@test.test", "test")
        self.group.user_set.add(self.user)
        self.entry = Entry.objects.create(owner_id=1, pdb_id="2abc", data_resource="funsites")
        self.data = MockData()

    def generic_put_test(self, url, code):
        self.client.login(username='test', password='test')
        response = self.client.post(url, json.dumps(self.data.data), content_type="application/json")
        self.assertEqual(response.status_code, code)

    """
    Test if DELETE&POST works when user logged in and permitted
    This should succeed with 201 (created)
    """
    def test_updating(self):
        self.generic_put_test('/funpdbe_deposition/entries/resource/funsites/2abc/', 201)

    """
    Test if DELETE&POST works when user is not logged in
    This should fail with 403 (forbidden)
    """
    def test_updating_when_not_logged_in(self):
        response = self.client.post('/funpdbe_deposition/entries/resource/funsites/2abc/', json.dumps(self.data.data), content_type="application/json")
        self.assertEqual(response.status_code, 403)

    """
    Test if DELETE&POST works when user is logged in but not permitted
    This should fail with 403 (forbidden)
    """
    def test_updating_when_not_allowed(self):
        group2 = Group.objects.create(name="nod")
        user2 = User.objects.create_user("test2", "test2@test.test", "test2")
        group2.user_set.add(user2)
        self.client.login(username='test2', password='test2')
        url = '/funpdbe_deposition/entries/resource/funsites/2abc/'
        response = self.client.post(url, json.dumps(self.data.data), content_type="application/json")
        self.assertEqual(response.status_code, 403)

    """
    Test if DELETE&POST works when user is logged in and permitted,
    but not the owner
    This should succeed with 201 (created)
    """
    def test_updating_with_permission_but_not_owner(self):
        user2 = User.objects.create_user("test2", "test2@test.test", "test2")
        self.group.user_set.add(user2)
        self.client.login(username='test2', password='test2')
        url = '/funpdbe_deposition/entries/resource/funsites/2abc/'
        response = self.client.post(url, json.dumps(self.data.data), content_type="application/json")
        self.assertEqual(response.status_code, 201)

    """
    Test if DELETE&POST works when PDB id in invalid
    This should fail with 400 (bad request)
    """
    def test_updating_with_invalid_pdb(self):
        self.generic_put_test('/funpdbe_deposition/entries/resource/funsites/invalid/', 400)

    """
    Test if DELETE&POST works when entry does not exist
    This should fail with 404 (not found)
    """
    def test_updating_entry_not_existing(self):
        self.generic_put_test('/funpdbe_deposition/entries/resource/funsites/1abc/', 404)

    """
    Test if DELETE&POST works when resource name in invalid
    This should fail with 400 (bad request)
    """
    def test_updating_with_invalid_resource(self):
        self.generic_put_test('/funpdbe_deposition/entries/resource/foo/1abc/', 400)

    """
    Test if DELETE&POST works when JSON is bad
    This should fail with 400 (bad request)
    """
    def test_updating_bad_json(self):
        self.data.data = {}
        self.generic_put_test('/funpdbe_deposition/entries/resource/funsites/2abc/', 400)

    """
    Test if DELETE&POST works when JSON is partially bad
    This should fail with 400 (bad request)
    """
    def test_updating_partly_bad_json(self):
        self.data.data = {"data_resource":"funsites"}
        self.generic_put_test('/funpdbe_deposition/entries/resource/funsites/2abc/', 400)

    """
    Test if DELETE&POST works when the resource name in the JSON
    does not match with the user provided resource name
    This should fail with 400 (bad request)
    """
    def test_updating_when_json_mismatched(self):
        Entry.objects.create(owner_id=1, pdb_id="2abc", data_resource="nod")
        group2 = Group.objects.create(name="nod")
        group2.user_set.add(self.user)
        self.generic_put_test('/funpdbe_deposition/entries/resource/nod/2abc/', 400)


class TestConfig(TestCase):

    def test_config(self):
        self.assertEqual(FunpdbeDepositionConfig.name, "funpdbe_deposition")