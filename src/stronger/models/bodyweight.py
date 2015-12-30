from django.conf import settings
from django.db import models

from ..managers import BodyWeightManager


class BodyWeight(models.Model):
    """Records the weight of a user on a particular date."""

    date = models.DateField()
    bodyweight = models.IntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    objects = BodyWeightManager()

    class Meta:
        # this is only applicable at the db level (no SQLite support)
        # so we cover this in the clean() method too
        unique_together = ('user', 'date')
        get_latest_by = 'date'
        ordering = ('-date',)

    def __unicode__(self):
        return "{} was {} on {}".format(self.user, self.bodyweight, self.date)

    def newsfeed_category(self):
        return 'bodyweight'

    def newsfeed_message(self):
        return "Weighed {} kg".format(self.bodyweight)

    def newsfeed_link(self):
        return "/users/{}".format(self.id)
