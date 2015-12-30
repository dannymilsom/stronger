import datetime
import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, Http404

from ..forms import FindUserForm, UserSettingsForm
from stronger.models import Friend, DailyNutrition, Workout

from .utils import _get_activites

User = get_user_model()


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

    user = get_object_or_404(User, username=request.user)

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
