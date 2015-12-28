from datetime import date, timedelta
import itertools
from operator import attrgetter, itemgetter

from django.db.models import Manager


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

        return [w.date.date() for w in self.get_queryset().filter(user=user)]

    def most_frequent_users(self, limit=10):
        """
        Returns a list of (user, int) tuples to represent the users 
        who have recorded the most workouts.

        A optional kwarg is to denotate the limit of users returned.
        """

        all_workouts = self.get_queryset().all().order_by('user')
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

        workouts = self.get_queryset().filter(user=user).order_by('date')
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
            workouts = self.get_queryset().filter(user=user,
                date__range=(start_date, end_date)).order_by('-date')
        else:
            workouts = self.get_queryset().filter(date__range=(
                start_date, end_date)).order_by('-date')

        temp_counter = {}
        for m, wko in itertools.groupby(workouts, attrgetter('date.month')):
            temp_counter[m] = len([w for w in wko])
        for i in xrange(1, 13):
            if i not in temp_counter:
                temp_counter[i] = 0
        return [v for k, v in sorted(temp_counter.iteritems(),
            key=itemgetter(0))]
