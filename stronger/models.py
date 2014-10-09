from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q

from datetime import datetime, date, timedelta
import itertools
from operator import attrgetter, itemgetter


class StrongerUser(AbstractUser):
    """
    Extends the built in django AbstractUser Class, to add additional 
    attributes useful for this app.
    """

    GOAL_CHOICES = (
        ('bb', 'Body Building'),
        ('pl', 'Powerlifting'),
        ('ft', 'Fitness'),
        ('sm', 'Strongman'),
    )

    gym = models.CharField(max_length=30)
    goals = models.CharField(choices=GOAL_CHOICES, max_length=10)
    about = models.CharField(max_length=200)
    height = models.IntegerField(null=True)
    gravatar = models.URLField(null=True, 
        default="http://findicons.com/files/icons/1072/face_avatars/300/k04.png")

    def get_absolute_url(self):
        """
        Returns a canonical URL for a user instance.
        """
        return reverse('profile', kwargs={'username': self.username})

    @property
    def bodyweight(self):
        """
        Returns the most recent bodyweight recording for the user.
        """

        try:
            return BodyWeight.objects.filter(user=self.id).order_by('-date')[:1][0].bodyweight
        except IndexError:
            return None

    def bodyweight_history(self):
        """
        Returns a QuerySet of bodyweight instanes, detailing the bodyweight of 
        a user over time.
        """
        return BodyWeight.objects.get_bodyweight_history(self)

    def count_following(self):
        """
        Returns the number of other users the user instance is following.
        """
        return Friend.objects.following(self).count()

    def count_followers(self):
        """
        Returns the number of followers a user instance has.
        """
        return Friend.objects.followers(self).count()

    def count_groups(self):
        """
        Returns the number of groups a user is a member of.
        """
        return GroupMember.objects.filter(user=self.id).count()

    def count_meals(self):
        """
        Returns the number of meals a user has recorded.
        """
        return DailyNutrition.objects.filter(user=self.id).count()

    def count_photos(self):
        """
        Returns the number of photos a user has uploaded.
        """
        return 0

    def count_workouts(self):
        """
        Returns te number of workouts a user has recorded.
        """
        return Workout.objects.filter(user=self).count()


class FriendManager(models.Manager):
    """
    Extends the Friend model manager, making class like methods available.
    """

    def followers(self, user):
        """
        Returns a QuerySet of Friend instances, representing users following 
        specified the user (passed as positional arg).
        """
        return Friend.objects.filter(friend=user)

    def following(self, user):
        """
        Returns a QuerySet of Friend instances, representing users the 
        specified has selected to follow (this user is specified by 
        passed as positional arg).
        """
        return Friend.objects.filter(user=user)


class Friend(models.Model):
    """
    Represents the relationship between a user and their follower.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    date = models.DateTimeField(default=datetime.now)
    manager = FriendManager()

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
        """
        Returns the number of members in a given group.
        """
        return self.get_members().count()

    def get_members(self):
        """
        Returns a QuerySet of GroupMember objects for a given group.
        """
        return GroupMember.objects.filter(group=self.name)

    def get_members_usernames(self):
        """
        Returns a iterable of GroupMember usernames.
        """
        return [m.user.username for m in self.get_members()]

    def get_pending_members(self):
        """
        Returns a QuerySet of members not yet approved by a group admin.
        """
        return GroupMember.objects.filter(group=self.group_id, approved=False)

    def get_admin(self):
        """
        Returns a QuerySet of members with admin permissions.
        """
        return GroupMember.objects.filter(group=self.group_id, admin=True)

    def get_admin_usernames(self):
        """
        Returns a iterable of group member usernames.
        """
        return [a.user.username for a in self.get_admin()]

    def __unicode__(self):
        return self.name


class GroupMember(models.Model):
    """
    Each row represents a user in a membership group.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    group = models.ForeignKey(Group)
    joined = models.DateField()
    approved = models.BooleanField()
    approved_by = models.BooleanField()
    admin = models.BooleanField()

    def __unicode__(self):
        return "{} - {}".format(self.user, self.group)

class WorkoutManager(models.Manager):
    """
    Custom manager for the Workout model class - adding a range of methods 
    which could be considered class methods.
    """

    def workout_dates(self, user):
        """
        Returns an iterable of ISO formatted dates when a specific user 
        has recorded a workout.
        """

        return [w.date.date() for w in Workout.objects.filter(user=user)]

    def most_frequent_users(self, limit=10):
        """
        Returns a list of (user, int) tuples to represent the users 
        who have recorded the most workouts.

        A optional kwarg is to denotate the limit of users returned.
        """

        all_workouts = Workout.objects.all().order_by('user')
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

        workouts = Workout.objects.filter(user=user).order_by('date')
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
            workouts = Workout.objects.filter(user=user,
                date__range=(start_date, end_date)).order_by('-date')
        else:
            workouts = Workout.objects.filter(date__range=(
                start_date, end_date)).order_by('-date')

        temp_counter = {}
        for m, wko in itertools.groupby(workouts, attrgetter('date.month')):
            temp_counter[m] = len([w for w in wko])
        for i in xrange(1, 13):
            if i not in temp_counter:
                temp_counter[i] = 0
        return [v for k, v in sorted(temp_counter.iteritems(),
            key=itemgetter(0))]

class Workout(models.Model):
    """
    Represents a single workout.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField()
    description = models.CharField(max_length=100)
    comments = models.CharField(max_length=100)

    objects = WorkoutManager()

    def __unicode__(self):
        return "{}".format(self.id)

    def get_absolute_url(self):
        """
        Returns a canonical URL for a workout instance.
        """
        return reverse('workout', kwargs={'workout_id': self.id})

    #custom methods
    def get_sets(self):
        """
        Returns a QuerySet of set instances recorded in the workout.
        """
        return Set.objects.filter(workout=self)

    def get_exercises(self):
        """
        Returns a QuerySet of all unqiue workout instances in a given workout.
        """
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
        """
        Returns a iterable of exercise name, rep tuples.
        """
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
        """
        This is a terrible implementation done in a rush.
        """

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
        """
        Violating some DRY here - this needs a rework.
        """

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

class ExerciseManager(models.Manager):

    def categorise_exercises(self):
        """
        Returns a list of exercises categorised by a their primary muscle 
        attribute.
        """

        categorised_exercises = []
        all_exercises = Exercise.objects.all().order_by('primary_muscle')

        for bodypart, exercises in itertools.groupby(all_exercises,
            key=attrgetter("primary_muscle")):
            categorised_exercises.append([bodypart, [(e, e) for e in exercises]])

        return categorised_exercises


class Exercise(models.Model):
    """
    Describes an excercise (for example Bench Press).

    Note:
        * the clean_name field should not be exposed in forms or other user 
          interfaces, as we over-ride this value in the save() method - see 
          _clean_exercise_name().
    """

    MUSCLE_CHOICES = (
        ('Triceps', 'Triceps'),
        ('Biceps', 'Biceps'),
        ('Back', 'Back'),
        ('Glutes', 'Glutes'),
        ('Hamstrings', 'Hamstrings'),
        ('Calves', 'Calves'),
        ('Quads', 'Quads'),
        ('Abs', 'Abs'),
        ('Forearms', 'Forearms'),
        ('Chest', 'Chest'),
        ('Shoulders', 'Shoulders'),
        ('Traps', 'Traps'),
    )

    name = models.CharField(primary_key=True, max_length=50)
    clean_name = models.CharField(max_length=50)
    primary_muscle = models.CharField(choices=MUSCLE_CHOICES, max_length=40)
    secondary_muscles = models.CharField(choices=MUSCLE_CHOICES, max_length=40)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    added_at = models.DateTimeField(default=datetime.now)

    objects = ExerciseManager()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.clean_name = self._clean_exercise_name()
        super(Exercise, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Returns a canonical URL for a exercise instance.
        """
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


class SetManager(models.Manager):

    def get_biggest_totals(self, user=None, friends=False):
        """
        Returns the a iterable of tuples denoting users with the largest 
        1RM total - by combining Squat, Deadlift and Bench lifts.

        Each tuple contains (user, squat, deadlift, bench) data.
        """

        exercises = ['squat', 'deadlift', 'bench']

        if user and friends:
            all_sets = Set.objects.filter(exercise__clean_name__in=exercises,
                workout__user__in=friends).order_by('workout__user')
        else:
            all_sets = Set.objects.filter(exercise__clean_name__in=exercises) \
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


class Set(models.Model):
    """
    Each set is performed as part of one workout, but each workout 
    includes a number of sets.
    """

    workout = models.ForeignKey(Workout)
    exercise = models.ForeignKey(Exercise)
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


class BodyWeightManager(models.Manager):

    def get_bodyweight_history(self, user):

        return BodyWeight.objects.filter(user=user).order_by('-date')

class BodyWeight(models.Model):
    """
    Records the weight of each user on a particular date.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    bodyweight = models.IntegerField()
    date = models.DateField()

    objects = BodyWeightManager()

    class Meta:
        # this is only applicable at the db level (no SQLite support)
        # so we cover this in the clean() method too
        unique_together = ('user', 'date')

    def __unicode__(self):
        return "{} was {} on {}".format(self.user, self.bodyweight, self.date)

    def newsfeed_category(self):
        return 'bodyweight'

    def newsfeed_message(self):
        return "Weighed {} kg".format(self.bodyweight)

    def newsfeed_link(self):
        return "/users/{}".format(self.id)


class DailyNutritionManager(models.Manager):

    def most_frequent_users(self, limit=10):
        """
        Returns a list of (user, int) tuples to represent the users 
        who have recorded the most nutritional data.

        A optional kwarg is to denotate the limit of users returned.
        """

        all_nutrition = DailyNutrition.objects.all().order_by('user')
        nutrition_count = []
        for user, nutrition in itertools.groupby(all_nutrition, attrgetter('user')):
            if len(nutrition_count) < limit:
                nutrition_count.append((user, len([i for i in nutrition])))
            else:
                break

        return nutrition_count

    def workout_day_nutrition(self, user, calories_only=False):
    
        wko_dates = Workout.objects.workout_dates(user)
        wko_data = DailyNutrition.objects.filter(user=user, date__in=wko_dates)

        if wko_data and calories_only:
            wko_data = sum([n.calories for n in wko_data]) / len(wko_data)
        
        return wko_data

    def rest_day_nutrition(self, user, calories_only=False):

        wko_dates = Workout.objects.workout_dates(user)
        rest_data = DailyNutrition.objects.filter(user=user) \
                                      .exclude(date__in=wko_dates)
        if rest_data and calories_only:
            rest_data = sum([n.calories for n in rest_data]) / len(rest_data)
        
        return rest_data

class DailyNutrition(models.Model):
    """
    Macro nutritional summary of the food consumed on a particular day 
    by a specific user.
    """

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
        """
        Returns a canonical URL for a DailyNutrition instance.
        """
        return reverse('meal', kwargs={'meal_id': self.id})

    def newsfeed_category(self):
        return 'nutrition'

    def newsfeed_message(self):
        return "Consumed {} calories".format(self.calories)

# now import signals

import stronger.signals