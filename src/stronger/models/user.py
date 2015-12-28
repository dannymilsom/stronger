from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.urlresolvers import reverse

from ..constants import GOAL_CHOICES


class StrongerUser(AbstractUser):
    """Custom user model for stronger user profile."""

    class Meta:
        app_label ='stronger'

    gym = models.CharField(max_length=30, blank=True)
    goals = models.CharField(choices=GOAL_CHOICES, max_length=10, blank=True)
    about = models.CharField(max_length=200, blank=True)
    height = models.IntegerField(null=True, blank=True)
    gravatar = models.URLField(null=True, 
        default="http://findicons.com/files/icons/1072/face_avatars/300/k04.png"
    )

    def get_absolute_url(self):
        """Returns a canonical URL for a user instance."""
        return reverse('profile', kwargs={'username': self.username})

    @property
    def bodyweight(self):
        """Returns the most recent bodyweight instance for the user."""
        from . import BodyWeight
        return BodyWeight.objects.current_bodyweight(self)

    def bodyweight_history(self):
        """Returns all bodyweight records relating to the user."""
        from . import BodyWeight
        return BodyWeight.objects.get_bodyweight_history(self)

    def count_following(self):
        """Returns the number of other users the user is following."""
        from . import Friend
        return Friend.objects.following(self).count()

    def count_followers(self):
        """Returns the number of followers the user has."""
        from . import Friend
        return Friend.objects.followers(self).count()

    def count_groups(self):
        """Returns the number of groups a user is a member of."""
        from . import GroupMember
        return GroupMember.objects.filter(user=self.id).count()

    def count_meals(self):
        """Returns the number of meals a user has recorded."""
        from . import DailyNutrition
        return DailyNutrition.objects.filter(user=self.id).count()

    def count_photos(self):
        """Returns the number of photos a user has uploaded."""
        return 0

    def count_workouts(self):
        """Returns the number of workouts a user has recorded."""
        from . import Workout
        return Workout.objects.filter(user=self).count()
