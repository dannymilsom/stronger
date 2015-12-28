from django.db import models

from ..managers import SetManager


class Set(models.Model):
    """
    Each set is performed as part of one workout, but each workout 
    includes a number of sets.
    """

    workout = models.ForeignKey('stronger.Workout', related_name='set')
    exercise = models.ForeignKey('stronger.Exercise', related_name='set')
    weight = models.FloatField()
    reps = models.IntegerField()

    objects = SetManager()

    def __unicode__(self):
        return "{} - {} x {}".format(self.exercise, self.weight, self.reps)

    @property
    def rep_range(self):
        if self.reps <=5:
            return 'strength'
        elif self.reps <=12:
            return 'hypertrophy'
        elif self.reps >=13:
            return 'endurance'
