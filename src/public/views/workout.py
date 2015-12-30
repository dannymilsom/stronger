import datetime
from collections import defaultdict
import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse

from ..forms import EditWorkoutForm, WorkoutForm, FindWorkoutForm, SetForm
from stronger.models import Workout, Exercise, Set, Friend

User = get_user_model()


@login_required
def workout(request, workout_id):
    """
    Renders a page representing a single workout object. If the workout_id 
    passed via the URI is not validated, a 404 is raised.

    Data needed by the charts displayed on this page are loaded via ajax 
    request which is routed to ajax_workout().
    """

    workout = get_object_or_404(Workout, id=workout_id)

    if request.method == 'POST':
        workout_form = EditWorkoutForm(request.POST, instance=workout)
        if workout_form.is_valid():
            workout_form.save()

    data = {
        'workout_user': workout.user,
        'workout': workout,
        'edit_workout_form': EditWorkoutForm(instance=workout),
        'user_workouts': Workout.objects.filter(user=workout.user)[:5],
        'js_data': json.dumps({'workout_id': workout_id})
    }

    return render(request, "workout.html", data)

def ajax_workout(request, workout_id):
    """
    Returns data via JSON which can be used to draw various workout charts on 
    a single workout page (rendered via workout()).
    """

    workout = get_object_or_404(Workout, id=workout_id)

    data = {
        'sets': workout.timeline(),
        'rep-ranges': workout.sets_in_rep_ranges(),
        'rep-ranges-per-muscle': workout.sets_in_rep_ranges_per_muscle(),
        'muscle-groups': workout.primary_muscles_targeted(),
    }

    return JsonResponse(data)

@login_required
def workouts(request):
    """
    Renders a page displaying information about workout objects.
    """

    if request.GET.get('name'):
        # workout search form
        workout = Workout.objects.get(id=request.GET.get('name'))
        return redirect('workout', workout_id=workout.id)

    following = [f.friend for f in Friend.objects.following(request.user)]

    data = {
        'most_workouts': Workout.objects.most_frequent_users(),
        'workout_search': FindWorkoutForm(request.user),
        'workout_history': Workout.objects.filter(user=request.user)
            .order_by('-date')[:10],
        'friend_workout_history': Workout.objects.filter(user__in=following)
            .order_by('-date')[:10],
        'js_data': json.dumps({
            'user_id': request.user.id,
            'username': request.user.username
        })
    }

    return render(request, "workouts.html", data)

@login_required
def record_workout(request):
    """
    Renders a page displaying a record workout form.

    Successful submission of a form will see the user redirected to the 
    workout page in question. If any validation errors are detected the 
    record workout page will be rendered again, alongside a list of 
    all the problems identified.
    """

    SetFormSet = formset_factory(SetForm, extra=24)
    set_formset = SetFormSet(request.POST or None, request.FILES or None)
    wko_form =  WorkoutForm(request.POST or None, request.FILES or None)

    data = {
        'workout_form': wko_form,
        'set_formset': set_formset,
    }

    if request.method == 'POST' and wko_form.is_valid() and set_formset.is_valid():
        try:
            wko = wko_form.save(commit=False)
        except ValueError:
            return render(request, "record_workout.html", data)
        else:
            wko.user_id = request.user.id
            wko.save()
            _save_sets(request, wko)

            return HttpResponseRedirect(reverse('workout',
                            kwargs={'workout_id': wko.id}))

    return render(request, "record_workout.html", data)

def _save_sets(request, workout):
    """
    Iterates over the set formset in a POST request, creating a new 
    Set instance for each valid form input.
    """

    for i in range(int(request.POST.get('form-TOTAL_FORMS'))):
        if request.POST.get('form-{0}-exercise'.format(i)):
            Set(workout=workout,
                exercise=Exercise(request.POST.get(
                    'form-{0}-exercise'.format(i), '')),
                weight=request.POST.get(
                    'form-{0}-weight'.format(i), ''),
                reps=request.POST.get(
                    'form-{0}-reps'.format(i), '')).save()
        else:
            continue

def ajax_workouts(request):
    """
    Returns JSON serialised data needed to render highcharts on the 
    workouts page.
    """

    days_back = request.GET.get("days-back", "7")
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=int(days_back))

    recent_workouts = Workout.objects.filter(user=request.user,
        date__range=(start_date, end_date)).order_by('-date')

    # get user workout data
    range_counter = defaultdict(int)
    for wko in recent_workouts:
        for rep_range in wko.sets_in_rep_ranges():
            range_counter[rep_range] += \
                wko.sets_in_rep_ranges()[rep_range]

    # get muscle groups
    muscle_counter = defaultdict(int)
    for wko in recent_workouts:
        for muscle in wko.primary_muscles_targeted():
            muscle_counter[muscle] += wko.primary_muscles_targeted()[muscle]

    data = {
        'week-rep-ranges': range_counter,
        'week-muscle-groups': muscle_counter,
        'average-workout-count': {
            'user_average': Workout.objects.average_workouts_per_month(request.user),
            'site_average': Workout.objects.average_workouts_per_month(),
        }
    }

    return JsonResponse(data)
