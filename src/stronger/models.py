from datetime import datetime
import itertools
from operator import attrgetter

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q

from .constants import GOAL_CHOICES, MUSCLE_GROUPS
from .managers import (
    BodyWeightManager,
    DailyNutritionManager,
    ExerciseManager,
    FriendManager,
    SetManager,
    WorkoutManager,
)


class StrongerUser(AbstractUser):
    """Custom user model for stronger user profile."""

    gym = models.CharField(max_length=30, blank=True)
    goals = models.CharField(choices=GOAL_CHOICES, max_length=10, blank=True)
    about = models.CharField(max_length=200, blank=True)
    height = models.IntegerField(null=True, blank=True)
    gravatar = models.URLField(null=True, 
        default="http://findicons.com/files/icons/1072/face_avatars/300/k04.png"
    )

    def get_absolute_url(self):
        """Returns a canonical URL for a user instance."""
        return reverse('profile', kwargs={'username': self.username})

    @property
    def bodyweight(self):
        """Returns the most recent bodyweight instance for the user."""
        from stronger.models import BodyWeight
        return BodyWeight.objects.current_bodyweight(self)

    def bodyweight_history(self):
        """Returns all bodyweight records relating to the user."""
        from stronger.models import BodyWeight
        return BodyWeight.objects.get_bodyweight_history(self)

    def count_following(self):
        """Returns the number of other users the user is following."""
        from stronger.models import Friend
        return Friend.objects.following(self).count()

    def count_followers(self):
        """Returns the number of followers the user has."""
        from stronger.models import Friend
        return Friend.objects.followers(self).count()

    def count_groups(self):
        """Returns the number of groups a user is a member of."""
        from stronger.models import GroupMember
        return GroupMember.objects.filter(user=self.id).count()

    def count_meals(self):
        """Returns the number of meals a user has recorded."""
        from stronger.models import DailyNutrition
        return DailyNutrition.objects.filter(user=self.id).count()

    def count_photos(self):
        """Returns the number of photos a user has uploaded."""
        return 0

    def count_workouts(self):
        """Returns the number of workouts a user has recorded."""
        from stronger.models import Workout
        return Workout.objects.filter(user=self).count()


class BodyWeight(models.Model):
    """Records the weight of a user on a particular date."""

    date = models.DateField()
    bodyweight = models.IntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    objects = BodyWeightManager()

    class Meta:
        # this is only applicable at the db level (no SQLite support)
        # so we cover this in the clean() method too
        unique_together = ('user', 'date')
        ordering = ('-date',)

    def __unicode__(self):
        return "{} was {} on {}".format(self.user, self.bodyweight, self.date)

    def newsfeed_category(self):
        return 'bodyweight'

    def newsfeed_message(self):
        return "Weighed {} kg".format(self.bodyweight)

    def newsfeed_link(self):
        return "/users/{}".format(self.id)


class DailyNutrition(models.Model):
    """Nutritional record of the food consumed by a user on a given day."""

    date = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    calories = models.IntegerField()
    protein = models.IntegerField()
    carbs = models.IntegerField()
    fats = models.IntegerField()
    created_on = models.DateTimeField()

    objects = DailyNutritionManager()

    def __unicode__(self):
        return "{}".format(self.id)

    def get_absolute_url(self):
        """Returns a canonical URL for a DailyNutrition instance."""
        return reverse('meal', kwargs={'meal_id': self.id})

    def newsfeed_category(self):
        return 'nutrition'

    def newsfeed_message(self):
        return "Consumed {} calories".format(self.calories)


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
            sets_ordered_by_reps = Set.objects.filter(exercise=self,
                                    workout__user__exact=user).order_by('reps')
        else:
            sets_ordered_by_reps = Set.objects.filter(exercise=self).order_by('reps')
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


class Friend(models.Model):
    """Represents the relationship between a user and their follower."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    date = models.DateTimeField(default=datetime.now)

    objects = FriendManager()

    class Meta:
        # this is only applicable at the db level (no SQLite support)
        # so we cover this in the clean() method too
        unique_together = ('user', 'friend')

    def __unicode__(self):
        return self.user.username


class Group(models.Model):
    """
    Represents a group of users who want to share progress
    information.

    Group ID will be used to form URLs and should not
    contain spaces. The name is a user friendly screen label.
    """

    name = models.CharField(max_length=20, primary_key=True)
    about = models.CharField(max_length=500)
    created = models.DateField()
    background_url = models.URLField(
        default="http://uxrepo.com/static/icon-sets/elusive/svg/group.svg")

    def count_members(self):
        """Returns the number of members in a given group."""
        return self.get_members().count()

    def get_members(self):
        """Returns all user object members for a given group."""
        return GroupMember.objects.filter(group=self.name)

    def get_members_usernames(self):
        """Returns a list of all group member usernames."""
        return [m.user.username for m in self.get_members()]

    def get_pending_members(self):
        """Returns a QuerySet of members not yet approved by a group admin."""
        return GroupMember.objects.filter(group=self.group_id, approved=False)

    def get_admin(self):
        """Returns a QuerySet of members with admin permissions."""
        return GroupMember.objects.filter(group=self.group_id, admin=True)

    def get_admin_usernames(self):
        """Returns a list of group member usernames with admin permsissions."""
        return [a.user.username for a in self.get_admin()]

    def __unicode__(self):
        return self.name


class GroupMember(models.Model):
    """User membership for a group."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    group = models.ForeignKey(Group)
    joined = models.DateField()
    approved = models.BooleanField()
    approved_by = models.BooleanField()
    admin = models.BooleanField()

    def __unicode__(self):
        return "{} - {}".format(self.user, self.group)


class Set(models.Model):
    """
    Each set is performed as part of one workout, but each workout 
    includes a number of sets.
    """

    workout = models.ForeignKey('stronger.Workout')
    exercise = models.ForeignKey('stronger.Exercise')
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
        return Set.objects.filter(workout=self)

    def get_exercises(self):
        """Returns all unqiue workout instances in a given workout."""
        return Set.objects.filter(workout=self).values('exercise').distinct()

    def includes_exercise(self, exercise):
        """
        Returns a boolean to indicate if an exercise was performed during a 
        specified workout.
        """
        return True if Set.objects.filter(Q(workout=self) | \
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


# now import signals

import stronger.signals
