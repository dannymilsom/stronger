"""API URL configuration."""

from django.conf.urls import patterns, include, url

from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    BodyWeightViewSet,
    ExerciseViewSet,
    FriendViewSet,
    GroupViewSet,
    GroupMemberViewSet,
    NutritionViewSet,
    UserViewSet,
    WorkoutViewSet,
)


router = routers.DefaultRouter()
router.register(r'bodyweight', BodyWeightViewSet)
router.register(r'exercises', ExerciseViewSet)
router.register(r'friends', FriendViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'groupmembers', GroupMemberViewSet)
router.register(r'nutrition', NutritionViewSet)
router.register(r'users', UserViewSet)
router.register(r'workouts', WorkoutViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^get-auth-token$', obtain_auth_token),
)
