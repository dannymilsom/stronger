from django.db.models import Manager


class BodyWeightManager(Manager):

    def get_bodyweight_history(self, user):
        """Return all bodyweight instances for a given user."""
        return self.get_queryset().filter(user=user)

    def current_bodyweight(self, user):
        """Return latest bodyweight recorded by a given user."""
        try:
            return self.get_queryset().filter(user=user).latest()
        except self.model.DoesNotExist:
            return None
