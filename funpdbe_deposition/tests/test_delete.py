# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from funpdbe_deposition.models import Entry


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