"""Serializers for core models."""

from django.contrib.auth import get_user_model

from rest_framework import serializers

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


User = get_user_model()


class BodyWeightSerializer(serializers.ModelSerializer):
    """Model Serializer for the BodyWeight model."""

    class Meta:
        model = BodyWeight
        fields = (
            'user',
            'bodyweight',
            'date',
        )


class DailyNutritionSerializer(serializers.ModelSerializer):
    """Model Serializer for the DailyNutrition model."""

    class Meta:
        model = DailyNutrition


class ExerciseSerializer(serializers.ModelSerializer):
    """Model Serializer for the Exercise model."""

    class Meta:
        model = Exercise
        fields = (
            'name',
            'primary_muscle',
            'secondary_muscles',
        )


class FriendSerializer(serializers.ModelSerializer):
    """Model Serializer for the Friend model."""

    class Meta:
        model = Friend


class GroupSerializer(serializers.ModelSerializer):
    """Model Serializer for the Group model."""

    class Meta:
        model = Group
        fields = (
            'name',
            'about',
            'background_url',
        )


class GroupMembersSerializer(serializers.ModelSerializer):
    """Model Serializer for the GroupMember model."""

    class Meta:
        model = GroupMember
        fields = (
            'user',
            'group',
            'joined',
        )


class SetSerializer(serializers.ModelSerializer):
    """Model Serializer for the Set model."""

    class Meta:
        model = Set


class UserSerializer(serializers.ModelSerializer):
    """Model Serializer for the custom User model."""

    class Meta:
        model = User
        exclude = (
            'password',
            'last_login',
            'user_permissions',
            'is_staff',
        )


class WorkoutSerializer(serializers.ModelSerializer):
    """Model Serializer for the Workout model."""

    sets = serializers.SerializerMethodField('sets_in_workout')

    class Meta:
        model = Workout
        fields = (
            'user',
            'date',
            'description',
            'comments',
            'sets'
        )

    def sets_in_workout(self, obj):
        """Return a nested, serialized representation of all sets performed
        in this workout."""
        return SetSerializer(obj.get_sets(), many=True).data
