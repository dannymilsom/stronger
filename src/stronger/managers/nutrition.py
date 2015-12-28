import itertools
from operator import attrgetter

from django.db.models import Manager


class DailyNutritionManager(Manager):

    def most_frequent_users(self, limit=10):
        """
        Returns a list of (user, int) tuples to represent the users 
        who have recorded the most nutritional data.

        A optional kwarg is to denotate the limit of users returned.
        """

        all_nutrition = self.get_queryset().all().order_by('user')
        nutrition_count = []
        for user, nutrition in itertools.groupby(all_nutrition, attrgetter('user')):
            if len(nutrition_count) < limit:
                nutrition_count.append((user, len([i for i in nutrition])))
            else:
                break

        return nutrition_count

    def workout_day_nutrition(self, user, calories_only=False):
        from ..models import Workout
        wko_dates = Workout.objects.workout_dates(user)
        wko_data = self.get_queryset().filter(user=user, date__in=wko_dates)

        if wko_data and calories_only:
            wko_data = sum([n.calories for n in wko_data]) / len(wko_data)
        
        return wko_data

    def rest_day_nutrition(self, user, calories_only=False):
        from ..models import Workout
        wko_dates = Workout.objects.workout_dates(user)
        rest_data = self.get_queryset().filter(user=user).exclude(date__in=wko_dates)
        if rest_data and calories_only:
            rest_data = sum([n.calories for n in rest_data]) / len(rest_data)
        
        return rest_data
