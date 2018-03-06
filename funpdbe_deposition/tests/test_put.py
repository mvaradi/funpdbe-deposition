# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from funpdbe_deposition.models import Entry
from funpdbe_deposition.mock_data import MockData


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