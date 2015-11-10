from collections import defaultdict, Counter
import datetime
import json
from itertools import chain, groupby
import pytz
from operator import attrgetter

from django.conf import settings as stronger_settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView

from stronger.models import (
    BodyWeight,
    DailyNutrition,
    Exercise,
    Friend,
    Group,
    GroupMember,
    Set,
    Workout,
)

from .forms import (
    AddExerciseForm,
    BodyWeightForm,
    DailyNutritionForm,
    EditWorkoutForm,
    FindExerciseForm,
    FindUserForm,
    FindWorkoutForm,
    GroupForm,
    UserSettingsForm,
    LoginForm,
    SetForm,
    UserForm,
    WorkoutForm,
)


User = get_user_model()


class HomeTemplateView(TemplateView):
    """
    Renders the homepage template - with links for users to authenticate 
    or register new accounts.
    """

    template_name = 'home.html'


class AboutTemplateView(TemplateView):
    """
    Renders the about template - describing the motivations behind the 
    site and the technology used to create it.
    """

    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super(AboutTemplateView, self).get_context_data(**kwargs)
        context['github_url'] = stronger_settings.GITHUB_URL
        return context


def login(request):
    """
    Supports authentication for users. The response depends on the request type.
    """

    data = {'login_form': LoginForm}
    authenticated = request.user.is_authenticated()

    if request.method == 'GET':
        # probably re-directed to /login via @login_required
        return render(request, "login.html", data)

    elif request.method == 'POST' and not authenticated:
        user = authenticate(username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user is not None and user.is_active:
            auth_login(request, user)
            authenticated = True

    # check the referer to see if we should redirect or send a JSON response
    if '/login' in request.META['HTTP_REFERER']:
        if authenticated:
            return HttpResponseRedirect(reverse('home'))
        else:
            data['authentication_error'] = True
            return render(request, "login.html", data)
    else:
        return HttpResponse(json.dumps({'authenticated': authenticated}),
            content_type = "application/json")

@login_required
def logout(request):
    """
    Logs a authenticated user out and redirects them to the home page.
    """

    if request.user.is_authenticated():
        auth_logout(request)
        return HttpResponseRedirect(reverse('home'))

def signup(request):
    """
    Supports the creation of new user accounts.
    """

    data = {'signup_form': UserForm}

    if request.method == 'GET':
        # probably re-directed to /login via @login_required
        return render(request, "signup.html", data)

    registered = False
    authenticated = False

    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')

    if all((username, email, password)):
        user = User.objects.create_user(username, email, password)
        registered = True

        # authenticate them
        auth_user = authenticate(username=username, password=password)
        if auth_user is not None and auth_user.is_active:
            auth_login(request, auth_user)
            authenticated = True

    # check the referer to see if we should redirect or send a JSON response
    if '/signup' in request.META['HTTP_REFERER']:
        if authenticated:
            return HttpResponseRedirect(reverse('home'))
        else:
            data['signup_error'] = True
            return render(request, "signup.html", data)
    else:
        return HttpResponse(json.dumps({
            'registered': registered,
            'authenticated': authenticated
        }), content_type = "application/json")

@login_required
def settings(request):
    """
    Renders a form which allows users to modify their account settings.
    """

    if request.method == 'POST':
        user_form = UserSettingsForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()

    data = {'user_form': UserSettingsForm(instance=request.user)}
    return render(request, "settings.html", data)

@login_required
def dashboard(request):
    """
    Renders the dashboard homepage for an authenticated user.
    """

    data = {
        'news': _get_activites(request),
        'friends': User.objects.order_by('date_joined')[:6],
        'js_data': json.dumps({
            'user': request.user.id,
            'username': request.user.username
        })
    }

    return render(request, "dashboard_home.html", data)

@login_required
def profile(request, username):
    """
    Renders a profile page which presents data associated with a 
    particular user. This is a page other users would see.
    """

    user = get_object_or_404(User, username=username)

    data = {
        'news': _get_activites(request, username=username),
        'followers': Friend.objects.followers(user),
        'following': Friend.objects.following(user),
        'user': user,
        'js_data': {
            'user': request.user.id,
            'username': request.user.username,
            'friend': user.id,
            'friend_username': user.username,
        }
    }

    try:
        friendship = Friend.objects.get(user=request.user, friend=user)
        data['already_friends'] = True
        data['js_data']['friendship_id'] = friendship.id
    except Friend.DoesNotExist:
        data['already_friends'] = False
        data['js_data']['friendship_id'] = None

    data['js_data'] = json.dumps(data['js_data'])

    return render(request, "profile.html", data)

@login_required
def user_day(request, username, date):
    """
    Renders a page summarising the activities of a user on a given day.
    """

    user = get_object_or_404(user, username=request.user)

    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise Http404

    data = {
        'date': date,
        'meals': DailyNutrition.objects.filter(user=user, date=date),
        'workouts': Workout.objects.filter(user=user, date=date),
    }

    return render(request, "day.html", data)

### WORKOUTS ###

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

    return HttpResponse(json.dumps(data), content_type="application/json")

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

    return HttpResponse(json.dumps(data), content_type="application/json")

### EXERCISES ###

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

    data = {
        'exercise': exercise,
        'workouts': set([s.workout for s in Set.objects.filter(exercise=exercise)]),
        'edit_exercise_form': AddExerciseForm(instance=exercise),
    }

    return render(request, "exercise.html", data)

@login_required
def exercises(request):
    """
    Page displaying all exercise objects and a form to create new Exercise 
    instances.

    If the submission of a AddExerciseForm is successful, the user is 
    redirected to the page representing the new Exercise instance.
    """

    if request.GET.get('name'):
        # exercise search form
        exercise = Exercise.objects.get(name=request.GET.get('name'))
        return redirect('exercise', exercise_name=exercise.clean_name)

    if request.method == 'POST' and AddExerciseForm(request.POST).is_valid():
        new_exc = AddExerciseForm(request.POST).save(commit=False)
        new_exc.added_by = request.user
        new_exc.save()
        return HttpResponseRedirect(reverse('exercise',
                kwargs={'exercise_name': new_exc.clean_name}))

    following = [f.friend for f in Friend.objects.following(request.user)]
    data = {
        'exercise_count': Exercise.objects.all().count(),
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

    user = get_object_or_404(user, username=request.user)

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

    return HttpResponse(json.dumps(big_three_history),
            content_type = "application/json")

def ajax_popular_exercises(request):

    data = {
        'popular_exercises': Counter([s.exercise.name 
            for s in Set.objects.all()]).most_common(5)
    }

    return HttpResponse(json.dumps(data), content_type = "application/json")

def ajax_exercise_history(request, exercise_name):

    exercise = get_object_or_404(Exercise, clean_name=exercise_name)
    data = {
        'exercise-records': _exercise_records(request.user, exercise),
        'exercise-progress': _exercise_progression(request.user,
            exercise, request.GET.get('reps', '5')),
    }
    return HttpResponse(json.dumps(data), content_type = "application/json")

def _exercise_progression(user, exercise, reps=5):
    """
    Returns the highest weight lifted by a user for a specified exercise, in 
    a particular repo range, in each recorded workout.

    We expect this to demonstrate progression over time - but that is not 
    guaranteed!
    """

    exercise_sets = Set.objects.filter(exercise=exercise, reps=reps,
        workout__user__exact=user)

    history = {}
    for workout, sets in groupby(sorted(exercise_sets,
            key=attrgetter("workout")), key=attrgetter("workout")):
        history[workout.date.strftime("%Y-%m-%d")] = max([s.weight for s in sets])

    return history

def _exercise_records(user, exercise):

    def _format_records(records):
        temp_records = {}
        for i in xrange(1, 11):
            try:
                temp_records[i] = (records[i].weight,
                    records[i].workout.user.username)
            except KeyError:
                temp_records[i] = (0, 'unknown')
        return temp_records

    return {
        'personal_records' : _format_records(exercise.records(user)),
        'site_records': _format_records(exercise.records()),
    }

### NUTRITION ###

@login_required
def nutrition(request):
    """
    Renders a page displaying information about the nutrition of a user.

    This includes macro nutrition information, caloric intake, difference in 
    diet on workout and rest days etc.
    """

    if request.method == 'POST':
        transaction = False
        if ('calories' in request.POST and 
          DailyNutritionForm(request.POST).is_valid()):
            dailyn = DailyNutritionForm(request.POST).save(commit=False)
            dailyn.user = request.user
            dailyn.created_on = datetime.datetime.now()
            dailyn.save()
            transaction = True

        if transaction:
            return HttpResponseRedirect(reverse('meal',
                    kwargs={'meal_id': dailyn.id}))

    following = [f.id for f in Friend.objects.following(request.user)]

    data = {
        'meal_record_form': DailyNutritionForm(),
        'bodyweight_form': BodyWeightForm,
        'bodyweight': request.user.bodyweight_history(),
        'dn_history': DailyNutrition.objects.filter(user=request.user)
            .order_by('-date')[:5],
        'average_workout_kcal': DailyNutrition.objects.workout_day_nutrition(
            request.user, calories_only=True),
        'average_rest_kcal': DailyNutrition.objects.rest_day_nutrition(
            request.user, calories_only=True),
        'most_nutrition': DailyNutrition.objects.most_frequent_users(),
        'friend_nutrition_history': DailyNutrition.objects.filter(
            user__in=following).order_by('-date')[:10],
        'js_data': json.dumps({
            'user_id': request.user.id,
            'username': request.user.username
        })
    }

    return render(request, "nutrition.html", data)

@login_required
def meal(request, meal_id):
    """
    Returns data associated with a particular DailyNutrition instance.
    """

    dn = get_object_or_404(DailyNutrition, id=meal_id)

    if request.method == 'POST':
        dn_form = DailyNutritionForm(request.POST, instance=dn)
        if dn_form.is_valid():
            dn_form.save()

    try:
        workout = Workout.objects.get(user=request.user, date=dn.date)
    except Workout.DoesNotExist:
        workout = False

    data = {
        'nutrition_record': dn,
        'edit_nutrition_form': DailyNutritionForm(instance=dn),
        'workout': workout,
        'js_data': json.dumps({
            'meal-macros': {
                'carbs': dn.carbs,
                'fats': dn.fats,
                'protein': dn.protein,
            }
        })
    }

    return render(request, "meal.html", data)

def ajax_nutrition_summary(request):
    """
    Returns data needed by charts on /dashboard/nutrition. This includes 
    total calories and a macro nutrition break down over a time period, which 
    defaults to 14 days.
    """

    days_back = request.GET.get('days-back', '14')

    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=int(days_back))
    nutrition_history = DailyNutrition.objects.filter(user=request.user,
                    date__range=(start_date, end_date)).order_by('-date')

    calorie_history = dict()
    for daily_nutrition in nutrition_history:
        calorie_history[daily_nutrition.date.strftime("%Y-%m-%d")] \
            = daily_nutrition.calories

    total_macros = defaultdict(int)
    for daily_nutrition in nutrition_history:
        total_macros['fats'] += daily_nutrition.fats
        total_macros['carbs'] += daily_nutrition.carbs
        total_macros['protein'] += daily_nutrition.protein

    # calculate average macro breakdown on WO and non WO days
    workout_macros, rest_macros = _get_macro_breakdown(request.user,
        nutrition_history)

    data = {
        'calorie-tracker': calorie_history,
        'macros': total_macros,
        'macro-breakdown': {
            'workout_days': workout_macros,
            'rest_days': rest_macros,
        }
    }

    return HttpResponse(json.dumps(data), content_type="application/json")

def _get_macro_breakdown(user, data):

    workout_dates = [w.date.date() for w in Workout.objects.filter(user=user)]

    workout_day_nutrition = [n for n in data if n.date in workout_dates]
    off_day_nutrition = [n for n in data if n.date not in workout_dates]

    def calculate_macros(data, dates):

        temp = []
        no_dates = len(dates)

        try:
            # could loop over macro names if models supports __getitem__
            temp.append(sum([n.protein for n in data])/ no_dates)
            temp.append(sum([n.carbs for n in data]) / no_dates)
            temp.append(sum([n.fats for n in data]) / no_dates)
        except ZeroDivisionError:
            pass

        return temp

    return calculate_macros(workout_day_nutrition, workout_dates), \
        calculate_macros(off_day_nutrition, workout_dates)

### USERS ###

@login_required
def users(request):
    """
    Displays information about users who follow the authenticated user, 
    and users who the authenticated user follows.
    """

    if request.GET.get('username'):
        # user search form
        user = User.objects.get(id=request.GET.get('username'))
        return redirect('profile', username=user.username)

    data = {
        'followers': Friend.objects.followers(request.user),
        'following': Friend.objects.following(request.user),
        'new_users': User.objects.order_by('date_joined')[:6],
        'user_count': User.objects.all().count(),
        'find_user_form': FindUserForm(),
    }

    return render(request, "users.html", data)

### GROUPS ###

@login_required
def group(request, group_name):

    group = get_object_or_404(Group, name=group_name)

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()

    data = {
        'group': group,
        'group_form': GroupForm(instance=group)
    }

    return render(request, "group.html", data)

@login_required
def groups(request):
    """
    Renders a page displaying information about Group model instances.
    """

    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            Group.objects.create(name=request.POST.get('name'),
                                  about=request.POST.get('about'),
                                  created=datetime.date.today())
    data = {
        'groups': [g.group for g in GroupMember.objects.filter(
            user=request.user).order_by('-joined')],
        'group_form': GroupForm(),
    }

    return render(request, "groups.html", data)

### Private Methods ###

def _get_activites(request, username=None):

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
