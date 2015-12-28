from django.db.models import Manager


class BodyWeightManager(Manager):

    def get_bodyweight_history(self, user):
        return self.get_queryset().filter(user=user).order_by('-date')

    def current_bodyweight(self, user):
        """The latest bodyweight recorded by a given user."""
        try:
            bodyweight = self.get_queryset().filter(user=user).last()[0]
        except IndexError:
            bodyweight = None
        return bodyweight
