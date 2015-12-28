import itertools
from operator import attrgetter, itemgetter

from django.db.models import Manager


class SetManager(Manager):

    def get_biggest_totals(self, user=None, friends=False):
        """
        Returns the a iterable of tuples denoting users with the largest 
        1RM total - by combining Squat, Deadlift and Bench lifts.

        Each tuple contains (user, squat, deadlift, bench) data.
        """

        exercises = ['squat', 'deadlift', 'bench']

        if user and friends:
            all_sets = self.get_queryset().filter(exercise__clean_name__in=exercises,
                workout__user__in=friends).order_by('workout__user')
        else:
            all_sets = self.get_queryset().filter(exercise__clean_name__in=exercises) \
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
