# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from funpdbe_deposition.mock_data import MockData


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