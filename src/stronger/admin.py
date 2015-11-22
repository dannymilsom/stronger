from django.contrib import admin

from .models import (
    BodyWeight,
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
        BodyWeight,
        DailyNutrition,
        Exercise,
        Friend,
        Group,
        GroupMember,
        Set,
        Workout,
    )
)
