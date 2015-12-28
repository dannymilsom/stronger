from django.db.models import Manager


class FriendManager(Manager):
    """
    Extends the Friend model manager, making class like methods available.
    """

    def followers(self, user):
        """
        Returns a QuerySet of Friend instances, representing users following 
        specified the user (passed as positional arg).
        """
        return self.get_queryset().filter(friend=user)

    def following(self, user):
        """
        Returns a QuerySet of Friend instances, representing users the 
        specified has selected to follow (this user is specified by 
        passed as positional arg).
        """
        return self.get_queryset().filter(user=user)
