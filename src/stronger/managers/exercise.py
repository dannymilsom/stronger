import itertools
from operator import attrgetter

from django.db.models import Manager


class ExerciseManager(Manager):

    def categorise_exercises(self):
        """
        Returns a list of exercises categorised by a their primary muscle 
        attribute.
        """

        categorised_exercises = []
        all_exercises = self.get_queryset().all().order_by('primary_muscle')

        for bodypart, exercises in itertools.groupby(all_exercises,
            key=attrgetter("primary_muscle")):
            categorised_exercises.append([bodypart, [(e, e) for e in exercises]])

        return categorised_exercises
