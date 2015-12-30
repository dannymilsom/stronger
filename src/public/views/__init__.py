from .about import HomeTemplateView, AboutTemplateView
from .auth import login, logout, signup
from .exercise import (
    exercise,
    exercises,
    ajax_big_three_progress,
    ajax_popular_exercises,
    ajax_exercise_history,
)
from .group import group, groups
from .nutrition import nutrition, meal, ajax_nutrition_summary
from .user import profile, users, dashboard, user_day, settings
from .workout import (
    workout,
    workouts,
    ajax_workout,
    record_workout,
    ajax_workouts,
)
