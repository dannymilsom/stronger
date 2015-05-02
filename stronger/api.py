from datetime import datetime

from django.contrib.auth import get_user_model

from rest_framework import generics, filters

from .models import (Group, GroupMember, Friend, Workout, 
                     Exercise, BodyWeight, DailyNutrition)
from .serializer import (GroupSerializer, GroupMembersSerializer, 
                         UserSerializer, FriendSerializer,
                         DailyNutritionSerializer, BodyWeightSerializer,
                         ExerciseSerializer, WorkoutSerializer)

User = get_user_model()


class BodyWeightDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Supports GET, PUT and DELETE requests to view / update / remove a 
    specific BodyWeight instance.
    """

    queryset = BodyWeight.objects.all()
    serializer_class = BodyWeightSerializer


class BodyWeightList(generics.ListCreateAPIView):
    """
    Supports GET and POST requests to view / create BodyWeight instances.
    """

    queryset = BodyWeight.objects.all()
    serializer_class = BodyWeightSerializer
    filter_fields = ('user',)


class ExerciseDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Supports GET, PUT and DELETE requests to view / update / remove a 
    specific Exercise instance.
    """

    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    lookup_field = 'clean_name'


class ExerciseList(generics.ListCreateAPIView):
    """
    Supports GET and POST requests to view / create Exercise instances.
    """

    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    filter_fields = ('primary_muscle',)

    def pre_save(self, obj):
        """
        Set additional attributes which are implicit from the request data.
        """
        obj.added_by = self.request.user
        obj.added_at = datetime.now()


class FriendDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Supports GET, PUT and DELETE requests to view / update / remove a 
    specific Friend instance.
    """

    queryset = Friend.objects.all()
    serializer_class = FriendSerializer


class FriendList(generics.ListCreateAPIView):
    """
    Supports GET and POST requests to view / create Friend instances.
    """

    queryset = Friend.objects.all()
    serializer_class = FriendSerializer


class GroupDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Supports GET, PUT and DELETE requests to view / update / remove a 
    specific Group instance.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class GroupList(generics.ListCreateAPIView):
    """
    Supports GET and POST requests to view / create Group instances.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class GroupMemberDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Supports GET, PUT and DELETE requests to view / update / remove a 
    specific GroupMember instance.
    """

    queryset = GroupMember.objects.all()
    serializer_class = GroupMembersSerializer


class GroupMemberList(generics.ListCreateAPIView):
    """
    Supports GET and POST requests to view / create GroupMember instances.
    """

    queryset = GroupMember.objects.all()
    serializer_class = GroupMembersSerializer

    def pre_save(self, obj):
        """
        Set additional attributes which are implicit from the request data.
        """
        obj.approved = True
        obj.approved_by = True
        obj.admin = False


class NutritionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Supports GET, PUT and DELETE requests to view / update / remove a 
    specific Friend instance.
    """

    queryset = DailyNutrition.objects.all()
    serializer_class = DailyNutritionSerializer


class NutritionList(generics.ListCreateAPIView):
    """
    Supports GET and POST requests to view / create Friend instances.
    """

    queryset = DailyNutrition.objects.all()
    serializer_class = DailyNutritionSerializer
    filter_fields = ('user',)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Supports GET, PUT and DELETE requests to view / update / remove a 
    specific User instance.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'


class UserList(generics.ListCreateAPIView):
    """
    Supports GET and POST requests to view / create User instances.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_fields = ('username',)


class WorkoutDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Supports GET, PUT and DELETE requests to view / update / remove a 
    specific Workout instance.
    """

    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer


class WorkoutList(generics.ListCreateAPIView):
    """
    Supports GET and POST requests to view / create Workout instances.
    """

    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    filter_fields = ('user')


