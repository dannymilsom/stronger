from django.contrib import admin

from .models import (Friend, Group, GroupMember, Workout, Set, 
                     Exercise, BodyWeight, DailyNutrition)

admin.site.register((Friend, Group, GroupMember, Workout, 
                     Set, Exercise, BodyWeight, DailyNutrition))