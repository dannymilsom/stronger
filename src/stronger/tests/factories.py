from datetime import timedelta

from django.utils import timezone

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from .. import models


class UserFactory(DjangoModelFactory):
    class Meta:
        model = models.StrongerUser

    username = fuzzy.FuzzyText(length=15)
    email = factory.LazyAttribute(lambda a: '{}@example.com'.format(a.username).lower())
    password = fuzzy.FuzzyText(length=8)


class BodyweightFactory(DjangoModelFactory):
    class Meta:
        model = models.BodyWeight

    user = factory.SubFactory(UserFactory)
    bodyweight = fuzzy.FuzzyInteger(150)
    date = fuzzy.FuzzyDate(timezone.now().date() - timedelta(weeks=52))
