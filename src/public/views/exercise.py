import json
from itertools import groupby
from operator import attrgetter

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse

from ..forms import AddExerciseForm, FindExerciseForm, Friend
from stronger.models import Exercise, Set

User = get_user_model()


@login_required
def exercise(request, exercise_name):
    """
    Renders a page displaying information and charts relating to a specific
    Exercise instance.
    """

    exercise = get_object_or_404(Exercise, clean_name=exercise_name)

    if request.method == 'POST':
        exercise_form = AddExerciseForm(request.POST, instance=exercise)
        if exercise_form.is_valid():
            exercise_form.save()

    workouts_including_exercise = [
        s.workout for s in Set.objects.filter(
            exercise=exercise
        ).select_related('workout')
    ]

    data = {
        'exercise': exercise,
        'workouts': workouts_including_exercise,
        'edit_exercise_form': AddExerciseForm(instance=exercise),
    }

    return render(request, "exercise.html", data)

@login_required
def exercises(request):
    """
    Page displaying all exercise instances and an Exercise form.

    If the submission of a AddExerciseForm is successful, the user is 
    redirected to the page representing the new Exercise instance.
    """

    if request.GET.get('name'):
        # exercise search form
        exercise = Exercise.objects.get(name=request.GET.get('name'))
        return redirect('exercise', exercise_name=exercise.clean_name)

    if request.method == 'POST' and AddExerciseForm(request.POST).is_valid():
        new_excercise = AddExerciseForm(request.POST).save(commit=False)
        new_excercise.added_by = request.user
        new_excercise.save()

        return HttpResponseRedirect(
            reverse(
                'exercise', kwargs={'exercise_name': new_excercise.clean_name}
            )
        )

    following = [friend for friend in Friend.objects.following(request.user)]
    data = {
        'exercise_count': Exercise.objects.count(),
        'exercise_form': AddExerciseForm(),
        'exercise_search': FindExerciseForm(),
        'recently_added': Exercise.objects.all().order_by('-added_at')[:4],
        'biggest_totals': Set.objects.get_biggest_totals(),
        'biggest_friend_totals': Set.objects.get_biggest_totals(
            request.user, friends=following),
        'js_data': json.dumps({
            'user': request.user.id,
            'username': request.user.username
        })
    }

    return render(request, "exercises.html", data)

def ajax_big_three_progress(request, username):
    """
    Returns the ajax history for the three big powerlifting exercises - 
    squat, deadlift and bench.
    """

    user = get_object_or_404(User, username=request.user)

    big_three_history = {
        'squat': _exercise_history(user,
            get_object_or_404(Exercise, clean_name='squat')),
        'deadlift': _exercise_history(user,
            get_object_or_404(Exercise, clean_name='deadlift')),
        'bench': _exercise_history(user,
            get_object_or_404(Exercise, clean_name='bench'))
    }

    # we only want to keep the greatest weight lifted per workout
    for exercise, history in big_three_history.iteritems():
        big_three_history[exercise] = dict((d, max(w)) 
            for d, w in history.iteritems())

    return JsonResponse(big_three_history)

def ajax_popular_exercises(request):
    """Return the most popular exercises."""
    data = {
        'popular_exercises': Exercise.objects.most_popular(5)
    }
    return JsonResponse(data)

def ajax_exercise_history(request, exercise_name):

    exercise = get_object_or_404(Exercise, clean_name=exercise_name)
    data = {
        'exercise-records': _exercise_records(request.user, exercise),
        'exercise-progress': _exercise_progression(request.user,
            exercise, request.GET.get('reps', '5')),
    }
    return JsonResponse(data)

def _exercise_progression(user, exercise, reps=5):
    """
    Returns the highest weight lifted by a user for a specified exercise, in
    a particular rep range, in each recorded workout.

    We expect this to demonstrate progression over time - but that is not
    guaranteed!
    """
    exercise_sets = Set.objects.filter(
        exercise=exercise,
        reps=reps,
        workout__user=user
    )

    history = {}
    exercises_sorted_by_workout = sorted(exercise_sets, key=attrgetter("workout"))
    for workout, sets in groupby(
        exercises_sorted_by_workout, key=attrgetter("workout")):
        history[workout.date.strftime("%Y-%m-%d")] = max([s.weight for s in sets])

    return history

def _exercise_records(user, exercise):
    """Returns the user specific and site wide records of the heavies weight
    used to perform varied reps of a given exercise."""

    def _format_records(records):
        temp_records = {}
        for i in xrange(1, 11):
            try:
                record = records[i]
            except KeyError:
                temp_records[i] = (0, None)
            else:
                temp_records[i] = (record.weight, record.workout.user.username)
        return temp_records

    return {
        'personal_records' : _format_records(exercise.records(user)),
        'site_records': _format_records(exercise.records()),
    }
