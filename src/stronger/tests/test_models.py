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


class TestSelectRealted(TestCase):

    def setUp(self):

        from ..models import Exercise, Workout, Set

        self.danny = UserFactory(username='danny')

        self.rows = Exercise.objects.create(
            name='barbell rows',
            clean_name='barbellrows',
            primary_muscle='Back',
            secondary_muscles='Biceps',
            added_by=self.danny,
        )

        workout1 = Workout.objects.create(
            user=self.danny,
            date=timezone.now().date(),
            description='qqqq',
            comments='dsfdsfsdf'
        )

        workout2 = Workout.objects.create(
            user=self.danny,
            date=timezone.now().date(),
            description='wwww',
            comments='dfgfdg'
        )

        set1 = Set.objects.create(
            workout=workout1,
            exercise=self.rows,
            weight=100,
            reps=10
        )

        set2 = Set.objects.create(
            workout=workout1,
            exercise=self.rows,
            weight=90,
            reps=5
        )

        set3 = Set.objects.create(
            workout=workout2,
            exercise=self.rows,
            weight=110,
            reps=10
        )

        set2 = Set.objects.create(
            workout=workout1,
            exercise=self.rows,
            weight=120,
            reps=5
        )


    def test_raw_query_count(self):
        from ..models import Set
        with self.assertNumQueries(5):
            [s.workout for s in Set.objects.filter(exercise=self.rows)]

    def test_values_list_query_count(self):
        from ..models import Set
        with self.assertNumQueries(1):
            [s for s in Set.objects.filter(exercise=self.rows).values_list('workout', flat=True)]

    def test_select_related_query_count(self):
        from ..models import Set
        with self.assertNumQueries(1):
            [s for s in Set.objects.filter(exercise=self.rows).select_related('workout').values_list('workout', flat=True)]

