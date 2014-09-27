from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
admin.autodiscover()

from stronger.api import (GroupList, GroupDetail, GroupMemberList,
                         UserDetail, FriendList, FriendDetail, WorkoutList,
                         WorkoutDetail, ExerciseList, BodyWeightList,
                         BodyWeightDetail, UserList, NutritionList, 
                         NutritionDetail, ExerciseDetail)

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="home.html"), name='home'),
    url(r'^about$', TemplateView.as_view(template_name="about.html"), 
        name='about'),

    # authentication
    url(r'^login$', 'stronger.views.login', name='login'),
    url(r'^logout$', 'stronger.views.logout', name='logout'),
    url(r'^signup$', 'stronger.views.signup', name='signup'),

    # dashboard
     url(r'^dashboard$', 'stronger.views.dashboard', name='dashboard'),

    # profile
    url(r'^users/(?P<username>[-a-zA-Z0-9]+)/$', 'stronger.views.profile',
        name='profile'),
    url(r'^user/(?P<username>[-a-zA-Z0-9]+)/(?P<date>[-0-9]+)$',
        'stronger.views.user_day', name='user_day'),
    url(r'^users/$', 'stronger.views.users', name='users'),
    url(r'^settings$', 'stronger.views.settings', name='settings'),

    # workouts
    url(r'^workouts$', 'stronger.views.workouts', name='workouts'),
    url(r'^workouts/(?P<workout_id>[0-9]+)$', 'stronger.views.workout',
        name='workout'),
    url(r'^record-workout$', 'stronger.views.record_workout',
        name='record_workout'),

    # internal workout ajax requests
    url(r'^ajax/workout/(?P<workout_id>[0-9]+)$', 'stronger.views.ajax_workout',
        name='ajax_workout'),
    url(r'^ajax/workouts/$', 'stronger.views.ajax_workouts',
        name='ajax_workouts'),

    # meals
    url(r'^nutrition$', 'stronger.views.nutrition', name='nutrition'),
    url(r'^nutrition/(?P<meal_id>[0-9]+)$', 'stronger.views.meal', name='meal'),

    # internal meal ajax requests
    url(r'^ajax/nutrition-summary/$', 'stronger.views.ajax_nutrition_summary',
        name='ajax_nutrition_summary'),

    # exercises
    url(r'^exercises$', 'stronger.views.exercises', name='exercises'),
    url(r'^exercises/(?P<exercise_name>[-a-zA-Z]+)$', 'stronger.views.exercise',
        name='exercise'),

    url(r'^ajax/exercises/(?P<exercise_name>[-a-zA-Z]+)$',
        'stronger.views.ajax_exercise_history', name='ajax_exercise_history'),
    url(r'^ajax/big-three-progress/(?P<username>[-a-zA-Z0-9]+)/$',
        'stronger.views.ajax_big_three_progress', name='ajax_big_three_progress'),
    url(r'^ajax/popular-exercises$', 'stronger.views.ajax_popular_exercises',
        name='ajax_popular_exercises'),

    # groups and users
    url(r'^groups/(?P<group_name>[-a-zA-Z0-9]+)$', 'stronger.views.group',
        name='group'),
    url(r'^groups$', 'stronger.views.groups', name='groups'),

    # users
    url(r'^users/$', 'stronger.views.users', name='users'),

    # api
    url(r'^api/get-auth-token$', 'rest_framework.authtoken.views.obtain_auth_token'),

    url(r'^api/users$', UserList.as_view()),
    url(r'^api/users/(?P<username>[-a-zA-Z0-9]+)$', UserDetail.as_view()),

    url(r'^api/workouts$', WorkoutList.as_view()),
    url(r'^api/workouts/(?P<pk>[0-9]+)$', WorkoutDetail.as_view()),

    url(r'^api/exercises$', ExerciseList.as_view()),
    url(r'^api/exercises/(?P<clean_name>[-a-zA-Z]+)$', ExerciseDetail.as_view()),

    url(r'^api/nutrition$', NutritionList.as_view()),
    url(r'^api/nutrition/(?P<pk>[0-9]+)$', NutritionDetail.as_view()),

    url(r'^api/friends$', FriendList.as_view()),
    url(r'^api/friends/(?P<pk>[0-9]+)$', FriendDetail.as_view()),

    url(r'^api/groups$', GroupList.as_view()),
    url(r'^api/groups/(?P<pk>[-a-zA-Z0-9]+)$', GroupDetail.as_view()),
    url(r'^api/groupmembers/$', GroupMemberList.as_view()),

    url(r'^api/bodyweight$',BodyWeightList.as_view()),
    url(r'^api/bodyweight/(?P<pk>[0-9]+)$', BodyWeightDetail.as_view()),

    # admin
    url(r'^admin/', include(admin.site.urls)),
)
