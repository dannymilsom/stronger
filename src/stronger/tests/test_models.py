from datetime import timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

import factory

from .factories import UserFactory, BodyweightFactory
from ..models import BodyWeight

User = get_user_model()


class TestBodyweightModel(TestCase):

    def setUp(self):
        self.danny = UserFactory(username='danny')
        self.steve = UserFactory(username='steve')

        today = timezone.now().date()
        last_week = today - timedelta(days=7)

        self.danny_bodyweights = BodyweightFactory.create_batch(
            2,
            user=self.danny,
            date=factory.Iterator([today, last_week]),
        )

        self.steve_bodyweights = BodyweightFactory.create_batch(
            2,
            user=self.steve,
            date=factory.Iterator([today, last_week]),
        )

    def test_bodyweight_history(self):
        """Assert that the get_bodyweight_history method returns all instances
        with a reference to the given user in descending date order."""
        self.assertEqual(
            list(BodyWeight.objects.get_bodyweight_history(self.danny)),
            self.danny_bodyweights
        )

    def test_current_bodyweight(self):
        """Assert that the current bodyweight method returns the latest
        bodyweight instance recorded by a given user."""
        self.assertEqual(
            BodyWeight.objects.current_bodyweight(self.danny),
            self.danny_bodyweights[0]
        )

