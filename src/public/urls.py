"""Public URL configuration."""

from django.conf.urls import patterns, include, url

from .views import HomeTemplateView, AboutTemplateView

urlpatterns = patterns('',
    url(r'^$', HomeTemplateView.as_view(), name='home'),
    url(r'^about$', AboutTemplateView.as_view(), name='about'),

    # authentication
    url(r'^login$', 'public.views.login', name='login'),
    url(r'^logout$', 'public.views.logout', name='logout'),
    url(r'^signup$', 'public.views.signup', name='signup'),

    # dashboard
     url(r'^dashboard$', 'public.views.dashboard', name='dashboard'),

    # profile
    url(r'^users/(?P<username>[-a-zA-Z0-9]+)/$', 'public.views.profile',
        name='profile'),
    url(r'^user/(?P<username>[-a-zA-Z0-9]+)/(?P<date>[-0-9]+)$',
        'public.views.user_day', name='user_day'),
    url(r'^users/$', 'public.views.users', name='users'),
    url(r'^settings$', 'public.views.settings', name='settings'),

    # workouts
    url(r'^workouts$', 'public.views.workouts', name='workouts'),
    url(r'^workouts/(?P<workout_id>[0-9]+)$', 'public.views.workout',
        name='workout'),
    url(r'^record-workout$', 'public.views.record_workout',
        name='record_workout'),

    # internal workout ajax requests
    url(r'^ajax/workout/(?P<workout_id>[0-9]+)$', 'public.views.ajax_workout',
        name='ajax_workout'),
    url(r'^ajax/workouts/$', 'public.views.ajax_workouts',
        name='ajax_workouts'),

    # meals
    url(r'^nutrition$', 'public.views.nutrition', name='nutrition'),
    url(r'^nutrition/(?P<meal_id>[0-9]+)$', 'public.views.meal', name='meal'),

    # internal meal ajax requests
    url(r'^ajax/nutrition-summary/$', 'public.views.ajax_nutrition_summary',
        name='ajax_nutrition_summary'),

    # exercises
    url(r'^exercises$', 'public.views.exercises', name='exercises'),
    url(r'^exercises/(?P<exercise_name>[-a-zA-Z]+)$', 'public.views.exercise',
        name='exercise'),

    url(r'^ajax/exercises/(?P<exercise_name>[-a-zA-Z]+)$',
        'public.views.ajax_exercise_history', name='ajax_exercise_history'),
    url(r'^ajax/big-three-progress/(?P<username>[-a-zA-Z0-9]+)/$',
        'public.views.ajax_big_three_progress', name='ajax_big_three_progress'),
    url(r'^ajax/popular-exercises$', 'public.views.ajax_popular_exercises',
        name='ajax_popular_exercises'),

    # groups and users
    url(r'^groups/(?P<group_name>[-a-zA-Z0-9]+)$', 'public.views.group',
        name='group'),
    url(r'^groups$', 'public.views.groups', name='groups'),

    # users
    url(r'^users/$', 'public.views.users', name='users'),
)
