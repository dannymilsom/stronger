from django.conf import settings
from django.db import models


class GroupMember(models.Model):
    """User membership for a group."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    group = models.ForeignKey('stronger.Group')
    joined = models.DateField()
    approved = models.BooleanField(default=False)
    approved_by = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    class Meta:
        ordering = ('-joined',)

    def __unicode__(self):
        return "{} - {}".format(self.user, self.group)
