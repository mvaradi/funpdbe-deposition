from __future__ import unicode_literals
from django.test import TestCase
from django.contrib.auth.models import User
from funpdbe_deposition.serializers import EntrySerializer

class TestEntrySerializer(TestCase):

    def setUp(self):
        self.es = EntrySerializer()

    def test_create_chains_or_residues(self):
        self.assertIsNone(self.es.create_chains_or_residues(None, None, None))