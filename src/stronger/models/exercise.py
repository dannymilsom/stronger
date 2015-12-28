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
        Returns a dictionary where the keys are the reps and the values are
        a set object representing the heaviest amount of of weight lifted 
        for a certain exercise.

        If no user kwarg is passed, we return the site wide records.
        """

        pbs = {}
        if user:
            sets_ordered_by_reps = self.set.objects.filter(exercise=self,
                                    workout__user__exact=user).order_by('reps')
        else:
            sets_ordered_by_reps = self.set.filter(exercise=self).order_by('reps')
        for reps, sets in itertools.groupby(sets_ordered_by_reps, attrgetter('reps')):
            pbs[reps] = max(sets, key=attrgetter('weight'))
        return pbs

    def _clean_exercise_name(self):
        """
        Creates a database friendly version of the exercise name, in lower 
        case without whitespace. This is used as part of the URI design.

        For example the name 'Military Press' would be transformed into 
        militarypress.
        """

        return ''.join(self.name.split()).lower()
