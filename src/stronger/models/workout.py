import itertools
from operator import attrgetter

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q

from ..managers import WorkoutManager


class Workout(models.Model):
    """Represents a single workout by a given user."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField()
    description = models.CharField(max_length=100)
    comments = models.CharField(max_length=100)

    objects = WorkoutManager()

    def __unicode__(self):
        return "{}".format(self.id)

    def get_absolute_url(self):
        """Returns a canonical URL for a workout instance."""
        return reverse('workout', kwargs={'workout_id': self.id})

    #custom methods
    def get_sets(self):
        """Returns all sets recorded in the workout."""
        return self.set.filter(workout=self)

    def get_exercises(self):
        """Returns all unqiue workout instances in a given workout."""
        return self.set.filter(workout=self).values('exercise').distinct()

    def includes_exercise(self, exercise):
        """
        Returns a boolean to indicate if an exercise was performed during a 
        specified workout.
        """
        return True if self.set.filter(Q(workout=self) | \
            Q(exercise=exercise)) else False

    def newsfeed_category(self):
        """
        Returns a classificaton of the activity, used to create human 
        readable strings in activity feeds / newsfeeds.
        """
        return 'workout'

    def newsfeed_message(self):
        """
        Returns a description of the activity, used to create human 
        readable strings in activity feeds / newsfeeds.
        """
        return self.description

    def timeline(self):
        """Returns a list of exercise (name, reps) tuples."""
        return [(s.exercise.name, s.reps) for s in self.get_sets()]

    def primary_muscles_targeted(self):
        """
        Returns the number of sets which targeted each primary muscle 
        group during the workout.
        """

        data = {}
        for s in self.get_sets():
            data.setdefault(s.exercise.primary_muscle, 0)
            data[s.exercise.primary_muscle] += 1
        return data

    def sets_in_rep_ranges(self, sets=None):
        """
        Counts the number of sets in each workout which fall into 
        Strength, Hypertrophy and Endurance rep ranges.
        """

        if sets is None:
            sets = self.get_sets()

        return {
            'strength': sets.filter(reps__range=(1, 5)).count(),
            'hypertrophy': sets.filter(reps__range=(6, 12)).count(),
            'endurance': sets.filter(reps__range=(12, 100)).count(),
        }

    def sets_in_rep_ranges_per_exercise(self):
        """TODO - improve this rubbish implementation :/"""

        data = {
            'exercises': [],
            'strength': [],
            'hypertrophy': [],
            'endurance': []
        }

        for exercise, s in itertools.groupby(sorted(self.get_sets(),
            key=attrgetter('exercise.name')), attrgetter('exercise')):

            s_copy = list(s)
            data['exercises'].append(exercise.name)
            data['strength'].append(len([i for i in s_copy
                if i.rep_range == 'strength']))
            data['hypertrophy'].append(len([i for i in s_copy
                if i.rep_range == 'hypertrophy']))
            data['endurance'].append(len([i for i in s_copy
                if i.rep_range == 'endurance']))

        return data

    def sets_in_rep_ranges_per_muscle(self):
        """TODO - stop not being DRY"""

        data = {
            'muscles': [],
            'strength': [],
            'hypertrophy': [],
            'endurance': []
        }

        for muscle, s in itertools.groupby(sorted(self.get_sets(),
                                    key=attrgetter('exercise.primary_muscle')),
                                    attrgetter('exercise.primary_muscle')):
            s_copy = list(s)
            data['muscles'].append(muscle)
            data['strength'].append(len([i for i in s_copy
                                           if i.rep_range == 'strength']))
            data['hypertrophy'].append(len([i for i in s_copy
                                               if i.rep_range == 'hypertrophy']))
            data['endurance'].append(len([i for i in s_copy
                                            if i.rep_range == 'endurance']))

        return data
