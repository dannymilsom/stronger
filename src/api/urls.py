"""API URL configuration."""

from django.conf.urls import patterns, include, url

from .views import (
    BodyWeightList,
    BodyWeightDetail,
    ExerciseList,
    ExerciseDetail,
    FriendList,
    FriendDetail,
    GroupList,
    GroupDetail,
    GroupMemberList,
    NutritionList,
    NutritionDetail,
    UserDetail,
    UserList,
    WorkoutList,
    WorkoutDetail,
)

# TODO - use a router and more generic viewsets
urlpatterns = patterns('',
    url(r'^bodyweight$',BodyWeightList.as_view()),
    url(r'^bodyweight/(?P<pk>[0-9]+)$', BodyWeightDetail.as_view()),

    url(r'^exercises$', ExerciseList.as_view()),
    url(r'^exercises/(?P<clean_name>[-a-zA-Z]+)$', ExerciseDetail.as_view()),

    url(r'^friends$', FriendList.as_view()),
    url(r'^friends/(?P<pk>[0-9]+)$', FriendDetail.as_view()),

    url(r'^groups$', GroupList.as_view()),
    url(r'^groups/(?P<pk>[-a-zA-Z0-9]+)$', GroupDetail.as_view()),
    url(r'^groupmembers/$', GroupMemberList.as_view()),

    url(r'^nutrition$', NutritionList.as_view()),
    url(r'^nutrition/(?P<pk>[0-9]+)$', NutritionDetail.as_view()),

    url(r'^users$', UserList.as_view()),
    url(r'^users/(?P<username>[-a-zA-Z0-9]+)$', UserDetail.as_view()),

    url(r'^workouts$', WorkoutList.as_view()),
    url(r'^workouts/(?P<pk>[0-9]+)$', WorkoutDetail.as_view()),

    url(r'^get-auth-token$', 'rest_framework.authtoken.views.obtain_auth_token'),
)
