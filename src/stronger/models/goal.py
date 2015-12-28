from django.conf import settings
from django.db import models


class Goal(models.Model):
    """Exercise specific goals a user aims to reach before a given date."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    exercise = models.ForeignKey('stronger.Exercise')
    weight = models.FloatField()
    reps = models.IntegerField()
    objective_date = models.DateField()
    completed_date = models.DateField()

    def __unicode__(self):
        return "{} goal for {}".format(self.exercise, self.goal)

    @property
    def completed(self):
        return True if self.completed_date else False
