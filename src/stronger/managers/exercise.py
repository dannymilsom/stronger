from collections import Counter
import itertools
from operator import attrgetter

from django.db.models import Manager

class ExerciseManager(Manager):

    def categorise_exercises(self):
        """Returns a list of exercises grouped by primary muscle attribute."""
        all_exercises = self.get_queryset().order_by('primary_muscle')

        categorised_exercises = []
        for bodypart, exercises in itertools.groupby(
            all_exercises, key=attrgetter("primary_muscle")):
            categorised_exercises.append(
                (bodypart, [(exercise, exercise) for exercise in exercises])
            )

        return categorised_exercises

    def most_popular(self, limit=5):
        """Returns the most popular exercises by counting the number of sets
        recorded in user workouts."""
        from ..models import Set
        exercise_sets = Set.objects.all().select_related(
            'exercise'
        ).values_list('exercise__name', flat=True)

        return Counter(exercise_sets).most_common(limit)
