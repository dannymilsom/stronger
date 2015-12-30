import datetime
from itertools import chain
import pytz
from operator import attrgetter

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from stronger.models import Workout, DailyNutrition, BodyWeight

User = get_user_model()


def _get_activites(request, username=None):
    """Get all timeline activities."""

    if username:
        user = get_object_or_404(User, username=username)
        workouts = Workout.objects.filter(user=user).order_by('-date')
        nutrition = DailyNutrition.objects.filter(user=user).order_by('-date')
        bodyweight = BodyWeight.objects.filter(user=user).order_by('date')
    else:
        workouts = Workout.objects.all().order_by('-date')
        nutrition = DailyNutrition.objects.all().order_by('-date')
        bodyweight = BodyWeight.objects.all().order_by('date')

    # we need to transform date objects into datetime objects
    # otherwise the comparison with attrgetter() will raise a TypeError
    for d in chain(nutrition, bodyweight):
        # to make the new date timezone area we use the pytz package
        d.date = pytz.utc.localize(datetime.datetime.combine(d.date,
            datetime.datetime.min.time()))

    return sorted(chain(workouts, nutrition, bodyweight),
        key=attrgetter('date'), reverse=True)[:10]
