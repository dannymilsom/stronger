from collections import defaultdict
from datetime import timedelta
import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone

from ..forms import DailyNutritionForm, BodyWeightForm, Friend
from stronger.models import DailyNutrition, Workout

User = get_user_model()


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
            dailyn.created_on = timezone.now().date()
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

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=int(days_back))
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

    return JsonResponse(data)

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
