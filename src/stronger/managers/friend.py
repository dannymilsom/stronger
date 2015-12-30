from django.db.models import Manager


class FriendManager(Manager):

    def followers(self, user):
        """
        Returns a QuerySet of Friend instances, representing users following
        the specified user.
        """
        return self.get_queryset().filter(friend=user).select_related('user')

    def following(self, user):
        """
        Returns a QuerySet of Friend instances, representing users the
        specified has selected to follow.
        """
        return self.get_queryset().filter(user=user).select_related('friend')
