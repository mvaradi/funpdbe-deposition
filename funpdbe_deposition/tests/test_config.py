# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from funpdbe_deposition.apps import FunpdbeDepositionConfig


class TestConfig(TestCase):

    def test_config(self):
        self.assertEqual(FunpdbeDepositionConfig.name, "funpdbe_deposition")