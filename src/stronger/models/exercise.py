from datetime import datetime
import itertools
from operator import attrgetter

from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse

from ..constants import MUSCLE_GROUPS
from ..managers import ExerciseManager


class Exercise(models.Model):
    """
    Describes an excercise (for example Bench Press).

    Note:
        * the clean_name field should not be exposed in forms or other user 
          interfaces, as we over-ride this value in the save() method - see 
          _clean_exercise_name().
    """

    name = models.CharField(primary_key=True, max_length=50)
    clean_name = models.CharField(max_length=50)
    primary_muscle = models.CharField(choices=MUSCLE_GROUPS, max_length=40)
    secondary_muscles = models.CharField(choices=MUSCLE_GROUPS, max_length=40)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    added_at = models.DateTimeField(default=datetime.now)

    objects = ExerciseManager()

    class Meta:
        ordering = ('primary_muscle',)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.clean_name = self._clean_exercise_name()
        super(Exercise, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns a canonical URL for a exercise instance."""
        return reverse('exercise', kwargs={'exercise_name': self.clean_name})

    def records(self, user=None):
        """
        Returns a dictionary where the keys are the reps and the values are a
        set representing the heaviest amount of of weight lifted for a given
        exercise. If no user kwarg is passed, we return the site wide records.
        """
        exercise_sets = self.set.filter(exercise=self).order_by('reps')
        if user:
            exercise_sets.filter(workout__user=user)

        exercise_records = {}
        for reps, sets in itertools.groupby(exercise_sets, attrgetter('reps')):
            exercise_records[reps] = max(sets, key=attrgetter('weight'))

        return exercise_records

    def sum_reps(self, user, time_limit=None):
        """Count the number of reps performed during a given period by a user."""
        if time_limit is None:
            exercise_sets = self.set.filter(
                exercise=self,
                workout__user=user,
            )
        else:
            exercise_sets = self.set.filter(
                exercise=self,
                workout__user=user,
                workout__date__gt=time_limit,
            )
        return exercise_sets.aggregate(models.Sum('reps'))['reps__sum']

    def _clean_exercise_name(self):
        """
        Creates a database friendly version of the exercise name, in lower 
        case without whitespace. This is used as part of the URI design.

        For example the name 'Military Press' would be transformed into 
        militarypress.
        """

        return ''.join(self.name.split()).lower()
