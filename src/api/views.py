"""Model based views for API."""

from django.contrib.auth import get_user_model

from rest_framework import viewsets, filters

from stronger.models import (
    BodyWeight,
    DailyNutrition,
    Exercise,
    Friend,
    Group,
    GroupMember,
    Workout,
)

from .serializers import (
    BodyWeightSerializer,
    DailyNutritionSerializer,
    ExerciseSerializer,
    FriendSerializer,
    GroupSerializer,
    GroupMembersSerializer,
    UserSerializer,
    WorkoutSerializer,
)

from .mixins import AuthorPreSaveMixin

User = get_user_model()


class BodyWeightViewSet(viewsets.ModelViewSet):
    """Viewset for the BodyWeight model."""

    queryset = BodyWeight.objects.all()
    serializer_class = BodyWeightSerializer
    filter_fields = ('user,')


class ExerciseViewSet(AuthorPreSaveMixin, viewsets.ModelViewSet):
    """Viewset for the Exercise model."""

    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    lookup_field = 'clean_name'


class FriendViewSet(viewsets.ModelViewSet):
    """Viewset for the Friend model."""

    queryset = Friend.objects.all()
    serializer_class = FriendSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """Viewset for the Group model."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class GroupMemberViewSet(viewsets.ModelViewSet):
    """Viewset for the GroupMember model."""

    queryset = GroupMember.objects.all()
    serializer_class = GroupMembersSerializer

    def pre_save(self, obj):
        """Set additional attributes which are implicit from the request."""
        obj.approved = True
        obj.approved_by = True
        obj.admin = False


class NutritionViewSet(viewsets.ModelViewSet):
    """Viewset for the Nutrition model."""

    queryset = DailyNutrition.objects.all()
    serializer_class = DailyNutritionSerializer
    filter_fields = ('user',)


class UserViewSet(viewsets.ModelViewSet):
    """Viewset for the User model."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'


class WorkoutViewSet(viewsets.ModelViewSet):
    """Viewset for the Workout model."""

    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    filter_fields = ('user',)
