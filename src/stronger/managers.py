from datetime import date, timedelta
import itertools
from operator import attrgetter, itemgetter

from django.db.models import Manager

from . import models


class BodyWeightManager(Manager):

    def get_bodyweight_history(self, user):
        return self.get_queryset.filter(user=user).order_by('-date')

    def current_bodyweight(self, user):
        """The latest bodyweight recorded by a given user."""
        try:
            bodyweight = self.get_queryset.filter(user=user).last()[0]
        except IndexError:
            bodyweight = None
        return bodyweight


class DailyNutritionManager(Manager):

    def most_frequent_users(self, limit=10):
        """
        Returns a list of (user, int) tuples to represent the users 
        who have recorded the most nutritional data.

        A optional kwarg is to denotate the limit of users returned.
        """

        all_nutrition = self.get_queryset.all().order_by('user')
        nutrition_count = []
        for user, nutrition in itertools.groupby(all_nutrition, attrgetter('user')):
            if len(nutrition_count) < limit:
                nutrition_count.append((user, len([i for i in nutrition])))
            else:
                break

        return nutrition_count

    def workout_day_nutrition(self, user, calories_only=False):
    
        wko_dates = models.Workout.objects.workout_dates(user)
        wko_data = self.get_queryset.filter(user=user, date__in=wko_dates)

        if wko_data and calories_only:
            wko_data = sum([n.calories for n in wko_data]) / len(wko_data)
        
        return wko_data

    def rest_day_nutrition(self, user, calories_only=False):

        wko_dates = models.Workout.objects.workout_dates(user)
        rest_data = self.get_queryset.filter(user=user).exclude(date__in=wko_dates)
        if rest_data and calories_only:
            rest_data = sum([n.calories for n in rest_data]) / len(rest_data)
        
        return rest_data


class ExerciseManager(Manager):

    def categorise_exercises(self):
        """
        Returns a list of exercises categorised by a their primary muscle 
        attribute.
        """

        categorised_exercises = []
        all_exercises = self.get_queryset.s.all().order_by('primary_muscle')

        for bodypart, exercises in itertools.groupby(all_exercises,
            key=attrgetter("primary_muscle")):
            categorised_exercises.append([bodypart, [(e, e) for e in exercises]])

        return categorised_exercises


class FriendManager(Manager):
    """
    Extends the Friend model manager, making class like methods available.
    """

    def followers(self, user):
        """
        Returns a QuerySet of Friend instances, representing users following 
        specified the user (passed as positional arg).
        """
        return self.get_queryset.filter(friend=user)

    def following(self, user):
        """
        Returns a QuerySet of Friend instances, representing users the 
        specified has selected to follow (this user is specified by 
        passed as positional arg).
        """
        return self.get_queryset.filter(user=user)


class SetManager(Manager):

    def get_biggest_totals(self, user=None, friends=False):
        """
        Returns the a iterable of tuples denoting users with the largest 
        1RM total - by combining Squat, Deadlift and Bench lifts.

        Each tuple contains (user, squat, deadlift, bench) data.
        """

        exercises = ['squat', 'deadlift', 'bench']

        if user and friends:
            all_sets = self.get_queryset.filter(exercise__clean_name__in=exercises,
                workout__user__in=friends).order_by('workout__user')
        else:
            all_sets = self.get_queryset.filter(exercise__clean_name__in=exercises) \
                .order_by('workout__user')

        total_counter = {}
        for user, sets in itertools.groupby(all_sets, attrgetter('workout.user')):
            total_counter[user] = {}
            for exercise, exercise_sets in itertools.groupby(sorted(sets,
              key=attrgetter('exercise.clean_name')),
              attrgetter('exercise.clean_name')):
                total_counter[user][exercise] = \
                    max([s.weight for s in exercise_sets])

        # now get the totals
        totals_list = []
        for k, v in total_counter.iteritems():
            totals_list.append([k, sum(v.values())])

        sorted_totals = sorted(totals_list, key=itemgetter(1), reverse=True)
        return [(t[0], t[1],
            total_counter[t[0]].get('squat', 0),
            total_counter[t[0]].get('deadlift', 0),
            total_counter[t[0]].get('bench', 0)) for t in sorted_totals]


class WorkoutManager(Manager):
    """
    Custom manager for the Workout model class - adding a range of methods 
    which could be considered class methods.
    """

    def workout_dates(self, user):
        """
        Returns an iterable of ISO formatted dates when a specific user 
        has recorded a workout.
        """

        return [w.date.date() for w in self.get_queryset.filter(user=user)]

    def most_frequent_users(self, limit=10):
        """
        Returns a list of (user, int) tuples to represent the users 
        who have recorded the most workouts.

        A optional kwarg is to denotate the limit of users returned.
        """

        all_workouts = self.get_queryset.all().order_by('user')
        workout_count = []
        for user, workouts in itertools.groupby(all_workouts, attrgetter('user')):
            if len(workout_count) < limit:
                workout_count.append((user, len([i for i in workouts])))
            else:
                break

        return sorted(workout_count, key=itemgetter(1), reverse=True)

    def get_workouts_including_exercise(self, user, exercise):
        """
        Returns a queryset of workout instances that a particular user has 
        logged, which include a specified exercise.
        """

        workouts = self.get_queryset.filter(user=user).order_by('date')
        return [w for w in workouts if w.includes_exercise(exercise)]

    def average_workouts_per_month(self, user=None, history=365):
        """
        Returns an iterable denoting the average number of workouts recorded 
        each month.

        By default this method returns data for the last 365 days and includes 
        all users.
        """

        days_back = history
        end_date = date.today()
        start_date = end_date - timedelta(days=int(days_back))

        if user:
            workouts = self.get_queryset.filter(user=user,
                date__range=(start_date, end_date)).order_by('-date')
        else:
            workouts = self.get_queryset.filter(date__range=(
                start_date, end_date)).order_by('-date')

        temp_counter = {}
        for m, wko in itertools.groupby(workouts, attrgetter('date.month')):
            temp_counter[m] = len([w for w in wko])
        for i in xrange(1, 13):
            if i not in temp_counter:
                temp_counter[i] = 0
        return [v for k, v in sorted(temp_counter.iteritems(),
            key=itemgetter(0))]
