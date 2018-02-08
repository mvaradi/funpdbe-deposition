# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.auth.models import Group


class MockData(object):

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
                    "eco_term": "manually_curated",
                    "eco_code": "ECO000042"
                }
            ]
        }


class ApiTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.data = MockData()


    """
    Test if POST is allowed without providing user login information
    This should fail with 403 (forbidden)
    """
    def test_posting_without_login(self):
        response = self.client.post("/funpdbe_deposition/entries/resource/funsites/", data=self.data.data)
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
        response = self.client.post("/funpdbe_deposition/entries/resource/funsites/", data=self.data.data)
        self.assertEqual(response.status_code, 403)
        self.client.logout()
        user.delete()


    """
    Test if POST works for a user who has permission to POST to a
    specific resource
    
    This should succeed with 201 (created)
    """
    def test_posting_with_permission(self):
        group = Group.objects.create(name="funsites")
        user = User.objects.create_user('test', 'test@test.test', 'test')
        group.user_set.add(user)
        self.client.login(username='test', password='test')
        response = self.client.post("/funpdbe_deposition/entries/resource/funsites/", data=self.data.data)
        self.assertEqual(response.status_code, 201)
        self.client.logout()
        user.delete()
        group.delete()


    """
    Test if POST works for a permitted user who sends data where the resource
    name does not match the intended resource name 
    
    This should fail with 400 (bad request)
    """
    def test_posting_with_permission_but_resource_mismatch(self):
        group = Group.objects.create(name="nod")
        user = User.objects.create_user('test', 'test@test.test', 'test')
        group.user_set.add(user)
        self.client.login(username='test', password='test')
        response = self.client.post("/funpdbe_deposition/entries/resource/nod/", data=self.data.data)
        self.assertEqual(response.status_code, 400)
        self.client.logout()
        user.delete()
        group.delete()

    """
    Test if POST works for a permitted user who sends data that is
    already in the database

    This should fail with 400 (bad request)
    """

    def test_posting_with_permission_but_entry_is_there_already(self):
        group = Group.objects.create(name="funsites")
        user = User.objects.create_user('test', 'test@test.test', 'test')
        group.user_set.add(user)
        self.client.login(username='test', password='test')
        self.client.post("/funpdbe_deposition/entries/resource/funsites/", data=self.data.data)
        response_2 = self.client.post("/funpdbe_deposition/entries/resource/funsites/", data=self.data.data)
        self.assertEqual(response_2.status_code, 400)
        self.client.logout()
        user.delete()
        group.delete()


    """
    Test simple GET for all entries
    
    This should return 200
    """
    def test_getting_all_entries(self):
        response = self.client.get("/funpdbe_deposition/entries/")
        self.assertEqual(response.status_code, 200)