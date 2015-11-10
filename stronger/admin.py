from django.contrib import admin

from .models import (
    Bodyweight,
    DailyNutrition,
    Exercise,
    Friend,
    Group,
    GroupMember,
    Set,
    Workout,
)

admin.site.register(
    (
        Bodyweight,
        DailyNutrition,
        Exercise,
        Friend,
        Group,
        GroupMember,
        Set,
        Workout,
    )
)
