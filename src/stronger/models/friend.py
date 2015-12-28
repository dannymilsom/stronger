from datetime import datetime

from django.conf import settings
from django.db import models

from ..managers import FriendManager


class Friend(models.Model):
    """Represents the relationship between a user and their follower."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    date = models.DateTimeField(default=datetime.now)

    objects = FriendManager()

    class Meta:
        # this is only applicable at the db level (no SQLite support)
        # so we cover this in the clean() method too
        unique_together = ('user', 'friend')

    def __unicode__(self):
        return self.user.username
